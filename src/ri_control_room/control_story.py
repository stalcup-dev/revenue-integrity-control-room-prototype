from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.case_detail import build_case_detail_payload


ANCHOR_DEPARTMENTS = (
    "Outpatient Infusion / Oncology Infusion",
    "Radiology / Interventional Radiology",
    "OR / Hospital Outpatient Surgery / Procedural Areas",
)

CONTROL_FAILURE_TYPES = {
    "Charge Reconciliation Monitor": "Charge capture reconciliation",
    "Documentation Support Exceptions": "Documentation support",
    "Coding Pending Review": "Coding alignment review",
    "Modifiers / Edits / Prebill Holds": "Prebill edit resolution",
    "Correction / Rebill Pending": "Correction / rebill follow-through",
}

ACTION_PATHS = {
    "Documentation behavior": "Education",
    "Workflow / handoff": "Billing",
    "Coding practice": "Coding",
    "Billing edit management": "Billing",
    "CDM / rule configuration": "Build",
}

NEXT_ACTIONS = {
    "Education": "Document coaching target and close documentation support gap.",
    "Build": "Open build correction and confirm rule or CDM change owner.",
    "Coding": "Route coding review and validate modifier or code alignment.",
    "Billing": "Work assigned queue, clear hold, and confirm account release path.",
}

EMPTY_STORY_TEXT = "No active routed exceptions match the current filters."
REPRESENTATIVE_CASE_SELECTION_NOTE = (
    "Representative case rule: highest current priority in the featured story scope; "
    "tie-breakers are oldest current stage aging, then stable queue item ID."
)


@dataclass(frozen=True)
class DeterministicControlStory:
    queue_item_id: str
    service_line: str
    department: str
    control_failure_type: str
    issue_domain: str
    root_cause_mechanism: str
    exception_pattern: str
    current_prebill_stage: str
    current_primary_blocker_state: str
    current_queue: str
    accountable_owner: str
    aging_sla_status: str
    recoverability_status: str
    why_it_matters: str
    recommended_next_action: str
    story_path: str


def _clean_text(value: object, *, fallback: str = "") -> str:
    if value is None or pd.isna(value):
        return fallback
    return str(value).strip()


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def next_action_for_root_cause(root_cause_mechanism: object) -> str:
    action_path = ACTION_PATHS.get(_clean_text(root_cause_mechanism), "Education")
    return NEXT_ACTIONS[action_path]


def _select_story_row(filtered: pd.DataFrame) -> pd.Series | None:
    if filtered.empty:
        return None
    anchor_rows = filtered.loc[filtered["department"].isin(ANCHOR_DEPARTMENTS)].copy()
    candidate_rows = anchor_rows if not anchor_rows.empty else filtered
    return candidate_rows.iloc[0]


def _story_cohort(filtered: pd.DataFrame, selected_row: pd.Series) -> pd.DataFrame:
    keys = [
        "department",
        "service_line",
        "issue_domain",
        "root_cause_mechanism",
        "current_prebill_stage",
        "current_primary_blocker_state",
        "current_queue",
        "accountable_owner",
        "recoverability_status",
    ]
    cohort = filtered.copy()
    for key in keys:
        cohort = cohort.loc[cohort[key] == selected_row[key]]
    return cohort.copy()


def story_scope_population(
    filtered: pd.DataFrame,
    story: DeterministicControlStory,
) -> pd.DataFrame:
    if filtered.empty or story.queue_item_id == "":
        return filtered.iloc[0:0].copy()
    scope = filtered.copy()
    comparisons = {
        "department": story.department,
        "service_line": story.service_line,
        "issue_domain": story.issue_domain,
        "root_cause_mechanism": story.root_cause_mechanism,
        "current_prebill_stage": story.current_prebill_stage,
        "current_primary_blocker_state": story.current_primary_blocker_state,
        "current_queue": story.current_queue,
        "accountable_owner": story.accountable_owner,
        "recoverability_status": story.recoverability_status,
    }
    for column, value in comparisons.items():
        scope = scope.loc[scope[column] == value]
    return scope.copy()


def select_representative_case_row(
    filtered: pd.DataFrame,
    story: DeterministicControlStory,
) -> pd.Series | None:
    scope = story_scope_population(filtered, story)
    if scope.empty:
        return None
    # Keep the reviewer drill path deterministic inside the featured-story cohort:
    # highest priority first, then oldest current-stage aging, then stable queue item ID.
    ordered = scope.sort_values(
        ["priority_rank", "days_in_stage", "queue_item_id"],
        ascending=[True, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    return ordered.iloc[0]


def _primary_expected_opportunity(case_payload) -> pd.Series | None:
    expected_vs_actual = case_payload.expected_vs_actual.copy()
    if expected_vs_actual.empty:
        return None

    supported = expected_vs_actual.loc[
        expected_vs_actual["documented_performed_activity_flag"].fillna(False)
        & expected_vs_actual["separately_billable_flag"].fillna(False)
        & ~expected_vs_actual["packaged_or_integral_flag"].fillna(False)
        & ~expected_vs_actual["suppression_flag"].fillna(False)
    ].copy()
    if not supported.empty:
        return supported.iloc[0]

    visible = expected_vs_actual.loc[~expected_vs_actual["suppression_flag"].fillna(False)].copy()
    if not visible.empty:
        return visible.iloc[0]
    return expected_vs_actual.iloc[0]


def _build_exception_pattern(
    selected_row: pd.Series,
    cohort: pd.DataFrame,
    detail_row: pd.Series | None,
) -> str:
    count = int(len(cohort))
    count_text = "1 routed exception" if count == 1 else f"{count} routed exceptions"
    pattern = (
        f"{count_text} in {selected_row['service_line']} show {selected_row['issue_domain']} "
        f"from {selected_row['root_cause_mechanism']}."
    )
    if detail_row is None:
        return pattern

    signal_basis = _clean_text(
        detail_row.get("signal_basis"),
        fallback="documented_performed_activity",
    ).replace("_", " ")
    clinical_event = _clean_text(detail_row.get("clinical_event"))
    expected_opportunity = _clean_text(detail_row.get("expected_facility_charge_opportunity"))
    actual_charge_status = _clean_text(
        detail_row.get("actual_charge_status"),
        fallback="no posted charge",
    ).replace("_", " ")

    detail_parts = []
    if expected_opportunity and clinical_event:
        detail_parts.append(
            f"documented performed activity from {signal_basis} supports {expected_opportunity} for {clinical_event}"
        )
    elif expected_opportunity:
        detail_parts.append(
            f"documented performed activity from {signal_basis} supports {expected_opportunity}"
        )
    if actual_charge_status:
        detail_parts.append(f"actual charge state is {actual_charge_status}")
    if not detail_parts:
        return pattern
    return f"{pattern} " + "; ".join(detail_parts) + "."


def _build_aging_sla_status(selected_row: pd.Series) -> str:
    days_in_stage = int(selected_row["days_in_stage"])
    overdue_threshold_days = int(selected_row["overdue_threshold_days"])
    aging_basis_label = _clean_text(
        selected_row.get("aging_basis_label"),
        fallback="Days in current stage",
    )
    sla_status = _clean_text(selected_row.get("sla_status"), fallback="Within SLA")
    return (
        f"{days_in_stage} days in stage ({aging_basis_label}); "
        f"{sla_status} against {overdue_threshold_days}-day threshold."
    )


def _build_why_it_matters(
    selected_row: pd.Series,
    cohort: pd.DataFrame,
    case_payload,
) -> str:
    cohort_count = int(len(cohort))
    cohort_dollars = float(cohort["estimated_gross_dollars"].sum())
    cohort_text = "1 like-for-like account" if cohort_count == 1 else f"{cohort_count} like-for-like accounts"
    sentence = (
        f"{cohort_text} total {_format_currency(cohort_dollars)} gross and "
        f"sit in {selected_row['recoverability_status']} after "
        f"{int(selected_row['days_in_stage'])} days in the current stage."
    )
    if case_payload.suppression_note.get("suppressed_case_flag"):
        return (
            f"{sentence} Suppressed expected opportunities stay excluded from leakage counts."
        )
    return sentence


def _empty_story() -> DeterministicControlStory:
    return DeterministicControlStory(
        queue_item_id="",
        service_line="No active slice",
        department="No active slice",
        control_failure_type=EMPTY_STORY_TEXT,
        issue_domain="No active slice",
        root_cause_mechanism="No active slice",
        exception_pattern=EMPTY_STORY_TEXT,
        current_prebill_stage="No active slice",
        current_primary_blocker_state="No active slice",
        current_queue="No active slice",
        accountable_owner="No active slice",
        aging_sla_status=EMPTY_STORY_TEXT,
        recoverability_status="No active slice",
        why_it_matters=EMPTY_STORY_TEXT,
        recommended_next_action=EMPTY_STORY_TEXT,
        story_path=EMPTY_STORY_TEXT,
    )


def build_deterministic_control_story(
    filtered: pd.DataFrame,
    *,
    repo_root: Path | None = None,
) -> DeterministicControlStory:
    selected_row = _select_story_row(filtered)
    if selected_row is None:
        return _empty_story()

    case_payload = build_case_detail_payload(str(selected_row["queue_item_id"]), repo_root)
    detail_row = _primary_expected_opportunity(case_payload)
    cohort = _story_cohort(filtered, selected_row)
    control_failure_type = CONTROL_FAILURE_TYPES.get(
        _clean_text(selected_row.get("current_queue")),
        _clean_text(selected_row.get("queue_business_purpose"), fallback="Current routed control failure"),
    )
    exception_pattern = _build_exception_pattern(selected_row, cohort, detail_row)
    aging_sla_status = _build_aging_sla_status(selected_row)
    recommended_next_action = next_action_for_root_cause(selected_row.get("root_cause_mechanism"))
    story_path = " -> ".join(
        [
            control_failure_type,
            f"{selected_row['issue_domain']} from {selected_row['root_cause_mechanism']}",
            (
                f"{selected_row['current_prebill_stage']} | "
                f"{selected_row['current_primary_blocker_state']} | "
                f"{selected_row['current_queue']}"
            ),
            str(selected_row["accountable_owner"]),
            str(selected_row["recoverability_status"]),
            recommended_next_action,
        ]
    )
    return DeterministicControlStory(
        queue_item_id=str(selected_row["queue_item_id"]),
        service_line=str(selected_row["service_line"]),
        department=str(selected_row["department"]),
        control_failure_type=control_failure_type,
        issue_domain=str(selected_row["issue_domain"]),
        root_cause_mechanism=str(selected_row["root_cause_mechanism"]),
        exception_pattern=exception_pattern,
        current_prebill_stage=str(selected_row["current_prebill_stage"]),
        current_primary_blocker_state=str(selected_row["current_primary_blocker_state"]),
        current_queue=str(selected_row["current_queue"]),
        accountable_owner=str(selected_row["accountable_owner"]),
        aging_sla_status=aging_sla_status,
        recoverability_status=str(selected_row["recoverability_status"]),
        why_it_matters=_build_why_it_matters(selected_row, cohort, case_payload),
        recommended_next_action=recommended_next_action,
        story_path=story_path,
    )


def render_control_story_lines(
    story: DeterministicControlStory,
    *,
    memo_tight: bool = False,
) -> tuple[str, ...]:
    if story.queue_item_id == "":
        return (f"- Current control story: {story.exception_pattern}",)

    current_state = (
        f"{story.current_prebill_stage} -> "
        f"{story.current_primary_blocker_state} -> "
        f"{story.current_queue}"
    )
    labels = {
        "service_line_department": "Service line / department",
        "control_failure": "Control failure type",
        "issue_domain": "Issue domain",
        "root_cause": "Root cause mechanism",
        "exception_pattern": "Exception pattern surfaced",
        "current_state": "Where work is stuck now" if memo_tight else "Current state",
        "owner": "Who owns it now" if memo_tight else "Owner now",
        "aging": "Aging / SLA",
        "recoverability": "Recoverability",
        "why_it_matters": "Why it matters",
        "next_action": "Recommended next action",
        "story_path": "Story path",
    }
    return (
        f"- {labels['story_path']}: {story.story_path}",
        (
            f"- {labels['service_line_department']}: "
            f"{story.service_line} | {story.department}"
        ),
        f"- {labels['control_failure']}: {story.control_failure_type}",
        f"- {labels['issue_domain']}: {story.issue_domain}",
        f"- {labels['root_cause']}: {story.root_cause_mechanism}",
        f"- {labels['exception_pattern']}: {story.exception_pattern}",
        f"- {labels['current_state']}: {current_state}",
        f"- {labels['owner']}: {story.accountable_owner}",
        f"- {labels['aging']}: {story.aging_sla_status}",
        f"- {labels['recoverability']}: {story.recoverability_status}",
        f"- {labels['why_it_matters']}: {story.why_it_matters}",
        f"- {labels['next_action']}: {story.recommended_next_action}",
    )
