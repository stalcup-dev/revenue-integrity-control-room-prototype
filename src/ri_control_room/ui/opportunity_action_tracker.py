from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.case_detail import build_case_detail_payload
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
)
from ri_control_room.ui.theme import (
    KpiCard,
    panel,
    render_kpi_row,
    render_page_shell,
    render_section_header,
    render_table_section,
)


@dataclass(frozen=True)
class OpportunityActionTrackerView:
    filters: SummaryFilters
    filter_options: dict[str, tuple[str, ...]]
    filtered_population: pd.DataFrame
    story_cue: PageStoryCue
    queue_item_selector_options: tuple[str, ...]
    default_selected_queue_item_id: str | None
    queue_priority_ranking: pd.DataFrame
    recurring_issue_patterns: pd.DataFrame
    intervention_owner_summary: pd.DataFrame
    action_tracker: pd.DataFrame
    open_actions_count: int


def _base_population(repo_root: Path | None = None) -> pd.DataFrame:
    population = load_work_population(repo_root)
    try:
        intervention_tracking = load_processed_artifact("intervention_tracking", repo_root)
    except FileNotFoundError:
        return population
    return population.merge(
        intervention_tracking,
        on=[
            "queue_item_id",
            "account_status_id",
            "claim_id",
            "account_id",
            "encounter_id",
            "department",
            "service_line",
            "current_queue",
            "current_prebill_stage",
            "issue_domain",
            "root_cause_mechanism",
        ],
        how="left",
        suffixes=("", "_intervention"),
    )


def _action_path(root_cause_mechanism: str) -> str:
    mapping = {
        "Documentation behavior": "Education",
        "Workflow / handoff": "Billing",
        "Coding practice": "Coding",
        "Billing edit management": "Billing",
        "CDM / rule configuration": "Build",
    }
    return mapping.get(root_cause_mechanism, "Education")


def _next_action(action_path: str) -> str:
    reverse_lookup = {
        "Education": "Documentation behavior",
        "Build": "CDM / rule configuration",
        "Coding": "Coding practice",
        "Billing": "Workflow / handoff",
    }
    return next_action_for_root_cause(reverse_lookup[action_path])


def _intervention_owner(row: pd.Series) -> str:
    action_path = row["action_path"]
    if action_path == "Education":
        return str(row["supporting_owner"] or row["accountable_owner"])
    if action_path == "Build":
        return str(row["escalation_owner"] or row["supporting_owner"] or row["accountable_owner"])
    if action_path == "Coding":
        if row["current_queue"] == "Coding Pending Review":
            return str(row["accountable_owner"])
        return str(row["supporting_owner"] or row["accountable_owner"])
    return str(row["accountable_owner"])


def _target_completion_date(row: pd.Series) -> str:
    snapshot_ts = pd.to_datetime(row["queue_snapshot_ts"])
    days_remaining = max(int(row["overdue_threshold_days"]) - int(row["stage_age_days"]), 0)
    if row["sla_status"] == "Overdue":
        target_ts = snapshot_ts.normalize() + pd.Timedelta(days=1)
    elif row["sla_status"] == "At risk":
        target_ts = snapshot_ts.normalize() + pd.Timedelta(days=max(1, days_remaining))
    else:
        target_ts = snapshot_ts.normalize() + pd.Timedelta(days=max(2, days_remaining))
    return target_ts.strftime("%Y-%m-%d")


def _checkpoint_status(row: pd.Series) -> str:
    if row["sla_status"] == "Overdue":
        return "Checkpoint overdue"
    if row["sla_status"] == "At risk":
        return "Checkpoint due now"
    if row["repeat_exception_flag"]:
        return "Monitor recurrence"
    return "On track"


def _before_after_validation_note(action_path: str) -> str:
    notes = {
        "Education": "Compare documentation-support volume and reroute recurrence on the next validation run.",
        "Build": "Rerun build and validate queue routing, suppression, or CDM-rule behavior after change.",
        "Coding": "Compare coding or modifier exception volume and queue age before and after validation.",
        "Billing": "Confirm hold clearance, queue exit, and recoverable dollars remaining on the next validation run.",
    }
    return notes[action_path]


def _recommendation(row: pd.Series) -> str:
    if row["repeat_exception_flag"] and row["recoverability_status"] == "Pre-final-bill recoverable":
        return "Expand"
    if row["sla_status"] == "Within SLA" and not row["repeat_exception_flag"]:
        return "Hold"
    return "Revise"


def _queue_priority_ranking(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "priority_rank",
                "queue_item_id",
                "current_prebill_stage",
                "current_primary_blocker_state",
                "current_queue",
                "issue_domain",
                "root_cause_mechanism",
                "accountable_owner",
                "days_in_stage",
                "sla_status",
                "recoverability_status",
                "estimated_gross_dollars",
            ]
        )
    ranking = filtered[
        [
            "priority_rank",
            "queue_item_id",
            "current_prebill_stage",
            "current_primary_blocker_state",
            "current_queue",
            "issue_domain",
            "root_cause_mechanism",
            "accountable_owner",
            "days_in_stage",
            "sla_status",
            "recoverability_status",
            "estimated_gross_dollars",
        ]
    ].copy()
    ranking["estimated_gross_dollars"] = ranking["estimated_gross_dollars"].round(2)
    return ranking


def _queue_item_selector_options(filtered: pd.DataFrame) -> tuple[str, ...]:
    if filtered.empty:
        return ()
    return tuple(filtered["queue_item_id"].tolist())


def _default_selected_queue_item_id(filtered: pd.DataFrame) -> str | None:
    if filtered.empty:
        return None
    return str(filtered.iloc[0]["queue_item_id"])


def _queue_item_label(filtered: pd.DataFrame, queue_item_id: str) -> str:
    match = filtered.loc[filtered["queue_item_id"] == queue_item_id]
    if match.empty:
        return queue_item_id
    row = match.iloc[0]
    return (
        f"{queue_item_id} | {row['encounter_id']} | {row['current_queue']} | "
        f"{row['current_primary_blocker_state']} | {row['accountable_owner']}"
    )


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


def _render_control_narrative(narrative: str) -> None:
    import streamlit as st

    with panel():
        render_section_header(
            "Control Narrative",
            "One deterministic sentence that ties evidence, expected opportunity, current blocker, ownership, recoverability, and suppression together.",
        )
        if hasattr(st, "markdown"):
            st.markdown(narrative)
            return
        st.caption(narrative)


def _cue_action_text(row: pd.Series) -> str:
    queue_name = str(row["current_queue"])
    queue_actions = {
        "Modifiers / Edits / Prebill Holds": "clear the prebill hold",
        "Correction / Rebill Pending": "work the correction / rebill path",
        "Documentation Support Exceptions": "close the documentation support gap",
        "Coding Pending Review": "route coding review",
        "Charge Reconciliation Monitor": "reconcile the encounter",
    }
    if queue_name in queue_actions:
        return queue_actions[queue_name]

    action_path = str(row.get("action_path", ""))
    action_map = {
        "Education": "close the documentation support gap",
        "Build": "correct the build issue",
        "Coding": "route coding review",
        "Billing": "clear the active queue blocker",
    }
    return action_map.get(action_path, "work the active exception")


def _cue_validation_clause(row: pd.Series) -> str:
    queue_name = str(row["current_queue"])
    queue_validations = {
        "Modifiers / Edits / Prebill Holds": "validate queue exit on the next run",
        "Correction / Rebill Pending": "validate turnaround on the next run",
        "Documentation Support Exceptions": "validate documentation-support recurrence on the next run",
        "Coding Pending Review": "validate coding-review recurrence after validation",
        "Charge Reconciliation Monitor": "validate reconciliation workdown on the next run",
    }
    if queue_name in queue_validations:
        return queue_validations[queue_name]

    action_path = str(row.get("action_path", ""))
    action_map = {
        "Education": "validate documentation-support recurrence on the next run",
        "Build": "validate routing after the build change",
        "Coding": "validate coding-review recurrence after validation",
        "Billing": "validate queue exit on the next run",
    }
    return action_map.get(action_path, "validate the next checkpoint result")


def _story_cue(
    filtered: pd.DataFrame,
    action_tracker: pd.DataFrame,
) -> PageStoryCue:
    if filtered.empty or action_tracker.empty:
        return PageStoryCue(
            sentence="Owned intervention follow-through is out of scope for the current filters.",
            callouts=(
                StoryCallout(
                    "Control",
                    "Intervention follow-through with checkpoint status and validation notes.",
                ),
                StoryCallout(
                    "Current pressure",
                    "No active intervention backlog is in scope right now.",
                ),
                StoryCallout(
                    "Next move",
                    "No hold / expand / revise decision is pending until active work re-enters scope.",
                ),
            ),
            note="Selected-case evidence trace will repopulate when active routed work exists.",
        )

    lead_row = action_tracker.sort_values(
        ["priority_rank", "queue_item_id"],
        ascending=[True, True],
        kind="mergesort",
    ).iloc[0]
    checkpoint_due_now = int(filtered["sla_status"].isin(["At risk", "Overdue"]).sum())
    sentence = (
        "Active routed exceptions are translated here into owned interventions with checkpoint "
        "and validation signals."
    )
    pressure_text = (
        f"{checkpoint_due_now} intervention checkpoint(s) are due now; "
        f"{lead_row['hold_expand_revise_recommendation']} leads on {lead_row['queue_item_id']}."
    )
    next_move = (
        f"{lead_row['intervention_owner']} should {_cue_action_text(lead_row)} on "
        f"{lead_row['queue_item_id']}; {_cue_validation_clause(lead_row)}."
    )
    return PageStoryCue(
        sentence=sentence,
        callouts=(
            StoryCallout(
                "Control",
                "Owned intervention path, checkpoint status, and observed follow-through on active work.",
            ),
            StoryCallout("Current pressure", pressure_text),
            StoryCallout("Next move", next_move),
        ),
        note=(
            "Hold / Expand / Revise is tied to the monitored metric and downstream signal, "
            "not generic task status."
        ),
    )


def _recurring_issue_patterns(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "issue_domain",
                "root_cause_mechanism",
                "action_path",
                "recurring_issue_pattern",
                "open_actions",
                "repeat_exceptions",
                "repeat_rate",
                "recoverable_dollars",
                "recommendation",
            ]
        )
    patterned = filtered.copy()
    if "action_path" not in patterned.columns:
        patterned["action_path"] = patterned["root_cause_mechanism"].map(_action_path)
    if "recurring_issue_pattern" not in patterned.columns:
        patterned["recurring_issue_pattern"] = patterned.apply(
            lambda row: f"{row['department']} | {row['current_queue']} | {row['root_cause_mechanism']}",
            axis=1,
        )
    if "hold_expand_revise_recommendation" not in patterned.columns:
        patterned["hold_expand_revise_recommendation"] = patterned.apply(_recommendation, axis=1)
    summary = (
        patterned.groupby(
            ["issue_domain", "root_cause_mechanism", "action_path", "recurring_issue_pattern"],
            as_index=False,
        )
        .agg(
            open_actions=("queue_item_id", "size"),
            repeat_exceptions=("repeat_exception_flag", "sum"),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
            recommendation=("hold_expand_revise_recommendation", lambda values: values.mode().iloc[0]),
        )
        .sort_values(["open_actions", "recoverable_dollars"], ascending=[False, False])
        .reset_index(drop=True)
    )
    summary["repeat_rate"] = (summary["repeat_exceptions"] / summary["open_actions"]).round(2)
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    return summary


def _intervention_owner_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "intervention_owner",
                "action_path",
                "open_actions",
                "checkpoint_due_now",
                "checkpoint_status_mix",
                "recoverable_dollars",
            ]
        )
    assignments = filtered.assign(
        action_path=lambda df: df.get("action_path", df["root_cause_mechanism"].map(_action_path)),
    )
    if "intervention_owner" not in assignments.columns:
        assignments["intervention_owner"] = assignments.apply(_intervention_owner, axis=1)
    if "checkpoint_status" not in assignments.columns:
        assignments["checkpoint_status"] = assignments.apply(_checkpoint_status, axis=1)
    assignments["checkpoint_due_now"] = assignments["checkpoint_status"].isin(
        ["Checkpoint overdue", "Monitor next checkpoint", "Turnaround improving"]
    )
    summary = (
        assignments.groupby(["intervention_owner", "action_path"], as_index=False)
        .agg(
            open_actions=("queue_item_id", "size"),
            checkpoint_due_now=("checkpoint_due_now", "sum"),
            checkpoint_status_mix=("checkpoint_status", lambda values: "; ".join(sorted(set(values)))),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(["checkpoint_due_now", "open_actions", "recoverable_dollars"], ascending=[False, False, False])
        .reset_index(drop=True)
    )
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    return summary


def _action_tracker(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(
            [
                "priority_rank",
                "queue_item_id",
                "issue_domain",
                "root_cause_mechanism",
                "current_prebill_stage",
                "current_primary_blocker_state",
                "current_queue",
                "intervention_type",
                "intervention_owner",
                "target_completion_date",
                "checkpoint_status",
                "baseline_metric",
                "current_metric",
                "correction_turnaround_signal",
                "downstream_outcome_signal",
                "before_after_validation_note",
                "hold_expand_revise_recommendation",
                "next_action",
            ]
        )
    tracker = filtered.copy()
    if "action_path" not in tracker.columns:
        tracker["action_path"] = tracker["root_cause_mechanism"].map(_action_path)
    if "intervention_type" not in tracker.columns:
        tracker["intervention_type"] = tracker["action_path"].map(
            {
                "Education": "Education",
                "Build": "Build / configuration fix",
                "Coding": "Coding follow-up",
                "Billing": "Billing / correction action",
            }
        )
    if "intervention_owner" not in tracker.columns:
        tracker["intervention_owner"] = tracker.apply(_intervention_owner, axis=1)
    if "target_completion_date" not in tracker.columns:
        tracker["target_completion_date"] = tracker.apply(_target_completion_date, axis=1)
    if "checkpoint_status" not in tracker.columns:
        tracker["checkpoint_status"] = tracker.apply(_checkpoint_status, axis=1)
    if "baseline_metric" not in tracker.columns:
        pattern_metrics = (
            tracker.groupby(["issue_domain", "root_cause_mechanism", "action_path"], as_index=False)
            .agg(
                pattern_open_actions=("queue_item_id", "size"),
                pattern_repeat_exceptions=("repeat_exception_flag", "sum"),
                pattern_recoverable_dollars=("estimated_gross_dollars", "sum"),
            )
        )
        pattern_metrics["pattern_repeat_rate"] = (
            pattern_metrics["pattern_repeat_exceptions"] / pattern_metrics["pattern_open_actions"]
        ).fillna(0.0)
        tracker = tracker.merge(
            pattern_metrics,
            on=["issue_domain", "root_cause_mechanism", "action_path"],
            how="left",
        )
        tracker["baseline_metric"] = tracker.apply(
            lambda row: (
                f"{int(row['pattern_open_actions'])} open in pattern; "
                f"{row['pattern_repeat_rate']:.0%} repeat routing baseline."
            ),
            axis=1,
        )
        tracker["current_metric"] = tracker.apply(
            lambda row: (
                f"{row['sla_status']}; {int(row['stage_age_days'])} days aged; "
                f"{format_currency(float(row['estimated_gross_dollars']))} open; "
                f"{row['recoverability_status']}."
            ),
            axis=1,
        )
    if "correction_turnaround_signal" not in tracker.columns:
        tracker["correction_turnaround_signal"] = "Not correction-led"
    if "downstream_outcome_signal" not in tracker.columns:
        tracker["downstream_outcome_signal"] = tracker["correction_turnaround_signal"]
    if "before_after_validation_note" not in tracker.columns:
        tracker["before_after_validation_note"] = tracker["action_path"].map(_before_after_validation_note)
    if "hold_expand_revise_recommendation" not in tracker.columns:
        tracker["hold_expand_revise_recommendation"] = tracker.apply(_recommendation, axis=1)
    tracker["next_action"] = tracker["action_path"].map(_next_action)
    return tracker[
        [
            "priority_rank",
            "queue_item_id",
            "issue_domain",
            "root_cause_mechanism",
            "current_prebill_stage",
            "current_primary_blocker_state",
            "current_queue",
            "intervention_type",
            "intervention_owner",
            "target_completion_date",
            "checkpoint_status",
            "baseline_metric",
            "current_metric",
            "correction_turnaround_signal",
            "downstream_outcome_signal",
            "before_after_validation_note",
            "hold_expand_revise_recommendation",
            "next_action",
        ]
    ].copy()


def build_opportunity_action_tracker_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> OpportunityActionTrackerView:
    population = _base_population(repo_root)
    normalized_filters = normalize_filters(filters)
    filter_options = get_filter_options(population)
    filtered = apply_filters(population, normalized_filters)
    action_tracker = _action_tracker(filtered)
    return OpportunityActionTrackerView(
        filters=normalized_filters,
        filter_options=filter_options,
        filtered_population=filtered,
        story_cue=_story_cue(filtered, action_tracker),
        queue_item_selector_options=_queue_item_selector_options(filtered),
        default_selected_queue_item_id=_default_selected_queue_item_id(filtered),
        queue_priority_ranking=_queue_priority_ranking(filtered),
        recurring_issue_patterns=_recurring_issue_patterns(filtered),
        intervention_owner_summary=_intervention_owner_summary(filtered),
        action_tracker=action_tracker,
        open_actions_count=int(len(filtered)),
    )


def render_opportunity_action_tracker_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        "Priority-ranked intervention view of who should act next, what pattern is recurring, and how to validate follow-through across current active work.",
        scope_note,
        badges=("Facility-side only", "Outpatient-first", "Deterministic routing"),
    )
    selected_filters = get_global_filters(global_filter_options)
    view = build_opportunity_action_tracker_view(repo_root=repo_root, filters=selected_filters)
    render_active_filter_summary(view.filters)
    render_page_story_cue(view.story_cue)

    render_section_header(
        "Intervention Snapshot",
        "Top-line operating view of open interventions, recurring patterns, and accountable follow-through.",
    )
    render_kpi_row(
        [
            KpiCard(
                "Open interventions",
                format_count(view.open_actions_count),
                "Priority-ranked work items currently requiring visible intervention follow-through.",
            ),
            KpiCard(
                "Checkpoint due now",
                format_count(int(view.filtered_population["sla_status"].isin(["At risk", "Overdue"]).sum())),
                "Items that need immediate review or escalation based on current SLA status.",
            ),
            KpiCard(
                "Recurring actions",
                format_count(int(view.filtered_population["repeat_exception_flag"].sum())),
                "Open items that have already rerouted at least once and may need broader intervention.",
            ),
            KpiCard(
                "Intervention owners",
                format_count(
                    int(view.intervention_owner_summary["intervention_owner"].nunique())
                    if not view.intervention_owner_summary.empty
                    else 0
                ),
                "Distinct owners currently carrying intervention follow-through.",
            ),
        ]
    )

    if view.filtered_population.empty:
        st.warning("No action-tracker work matches the current filters.")
        return

    render_table_section(
        "Queue Priority Ranking",
        "Priority-ordered queue view for rapid triage of stage, blocker, owner, aging, and recoverability.",
        view.queue_priority_ranking,
        column_labels={
            "priority_rank": "Priority rank",
            "queue_item_id": "Queue item",
            "current_prebill_stage": "Current stage",
            "current_primary_blocker_state": "Current primary blocker",
            "current_queue": "Current queue",
            "issue_domain": "Issue domain",
            "root_cause_mechanism": "Root cause mechanism",
            "accountable_owner": "Accountable owner",
            "days_in_stage": "Days in stage",
            "sla_status": "SLA status",
            "recoverability_status": "Recoverability",
            "estimated_gross_dollars": "Estimated gross dollars",
        },
        integer_columns=("priority_rank", "days_in_stage"),
        status_columns=("sla_status", "recoverability_status"),
        currency_columns=("estimated_gross_dollars",),
        height=340,
    )

    render_section_header(
        "Selected Case Evidence Trace",
        "Choose one active queue item from the current worklist and inspect the full deterministic control story.",
    )
    selected_queue_item_id = st.selectbox(
        "Queue item",
        options=list(view.queue_item_selector_options),
        index=0,
        format_func=lambda queue_item_id: _queue_item_label(
            view.filtered_population,
            queue_item_id,
        ),
    )
    selected_payload = build_case_detail_payload(selected_queue_item_id, repo_root)
    intervention_follow_through_table = _detail_mapping_table(
        selected_payload.intervention_follow_through,
        (
            ("intervention_type", "Intervention type"),
            ("action_path", "Action path"),
            ("intervention_owner", "Intervention owner"),
            ("target_completion_date", "Target completion date"),
            ("checkpoint_status", "Checkpoint status"),
            ("baseline_metric", "Baseline metric"),
            ("current_metric", "Current metric"),
            ("before_after_validation_note", "Before / after validation note"),
            ("hold_expand_revise_recommendation", "Recommendation"),
            ("recommendation_rationale", "Recommendation rationale"),
        ),
    )
    downstream_outcome_table = _detail_mapping_table(
        selected_payload.downstream_outcome,
        (
            ("downstream_outcome_type", "Outcome signal type"),
            ("downstream_outcome_signal", "Outcome signal"),
            ("correction_turnaround_signal", "Turnaround trend"),
            ("correction_turnaround_days", "Observed correction turnaround days"),
            ("rebill_outcome_status", "Observed rebill outcome status"),
            ("correction_type", "Correction type"),
            ("correction_id", "Correction ID"),
            ("rebill_required_flag", "Rebill required"),
            ("financial_recovery_pathway", "Financial recovery pathway"),
            ("last_activity_datetime", "Last downstream activity"),
        ),
    )

    suppression_label = (
        "Suppressed by design"
        if selected_payload.suppression_note["suppressed_case_flag"]
        else "No suppression on current expected rows"
    )
    render_kpi_row(
        [
            KpiCard(
                "Current blocker",
                str(selected_payload.classification["current_primary_blocker_state"]),
                "The one governed blocker that is allowed to drive the current active queue item.",
            ),
            KpiCard(
                "Current owner",
                str(selected_payload.classification["accountable_owner"]),
                "The accountable owner for the current routed blocker.",
            ),
            KpiCard(
                "Recoverability",
                str(selected_payload.classification["recoverability_status"]),
                "Financial recovery framing for the current case.",
            ),
            KpiCard(
                "Suppression status",
                suppression_label,
                "Suppressed expected opportunities are distinct from active leakage and stay visible here.",
            ),
        ]
    )
    _render_control_narrative(selected_payload.control_narrative)
    if selected_payload.suppression_note["suppressed_case_flag"]:
        st.info(str(selected_payload.suppression_note["note_text"]))
    else:
        st.caption(
            "No suppressed expected opportunities are attached to the currently selected queue item."
        )

    render_section_header(
        "Selected Intervention Follow-Through",
        "Compact end-to-end view of the intervention path, monitored metric, downstream result, and current hold / expand / revise recommendation.",
    )
    left_col, right_col = st.columns(2)
    with left_col:
        render_table_section(
            "Intervention Follow-Through",
            "The active intervention is kept separate from the exception type and shown with owner, checkpoint, metric, and validation note.",
            intervention_follow_through_table,
            column_labels={
                "field": "Field",
                "value": "Value",
            },
            height=360,
        )
    with right_col:
        render_table_section(
            "Downstream Outcome Signal",
            "Observed correction / rebill or operating-result signal tied to the selected intervention path.",
            downstream_outcome_table,
            column_labels={
                "field": "Field",
                "value": "Value",
            },
            height=360,
        )

    header_table = _detail_mapping_table(
        selected_payload.case_header,
        (
            ("queue_item_id", "Queue item"),
            ("encounter_id", "Encounter"),
            ("claim_id", "Claim"),
            ("account_id", "Account"),
            ("department", "Department"),
            ("service_line", "Service line"),
            ("patient_type", "Patient type"),
            ("scenario_code", "Scenario code"),
            ("current_stage", "Current stage"),
            ("current_queue", "Current queue"),
            ("accountable_owner", "Accountable owner"),
            ("days_in_stage", "Days in stage"),
            ("sla_status", "SLA status"),
            ("aging_basis_label", "Aging basis"),
            ("priority_rank", "Priority rank"),
            ("priority_score", "Priority score"),
            ("estimated_gross_dollars", "Estimated gross dollars"),
        ),
    )
    classification_table = _detail_mapping_table(
        selected_payload.classification,
        (
            ("issue_domain", "Issue domain"),
            ("root_cause_mechanism", "Root cause mechanism"),
            ("current_primary_blocker_state", "Current blocker"),
            ("current_primary_blocker_code", "Current blocker code"),
            ("accountable_owner", "Accountable owner"),
            ("supporting_owner", "Supporting owner"),
            ("recoverability_status", "Recoverability"),
            ("recoverability_financial_meaning", "Financial meaning"),
            ("recoverability_window_rule", "Recoverability window rule"),
            ("reconciliation_status", "Reconciliation status"),
            ("evidence_completeness_status", "Evidence completeness"),
            ("why_not_billable_explanation", "Why not billable explanation"),
            ("failure_summary", "Failure summary"),
        ),
    )
    queue_governance_table = _detail_mapping_table(
        selected_payload.queue_governance,
        (
            ("current_queue", "Current queue"),
            ("current_stage", "Current stage"),
            ("accountable_owner", "Accountable owner"),
            ("supporting_owner", "Supporting owner"),
            ("escalation_owner", "Escalation owner"),
            ("days_in_stage", "Days in stage"),
            ("sla_status", "SLA status"),
            ("aging_basis_label", "Aging basis label"),
            ("clock_start_event", "Clock start event"),
            ("queue_entry_rule", "Entry rule"),
            ("queue_exit_rule", "Exit rule"),
            ("escalation_trigger", "Escalation trigger"),
            ("queue_aging_clock_start_basis", "Queue aging basis"),
            ("sla_target_days", "SLA target days"),
            ("overdue_threshold_days", "Overdue threshold days"),
            ("queue_business_purpose", "Business purpose"),
        ),
    )
    routing_table = _detail_mapping_table(
        selected_payload.routing_history,
        (
            ("transition_event_count", "Transition events"),
            ("transition_event_index", "Current event index"),
            ("transition_event_type", "Current event type"),
            ("current_queue", "Current queue"),
            ("prior_queue", "Prior queue"),
            ("current_prebill_stage", "Current stage"),
            ("prior_stage", "Prior stage"),
            ("reroute_count", "Reroute count"),
            ("ever_rerouted_flag", "Ever rerouted"),
            ("first_queue_entry_ts", "First queue entry"),
            ("current_queue_entry_ts", "Current queue entry"),
            ("latest_reroute_ts", "Latest reroute"),
            ("stage_transition_path", "Stage transition path"),
            ("queue_transition_path", "Queue transition path"),
            ("routing_reason", "Routing reason"),
        ),
    )

    left_col, right_col = st.columns(2)
    with left_col:
        render_table_section(
            "Case Header",
            "Who the case is, where it sits now, and why it matters operationally.",
            header_table,
            column_labels={
                "field": "Field",
                "value": "Value",
            },
            height=360,
        )
    with right_col:
        render_table_section(
            "Classification",
            "Current failure logic with issue domain and root cause kept separate from ownership and recoverability.",
            classification_table,
            column_labels={
                "field": "Field",
                "value": "Value",
            },
            height=360,
        )

    render_table_section(
        "Queue Governance",
        "Governed operating definition for the currently selected exception, including queue purpose, stage aging basis, SLA thresholds, and escalation conditions.",
        queue_governance_table,
        column_labels={
            "field": "Field",
            "value": "Value",
        },
        height=360,
    )

    left_col, right_col = st.columns(2)
    with left_col:
        render_table_section(
            "Routing History",
            "Current routing path and prior queue movement for the selected active item.",
            routing_table,
            column_labels={
                "field": "Field",
                "value": "Value",
            },
            height=320,
        )
    with right_col:
        render_table_section(
            "Expected Vs Actual",
            "Expected opportunity logic against actual charge and claim-line state, with suppressed rows left visible instead of treated as leakage.",
            selected_payload.expected_vs_actual,
            column_labels={
                "expected_opportunity_id": "Expected opportunity",
                "clinical_event": "Clinical event",
                "expected_facility_charge_opportunity": "Expected opportunity description",
                "expected_code_hint": "Expected code",
                "expected_modifier_hint": "Expected modifier",
                "expected_units": "Expected units",
                "evidence_completeness_status": "Evidence completeness",
                "separately_billable_flag": "Separately billable",
                "charge_event_exists_flag": "Charge exists",
                "actual_charge_status": "Actual charge status",
                "actual_charge_code": "Actual charge code",
                "actual_modifier_code": "Actual modifier",
                "actual_claim_line_status": "Claim-line status",
                "actual_gross_charge_amount": "Actual gross charge amount",
                "opportunity_status": "Opportunity status",
                "suppression_flag": "Suppressed",
                "why_not_billable_explanation": "Why not billable",
            },
            decimal_columns=("expected_units",),
            currency_columns=("actual_gross_charge_amount",),
            height=320,
        )

    render_table_section(
        "Upstream Evidence",
        "Order context plus the documented performed-activity evidence that explains what happened before queue routing. The control story is driven by documented activity, not orders alone.",
        selected_payload.upstream_evidence,
        column_labels={
            "order_id": "Order",
            "order_type": "Order type",
            "order_status": "Order status",
            "ordered_ts": "Ordered at",
            "documentation_event_id": "Documentation event",
            "documentation_type": "Documentation type",
            "documentation_status": "Documentation status",
            "documentation_event_ts": "Documentation event at",
            "documentation_completion_ts": "Documentation completed at",
            "documentation_gap_type": "Documentation gap",
            "activity_signal_id": "Activity signal",
            "signal_type": "Signal type",
            "activity_code": "Activity code",
            "activity_description": "Activity description",
            "activity_ts": "Activity at",
            "performed_flag": "Performed",
            "signal_support_status": "Support status",
            "signal_basis": "Signal basis",
            "traceable_to_documentation_flag": "Traceable to documentation",
            "packaged_or_integral_candidate_flag": "Packaged candidate",
            "non_billable_candidate_flag": "Non-billable candidate",
            "non_billable_reason": "Non-billable reason",
            "late_post_risk_flag": "Late-post risk",
            "timestamp_dependency_flag": "Timestamp dependency",
        },
        height=360,
    )

    left_col, right_col = st.columns(2)
    with left_col:
        render_table_section(
            "Recurring Issue Patterns",
            "Recurring issue and root-cause patterns that may justify hold, revise, or expand decisions.",
            view.recurring_issue_patterns,
            column_labels={
                "issue_domain": "Issue domain",
                "root_cause_mechanism": "Root cause mechanism",
                "action_path": "Action path",
                "recurring_issue_pattern": "Recurring pattern",
                "open_actions": "Open actions",
                "repeat_exceptions": "Repeat exceptions",
                "repeat_rate": "Repeat rate",
                "recoverable_dollars": "Recoverable dollars",
                "recommendation": "Recommendation",
            },
            integer_columns=("open_actions", "repeat_exceptions"),
            percent_columns=("repeat_rate",),
            currency_columns=("recoverable_dollars",),
            status_columns=("recommendation",),
            height=300,
        )
    with right_col:
        render_table_section(
            "Intervention Owners",
            "Who should act next by action path, open volume, and items already at checkpoint.",
            view.intervention_owner_summary,
            column_labels={
                "intervention_owner": "Intervention owner",
                "action_path": "Action path",
                "open_actions": "Open actions",
                "checkpoint_due_now": "Checkpoint due now",
                "checkpoint_status_mix": "Checkpoint mix",
                "recoverable_dollars": "Recoverable dollars",
            },
            integer_columns=("open_actions", "checkpoint_due_now"),
            currency_columns=("recoverable_dollars",),
            height=300,
        )

    render_table_section(
        "Intervention Plan",
        "Follow-through detail for intervention path, owner, target date, current metric, and validation note.",
        view.action_tracker,
        column_labels={
            "priority_rank": "Priority rank",
            "queue_item_id": "Queue item",
            "issue_domain": "Issue domain",
            "root_cause_mechanism": "Root cause mechanism",
            "current_prebill_stage": "Current stage",
            "current_primary_blocker_state": "Current primary blocker",
            "current_queue": "Current queue",
            "intervention_type": "Intervention type / action path",
            "intervention_owner": "Intervention owner",
            "target_completion_date": "Target completion date",
            "checkpoint_status": "Checkpoint status",
            "baseline_metric": "Baseline metric",
            "current_metric": "Current metric",
            "correction_turnaround_signal": "Correction turnaround",
            "downstream_outcome_signal": "Downstream outcome signal",
            "before_after_validation_note": "Before/after validation note",
            "hold_expand_revise_recommendation": "Recommendation",
            "next_action": "Next action",
        },
        integer_columns=("priority_rank",),
        status_columns=("checkpoint_status", "hold_expand_revise_recommendation"),
        height=460,
    )
