from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_case_detail_payload_explains_documentation_failure() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.case_detail import build_case_detail_payload

    build_operating_artifacts(ROOT)
    payload = build_case_detail_payload("QUEUE-ACC-1026", ROOT)

    assert payload.case_header["encounter_id"] == "OR007"
    assert payload.case_header["current_queue"] == "Documentation Support Exceptions"
    assert payload.case_header["current_stage"] == "Documentation pending"
    assert payload.case_header["accountable_owner"] == "Department operations"
    assert payload.case_header["days_in_stage"] == payload.case_header["stage_age_days"]
    assert payload.case_header["aging_basis_label"] == (
        "Days since documentation deficiency was identified"
    )
    assert payload.classification["recoverability_status"] == "Post-window financially lost"
    assert payload.queue_governance["queue_entry_rule"] == (
        "Charge support is incomplete late or inconsistent"
    )
    assert payload.queue_governance["queue_exit_rule"] == (
        "Required documentation becomes complete or case is suppressed as nonbillable"
    )
    assert payload.queue_governance["escalation_trigger"] == (
        "Documentation support remains incomplete after SLA target"
    )
    assert payload.classification["failure_summary"] == (
        "Documentation support failure: Documentation support incomplete"
    )
    assert payload.classification["suppressed_case_flag"] is False
    assert "Documented performed activity traced from documentation event" in (
        payload.control_narrative
    )
    assert "The one current blocker is 'Documentation support incomplete'" in (
        payload.control_narrative
    )
    assert "Issue domain is Documentation support failure" in payload.control_narrative
    assert "root cause is Documentation behavior" in payload.control_narrative
    assert "Recoverability is Post-window financially lost." in payload.control_narrative

    assert not payload.upstream_evidence.empty
    assert set(payload.upstream_evidence["activity_signal_id"]) == {"SIG-DOC-ORD-OR007-1"}
    assert set(payload.upstream_evidence["documentation_gap_type"]) == {"missing_case_timestamp"}

    assert len(payload.expected_vs_actual) == 1
    detail_row = payload.expected_vs_actual.iloc[0]
    assert detail_row["opportunity_status"] == "unsupported_charge_risk"
    assert (
        detail_row["expected_facility_charge_opportunity"]
        == "Timestamp-dependent procedural facility charge"
    )
    assert detail_row["actual_charge_status"] == "posted_pending_support"
    assert detail_row["actual_gross_charge_amount"] == 1250.0

    assert payload.routing_history["stage_transition_path"] == (
        "Charge capture pending -> Documentation pending"
    )
    assert payload.routing_history["reroute_count"] == 1
    assert payload.routing_history["transition_event_count"] == 2
    assert payload.routing_history["routing_reason"] == (
        "Missing case timestamp kept the account in documentation review past the window."
    )
    assert payload.suppression_note["suppressed_case_flag"] is False
    assert payload.suppression_note["suppressed_opportunity_count"] == 0


def test_case_detail_payload_preserves_suppression_context_for_active_edit_case() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.case_detail import build_case_detail_payload

    build_operating_artifacts(ROOT)
    payload = build_case_detail_payload("QUEUE-ACC-1021", ROOT)

    assert payload.case_header["encounter_id"] == "OR002"
    assert payload.case_header["current_queue"] == "Modifiers / Edits / Prebill Holds"
    assert payload.case_header["current_stage"] == "Prebill edit / hold"
    assert payload.classification["current_primary_blocker_state"] == (
        "Prebill edit or hold unresolved"
    )
    assert payload.classification["accountable_owner"] == "Billing operations"
    assert payload.classification["recoverability_status"] == "Pre-final-bill recoverable"
    assert payload.queue_governance["aging_basis_label"] == (
        "Days since edit or prebill hold opened"
    )
    assert payload.queue_governance["sla_status"] == "At risk"
    assert (
        "Suppression remains visible: discontinued_before_billable_procedure_threshold is treated as suppressed by design"
        in payload.control_narrative
    )

    assert len(payload.expected_vs_actual) == 1
    detail_row = payload.expected_vs_actual.iloc[0]
    assert detail_row["opportunity_status"] == "packaged_or_nonbillable_suppressed"
    assert bool(detail_row["suppression_flag"]) is True
    assert (
        detail_row["why_not_billable_explanation"]
        == "discontinued_before_billable_procedure_threshold"
    )
    assert detail_row["actual_charge_status"] == "posted_held_prebill"
    assert detail_row["actual_modifier_code"] == "MODCHK"

    assert payload.routing_history["reroute_count"] == 2
    assert payload.routing_history["prior_queue"] == "Coding Pending Review"
    assert payload.suppression_note["suppressed_case_flag"] is True
    assert payload.suppression_note["suppressed_opportunity_count"] == 1
    assert payload.suppression_note["suppression_reasons"] == (
        "discontinued_before_billable_procedure_threshold",
    )
    assert "should not be treated as active leakage" in payload.suppression_note["note_text"]


def test_case_detail_payload_includes_intervention_follow_through_for_correction_case() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.case_detail import build_case_detail_payload

    build_operating_artifacts(ROOT)
    payload = build_case_detail_payload("QUEUE-ACC-1029", ROOT)

    assert payload.case_header["encounter_id"] == "OR010"
    assert payload.case_header["current_queue"] == "Correction / Rebill Pending"
    assert payload.classification["recoverability_status"] == (
        "Post-final-bill recoverable by correction / rebill"
    )

    intervention = payload.intervention_follow_through
    assert intervention["intervention_type"] == "Billing / correction action"
    assert intervention["action_path"] == "Billing"
    assert intervention["intervention_owner"] == "Billing operations"
    assert intervention["checkpoint_status"] == "Turnaround improving"
    assert intervention["hold_expand_revise_recommendation"] == "Revise"
    assert "Median handoff turnaround days" in str(intervention["baseline_metric"])
    assert "Median handoff turnaround days" in str(intervention["current_metric"])
    assert "Recommendation remains revise" in str(intervention["before_after_validation_note"])

    downstream = payload.downstream_outcome
    assert downstream["rebill_outcome_status"] == "open_recoverable"
    assert downstream["correction_turnaround_days"] == 2.0
    assert downstream["correction_type"] == "technical_rebill_review"
    assert downstream["rebill_required_flag"] is True
    assert downstream["financial_recovery_pathway"] == (
        "Post-final-bill recoverable by correction / rebill"
    )
    assert "correction turnaround 2.0 days" in str(downstream["downstream_outcome_signal"])


def test_case_detail_payload_rejects_unknown_queue_item_id() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.case_detail import build_case_detail_payload

    build_operating_artifacts(ROOT)

    with pytest.raises(ValueError, match="Unknown queue_item_id"):
        build_case_detail_payload("QUEUE-DOES-NOT-EXIST", ROOT)


@pytest.mark.parametrize(
    ("queue_item_id", "encounter_id", "department", "suppressed_case_flag"),
    [
        (
            "QUEUE-ACC-1003",
            "INF004",
            "Outpatient Infusion / Oncology Infusion",
            False,
        ),
        (
            "QUEUE-ACC-1015",
            "IR001",
            "Radiology / Interventional Radiology",
            False,
        ),
        (
            "QUEUE-ACC-1026",
            "OR007",
            "OR / Hospital Outpatient Surgery / Procedural Areas",
            False,
        ),
        (
            "QUEUE-ACC-1021",
            "OR002",
            "OR / Hospital Outpatient Surgery / Procedural Areas",
            True,
        ),
    ],
)
def test_case_detail_payload_manual_qa_coverage_by_department(
    queue_item_id: str,
    encounter_id: str,
    department: str,
    suppressed_case_flag: bool,
) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.case_detail import build_case_detail_payload

    build_operating_artifacts(ROOT)
    payload = build_case_detail_payload(queue_item_id, ROOT)

    assert payload.case_header["encounter_id"] == encounter_id
    assert payload.case_header["department"] == department
    assert payload.case_header["current_primary_blocker_state"]
    assert payload.case_header["accountable_owner"]
    assert payload.case_header["current_stage"]
    assert payload.case_header["days_in_stage"] == payload.case_header["stage_age_days"]
    assert payload.case_header["aging_basis_label"]
    assert payload.classification["recoverability_status"]
    assert payload.queue_governance["queue_entry_rule"]
    assert payload.queue_governance["queue_exit_rule"]
    assert payload.queue_governance["escalation_trigger"]
    assert payload.control_narrative
    assert "Documented performed activity" in payload.control_narrative
    assert "The one current blocker is" in payload.control_narrative
    assert "Issue domain is" in payload.control_narrative
    assert "root cause is" in payload.control_narrative
    assert "Recoverability is" in payload.control_narrative
    assert not payload.upstream_evidence.empty
    assert not payload.expected_vs_actual.empty
    assert payload.suppression_note["suppressed_case_flag"] is suppressed_case_flag
