from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_scorecard_inputs() -> dict[str, pd.DataFrame]:
    from ri_control_room.artifacts import load_processed_artifact
    from ri_control_room.build_pipeline import build_operating_artifacts

    build_operating_artifacts(ROOT)
    table_names = (
        "encounters",
        "claims_or_account_status",
        "documentation_events",
        "exception_queue",
        "queue_history",
        "expected_charge_opportunities",
        "priority_scores",
        "kpi_snapshot",
        "corrections_rebills",
        "intervention_tracking",
        "upstream_activity_signals",
        "denials_feedback",
    )
    return {name: load_processed_artifact(name, ROOT).copy() for name in table_names}


def _build_report(tables: dict[str, pd.DataFrame]) -> dict[str, object]:
    from ri_control_room.validation.realism_scorecard import build_realism_scorecard_from_tables

    return build_realism_scorecard_from_tables(
        statuses=tables["claims_or_account_status"],
        queue=tables["exception_queue"],
        queue_history=tables["queue_history"],
        expected=tables["expected_charge_opportunities"],
        priority_scores=tables["priority_scores"],
        kpis=tables["kpi_snapshot"],
        corrections=tables["corrections_rebills"],
        intervention_tracking=tables["intervention_tracking"],
        encounters=tables["encounters"],
        documentation_events=tables["documentation_events"],
        upstream_signals=tables["upstream_activity_signals"],
        denials_feedback=tables["denials_feedback"],
    )


def test_realism_scorecard_passes_for_tuned_artifacts() -> None:
    from ri_control_room.validation.realism_scorecard import build_realism_scorecard

    report = build_realism_scorecard(ROOT)

    assert report["overall_status"] == "pass"
    assert report["summary_counts"]["fail"] == 0
    assert set(report["dimensions"]) == {
        "recoverability_mix",
        "workflow_state_realism",
        "queue_history_realism",
        "transition_ledger_realism",
        "handoff_churn_realism",
        "intervention_followthrough_realism",
        "transition_intervention_antipatterns",
        "financial_consequence_realism",
        "exception_class_balance",
        "distribution_realism",
        "correction_history_realism",
        "infusion_story_realism",
        "radiology_story_realism",
        "or_procedural_story_realism",
        "department_story_antipatterns",
        "undercapture_balance_realism",
        "unsupported_balance_realism",
        "suppression_balance_realism",
        "suppression_balance_antipatterns",
        "medium_volume_ops_realism",
        "payable_state_signal_realism",
        "ops_mix_payable_antipatterns",
    }
    assert report["dimensions"]["infusion_story_realism"]["status"] == "pass"
    assert report["dimensions"]["radiology_story_realism"]["status"] == "pass"
    assert report["dimensions"]["or_procedural_story_realism"]["status"] == "pass"
    assert report["dimensions"]["department_story_antipatterns"]["status"] == "pass"
    assert report["dimensions"]["undercapture_balance_realism"]["status"] == "pass"
    assert report["dimensions"]["unsupported_balance_realism"]["status"] == "pass"
    assert report["dimensions"]["suppression_balance_realism"]["status"] == "pass"
    assert report["dimensions"]["suppression_balance_antipatterns"]["status"] == "pass"
    assert report["dimensions"]["medium_volume_ops_realism"]["status"] == "pass"
    assert report["dimensions"]["payable_state_signal_realism"]["status"] == "pass"
    assert report["dimensions"]["ops_mix_payable_antipatterns"]["status"] == "pass"


def test_realism_scorecard_flags_missing_queue_history_and_correction_support() -> None:
    tables = _load_scorecard_inputs()
    tables["queue_history"]["routing_reason"] = ""
    tables["corrections_rebills"] = tables["corrections_rebills"].iloc[0:0].copy()

    report = _build_report(tables)

    assert report["dimensions"]["queue_history_realism"]["status"] == "fail"
    assert "Routing reasons are absent." in report["dimensions"]["queue_history_realism"][
        "anti_pattern_flags"
    ]
    assert report["dimensions"]["correction_history_realism"]["status"] == "fail"


def test_realism_scorecard_flags_summary_only_queue_history_and_flat_interventions() -> None:
    tables = _load_scorecard_inputs()
    latest_rows = (
        tables["queue_history"]
        .sort_values(["encounter_id", "transition_event_index"])
        .drop_duplicates("encounter_id", keep="last")
        .copy()
    )
    latest_rows["queue_history_id"] = [
        f"QH-SUMMARY-{index + 1}" for index in range(len(latest_rows))
    ]
    latest_rows["transition_event_index"] = 1
    latest_rows["current_record_flag"] = True
    latest_rows["reroute_count"] = 0
    latest_rows["prior_queue"] = ""
    latest_rows["prior_stage"] = ""
    latest_rows["stage_transition_path"] = latest_rows["current_prebill_stage"]
    latest_rows["queue_transition_path"] = latest_rows["current_queue"]
    latest_rows["days_in_prior_queue"] = 0
    tables["queue_history"] = latest_rows
    tables["intervention_tracking"]["checkpoint_status"] = "Pilot checkpoint complete"
    tables["intervention_tracking"]["hold_expand_revise_recommendation"] = "Expand"
    tables["intervention_tracking"]["recurring_issue_pattern"] = ""

    report = _build_report(tables)

    assert report["dimensions"]["transition_ledger_realism"]["status"] == "fail"
    assert report["dimensions"]["intervention_followthrough_realism"]["status"] == "fail"
    assert report["dimensions"]["transition_intervention_antipatterns"]["status"] == "fail"


def test_realism_scorecard_flags_collapsed_recoverability_mix() -> None:
    tables = _load_scorecard_inputs()
    active_mask = tables["claims_or_account_status"]["current_queue_active_flag"]
    tables["claims_or_account_status"].loc[active_mask, "recoverability_status"] = (
        "Pre-final-bill recoverable"
    )
    tables["claims_or_account_status"].loc[
        tables["claims_or_account_status"]["recoverability_status"]
        == "Financially closed but still compliance-relevant",
        "recoverability_status",
    ] = "Post-window financially lost"

    report = _build_report(tables)

    assert report["dimensions"]["recoverability_mix"]["status"] == "fail"
    assert any(
        "Missing recoverability states" in flag
        or "No active post-window financially lost items" in flag
        for flag in report["dimensions"]["recoverability_mix"]["anti_pattern_flags"]
    )


def test_realism_scorecard_flags_department_story_antipatterns() -> None:
    tables = _load_scorecard_inputs()
    tables["expected_charge_opportunities"]["documented_performed_activity_flag"] = False

    report = _build_report(tables)

    assert report["dimensions"]["department_story_antipatterns"]["status"] == "fail"
    assert (
        "Expected opportunities are no longer grounded only in documented performed activity."
        in report["dimensions"]["department_story_antipatterns"]["anti_pattern_flags"]
    )


def test_realism_scorecard_flags_suppression_balance_antipatterns() -> None:
    tables = _load_scorecard_inputs()
    suppressed_mask = (
        tables["expected_charge_opportunities"]["opportunity_status"]
        == "packaged_or_nonbillable_suppressed"
    )
    tables["expected_charge_opportunities"].loc[
        suppressed_mask, "why_not_billable_explanation"
    ] = "packaged_or_integral"

    report = _build_report(tables)

    assert report["dimensions"]["suppression_balance_antipatterns"]["status"] == "fail"
    assert (
        "Suppression is too rare or too generic."
        in report["dimensions"]["suppression_balance_antipatterns"]["anti_pattern_flags"]
    )


def test_realism_scorecard_flags_payable_signal_antipatterns() -> None:
    tables = _load_scorecard_inputs()
    tables["denials_feedback"]["linked_upstream_issue_domain"] = ""

    report = _build_report(tables)

    assert report["dimensions"]["payable_state_signal_realism"]["status"] == "fail"
    assert report["dimensions"]["ops_mix_payable_antipatterns"]["status"] == "fail"
    assert (
        "Some payable-state signals are disconnected from upstream issue domains."
        in report["dimensions"]["ops_mix_payable_antipatterns"]["anti_pattern_flags"]
    )
