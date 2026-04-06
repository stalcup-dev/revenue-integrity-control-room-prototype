from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.control_story import next_action_for_root_cause
from ri_control_room.ui.shared import (
    PageStoryCue,
    StoryCallout,
    SummaryFilters,
    apply_filters,
    empty_summary,
    format_count,
    format_currency,
    get_global_filter_options,
    get_global_filters,
    get_filter_options,
    load_work_population,
    normalize_filters,
    render_active_filter_summary,
    render_page_story_cue,
    scope_global_filters,
)
from ri_control_room.ui.theme import (
    KpiCard,
    panel,
    render_dataframe,
    render_kpi_row,
    render_page_shell,
    render_section_header,
    render_table_section,
)


QUEUE_NAME = "Documentation Support Exceptions"
MISSING_TIME_GAPS = {"missing_stop_time", "missing_case_timestamp"}
TREND_BUSINESS_DAY_WINDOW = 10


@dataclass(frozen=True)
class DocumentationExceptionsView:
    filters: SummaryFilters
    filter_options: dict[str, tuple[str, ...]]
    filtered_population: pd.DataFrame
    story_cue: PageStoryCue
    unsupported_charge_trend: pd.DataFrame
    missing_time_docs: pd.DataFrame
    mismatch_summary: pd.DataFrame
    owner_routing: pd.DataFrame
    worklist: pd.DataFrame
    unsupported_exception_count: int


def _load_inputs(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        load_processed_artifact("documentation_events", repo_root),
        load_processed_artifact("expected_charge_opportunities", repo_root),
    )


def _base_population(repo_root: Path | None = None) -> pd.DataFrame:
    population = load_work_population(repo_root)
    return population.loc[population["current_queue"] == QUEUE_NAME].copy()


def _documentation_history_scope(
    repo_root: Path | None,
    filters: SummaryFilters,
) -> pd.DataFrame:
    population = load_work_population(repo_root)
    scoped_population = apply_filters(population, filters)
    scope_lookup = scoped_population[
        [
            "claim_id",
            "account_id",
            "encounter_id",
            "department",
            "service_line",
            "recoverability_status",
            "estimated_gross_dollars",
        ]
    ].drop_duplicates(["claim_id", "account_id", "encounter_id"])

    queue_history = load_processed_artifact("queue_history", repo_root).sort_values(
        ["claim_id", "account_id", "encounter_id", "transition_event_index"]
    )
    queue_history["next_queue_entry_ts"] = queue_history.groupby(
        ["claim_id", "account_id", "encounter_id"]
    )["current_queue_entry_ts"].shift(-1)
    history = queue_history.loc[queue_history["current_queue"] == QUEUE_NAME].copy()
    history = history.merge(
        scope_lookup,
        on=["claim_id", "account_id", "encounter_id"],
        how="inner",
    )
    return history


def _unsupported_charge_trend(
    filtered: pd.DataFrame,
    *,
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> pd.DataFrame:
    normalized_filters = normalize_filters(filters)
    history = _documentation_history_scope(repo_root, normalized_filters)
    if filtered.empty or history.empty:
        return empty_summary(["snapshot_date", "unsupported_exceptions", "recoverable_dollars"])
    trend_end = pd.Timestamp(filtered["queue_snapshot_ts"].max()).normalize()
    business_days = pd.bdate_range(end=trend_end, periods=TREND_BUSINESS_DAY_WINDOW)
    rows: list[dict[str, object]] = []
    for day in business_days:
        day_end = day + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        active = history.loc[
            (pd.to_datetime(history["current_queue_entry_ts"]) <= day_end)
            & (
                history["next_queue_entry_ts"].isna()
                | (pd.to_datetime(history["next_queue_entry_ts"]) > day_end)
            )
        ]
        rows.append(
            {
                "snapshot_date": day.date(),
                "unsupported_exceptions": int(len(active)),
                "recoverable_dollars": round(float(active["estimated_gross_dollars"].sum()), 2),
            }
        )
    return pd.DataFrame(rows)


def _missing_time_docs(filtered: pd.DataFrame, documentation_events: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(["encounter_id", "documentation_gap_type", "documentation_type", "documentation_status"])
    subset = documentation_events.loc[
        documentation_events["encounter_id"].isin(filtered["encounter_id"])
        & documentation_events["documentation_gap_type"].isin(MISSING_TIME_GAPS),
        ["encounter_id", "documentation_gap_type", "documentation_type", "documentation_status"],
    ].copy()
    return subset.sort_values(["encounter_id", "documentation_gap_type"]).reset_index(drop=True)


def _mismatch_bucket(gap_type: str) -> str:
    if gap_type in {"missing_device_linkage", "missing_implant_linkage"}:
        return "Order / documentation / admin mismatch"
    if gap_type == "missing_laterality":
        return "Order / documentation mismatch"
    if gap_type in MISSING_TIME_GAPS:
        return "Missing time documentation"
    return "Other documentation support failure"


def _mismatch_summary(filtered: pd.DataFrame, documentation_events: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(["mismatch_type", "open_exceptions"])
    subset = documentation_events.loc[
        documentation_events["encounter_id"].isin(filtered["encounter_id"])
        & (documentation_events["documentation_gap_type"].fillna("") != ""),
        ["documentation_gap_type"],
    ].copy()
    if subset.empty:
        return empty_summary(["mismatch_type", "open_exceptions"])
    subset["mismatch_type"] = subset["documentation_gap_type"].map(_mismatch_bucket)
    summary = (
        subset.groupby("mismatch_type", as_index=False)
        .size()
        .rename(columns={"size": "open_exceptions"})
        .sort_values(["open_exceptions", "mismatch_type"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return summary


def _owner_routing(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(["accountable_owner", "current_queue", "open_exceptions", "recoverable_dollars"])
    summary = (
        filtered.groupby(["accountable_owner", "current_queue"], as_index=False)
        .agg(
            open_exceptions=("queue_item_id", "size"),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(["open_exceptions", "recoverable_dollars"], ascending=[False, False])
        .reset_index(drop=True)
    )
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    return summary


def _operator_gap_label(gap_label: str) -> str:
    mapping = {
        "missing_case_timestamp": "Missing case time support",
        "missing_stop_time": "Missing stop-time support",
        "missing_laterality": "Missing laterality support",
        "missing_device_linkage": "Missing device linkage support",
        "missing_implant_linkage": "Missing implant linkage support",
        "Missing time documentation": "Missing case or stop-time support",
        "Order / documentation mismatch": "Order-to-documentation mismatch",
        "Order / documentation / admin mismatch": "Device or implant linkage mismatch",
        "Other documentation support failure": "Other documentation support failure",
    }
    if gap_label in mapping:
        return mapping[gap_label]
    return str(gap_label).replace("_", " ")


def _documentation_action_text(root_cause_mechanism: str) -> str:
    action = next_action_for_root_cause(root_cause_mechanism).strip().rstrip(".").lower()
    replacements = {
        "document coaching target and close documentation support gap": (
            "close the documentation support gap"
        ),
        "work assigned queue, clear hold, and confirm account release path": (
            "clear the documentation-support blocker"
        ),
        "route coding review and validate modifier or code alignment": "route coding review",
    }
    return replacements.get(action, action)


def _story_cue(
    filtered: pd.DataFrame,
    mismatch_summary: pd.DataFrame,
    owner_routing: pd.DataFrame,
) -> PageStoryCue:
    if filtered.empty:
        return PageStoryCue(
            sentence="Documentation support pressure is out of scope for the current filters.",
            callouts=(
                StoryCallout(
                    "Control",
                    "Documentation support failures that block expected facility charge support.",
                ),
                StoryCallout(
                    "Current pressure",
                    "No open documentation-support backlog is in scope right now.",
                ),
                StoryCallout(
                    "Next move",
                    "No documentation-owner follow-up is needed until an exception re-enters scope.",
                ),
            ),
            note="Owner routing will repopulate when documentation support work is active in the filtered slice.",
        )

    lead_row = filtered.sort_values(
        ["stage_age_days", "priority_rank", "queue_item_id"],
        ascending=[False, True, True],
        kind="mergesort",
    ).iloc[0]
    top_gap = (
        filtered["why_not_billable_explanation"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )
    if not top_gap.empty:
        pressure_text = (
            f"{_operator_gap_label(str(top_gap.index[0]))} is driving "
            f"{int(top_gap.iloc[0])} open documentation exception(s)."
        )
    elif not mismatch_summary.empty:
        mismatch_row = mismatch_summary.iloc[0]
        pressure_text = (
            f"{_operator_gap_label(str(mismatch_row['mismatch_type']))} is driving "
            f"{int(mismatch_row['open_exceptions'])} open documentation exception(s)."
        )
    else:
        pressure_text = (
            f"{int(len(filtered))} documentation exception(s) remain open in the current slice."
        )

    routing_row = owner_routing.iloc[0] if not owner_routing.empty else None
    next_move = (
        f"{lead_row['accountable_owner']} should "
        f"{_documentation_action_text(str(lead_row['root_cause_mechanism']))} "
        f"on {lead_row['encounter_id']}."
    )
    note = (
        f"{routing_row['accountable_owner']} is carrying the largest current owner bucket."
        if routing_row is not None
        else "Owner routing stays explicit rather than collapsing documentation, coding, and operations into one label."
    )
    return PageStoryCue(
        sentence=(
            "Documentation support is breaking where documented activity still lacks the billable "
            "support expected in the current slice."
        ),
        callouts=(
            StoryCallout(
                "Control",
                "Unsupported-charge backlog, documentation-gap pattern, and routed owner follow-through.",
            ),
            StoryCallout("Current pressure", pressure_text),
            StoryCallout("Next move", next_move),
        ),
        note=note,
    )


def _worklist(filtered: pd.DataFrame, expected_opportunities: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "encounter_id",
                "department",
                "service_line",
                "accountable_owner",
                "why_not_billable_explanation",
                "estimated_gross_dollars",
            ]
        )
    expected_lookup = expected_opportunities.groupby("encounter_id", as_index=False).agg(
        why_not_billable_explanation_expected=("why_not_billable_explanation", "first"),
    )
    merged = filtered.merge(expected_lookup, on="encounter_id", how="left")
    merged["display_explanation"] = (
        merged["why_not_billable_explanation"].replace("", pd.NA)
        .fillna(merged["why_not_billable_explanation_expected"].fillna(""))
    )
    worklist = merged[
        [
            "encounter_id",
            "department",
            "service_line",
            "accountable_owner",
            "display_explanation",
            "estimated_gross_dollars",
        ]
    ].rename(columns={"display_explanation": "why_not_billable_explanation"})
    worklist["estimated_gross_dollars"] = worklist["estimated_gross_dollars"].round(2)
    return worklist


def build_documentation_exceptions_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> DocumentationExceptionsView:
    population = _base_population(repo_root)
    normalized_filters = normalize_filters(filters)
    filter_options = get_filter_options(population)
    filtered = apply_filters(population, normalized_filters)
    documentation_events, expected_opportunities = _load_inputs(repo_root)
    mismatch_summary = _mismatch_summary(filtered, documentation_events)
    owner_routing = _owner_routing(filtered)
    return DocumentationExceptionsView(
        filters=normalized_filters,
        filter_options=filter_options,
        filtered_population=filtered,
        story_cue=_story_cue(
            filtered,
            mismatch_summary,
            owner_routing,
        ),
        unsupported_charge_trend=_unsupported_charge_trend(
            filtered,
            repo_root=repo_root,
            filters=normalized_filters,
        ),
        missing_time_docs=_missing_time_docs(filtered, documentation_events),
        mismatch_summary=mismatch_summary,
        owner_routing=owner_routing,
        worklist=_worklist(filtered, expected_opportunities),
        unsupported_exception_count=int(len(filtered)),
    )


def render_documentation_exceptions_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        "Operational view of unsupported charge exceptions, missing documentation, and documentation-routing pressure.",
        scope_note,
        badges=("Facility-side only", "Outpatient-first", QUEUE_NAME),
    )
    selected_filters = scope_global_filters(
        get_global_filters(global_filter_options),
        queues=False,
    )
    view = build_documentation_exceptions_view(repo_root=repo_root, filters=selected_filters)
    render_active_filter_summary(
        view.filters,
        inactive_reasons={
            "queues": f"Fixed to {QUEUE_NAME} on this page.",
        },
    )
    render_page_story_cue(view.story_cue)

    render_section_header(
        "Documentation Snapshot",
        "Current unsupported-charge workload and documentation-gap concentration.",
    )
    render_kpi_row(
        [
            KpiCard(
                "Unsupported charge exceptions",
                format_count(view.unsupported_exception_count),
                "Open documentation support exceptions in the current filtered slice.",
            ),
            KpiCard(
                "Missing time docs",
                format_count(int(len(view.missing_time_docs))),
                "Missing stop-time or case-time documentation events tied to open work.",
            ),
            KpiCard(
                "Documentation dollars open",
                format_currency(float(view.filtered_population["estimated_gross_dollars"].sum())),
                "Estimated gross dollars currently blocked by documentation support issues.",
            ),
        ]
    )

    if view.filtered_population.empty:
        st.warning("No documentation exceptions match the current filters.")
        return

    with panel():
        render_section_header(
            "Unsupported Charge Trend",
            "Recent business-day unsupported-charge backlog trend based on documentation queue entry and workdown history.",
        )
        st.line_chart(
            view.unsupported_charge_trend.set_index("snapshot_date")[["unsupported_exceptions"]],
            use_container_width=True,
        )
        render_dataframe(
            view.unsupported_charge_trend,
            column_labels={
                "snapshot_date": "Snapshot date",
                "unsupported_exceptions": "Unsupported exceptions",
                "recoverable_dollars": "Recoverable dollars",
            },
            integer_columns=("unsupported_exceptions",),
            currency_columns=("recoverable_dollars",),
            height=240,
        )

    left, right = st.columns(2)
    with left:
        render_table_section(
            "Missing Time Docs",
            "Documentation gaps tied to missing stop-time or case-time support.",
            view.missing_time_docs,
            column_labels={
                "encounter_id": "Encounter",
                "documentation_gap_type": "Gap type",
                "documentation_type": "Documentation type",
                "documentation_status": "Documentation status",
            },
            height=300,
        )
    with right:
        render_table_section(
            "Order / Documentation / Admin Mismatches",
            "Mismatch buckets contributing to the open documentation exception population.",
            view.mismatch_summary,
            column_labels={
                "mismatch_type": "Mismatch type",
                "open_exceptions": "Open exceptions",
            },
            integer_columns=("open_exceptions",),
            height=300,
        )

    render_table_section(
        "Owner Routing",
        "Queue ownership view for current documentation support work.",
        view.owner_routing,
        column_labels={
            "accountable_owner": "Accountable owner",
            "current_queue": "Current queue",
            "open_exceptions": "Open exceptions",
            "recoverable_dollars": "Recoverable dollars",
        },
        integer_columns=("open_exceptions",),
        currency_columns=("recoverable_dollars",),
        height=260,
    )
    render_table_section(
        "Current Documentation Work",
        "Current routed documentation exceptions with the operational blocker carried forward.",
        view.worklist,
        column_labels={
            "encounter_id": "Encounter",
            "department": "Department",
            "service_line": "Service line",
            "accountable_owner": "Accountable owner",
            "why_not_billable_explanation": "Current blocker explanation",
            "estimated_gross_dollars": "Estimated gross dollars",
        },
        currency_columns=("estimated_gross_dollars",),
        height=360,
    )
