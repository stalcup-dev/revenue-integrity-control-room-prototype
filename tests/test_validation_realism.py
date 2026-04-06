from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_validation_tables() -> dict[str, pd.DataFrame]:
    from ri_control_room.artifacts import load_existing_validation_tables
    from ri_control_room.build_pipeline import build_operating_artifacts

    build_operating_artifacts(ROOT)
    return {
        name: frame.copy()
        for name, frame in load_existing_validation_tables(ROOT).items()
    }


def _business_results_for(
    mutate_fn,
) -> pd.DataFrame:
    from ri_control_room.validation.business_rule_checks import (
        run_business_rule_checks_for_tables,
    )

    tables = _load_validation_tables()
    mutate_fn(tables)
    return run_business_rule_checks_for_tables(tables)


def _check_failed(results: pd.DataFrame, check_name: str) -> bool:
    return not bool(
        results.loc[results["check_name"] == check_name, "passed"].iloc[0]
    )


def test_missing_timestamp_case_fails_when_promoted_to_clean_expectation() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        expected = tables["expected_charge_opportunities"]
        target = expected["encounter_id"] == "OR007"
        expected.loc[target, "evidence_completeness_status"] = "complete"
        expected.loc[target, "opportunity_status"] = "recoverable_missed_charge"
        expected.loc[target, "separately_billable_flag"] = True

    results = _business_results_for(mutate)
    assert _check_failed(results, "timestamp_dependency_blocked")


def test_partial_documentation_case_fails_when_treated_as_recoverable() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        expected = tables["expected_charge_opportunities"]
        target = expected["encounter_id"] == "OR002"
        expected.loc[target, "evidence_completeness_status"] = "complete"
        expected.loc[target, "opportunity_status"] = "recoverable_missed_charge"

    results = _business_results_for(mutate)
    assert _check_failed(results, "partial_documentation_not_promoted")


def test_contradictory_charge_support_case_fails_when_marked_clean() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        expected = tables["expected_charge_opportunities"]
        target = expected["encounter_id"] == "INF004"
        expected.loc[target, "opportunity_status"] = "expected_charge_supported"

    results = _business_results_for(mutate)
    assert _check_failed(results, "contradictory_charge_support_flagged")


def test_duplicate_transition_path_is_rejected() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        queue_history = tables["queue_history"]
        target_index = queue_history.index[queue_history["reroute_count"] > 0][0]
        queue_history.loc[target_index, "stage_transition_path"] = (
            "Coding pending -> Coding pending -> Prebill edit / hold"
        )

    results = _business_results_for(mutate)
    assert _check_failed(results, "duplicate_transition_paths_blocked")


def test_correction_rebill_requires_postbill_context() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        statuses = tables["claims_or_account_status"]
        target = statuses["encounter_id"] == "OR010"
        statuses.loc[target, "final_bill_datetime"] = pd.NaT
        statuses.loc[target, "rebill_flag"] = False
        statuses.loc[target, "corrected_claim_flag"] = False

    results = _business_results_for(mutate)
    assert _check_failed(results, "correction_rebill_requires_postbill_context")


def test_suppressed_billable_lookalike_requires_explanation() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        expected = tables["expected_charge_opportunities"]
        target_index = expected.index[
            (expected["opportunity_status"] == "packaged_or_nonbillable_suppressed")
            & expected["charge_event_exists_flag"]
        ][0]
        expected.loc[target_index, "why_not_billable_explanation"] = ""

    results = _business_results_for(mutate)
    assert _check_failed(results, "suppressed_billable_lookalikes_explained")


def test_unsupported_charge_risk_requires_posted_charge_context() -> None:
    def mutate(tables: dict[str, pd.DataFrame]) -> None:
        expected = tables["expected_charge_opportunities"]
        target_index = expected.index[
            expected["opportunity_status"] == "unsupported_charge_risk"
        ][0]
        expected.loc[target_index, "charge_event_exists_flag"] = False
        expected.loc[target_index, "charge_status_example"] = ""

    results = _business_results_for(mutate)
    assert _check_failed(results, "unsupported_charge_risk_distinct_from_undercapture")


def test_moderate_volume_scenario_pack_keeps_views_stable(monkeypatch) -> None:
    from ri_control_room.synthetic.scenario_packs import build_moderate_volume_scenario_pack
    from ri_control_room.ui import control_room_summary, documentation_exceptions, opportunity_action_tracker, reconciliation_monitor

    pack = build_moderate_volume_scenario_pack(ROOT)
    priority_scores = pack["priority_scores"]
    statuses = pack["claims_or_account_status"]
    expected = pack["expected_charge_opportunities"]
    documentation = pack["documentation_events"]

    assert len(priority_scores) >= 40

    monkeypatch.setattr(
        control_room_summary,
        "_load_population",
        lambda repo_root=None: priority_scores.copy(),
    )
    monkeypatch.setattr(
        control_room_summary,
        "_load_scope_tables",
        lambda repo_root=None: (statuses.copy(), expected.copy()),
    )
    summary_view = control_room_summary.build_control_room_summary_view(ROOT)
    assert summary_view.open_exception_count == len(priority_scores)
    assert int(summary_view.backlog_trend.iloc[-1]["open_exceptions"]) == len(priority_scores)

    monkeypatch.setattr(
        reconciliation_monitor,
        "_base_population",
        lambda repo_root=None: priority_scores.loc[
            priority_scores["current_queue"] == reconciliation_monitor.QUEUE_NAME
        ].copy(),
    )
    monkeypatch.setattr(
        reconciliation_monitor,
        "_load_completion_inputs",
        lambda repo_root=None: (statuses.copy(), expected.copy()),
    )
    recon_view = reconciliation_monitor.build_reconciliation_monitor_view(ROOT)
    assert recon_view.unreconciled_encounters_count == int(
        (priority_scores["current_queue"] == reconciliation_monitor.QUEUE_NAME).sum()
    )

    monkeypatch.setattr(
        documentation_exceptions,
        "_base_population",
        lambda repo_root=None: priority_scores.loc[
            priority_scores["current_queue"] == documentation_exceptions.QUEUE_NAME
        ].copy(),
    )
    monkeypatch.setattr(
        documentation_exceptions,
        "_load_inputs",
        lambda repo_root=None: (documentation.copy(), expected.copy()),
    )
    documentation_view = documentation_exceptions.build_documentation_exceptions_view(ROOT)
    assert documentation_view.unsupported_exception_count == int(
        (priority_scores["current_queue"] == documentation_exceptions.QUEUE_NAME).sum()
    )
    assert not documentation_view.missing_time_docs.empty

    monkeypatch.setattr(
        opportunity_action_tracker,
        "_base_population",
        lambda repo_root=None: priority_scores.copy(),
    )
    tracker_view = opportunity_action_tracker.build_opportunity_action_tracker_view(ROOT)
    assert tracker_view.open_actions_count == len(priority_scores)
    assert not tracker_view.recurring_issue_patterns.empty
    assert not tracker_view.intervention_owner_summary.empty
