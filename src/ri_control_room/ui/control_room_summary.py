from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact, read_run_manifest
from ri_control_room.case_detail import build_case_detail_payload
from ri_control_room.control_story import (
    DeterministicControlStory,
    REPRESENTATIVE_CASE_SELECTION_NOTE,
    build_deterministic_control_story,
    render_control_story_lines,
    select_representative_case_row,
    story_scope_population,
)
from ri_control_room.decision_pack import render_revenue_integrity_decision_pack_panel
from ri_control_room.ui.shared import (
    RECOVERABLE_STATES,
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


STAGE_LABELS = {
    "Charge capture pending": "Charge pending",
    "Documentation pending": "Documentation pending",
    "Coding pending": "Coding pending",
    "Prebill edit / hold": "Prebill edit / hold",
    "Correction / rebill pending": "Correction / rebill pending",
}

BLOCKER_LABELS = {
    "Documentation support incomplete": "Documentation incomplete",
    "Missing or late charge capture": "Missing / late charge",
    "Coding or modifier review pending": "Coding / modifier review",
    "Prebill edit or hold unresolved": "Prebill edit unresolved",
    "Correction or rebill pending": "Correction / rebill pending",
}

QUEUE_LABELS = {
    "Charge Reconciliation Monitor": "Charge reconciliation",
    "Documentation Support Exceptions": "Documentation support",
    "Coding Pending Review": "Coding review",
    "Modifiers / Edits / Prebill Holds": "Edits / prebill holds",
    "Correction / Rebill Pending": "Correction / rebill",
}

OWNER_LABELS = {
    "Department operations": "Dept ops",
    "Coding team": "Coding",
    "Billing operations": "Billing",
}


def _display_label(value: object, mapping: dict[str, str]) -> str:
    if value is None or pd.isna(value):
        return ""
    return mapping.get(str(value), str(value))


@dataclass(frozen=True)
class ArtifactLineageView:
    manifest_summary: pd.DataFrame
    artifact_row_counts: pd.DataFrame
    build_timestamp_utc: str
    last_validated_at_utc: str
    overall_validation_status: str


@dataclass(frozen=True)
class SummaryView:
    filters: SummaryFilters
    filter_options: dict[str, tuple[str, ...]]
    artifact_lineage: ArtifactLineageView
    control_story: DeterministicControlStory
    featured_story_proof: "FeaturedStoryProofView"
    filtered_population: pd.DataFrame
    suppression_summary: pd.DataFrame
    issue_root_cause_summary: pd.DataFrame
    stage_bottleneck_summary: pd.DataFrame
    actionable_vs_suppressed: pd.DataFrame
    owner_action_summary: pd.DataFrame
    recurring_patterns: pd.DataFrame
    backlog_trend: pd.DataFrame
    worklist: pd.DataFrame
    open_exception_count: int
    recoverable_now_dollars: float
    lost_dollars_now: float
    suppressed_case_count: int
    urgent_exception_count: int


@dataclass(frozen=True)
class FeaturedStoryProofView:
    proof_available: bool
    empty_state_message: str
    selection_rule_note: str
    story_scope_count: int
    representative_queue_item_id: str
    representative_encounter_id: str
    recommended_next_action: str
    control_narrative: str
    case_header: dict[str, object]
    classification: dict[str, object]
    routing_history: dict[str, object]
    suppression_note: dict[str, object]
    upstream_evidence: pd.DataFrame
    expected_vs_actual: pd.DataFrame


def _detail_mapping_table(
    mapping: dict[str, object],
    field_order: tuple[tuple[str, str], ...],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, label in field_order:
        value = mapping.get(key)
        if value is None or value == "":
            continue
        rows.append({"field": label, "value": str(value)})
    return pd.DataFrame(rows)


def _empty_featured_story_proof_view(message: str) -> FeaturedStoryProofView:
    return FeaturedStoryProofView(
        proof_available=False,
        empty_state_message=message,
        selection_rule_note=REPRESENTATIVE_CASE_SELECTION_NOTE,
        story_scope_count=0,
        representative_queue_item_id="",
        representative_encounter_id="",
        recommended_next_action="",
        control_narrative=message,
        case_header={},
        classification={},
        routing_history={},
        suppression_note={},
        upstream_evidence=empty_summary([]),
        expected_vs_actual=empty_summary([]),
    )


def _build_featured_story_proof_view(
    filtered: pd.DataFrame,
    story: DeterministicControlStory,
    repo_root: Path | None = None,
) -> FeaturedStoryProofView:
    if filtered.empty or story.queue_item_id == "":
        return _empty_featured_story_proof_view(
            "No representative case is available because the current filters do not leave any active routed work in scope."
        )

    scope = story_scope_population(filtered, story)
    representative_row = select_representative_case_row(filtered, story)
    if representative_row is None:
        return _empty_featured_story_proof_view(
            "No representative case remains inside the featured story scope for the current filters."
        )

    try:
        payload = build_case_detail_payload(str(representative_row["queue_item_id"]), repo_root)
    except ValueError:
        return _empty_featured_story_proof_view(
            "The featured story has no readable representative case payload in the current governed scope."
        )

    return FeaturedStoryProofView(
        proof_available=True,
        empty_state_message="",
        selection_rule_note=REPRESENTATIVE_CASE_SELECTION_NOTE,
        story_scope_count=int(len(scope)),
        representative_queue_item_id=str(payload.case_header.get("queue_item_id") or ""),
        representative_encounter_id=str(payload.case_header.get("encounter_id") or ""),
        recommended_next_action=story.recommended_next_action,
        control_narrative=payload.control_narrative,
        case_header=payload.case_header,
        classification=payload.classification,
        routing_history=payload.routing_history,
        suppression_note=payload.suppression_note,
        upstream_evidence=payload.upstream_evidence,
        expected_vs_actual=payload.expected_vs_actual,
    )


def _load_population(repo_root: Path | None = None) -> pd.DataFrame:
    return load_work_population(repo_root)


def _load_scope_tables(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        load_processed_artifact("claims_or_account_status", repo_root),
        load_processed_artifact("expected_charge_opportunities", repo_root),
    )


def _manifest_status_text(value: object) -> str:
    if value is True:
        return "Passed"
    if value is False:
        return "Failed"
    return "Not yet run"


def _manifest_scalar_text(value: object) -> str:
    if value is None or value == "":
        return "Not set"
    return str(value)


def _build_artifact_lineage_view(repo_root: Path | None = None) -> ArtifactLineageView:
    manifest = read_run_manifest(repo_root)
    validation_status = manifest.get("validation_status", {})
    if not isinstance(validation_status, dict):
        validation_status = {}

    build_timestamp_utc = _manifest_scalar_text(manifest.get("run_timestamp_utc"))
    last_validated_at_utc = _manifest_scalar_text(validation_status.get("last_validated_at_utc"))
    overall_validation_status = _manifest_status_text(
        validation_status.get("overall_passed")
    )

    manifest_summary = pd.DataFrame(
        [
            {"field": "Build timestamp (UTC)", "value": build_timestamp_utc},
            {"field": "Overall validation status", "value": overall_validation_status},
            {
                "field": "Schema checks",
                "value": _manifest_status_text(validation_status.get("schema_checks_passed")),
            },
            {
                "field": "Business-rule checks",
                "value": _manifest_status_text(
                    validation_status.get("business_rule_checks_passed")
                ),
            },
            {"field": "Last validated at (UTC)", "value": last_validated_at_utc},
            {"field": "Seed", "value": _manifest_scalar_text(manifest.get("seed"))},
            {
                "field": "Synthetic data version",
                "value": _manifest_scalar_text(manifest.get("synthetic_data_version")),
            },
            {
                "field": "Ruleset version",
                "value": _manifest_scalar_text(manifest.get("ruleset_version")),
            },
            {
                "field": "Schema version",
                "value": _manifest_scalar_text(manifest.get("schema_version")),
            },
            {
                "field": "Priority score version",
                "value": _manifest_scalar_text(manifest.get("priority_score_version")),
            },
        ]
    )

    row_counts = manifest.get("artifact_row_counts", {})
    if isinstance(row_counts, dict):
        artifact_row_counts = pd.DataFrame(
            [
                {"artifact": artifact_name, "row_count": row_count}
                for artifact_name, row_count in row_counts.items()
            ]
        )
    else:
        artifact_row_counts = empty_summary(["artifact", "row_count"])

    return ArtifactLineageView(
        manifest_summary=manifest_summary,
        artifact_row_counts=artifact_row_counts,
        build_timestamp_utc=build_timestamp_utc,
        last_validated_at_utc=last_validated_at_utc,
        overall_validation_status=overall_validation_status,
    )


def _build_kpi_lookup(repo_root: Path | None = None) -> pd.DataFrame:
    kpi_snapshot = load_processed_artifact("kpi_snapshot", repo_root)
    return kpi_snapshot.loc[kpi_snapshot["record_type"] == "kpi"].copy()


def _scoped_kpi_numerator_value(
    kpi_rows: pd.DataFrame,
    *,
    kpi_name: str,
    filters: SummaryFilters,
) -> float:
    scoped = kpi_rows.loc[kpi_rows["kpi_name"] == kpi_name].copy()
    if scoped.empty:
        return 0.0
    if filters.departments:
        department_rows = scoped.loc[scoped["department"].isin(filters.departments)].copy()
        if not department_rows.empty:
            return float(department_rows["numerator_value"].fillna(0.0).sum())
    all_scope_rows = scoped.loc[scoped["setting_name"] == "All frozen V1 departments"].copy()
    if not all_scope_rows.empty:
        return float(all_scope_rows.iloc[0]["numerator_value"] or 0.0)
    return float(scoped["numerator_value"].fillna(0.0).sum())


def _scope_filter(
    df: pd.DataFrame,
    filters: SummaryFilters,
) -> pd.DataFrame:
    scoped = df.copy()
    if filters.departments and "department" in scoped.columns:
        scoped = scoped.loc[scoped["department"].isin(filters.departments)]
    if filters.service_lines and "service_line" in scoped.columns:
        scoped = scoped.loc[scoped["service_line"].isin(filters.service_lines)]
    if filters.recoverability_states and "recoverability_status" in scoped.columns:
        scoped = scoped.loc[scoped["recoverability_status"].isin(filters.recoverability_states)]
    return scoped.copy()


def _build_issue_root_cause_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "issue_domain",
                "root_cause_mechanism",
                "open_exceptions",
                "recoverable_dollars",
            ]
        )
    summary = (
        filtered.groupby(["issue_domain", "root_cause_mechanism"], as_index=False)
        .agg(
            open_exceptions=("queue_item_id", "size"),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(
            ["open_exceptions", "recoverable_dollars", "issue_domain", "root_cause_mechanism"],
            ascending=[False, False, True, True],
        )
        .reset_index(drop=True)
    )
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    return summary


def _build_stage_bottleneck_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "current_prebill_stage",
                "current_primary_blocker_state",
                "current_queue",
                "accountable_owner",
                "open_exceptions",
                "urgent_exceptions",
                "average_age_days",
            ]
        )
    summary = (
        filtered.assign(urgent_flag=lambda df: df["sla_status"] != "Within SLA").groupby(
            [
                "current_prebill_stage",
                "current_primary_blocker_state",
                "current_queue",
                "accountable_owner",
            ],
            as_index=False,
        )
        .agg(
            open_exceptions=("queue_item_id", "size"),
            urgent_exceptions=("urgent_flag", "sum"),
            average_age_days=("stage_age_days", "mean"),
        )
        .sort_values(
            [
                "urgent_exceptions",
                "open_exceptions",
                "current_prebill_stage",
                "current_queue",
            ],
            ascending=[False, False, True, True],
        )
        .reset_index(drop=True)
    )
    summary["average_age_days"] = summary["average_age_days"].round(2)
    summary["current_prebill_stage"] = summary["current_prebill_stage"].map(
        lambda value: _display_label(value, STAGE_LABELS)
    )
    summary["current_primary_blocker_state"] = summary["current_primary_blocker_state"].map(
        lambda value: _display_label(value, BLOCKER_LABELS)
    )
    summary["current_queue"] = summary["current_queue"].map(
        lambda value: _display_label(value, QUEUE_LABELS)
    )
    summary["accountable_owner"] = summary["accountable_owner"].map(
        lambda value: _display_label(value, OWNER_LABELS)
    )
    return summary


def _build_actionable_vs_suppressed(
    filtered: pd.DataFrame,
    scoped_statuses: pd.DataFrame,
    scoped_expected: pd.DataFrame,
) -> pd.DataFrame:
    if scoped_statuses.empty:
        return empty_summary(
            [
                "bucket",
                "encounter_count",
                "share_of_scope",
                "routing_state",
            ]
        )
    suppressed_encounters = set(
        scoped_expected.loc[
            scoped_expected["opportunity_status"] == "packaged_or_nonbillable_suppressed",
            "encounter_id",
        ]
    )
    active_encounters = set(filtered["encounter_id"])
    all_scope_encounters = set(scoped_statuses["encounter_id"])
    out_of_queue_encounters = all_scope_encounters - active_encounters - suppressed_encounters
    total_scope = max(len(all_scope_encounters), 1)

    rows = [
        {
            "bucket": "Actionable active work",
            "encounter_count": len(active_encounters),
            "share_of_scope": len(active_encounters) / total_scope,
            "routing_state": "Work current blocker now",
        },
        {
            "bucket": "Suppressed by design",
            "encounter_count": len(suppressed_encounters),
            "share_of_scope": len(suppressed_encounters) / total_scope,
            "routing_state": "Out of queue by design",
        },
        {
            "bucket": "No active queue now",
            "encounter_count": len(out_of_queue_encounters),
            "share_of_scope": len(out_of_queue_encounters) / total_scope,
            "routing_state": "No current action queue",
        },
    ]
    return pd.DataFrame(rows)


def _build_suppression_summary(actionable_vs_suppressed: pd.DataFrame) -> pd.DataFrame:
    if actionable_vs_suppressed.empty:
        return empty_summary(["bucket", "encounter_count", "share_of_scope", "routing_state"])
    suppressed = actionable_vs_suppressed.loc[
        actionable_vs_suppressed["bucket"] == "Suppressed by design"
    ].copy()
    if suppressed.empty:
        return empty_summary(["bucket", "encounter_count", "share_of_scope", "routing_state"])
    return suppressed.reset_index(drop=True)


def _build_owner_action_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "accountable_owner",
                "current_queue",
                "current_primary_blocker_state",
                "open_exceptions",
                "urgent_exceptions",
                "recoverable_dollars",
            ]
        )
    summary = (
        filtered.assign(urgent_flag=lambda df: df["sla_status"] != "Within SLA")
        .groupby(
            ["accountable_owner", "current_queue", "current_primary_blocker_state"],
            as_index=False,
        )
        .agg(
            open_exceptions=("queue_item_id", "size"),
            urgent_exceptions=("urgent_flag", "sum"),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(
            ["urgent_exceptions", "open_exceptions", "recoverable_dollars", "accountable_owner"],
            ascending=[False, False, False, True],
        )
        .reset_index(drop=True)
    )
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    summary["accountable_owner"] = summary["accountable_owner"].map(
        lambda value: _display_label(value, OWNER_LABELS)
    )
    summary["current_queue"] = summary["current_queue"].map(
        lambda value: _display_label(value, QUEUE_LABELS)
    )
    summary["current_primary_blocker_state"] = summary["current_primary_blocker_state"].map(
        lambda value: _display_label(value, BLOCKER_LABELS)
    )
    return summary


def _build_recurring_patterns(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "issue_domain",
                "root_cause_mechanism",
                "open_exceptions",
                "repeat_exceptions",
                "repeat_rate",
            ]
        )
    summary = (
        filtered.groupby(["issue_domain", "root_cause_mechanism"], as_index=False)
        .agg(
            open_exceptions=("queue_item_id", "size"),
            repeat_exceptions=("repeat_exception_flag", "sum"),
        )
        .assign(
            repeat_rate=lambda df: (
                df["repeat_exceptions"] / df["open_exceptions"].replace(0, pd.NA)
            ).fillna(0.0)
        )
        .sort_values(
            ["repeat_exceptions", "open_exceptions", "issue_domain", "root_cause_mechanism"],
            ascending=[False, False, True, True],
        )
        .reset_index(drop=True)
    )
    summary["repeat_rate"] = summary["repeat_rate"].round(4)
    return summary


def _build_backlog_trend(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(["snapshot_date", "open_exceptions", "recoverable_dollars"])
    trend_end = pd.Timestamp(filtered["queue_snapshot_ts"].max()).normalize()
    trend_start = trend_end - pd.Timedelta(days=6)
    rows: list[dict[str, object]] = []
    for day in pd.date_range(trend_start, trend_end, freq="D"):
        day_end = day + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        active = filtered.loc[filtered["aging_clock_start_ts"] <= day_end]
        rows.append(
            {
                "snapshot_date": day.date(),
                "open_exceptions": int(len(active)),
                "recoverable_dollars": round(float(active["estimated_gross_dollars"].sum()), 2),
            }
        )
    return pd.DataFrame(rows)


def _build_worklist(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "queue_item_id",
                "current_prebill_stage",
                "current_primary_blocker_state",
                "current_queue",
                "accountable_owner",
                "days_in_stage",
                "sla_status",
                "recoverability_status",
                "department",
                "service_line",
                "issue_domain",
                "root_cause_mechanism",
                "estimated_gross_dollars",
                "why_not_billable_explanation",
            ]
        )
    worklist = filtered[
        [
            "queue_item_id",
            "current_prebill_stage",
            "current_primary_blocker_state",
            "current_queue",
            "accountable_owner",
            "days_in_stage",
            "sla_status",
            "recoverability_status",
            "department",
            "service_line",
            "issue_domain",
            "root_cause_mechanism",
            "estimated_gross_dollars",
            "why_not_billable_explanation",
        ]
    ].copy()
    worklist["estimated_gross_dollars"] = worklist["estimated_gross_dollars"].round(2)
    return worklist


def build_control_room_summary_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> SummaryView:
    population = _load_population(repo_root)
    statuses, expected_opportunities = _load_scope_tables(repo_root)
    kpi_rows = _build_kpi_lookup(repo_root)
    normalized_filters = normalize_filters(filters)
    options = get_filter_options(population)
    filtered = apply_filters(population, normalized_filters)
    scoped_statuses = _scope_filter(statuses, normalized_filters)
    scoped_expected = _scope_filter(expected_opportunities, normalized_filters)
    actionable_vs_suppressed = _build_actionable_vs_suppressed(
        filtered,
        scoped_statuses,
        scoped_expected,
    )

    recoverable_now_dollars = round(
        float(
            filtered.loc[
                filtered["recoverability_status"].isin(RECOVERABLE_STATES),
                "estimated_gross_dollars",
            ].sum()
        ),
        2,
    )
    suppressed_case_count = int(
        scoped_expected.loc[
            scoped_expected["opportunity_status"] == "packaged_or_nonbillable_suppressed",
            "encounter_id",
        ].nunique()
    )
    urgent_exception_count = int((filtered["sla_status"] != "Within SLA").sum())
    lost_dollars_now = round(
        _scoped_kpi_numerator_value(
            kpi_rows,
            kpi_name="Dollars already lost after timing window",
            filters=normalized_filters,
        ),
        2,
    )
    control_story = build_deterministic_control_story(filtered, repo_root=repo_root)

    return SummaryView(
        filters=normalized_filters,
        filter_options=options,
        artifact_lineage=_build_artifact_lineage_view(repo_root),
        control_story=control_story,
        featured_story_proof=_build_featured_story_proof_view(
            filtered,
            control_story,
            repo_root=repo_root,
        ),
        filtered_population=filtered,
        suppression_summary=_build_suppression_summary(actionable_vs_suppressed),
        issue_root_cause_summary=_build_issue_root_cause_summary(filtered),
        stage_bottleneck_summary=_build_stage_bottleneck_summary(filtered),
        actionable_vs_suppressed=actionable_vs_suppressed,
        owner_action_summary=_build_owner_action_summary(filtered),
        recurring_patterns=_build_recurring_patterns(filtered),
        backlog_trend=_build_backlog_trend(filtered),
        worklist=_build_worklist(filtered),
        open_exception_count=int(len(filtered)),
        recoverable_now_dollars=recoverable_now_dollars,
        lost_dollars_now=lost_dollars_now,
        suppressed_case_count=suppressed_case_count,
        urgent_exception_count=urgent_exception_count,
    )


def render_control_room_summary_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        (
            "Fast operational scan of active exceptions, recoverability, and control pressure "
            "across the current in-scope facility footprint."
        ),
        scope_note,
        badges=(
            "Facility-side only",
            "Outpatient-first",
            "Current operating summary",
        ),
    )
    selected_filters = get_global_filters(global_filter_options)

    view = build_control_room_summary_view(
        repo_root=repo_root,
        filters=selected_filters,
    )
    render_active_filter_summary(view.filters)

    render_section_header(
        "Control Room Snapshot",
        "Start with current pressure now, then move through why it is happening, where it is stuck, who should act next, and what should not be worked as leakage.",
    )
    with panel():
        render_kpi_row(
            [
                KpiCard(
                    "Open actionable exceptions",
                    format_count(view.open_exception_count),
                    "Active owner-routed work items in the current filtered slice.",
                ),
                KpiCard(
                    "Needs action now",
                    format_count(view.urgent_exception_count),
                    "At-risk or overdue routed exceptions requiring immediate attention.",
                ),
                KpiCard(
                    "Recoverable dollars open",
                    format_currency(view.recoverable_now_dollars),
                    "Estimated gross dollars still sitting in recoverable routed work.",
                ),
                KpiCard(
                    "Already lost",
                    format_currency(view.lost_dollars_now),
                    "Governed gross dollars already beyond the timing window. Department-scoped when department filters are applied.",
                ),
            ]
        )

    with panel():
        render_section_header(
            "Featured Deterministic Story",
            (
                "One selected control story from the current governed queue, kept to "
                "issue domain, root cause, blocker, owner, aging, recoverability, "
                "and next action."
            ),
        )
        story_lines = render_control_story_lines(view.control_story)
        if hasattr(st, "markdown"):
            st.markdown("\n".join(story_lines))
        elif hasattr(st, "caption"):
            for line in story_lines:
                st.caption(line)
        proof_label = (
            f"View proof for representative case: {view.featured_story_proof.representative_queue_item_id}"
            if view.featured_story_proof.proof_available
            else "View proof for representative case"
        )
        with st.expander(proof_label, expanded=False):
            render_section_header(
                "Representative Case Proof",
                "Read-only proof tied to the featured story so a reviewer can inspect the underlying deterministic evidence on the same page.",
            )
            if hasattr(st, "caption"):
                st.caption(
                    f"{view.featured_story_proof.selection_rule_note} "
                    f"Current story scope: {view.featured_story_proof.story_scope_count} matching routed case(s)."
                )
            if not view.featured_story_proof.proof_available:
                st.warning(view.featured_story_proof.empty_state_message)
            else:
                render_kpi_row(
                    [
                        KpiCard(
                            "Representative queue item",
                            view.featured_story_proof.representative_queue_item_id,
                            "Single reviewer drill case chosen deterministically from the featured story scope.",
                        ),
                        KpiCard(
                            "Encounter",
                            view.featured_story_proof.representative_encounter_id,
                            "Encounter attached to the selected representative case.",
                        ),
                        KpiCard(
                            "Recoverability",
                            str(
                                view.featured_story_proof.classification.get(
                                    "recoverability_status",
                                    "Not available",
                                )
                            ),
                            "Current recoverability framing for the representative case.",
                        ),
                        KpiCard(
                            "Recommended next action",
                            view.featured_story_proof.recommended_next_action,
                            "Same governed next step used by the featured deterministic story.",
                        ),
                    ]
                )
                if hasattr(st, "markdown"):
                    st.markdown(view.featured_story_proof.control_narrative)
                elif hasattr(st, "caption"):
                    st.caption(view.featured_story_proof.control_narrative)

                if view.featured_story_proof.suppression_note.get("suppressed_case_flag"):
                    st.info(str(view.featured_story_proof.suppression_note.get("note_text") or ""))
                elif hasattr(st, "caption"):
                    st.caption(
                        "Suppression note: no suppressed expected opportunities are attached to the representative case."
                    )

                proof_summary_table = _detail_mapping_table(
                    {
                        **view.featured_story_proof.case_header,
                        **view.featured_story_proof.classification,
                        "recommended_next_action": view.featured_story_proof.recommended_next_action,
                    },
                    (
                        ("queue_item_id", "Queue item"),
                        ("encounter_id", "Encounter"),
                        ("department", "Department"),
                        ("service_line", "Service line"),
                        ("issue_domain", "Issue domain"),
                        ("root_cause_mechanism", "Root cause mechanism"),
                        ("current_primary_blocker_state", "Current primary blocker"),
                        ("current_queue", "Current queue"),
                        ("accountable_owner", "Accountable owner"),
                        ("recoverability_status", "Recoverability"),
                        ("recommended_next_action", "Recommended next action"),
                    ),
                )
                routing_history_table = _detail_mapping_table(
                    view.featured_story_proof.routing_history,
                    (
                        ("transition_event_count", "Transition events"),
                        ("current_queue", "Current queue"),
                        ("prior_queue", "Prior queue"),
                        ("current_prebill_stage", "Current stage"),
                        ("prior_stage", "Prior stage"),
                        ("reroute_count", "Reroute count"),
                        ("routing_reason", "Routing reason"),
                        ("current_queue_entry_ts", "Current queue entry"),
                        ("latest_reroute_ts", "Latest reroute"),
                        ("recoverability_status", "Recoverability at current event"),
                    ),
                )

                left_col, right_col = st.columns(2)
                with left_col:
                    render_table_section(
                        "Representative Case Summary",
                        "Representative queue item, operating ownership, blocker, recoverability, and next action tied to the featured story.",
                        proof_summary_table,
                        column_labels={"field": "Field", "value": "Value"},
                        height=320,
                    )
                with right_col:
                    render_table_section(
                        "Routing History Summary",
                        "Current queue-history path for the representative case, including reroute count and current routing reason.",
                        routing_history_table,
                        column_labels={"field": "Field", "value": "Value"},
                        height=320,
                    )

                left_col, right_col = st.columns(2)
                with left_col:
                    render_table_section(
                        "Documented Activity / Documentation Basis",
                        "Performed and documented activity that drives the expected control logic. This is evidence-driven, not order-only.",
                        view.featured_story_proof.upstream_evidence,
                        column_labels={
                            "documentation_event_id": "Documentation event",
                            "documentation_type": "Documentation type",
                            "documentation_status": "Documentation status",
                            "activity_signal_id": "Activity signal",
                            "activity_description": "Activity description",
                            "activity_ts": "Activity at",
                            "performed_flag": "Performed",
                            "signal_basis": "Signal basis",
                            "traceable_to_documentation_flag": "Traceable to documentation",
                            "supports_charge_flag": "Supports charge",
                            "non_billable_reason": "Non-billable reason",
                        },
                        height=300,
                    )
                with right_col:
                    render_table_section(
                        "Expected Vs Actual Charge / Control Evidence",
                        "Expected opportunity logic against actual charge and claim-line state, with suppression kept visible when it applies.",
                        view.featured_story_proof.expected_vs_actual,
                        column_labels={
                            "expected_opportunity_id": "Expected opportunity",
                            "clinical_event": "Clinical event",
                            "expected_facility_charge_opportunity": "Expected opportunity description",
                            "evidence_completeness_status": "Evidence completeness",
                            "documented_performed_activity_flag": "Documented performed activity",
                            "separately_billable_flag": "Separately billable",
                            "actual_charge_status": "Actual charge status",
                            "actual_claim_line_status": "Claim-line status",
                            "opportunity_status": "Opportunity status",
                            "suppression_flag": "Suppressed",
                            "why_not_billable_explanation": "Why not billable",
                        },
                        height=300,
                    )

    render_revenue_integrity_decision_pack_panel(
        repo_root=repo_root,
        filters=view.filters,
    )

    if view.filtered_population.empty:
        st.warning("No active routed work matches the current filters.")
        return

    section_left, section_right = st.columns([1.05, 1.35])
    with section_left:
        render_table_section(
            "Why The Backlog Exists",
            "Issue domain and root cause mechanism together so the current control failure is visible, not just the queue count.",
            view.issue_root_cause_summary,
            column_labels={
                "issue_domain": "Issue domain",
                "root_cause_mechanism": "Root cause mechanism",
                "open_exceptions": "Open",
                "recoverable_dollars": "Recoverable $",
            },
            integer_columns=("open_exceptions",),
            currency_columns=("recoverable_dollars",),
            column_widths={
                "issue_domain": "medium",
                "root_cause_mechanism": "medium",
                "open_exceptions": "small",
                "recoverable_dollars": "small",
            },
            height=320,
        )
    with section_right:
        render_table_section(
            "Where Work Is Stuck Now",
            "Current stage, blocker, queue, owner, open volume, urgency, and age for the active backlog.",
            view.stage_bottleneck_summary,
            column_labels={
                "current_prebill_stage": "Stage",
                "current_primary_blocker_state": "Primary blocker",
                "current_queue": "Queue",
                "accountable_owner": "Owner",
                "open_exceptions": "Open",
                "urgent_exceptions": "Urgent",
                "average_age_days": "Avg age d",
            },
            integer_columns=("open_exceptions", "urgent_exceptions"),
            decimal_columns=("average_age_days",),
            column_widths={
                "current_prebill_stage": "small",
                "current_primary_blocker_state": "medium",
                "current_queue": "small",
                "accountable_owner": "small",
                "open_exceptions": "small",
                "urgent_exceptions": "small",
                "average_age_days": "small",
            },
            height=320,
        )

    section_left, section_right = st.columns([1.25, 0.95])
    with section_left:
        render_table_section(
            "Who Should Act Next",
            "Owner, queue, and blocker combinations carrying the most urgent current follow-through.",
            view.owner_action_summary,
            column_labels={
                "accountable_owner": "Owner",
                "current_queue": "Queue",
                "current_primary_blocker_state": "Blocker",
                "open_exceptions": "Open",
                "urgent_exceptions": "Urgent",
                "recoverable_dollars": "Recoverable $",
            },
            integer_columns=("open_exceptions", "urgent_exceptions"),
            currency_columns=("recoverable_dollars",),
            column_widths={
                "accountable_owner": "small",
                "current_queue": "small",
                "current_primary_blocker_state": "medium",
                "open_exceptions": "small",
                "urgent_exceptions": "small",
                "recoverable_dollars": "small",
            },
            height=300,
        )
    with section_right:
        render_table_section(
            "What Should Not Be Worked As Leakage",
            "Suppressed packaged, non-billable, and false-positive work stays visible here but secondary to the active control story.",
            view.suppression_summary,
            column_labels={
                "bucket": "Bucket",
                "encounter_count": "Cases",
                "share_of_scope": "Share",
                "routing_state": "Routing state",
            },
            integer_columns=("encounter_count",),
            percent_columns=("share_of_scope",),
            column_widths={
                "bucket": "medium",
                "encounter_count": "small",
                "share_of_scope": "small",
                "routing_state": "medium",
            },
            height=300,
        )

    section_left, section_right = st.columns(2)
    with section_left:
        render_table_section(
            "What Pattern Is Recurring",
            "Repeat routing patterns surfaced by issue domain and root cause mechanism.",
            view.recurring_patterns,
            column_labels={
                "issue_domain": "Issue domain",
                "root_cause_mechanism": "Root cause mechanism",
                "open_exceptions": "Open exceptions",
                "repeat_exceptions": "Repeat exceptions",
                "repeat_rate": "Repeat rate",
            },
            integer_columns=("open_exceptions", "repeat_exceptions"),
            percent_columns=("repeat_rate",),
            height=300,
        )
    with section_right:
        with panel():
            render_section_header(
                "Backlog Trend",
                "Seven-day trend of open actionable exceptions and recoverable dollars.",
            )
            trend_chart = view.backlog_trend.set_index("snapshot_date")[["open_exceptions"]]
            st.line_chart(trend_chart, use_container_width=True)
            render_dataframe(
                view.backlog_trend,
                column_labels={
                    "snapshot_date": "Snapshot date",
                    "open_exceptions": "Open exceptions",
                    "recoverable_dollars": "Recoverable dollars",
                },
                integer_columns=("open_exceptions",),
                currency_columns=("recoverable_dollars",),
                height=220,
            )

    render_table_section(
        "Current Routed Worklist",
        "Current routed work with stage, blocker, issue domain, root cause, owner, aging, and recoverability in one place.",
        view.worklist,
        column_labels={
            "queue_item_id": "Queue item",
            "current_prebill_stage": "Current stage",
            "current_primary_blocker_state": "Current primary blocker",
            "current_queue": "Current queue",
            "accountable_owner": "Owner",
            "days_in_stage": "Days in stage",
            "sla_status": "SLA status",
            "recoverability_status": "Recoverability",
            "department": "Department",
            "service_line": "Service line",
            "issue_domain": "Issue domain",
            "root_cause_mechanism": "Root cause mechanism",
            "estimated_gross_dollars": "Estimated gross dollars",
            "why_not_billable_explanation": "Current blocker explanation",
        },
        integer_columns=("days_in_stage",),
        currency_columns=("estimated_gross_dollars",),
        status_columns=("sla_status", "recoverability_status"),
        height=460,
    )

    with st.expander("Data / Validation Status", expanded=False):
        render_kpi_row(
            [
                KpiCard(
                    "Latest build (UTC)",
                    view.artifact_lineage.build_timestamp_utc,
                    "Timestamp from run_manifest.json for the artifacts backing the current app session.",
                ),
                KpiCard(
                    "Validation status",
                    view.artifact_lineage.overall_validation_status,
                    "Overall manifest status from the latest validate command.",
                ),
                KpiCard(
                    "Last validated (UTC)",
                    view.artifact_lineage.last_validated_at_utc,
                    "Most recent manifest validation timestamp, or Not set if validate has not been run.",
                ),
                KpiCard(
                    "Artifacts tracked",
                    format_count(len(view.artifact_lineage.artifact_row_counts)),
                    "Number of processed artifacts with row counts recorded in the manifest.",
                ),
            ]
        )

        section_left, section_right = st.columns(2)
        with section_left:
            render_table_section(
                "Manifest Summary",
                "Build timestamp, validation results, seed, and version controls for the current artifact set.",
                view.artifact_lineage.manifest_summary,
                column_labels={
                    "field": "Field",
                    "value": "Value",
                },
                height=360,
            )
        with section_right:
            render_table_section(
                "Artifact Row Counts",
                "Current processed artifact inventory from the latest manifest.",
                view.artifact_lineage.artifact_row_counts,
                column_labels={
                    "artifact": "Artifact",
                    "row_count": "Row count",
                },
                integer_columns=("row_count",),
                height=360,
            )
