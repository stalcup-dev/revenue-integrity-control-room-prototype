from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.logic.build_queue_history import latest_queue_history_rows


@dataclass(frozen=True)
class CaseDetailPayload:
    case_header: dict[str, object]
    queue_governance: dict[str, object]
    control_narrative: str
    upstream_evidence: pd.DataFrame
    expected_vs_actual: pd.DataFrame
    classification: dict[str, object]
    routing_history: dict[str, object]
    suppression_note: dict[str, object]
    intervention_follow_through: dict[str, object]
    downstream_outcome: dict[str, object]


def _serialize_scalar(value: object) -> object:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item") and not isinstance(value, str):
        try:
            return value.item()
        except (AttributeError, ValueError):
            return value
    return value


def _row_to_dict(row: pd.Series, fields: tuple[str, ...]) -> dict[str, object]:
    return {field: _serialize_scalar(row.get(field)) for field in fields}


def _require_single_row(
    df: pd.DataFrame,
    *,
    column: str,
    value: str,
    description: str,
) -> pd.Series:
    matches = df.loc[df[column] == value]
    if matches.empty:
        raise ValueError(f"Unknown {description}: {value}")
    if len(matches) > 1:
        raise ValueError(f"Expected one {description} for {value}, found {len(matches)}")
    return matches.iloc[0]


def _load_case_detail_inputs(repo_root: Path | None = None) -> dict[str, pd.DataFrame]:
    artifact_names = (
        "priority_scores",
        "encounters",
        "claims_or_account_status",
        "orders",
        "documentation_events",
        "upstream_activity_signals",
        "charge_events",
        "claim_lines",
        "edits_bill_holds",
        "expected_charge_opportunities",
        "queue_history",
        "intervention_tracking",
        "corrections_rebills",
    )
    return {
        artifact_name: load_processed_artifact(artifact_name, repo_root)
        for artifact_name in artifact_names
    }


def _routing_history_row(queue_history: pd.DataFrame, encounter_id: str) -> pd.Series:
    history_subset = queue_history.loc[queue_history["encounter_id"] == encounter_id].copy()
    if history_subset.empty:
        raise ValueError(f"Unknown queue history row: {encounter_id}")
    return latest_queue_history_rows(history_subset).iloc[0]


def _maybe_single_row(
    df: pd.DataFrame,
    *,
    column: str,
    value: str,
) -> pd.Series | None:
    matches = df.loc[df[column] == value]
    if matches.empty:
        return None
    return matches.iloc[0]


def _build_upstream_evidence(
    encounter_id: str,
    *,
    orders: pd.DataFrame,
    documentation_events: pd.DataFrame,
    upstream_activity_signals: pd.DataFrame,
) -> pd.DataFrame:
    order_subset = (
        orders.loc[orders["encounter_id"] == encounter_id]
        .rename(
            columns={
                "order_type": "order_type",
                "order_status": "order_status",
                "ordered_ts": "ordered_ts",
                "scheduled_service_ts": "scheduled_service_ts",
                "procedure_code": "order_procedure_code",
                "procedure_description": "order_procedure_description",
                "order_group": "order_group",
            }
        )
        .copy()
    )
    documentation_subset = (
        documentation_events.loc[documentation_events["encounter_id"] == encounter_id]
        .rename(
            columns={
                "documentation_type": "documentation_type",
                "documentation_status": "documentation_status",
                "event_ts": "documentation_event_ts",
                "completion_ts": "documentation_completion_ts",
                "start_time": "documentation_start_time",
                "stop_time": "documentation_stop_time",
            }
        )
        .copy()
    )
    signal_subset = (
        upstream_activity_signals.loc[upstream_activity_signals["encounter_id"] == encounter_id]
        .rename(
            columns={
                "signal_type": "signal_type",
                "activity_code": "activity_code",
                "activity_description": "activity_description",
                "activity_ts": "activity_ts",
                "support_status": "signal_support_status",
            }
        )
        .copy()
    )

    evidence = (
        signal_subset.merge(
            documentation_subset,
            on=["encounter_id", "order_id", "documentation_event_id", "department", "service_line"],
            how="outer",
        )
        .merge(
            order_subset,
            on=["encounter_id", "order_id", "department", "service_line"],
            how="left",
        )
        .sort_values(
            ["activity_ts", "documentation_event_ts", "order_id"],
            na_position="last",
        )
        .reset_index(drop=True)
    )

    selected_columns = [
        "order_id",
        "order_type",
        "order_status",
        "ordered_ts",
        "scheduled_service_ts",
        "order_procedure_code",
        "order_procedure_description",
        "documentation_event_id",
        "documentation_type",
        "documentation_status",
        "documentation_event_ts",
        "documentation_completion_ts",
        "documentation_gap_type",
        "documentation_start_time",
        "documentation_stop_time",
        "supports_charge_flag",
        "activity_signal_id",
        "signal_type",
        "activity_code",
        "activity_description",
        "activity_ts",
        "performed_flag",
        "signal_support_status",
        "signal_basis",
        "traceable_to_documentation_flag",
        "packaged_or_integral_candidate_flag",
        "non_billable_candidate_flag",
        "non_billable_reason",
        "late_post_risk_flag",
        "timestamp_dependency_flag",
    ]
    return evidence.reindex(columns=selected_columns)


def _build_expected_vs_actual(
    encounter_id: str,
    *,
    expected_charge_opportunities: pd.DataFrame,
    charge_events: pd.DataFrame,
    claim_lines: pd.DataFrame,
) -> pd.DataFrame:
    expected_subset = expected_charge_opportunities.loc[
        expected_charge_opportunities["encounter_id"] == encounter_id
    ].copy()
    charge_subset = (
        charge_events.loc[charge_events["encounter_id"] == encounter_id]
        .rename(
            columns={
                "charge_event_id": "actual_charge_event_id",
                "charge_code": "actual_charge_code",
                "charge_description": "actual_charge_description",
                "charge_event_type": "actual_charge_event_type",
                "charge_status": "actual_charge_status",
                "charge_post_ts": "actual_charge_post_ts",
                "units": "actual_charge_units",
                "gross_charge_amount": "actual_gross_charge_amount",
                "support_status": "actual_support_status",
            }
        )
        .copy()
    )
    claim_line_subset = (
        claim_lines.loc[claim_lines["encounter_id"] == encounter_id]
        .rename(
            columns={
                "claim_line_id": "actual_claim_line_id",
                "charge_event_id": "actual_charge_event_id",
                "line_status": "actual_claim_line_status",
                "line_code": "actual_claim_line_code",
                "modifier_code": "actual_modifier_code",
                "billed_units": "actual_billed_units",
                "billed_amount": "actual_billed_amount",
                "final_billed_flag": "actual_final_billed_flag",
                "bill_drop_datetime": "actual_bill_drop_datetime",
            }
        )
        .copy()
    )

    merged = (
        expected_subset.merge(
            charge_subset[
                [
                    "encounter_id",
                    "activity_signal_id",
                    "actual_charge_event_id",
                    "actual_charge_code",
                    "actual_charge_description",
                    "actual_charge_event_type",
                    "actual_charge_status",
                    "actual_charge_post_ts",
                    "actual_charge_units",
                    "actual_gross_charge_amount",
                    "actual_support_status",
                ]
            ],
            on=["encounter_id", "activity_signal_id"],
            how="left",
        )
        .merge(
            claim_line_subset[
                [
                    "encounter_id",
                    "actual_charge_event_id",
                    "actual_claim_line_id",
                    "actual_claim_line_status",
                    "actual_claim_line_code",
                    "actual_modifier_code",
                    "actual_billed_units",
                    "actual_billed_amount",
                    "actual_final_billed_flag",
                    "actual_bill_drop_datetime",
                ]
            ],
            on=["encounter_id", "actual_charge_event_id"],
            how="left",
        )
        .sort_values(["expected_opportunity_id", "actual_charge_post_ts"], na_position="last")
        .reset_index(drop=True)
    )

    selected_columns = [
        "expected_opportunity_id",
        "activity_signal_id",
        "documentation_event_id",
        "signal_basis",
        "clinical_event",
        "expected_facility_charge_opportunity",
        "expected_code_hint",
        "expected_modifier_hint",
        "expected_units",
        "evidence_completeness_status",
        "documented_performed_activity_flag",
        "separately_billable_flag",
        "packaged_or_integral_flag",
        "charge_event_exists_flag",
        "actual_charge_event_id",
        "actual_charge_code",
        "actual_charge_description",
        "actual_charge_event_type",
        "actual_charge_status",
        "actual_charge_post_ts",
        "actual_charge_units",
        "actual_gross_charge_amount",
        "actual_support_status",
        "actual_claim_line_id",
        "actual_claim_line_status",
        "actual_claim_line_code",
        "actual_modifier_code",
        "actual_billed_units",
        "actual_billed_amount",
        "actual_final_billed_flag",
        "actual_bill_drop_datetime",
        "opportunity_status",
        "suppression_flag",
        "why_not_billable_explanation",
    ]
    return merged.reindex(columns=selected_columns)


def _build_suppression_note(expected_vs_actual: pd.DataFrame) -> dict[str, object]:
    suppressed = expected_vs_actual.loc[expected_vs_actual["suppression_flag"].fillna(False)].copy()
    suppression_reasons = tuple(
        sorted(
            {
                str(reason).strip()
                for reason in suppressed["why_not_billable_explanation"].fillna("")
                if str(reason).strip()
            }
        )
    )
    suppressed_case_flag = bool(len(suppressed) > 0)
    note_text = ""
    if suppressed_case_flag:
        note_text = (
            f"{len(suppressed)} expected opportunity row(s) are suppressed and should not be "
            f"treated as active leakage: {', '.join(suppression_reasons)}."
        )
    return {
        "suppressed_case_flag": suppressed_case_flag,
        "suppressed_opportunity_count": int(len(suppressed)),
        "suppression_reasons": suppression_reasons,
        "note_text": note_text,
    }


def _build_control_narrative(
    queue_row: pd.Series,
    expected_vs_actual: pd.DataFrame,
    suppression_note: dict[str, object],
) -> str:
    if expected_vs_actual.empty:
        evidence_clause = "No expected opportunity rows were found for the selected queue item."
        actual_clause = "Actual charge state is unavailable."
    else:
        detail_row = expected_vs_actual.iloc[0]
        signal_basis = str(detail_row.get("signal_basis") or "documented_performed_activity").replace(
            "_",
            " ",
        )
        expected_opportunity = str(detail_row.get("expected_facility_charge_opportunity") or "").strip()
        clinical_event = str(detail_row.get("clinical_event") or "").strip()
        actual_charge_status = str(detail_row.get("actual_charge_status") or "").strip()
        if actual_charge_status == "" or actual_charge_status.lower() == "none":
            actual_charge_status = "no posted charge"
        evidence_clause = (
            f"Documented performed activity traced from {signal_basis} for {clinical_event} "
            f"drives the expected opportunity '{expected_opportunity}'."
        )
        actual_clause = f"Actual charge state is {actual_charge_status}."

    blocker_clause = (
        f"The one current blocker is '{queue_row['current_primary_blocker_state']}' in "
        f"{queue_row['current_queue']} owned by {queue_row['accountable_owner']}."
    )
    classification_clause = (
        f"Issue domain is {queue_row['issue_domain']} and root cause is "
        f"{queue_row['root_cause_mechanism']}."
    )
    recoverability_clause = (
        f"Recoverability is {queue_row['recoverability_status']}."
    )

    suppression_clause = "No expected opportunity on this case is currently suppressed."
    if suppression_note["suppressed_case_flag"]:
        reasons = ", ".join(suppression_note["suppression_reasons"])
        suppression_clause = (
            f"Suppression remains visible: {reasons} is treated as suppressed by design, "
            "not active leakage."
        )

    return " ".join(
        [
            evidence_clause,
            actual_clause,
            blocker_clause,
            classification_clause,
            recoverability_clause,
            suppression_clause,
        ]
    )


def _build_intervention_follow_through(
    queue_item_id: str,
    encounter_id: str,
    *,
    intervention_tracking: pd.DataFrame,
    corrections_rebills: pd.DataFrame,
) -> tuple[dict[str, object], dict[str, object]]:
    intervention_row = _maybe_single_row(
        intervention_tracking,
        column="queue_item_id",
        value=queue_item_id,
    )
    if intervention_row is None:
        return {}, {}

    correction_matches = corrections_rebills.loc[
        corrections_rebills["encounter_id"] == encounter_id
    ].copy()
    correction_row: pd.Series | None = None
    if not correction_matches.empty:
        correction_row = (
            correction_matches.sort_values(
                ["last_activity_datetime", "correction_open_datetime"],
                ascending=[False, False],
            )
            .iloc[0]
        )

    intervention_follow_through = _row_to_dict(
        intervention_row,
        (
            "intervention_type",
            "action_path",
            "intervention_owner",
            "target_completion_date",
            "checkpoint_status",
            "baseline_metric",
            "current_metric",
            "before_after_validation_note",
            "hold_expand_revise_recommendation",
            "recommendation_rationale",
            "recurring_issue_pattern",
            "downstream_outcome_type",
            "downstream_outcome_signal",
        ),
    )

    downstream_outcome = _row_to_dict(
        intervention_row,
        (
            "downstream_outcome_type",
            "downstream_outcome_signal",
            "correction_turnaround_signal",
            "observed_rebill_outcome_status",
            "correction_type",
            "correction_id",
            "observed_rebill_required_flag",
            "observed_financial_recovery_pathway",
            "observed_rebill_last_activity_datetime",
        ),
    )
    if correction_row is not None:
        downstream_outcome.update(
            {
                "correction_id": _serialize_scalar(correction_row.get("correction_id")),
                "correction_type": _serialize_scalar(correction_row.get("correction_type")),
                "correction_turnaround_days": _serialize_scalar(correction_row.get("turnaround_days")),
                "rebill_outcome_status": _serialize_scalar(correction_row.get("outcome_status")),
                "rebill_required_flag": _serialize_scalar(correction_row.get("rebill_required_flag")),
                "financial_recovery_pathway": _serialize_scalar(
                    correction_row.get("financial_recovery_pathway")
                ),
                "last_activity_datetime": _serialize_scalar(
                    correction_row.get("last_activity_datetime")
                ),
            }
        )

    return intervention_follow_through, downstream_outcome


def build_case_detail_payload(
    queue_item_id: str,
    repo_root: Path | None = None,
) -> CaseDetailPayload:
    artifacts = _load_case_detail_inputs(repo_root)
    queue_row = _require_single_row(
        artifacts["priority_scores"],
        column="queue_item_id",
        value=queue_item_id,
        description="queue_item_id",
    )
    encounter_id = str(queue_row["encounter_id"])
    account_status_id = str(queue_row["account_status_id"])

    encounter_row = _require_single_row(
        artifacts["encounters"],
        column="encounter_id",
        value=encounter_id,
        description="encounter header",
    )
    status_row = _require_single_row(
        artifacts["claims_or_account_status"],
        column="account_status_id",
        value=account_status_id,
        description="account_status_id",
    )
    routing_history_row = _routing_history_row(artifacts["queue_history"], encounter_id)
    history_subset = artifacts["queue_history"].loc[
        artifacts["queue_history"]["encounter_id"] == encounter_id
    ].copy()

    upstream_evidence = _build_upstream_evidence(
        encounter_id,
        orders=artifacts["orders"],
        documentation_events=artifacts["documentation_events"],
        upstream_activity_signals=artifacts["upstream_activity_signals"],
    )
    expected_vs_actual = _build_expected_vs_actual(
        encounter_id,
        expected_charge_opportunities=artifacts["expected_charge_opportunities"],
        charge_events=artifacts["charge_events"],
        claim_lines=artifacts["claim_lines"],
    )
    suppression_note = _build_suppression_note(expected_vs_actual)
    control_narrative = _build_control_narrative(
        queue_row,
        expected_vs_actual,
        suppression_note,
    )
    intervention_follow_through, downstream_outcome = _build_intervention_follow_through(
        queue_item_id,
        encounter_id,
        intervention_tracking=artifacts["intervention_tracking"],
        corrections_rebills=artifacts["corrections_rebills"],
    )

    case_header = {
        **_row_to_dict(
            queue_row,
            (
                "queue_item_id",
                "account_status_id",
                "claim_id",
                "account_id",
                "encounter_id",
                "department",
                "service_line",
                "payer_group",
                "current_stage",
                "current_prebill_stage",
                "current_queue",
                "accountable_owner",
                "supporting_owner",
                "escalation_owner",
                "escalation_trigger",
                "current_primary_blocker_state",
                "current_primary_blocker_code",
                "aging_basis_label",
                "sla_status",
                "days_in_stage",
                "stage_age_days",
                "aging_bucket",
                "estimated_gross_dollars",
                "priority_score",
                "priority_rank",
            ),
        ),
        **_row_to_dict(
            encounter_row,
            (
                "scenario_code",
                "patient_type",
                "encounter_status",
                "service_start_ts",
                "service_end_ts",
                "final_bill_datetime",
            ),
        ),
    }

    queue_governance = _row_to_dict(
        queue_row,
        (
            "current_queue",
            "current_stage",
            "accountable_owner",
            "supporting_owner",
            "escalation_owner",
            "queue_business_purpose",
            "queue_entry_rule",
            "queue_exit_rule",
            "queue_aging_clock_start_basis",
            "aging_basis_label",
            "clock_start_event",
            "sla_target_days",
            "overdue_threshold_days",
            "days_in_stage",
            "sla_status",
            "escalation_trigger",
        ),
    )

    classification = {
        **_row_to_dict(
            queue_row,
            (
                "issue_domain",
                "root_cause_mechanism",
                "current_primary_blocker_state",
                "current_primary_blocker_code",
                "current_queue",
                "accountable_owner",
                "supporting_owner",
                "recoverability_status",
                "recoverability_window_rule",
                "recoverability_financial_meaning",
                "recoverability_active_queue_allowed",
                "why_not_billable_explanation",
                "active_issue_tag_count",
            ),
        ),
        **_row_to_dict(
            status_row,
            (
                "reconciliation_status",
                "evidence_completeness_status",
                "policy_window_start_ts",
                "policy_window_end_ts",
                "final_bill_datetime",
            ),
        ),
        "failure_summary": (
            f"{queue_row['issue_domain']}: {queue_row['current_primary_blocker_state']}"
        ),
        "suppressed_case_flag": suppression_note["suppressed_case_flag"],
    }

    routing_history = _row_to_dict(
        routing_history_row,
        (
            "transition_event_index",
            "transition_event_type",
            "current_prebill_stage",
            "prior_stage",
            "current_queue",
            "prior_queue",
            "reroute_count",
            "ever_rerouted_flag",
            "first_queue_entry_ts",
            "current_queue_entry_ts",
            "latest_reroute_ts",
            "stage_transition_path",
            "queue_transition_path",
            "routing_reason",
            "recoverability_status",
        ),
    )
    routing_history["transition_event_count"] = int(len(history_subset))

    return CaseDetailPayload(
        case_header=case_header,
        queue_governance=queue_governance,
        control_narrative=control_narrative,
        upstream_evidence=upstream_evidence,
        expected_vs_actual=expected_vs_actual,
        classification=classification,
        routing_history=routing_history,
        suppression_note=suppression_note,
        intervention_follow_through=intervention_follow_through,
        downstream_outcome=downstream_outcome,
    )
