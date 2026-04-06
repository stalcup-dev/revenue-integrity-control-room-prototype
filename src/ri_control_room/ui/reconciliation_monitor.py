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


QUEUE_NAME = "Charge Reconciliation Monitor"
TREND_BUSINESS_DAY_WINDOW = 10
RECONCILIATION_OVERDUE_THRESHOLD_DAYS = 4


@dataclass(frozen=True)
class ReconciliationMonitorView:
    filters: SummaryFilters
    filter_options: dict[str, tuple[str, ...]]
    filtered_population: pd.DataFrame
    story_cue: PageStoryCue
    aging_by_service_line: pd.DataFrame
    overdue_departments: pd.DataFrame
    control_completion_trend: pd.DataFrame
    worklist: pd.DataFrame
    unreconciled_encounters_count: int


def _load_completion_inputs(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        load_processed_artifact("claims_or_account_status", repo_root),
        load_processed_artifact("expected_charge_opportunities", repo_root),
    )


def _base_population(repo_root: Path | None = None) -> pd.DataFrame:
    population = load_work_population(repo_root)
    return population.loc[population["current_queue"] == QUEUE_NAME].copy()


def _scoped_population(
    repo_root: Path | None,
    filters: SummaryFilters,
) -> pd.DataFrame:
    population = load_work_population(repo_root)
    return apply_filters(population, filters)


def _reconciliation_history_scope(
    repo_root: Path | None,
    scoped_population: pd.DataFrame,
) -> pd.DataFrame:
    if scoped_population.empty:
        return empty_summary(
            [
                "claim_id",
                "account_id",
                "encounter_id",
                "department",
                "service_line",
                "estimated_gross_dollars",
                "current_queue_entry_ts",
                "next_queue_entry_ts",
                "current_record_flag",
            ]
        )

    scope_lookup = scoped_population[
        [
            "claim_id",
            "account_id",
            "encounter_id",
            "department",
            "service_line",
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
    return history.merge(
        scope_lookup,
        on=["claim_id", "account_id", "encounter_id"],
        how="inner",
    )


def _trend_end_date(
    filtered: pd.DataFrame,
    scoped_population: pd.DataFrame,
) -> pd.Timestamp | None:
    if not scoped_population.empty:
        return pd.Timestamp(scoped_population["queue_snapshot_ts"].max()).normalize()
    if not filtered.empty:
        return pd.Timestamp(filtered["queue_snapshot_ts"].max()).normalize()
    return None


def _recent_history_window(
    history: pd.DataFrame,
    trend_end: pd.Timestamp,
) -> pd.DataFrame:
    if history.empty:
        return history
    business_days = pd.bdate_range(end=trend_end, periods=TREND_BUSINESS_DAY_WINDOW)
    window_start = business_days.min()
    return history.loc[
        (pd.to_datetime(history["current_queue_entry_ts"]) <= trend_end + pd.Timedelta(days=1))
        & (
            history["next_queue_entry_ts"].isna()
            | (pd.to_datetime(history["next_queue_entry_ts"]) >= window_start)
        )
    ].copy()


def _aging_by_service_line(
    filtered: pd.DataFrame,
    history: pd.DataFrame,
    *,
    trend_end: pd.Timestamp | None,
) -> pd.DataFrame:
    if filtered.empty and history.empty:
        return empty_summary(["service_line", "open_exceptions", "average_age_days", "overdue_count"])

    current_summary = (
        filtered.assign(overdue_flag=lambda df: df["sla_status"] == "Overdue")
        .groupby("service_line", as_index=False)
        .agg(
            open_exceptions=("queue_item_id", "size"),
            average_age_days=("stage_age_days", "mean"),
            overdue_count=("overdue_flag", "sum"),
        )
    )
    if current_summary.empty:
        current_summary = empty_summary(
            ["service_line", "open_exceptions", "average_age_days", "overdue_count"]
        )

    recent_history = _recent_history_window(history, trend_end) if trend_end is not None else history
    if recent_history.empty:
        summary = current_summary.copy()
        if not summary.empty:
            summary["average_age_days"] = summary["average_age_days"].round(2)
        return summary

    effective_end_ts = (
        trend_end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        if trend_end is not None
        else pd.Timestamp.utcnow().normalize()
    )
    recent_history["effective_exit_ts"] = pd.to_datetime(
        recent_history["next_queue_entry_ts"]
    ).fillna(effective_end_ts)
    recent_history["interval_age_days"] = (
        recent_history["effective_exit_ts"] - pd.to_datetime(recent_history["current_queue_entry_ts"])
    ).dt.total_seconds().div(86400).clip(lower=0.0)
    recent_summary = (
        recent_history.groupby("service_line", as_index=False)
        .agg(
            recent_case_count=("encounter_id", "nunique"),
            recent_average_age_days=("interval_age_days", "mean"),
        )
        .sort_values(["recent_case_count", "recent_average_age_days", "service_line"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    summary = recent_summary.merge(current_summary, on="service_line", how="left")
    summary["open_exceptions"] = (
        pd.to_numeric(summary["open_exceptions"], errors="coerce").fillna(0).astype(int)
    )
    summary["overdue_count"] = (
        pd.to_numeric(summary["overdue_count"], errors="coerce").fillna(0).astype(int)
    )
    summary["average_age_days"] = summary["average_age_days"].where(
        summary["open_exceptions"] > 0,
        summary["recent_average_age_days"],
    )
    summary = summary[
        ["service_line", "open_exceptions", "average_age_days", "overdue_count"]
    ].copy()
    summary["average_age_days"] = (
        pd.to_numeric(summary["average_age_days"], errors="coerce").fillna(0.0).round(2)
    )
    return summary.sort_values(
        ["open_exceptions", "average_age_days", "service_line"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def _overdue_departments(filtered: pd.DataFrame) -> pd.DataFrame:
    overdue = filtered.loc[filtered["sla_status"] != "Within SLA"].copy()
    if overdue.empty:
        return empty_summary(["department", "open_exceptions", "average_age_days", "recoverable_dollars"])
    summary = (
        overdue.groupby("department", as_index=False)
        .agg(
            open_exceptions=("queue_item_id", "size"),
            average_age_days=("stage_age_days", "mean"),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(["open_exceptions", "recoverable_dollars", "department"], ascending=[False, False, True])
        .reset_index(drop=True)
    )
    summary["average_age_days"] = summary["average_age_days"].round(2)
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    return summary


def _story_cue(
    filtered: pd.DataFrame,
    aging_by_service_line: pd.DataFrame,
    overdue_departments: pd.DataFrame,
) -> PageStoryCue:
    if filtered.empty:
        return PageStoryCue(
            sentence=(
                "This page monitors charge capture reconciliation timeliness for the current slice, "
                "but no open reconciliation work matches the filters."
            ),
            callouts=(
                StoryCallout(
                    "Control",
                    "Charge capture reconciliation and policy-timing pressure.",
                ),
                StoryCallout(
                    "Current pressure",
                    "No open reconciliation backlog is in scope right now.",
                ),
                StoryCallout(
                    "Next move",
                    "No owner handoff is needed until a reconciliation exception re-enters scope.",
                ),
            ),
            note="Recently worked-down service lines appear only when in-scope queue history supports them.",
        )

    driver = aging_by_service_line.sort_values(
        ["overdue_count", "open_exceptions", "average_age_days", "service_line"],
        ascending=[False, False, False, True],
        kind="mergesort",
    ).iloc[0]
    lead_candidates = filtered.assign(
        _sla_severity=filtered["sla_status"].map(
            {
                "Overdue": 2,
                "At risk": 1,
                "Within SLA": 0,
            }
        ).fillna(0)
    )
    lead_row = lead_candidates.sort_values(
        ["_sla_severity", "stage_age_days", "priority_rank", "queue_item_id"],
        ascending=[False, False, True, True],
        kind="mergesort",
    ).iloc[0]
    service_line = str(driver["service_line"])
    sentence = (
        "This page monitors charge capture reconciliation timeliness, with "
        f"{service_line} driving the current filtered pressure."
    )
    if int(driver["open_exceptions"]) > 0:
        pressure_text = (
            f"{service_line} carries {int(driver['open_exceptions'])} open and "
            f"{int(driver['overdue_count'])} overdue reconciliation items at "
            f"{float(driver['average_age_days']):.1f} average days."
        )
    else:
        pressure_text = (
            f"{service_line} is kept visible as a recently worked-down in-scope line, "
            "while another filtered line is carrying the current open backlog."
        )

    overdue_department_count = int(len(overdue_departments))
    next_move = (
        f"{lead_row['accountable_owner']} owns the next move on {lead_row['encounter_id']}; "
        f"{next_action_for_root_cause(lead_row['root_cause_mechanism'])}"
    )
    note = (
        f"{overdue_department_count} department(s) currently carry non-within-SLA reconciliation work. "
        "The latest trend point stays aligned to the current filtered backlog."
    )
    return PageStoryCue(
        sentence=sentence,
        callouts=(
            StoryCallout(
                "Control",
                "Unreconciled encounter backlog versus overdue pressure in the current reconciliation slice.",
            ),
            StoryCallout("Current pressure", pressure_text),
            StoryCallout("Next move", next_move),
        ),
        note=note,
    )


def _control_completion_trend(
    filtered: pd.DataFrame,
    history: pd.DataFrame,
    *,
    trend_end: pd.Timestamp | None,
) -> pd.DataFrame:
    if filtered.empty and history.empty:
        return empty_summary(["snapshot_date", "open_unreconciled", "overdue_unreconciled"])
    if trend_end is None:
        return empty_summary(["snapshot_date", "open_unreconciled", "overdue_unreconciled"])

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
        ].copy()
        active["days_open_at_snapshot"] = (
            day_end - pd.to_datetime(active["current_queue_entry_ts"])
        ).dt.total_seconds().div(86400)
        rows.append(
            {
                "snapshot_date": day.date(),
                "open_unreconciled": int(len(active)),
                "overdue_unreconciled": int(
                    (active["days_open_at_snapshot"] >= RECONCILIATION_OVERDUE_THRESHOLD_DAYS).sum()
                ),
            }
        )
    trend = pd.DataFrame(rows)
    if not trend.empty:
        trend.loc[trend.index[-1], "open_unreconciled"] = int(len(filtered))
        trend.loc[trend.index[-1], "overdue_unreconciled"] = int(
            (filtered["sla_status"] != "Within SLA").sum()
        )
    return trend


def _worklist(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "queue_item_id",
                "encounter_id",
                "department",
                "service_line",
                "sla_status",
                "stage_age_days",
                "estimated_gross_dollars",
            ]
        )
    worklist = filtered[
        [
            "queue_item_id",
            "encounter_id",
            "department",
            "service_line",
            "sla_status",
            "stage_age_days",
            "estimated_gross_dollars",
        ]
    ].copy()
    worklist["estimated_gross_dollars"] = worklist["estimated_gross_dollars"].round(2)
    return worklist


def build_reconciliation_monitor_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> ReconciliationMonitorView:
    normalized_filters = normalize_filters(filters)
    population = _base_population(repo_root)
    filter_options = get_filter_options(population)
    scoped_population = _scoped_population(repo_root, normalized_filters)
    filtered = scoped_population.loc[scoped_population["current_queue"] == QUEUE_NAME].copy()
    reconciliation_history = _reconciliation_history_scope(repo_root, scoped_population)
    trend_end = _trend_end_date(filtered, scoped_population)
    aging_by_service_line = _aging_by_service_line(
        filtered,
        reconciliation_history,
        trend_end=trend_end,
    )
    overdue_departments = _overdue_departments(filtered)
    return ReconciliationMonitorView(
        filters=normalized_filters,
        filter_options=filter_options,
        filtered_population=filtered,
        story_cue=_story_cue(filtered, aging_by_service_line, overdue_departments),
        aging_by_service_line=aging_by_service_line,
        overdue_departments=overdue_departments,
        control_completion_trend=_control_completion_trend(
            filtered,
            reconciliation_history,
            trend_end=trend_end,
        ),
        worklist=_worklist(filtered),
        unreconciled_encounters_count=int(len(filtered)),
    )


def render_reconciliation_monitor_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        "Operational view of unreconciled charge-capture work and completion pressure against policy windows.",
        scope_note,
        badges=("Facility-side only", "Outpatient-first", QUEUE_NAME),
    )
    selected_filters = scope_global_filters(
        get_global_filters(global_filter_options),
        queues=False,
    )
    view = build_reconciliation_monitor_view(repo_root=repo_root, filters=selected_filters)
    render_active_filter_summary(
        view.filters,
        inactive_reasons={
            "queues": f"Fixed to {QUEUE_NAME} on this page.",
        },
    )
    render_page_story_cue(view.story_cue)

    render_section_header(
        "Reconciliation Snapshot",
        "Top-line backlog and timing pressure for the filtered reconciliation queue.",
    )
    render_kpi_row(
        [
            KpiCard(
                "Unreconciled encounters",
                format_count(view.unreconciled_encounters_count),
                "Active reconciliation work items still open in queue.",
            ),
            KpiCard(
                "Overdue departments",
                format_count(int(len(view.overdue_departments))),
                "Departments currently carrying non-within-SLA reconciliation work.",
            ),
            KpiCard(
                "Open reconciliation dollars",
                format_currency(float(view.filtered_population["estimated_gross_dollars"].sum())),
                "Estimated gross dollars tied to open reconciliation blockers.",
            ),
        ]
    )

    if (
        view.filtered_population.empty
        and view.aging_by_service_line.empty
        and view.control_completion_trend.empty
    ):
        st.warning("No reconciliation work matches the current filters.")
        return

    render_table_section(
        "Overdue Departments",
        "Department-level view of aging reconciliation exposure.",
        view.overdue_departments,
        column_labels={
            "department": "Department",
            "open_exceptions": "Open exceptions",
            "average_age_days": "Average age days",
            "recoverable_dollars": "Recoverable dollars",
        },
        integer_columns=("open_exceptions",),
        decimal_columns=("average_age_days",),
        currency_columns=("recoverable_dollars",),
        height=250,
    )
    render_table_section(
        "Aging By Service Line",
        "Service-line scan of current open reconciliation workload, with recently worked-down in-scope lines kept visible when recent reconciliation activity exists.",
        view.aging_by_service_line,
        column_labels={
            "service_line": "Service line",
            "open_exceptions": "Open exceptions",
            "average_age_days": "Average age days",
            "overdue_count": "Overdue count",
        },
        integer_columns=("open_exceptions", "overdue_count"),
        decimal_columns=("average_age_days",),
        height=250,
    )

    with panel():
        render_section_header(
            "Control Completion Trend",
            "Recent stock view of open unreconciled cases versus overdue unreconciled cases in the same filtered slice.",
        )
        st.line_chart(
            view.control_completion_trend.set_index("snapshot_date")[
                ["open_unreconciled", "overdue_unreconciled"]
            ],
            use_container_width=True,
        )
        render_dataframe(
            view.control_completion_trend,
            column_labels={
                "snapshot_date": "Snapshot date",
                "open_unreconciled": "Open unreconciled",
                "overdue_unreconciled": "Overdue unreconciled",
            },
            integer_columns=("open_unreconciled", "overdue_unreconciled"),
            height=240,
        )

    render_table_section(
        "Current Reconciliation Work",
        "Active reconciliation queue ordered for rapid operational review.",
        view.worklist,
        column_labels={
            "queue_item_id": "Queue item",
            "encounter_id": "Encounter",
            "department": "Department",
            "service_line": "Service line",
            "sla_status": "SLA status",
            "stage_age_days": "Age days",
            "estimated_gross_dollars": "Estimated gross dollars",
        },
        integer_columns=("stage_age_days",),
        currency_columns=("estimated_gross_dollars",),
        status_columns=("sla_status",),
        height=380,
    )
