from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _generate_queue_outputs() -> Path:
    from ri_control_room.logic.build_exception_queue import write_exception_queue_parquet
    from ri_control_room.logic.build_queue_history import write_queue_history_parquet

    write_exception_queue_parquet(ROOT)
    write_queue_history_parquet(ROOT)
    return ROOT / "data" / "processed"


def test_exception_queue_and_history_contract() -> None:
    from ri_control_room.constants import RECOVERABILITY_STATES
    from ri_control_room.reference_loader import load_reference_csv

    processed_dir = _generate_queue_outputs()
    exception_queue = pd.read_parquet(processed_dir / "exception_queue.parquet")
    queue_history = pd.read_parquet(processed_dir / "queue_history.parquet")
    encounters = pd.read_parquet(processed_dir / "encounters.parquet")
    documentation_events = pd.read_parquet(processed_dir / "documentation_events.parquet")

    assert not exception_queue.empty
    assert not queue_history.empty
    assert set(queue_history["encounter_id"]) == set(exception_queue["encounter_id"])
    assert len(queue_history) > len(exception_queue)

    assert exception_queue["account_id"].is_unique
    blocker_counts = exception_queue.groupby("account_id")["current_primary_blocker_code"].nunique()
    assert (blocker_counts == 1).all()

    assert set(exception_queue["recoverability_status"]).issubset(set(RECOVERABILITY_STATES))
    assert exception_queue["recoverability_active_queue_allowed"].all()

    allowed_pairs = {
        ("Charge capture pending", "Charge capture failure"): "Charge Reconciliation Monitor",
        ("Documentation pending", "Documentation support failure"): "Documentation Support Exceptions",
        ("Coding pending", "Coding failure"): "Coding Pending Review",
        ("Prebill edit / hold", "Billing / claim-edit failure"): "Modifiers / Edits / Prebill Holds",
        ("Correction / rebill pending", "Billing / claim-edit failure"): "Correction / Rebill Pending",
    }
    for _, row in exception_queue.iterrows():
        observed_pair = (row["current_prebill_stage"], row["issue_domain"])
        assert observed_pair in allowed_pairs
        assert row["current_queue"] == allowed_pairs[observed_pair]

    stage_rule_lookup = {
        row["stage_name"]: row for row in load_reference_csv("stage_aging_rules", ROOT)
    }
    queue_definition_lookup = {
        row["queue_name"]: row for row in load_reference_csv("queue_definitions", ROOT)
    }
    for _, row in exception_queue.iterrows():
        stage_rule = stage_rule_lookup[row["current_prebill_stage"]]
        queue_definition = queue_definition_lookup[row["current_queue"]]
        assert row["current_stage"] == row["current_prebill_stage"]
        assert row["days_in_stage"] == row["stage_age_days"]
        assert row["aging_basis_label"] == stage_rule["aging_basis"]
        assert row["clock_start_event"] == stage_rule["clock_start_event"]
        assert row["aging_clock_start_event"] == stage_rule["clock_start_event"]
        assert row["sla_target_days"] == int(stage_rule["sla_target_days"])
        assert row["overdue_threshold_days"] == int(stage_rule["overdue_threshold_days"])
        assert row["queue_entry_rule"] == queue_definition["entry_rule"]
        assert row["queue_exit_rule"] == queue_definition["exit_rule"]
        assert row["queue_aging_clock_start_basis"] == queue_definition["aging_clock_start_basis"]
        assert row["accountable_owner"] == queue_definition["accountable_owner"]
        assert row["supporting_owner"] == queue_definition["supporting_owner"]
        assert row["escalation_owner"] == queue_definition["escalation_owner"]
        assert row["escalation_trigger"] == queue_definition["escalation_trigger"]
        assert queue_definition["active_flag"] == "true"

    encounter_lookup = encounters.set_index("encounter_id").to_dict("index")
    deficient_docs = documentation_events.loc[
        documentation_events["documentation_gap_type"].fillna("") != ""
    ]
    first_deficient_event_ts = deficient_docs.groupby("encounter_id")["event_ts"].min().to_dict()
    latest_completion_ts = documentation_events.groupby("encounter_id")["completion_ts"].max().to_dict()

    for _, row in exception_queue.iterrows():
        encounter = encounter_lookup[row["encounter_id"]]
        if row["current_prebill_stage"] == "Charge capture pending":
            assert row["aging_clock_start_ts"] == encounter["service_end_ts"]
        elif row["current_prebill_stage"] == "Documentation pending":
            assert row["aging_clock_start_ts"] == first_deficient_event_ts[row["encounter_id"]]
        elif row["current_prebill_stage"] == "Coding pending":
            assert row["aging_clock_start_ts"] == latest_completion_ts[row["encounter_id"]] + pd.Timedelta(hours=2)
        elif row["current_prebill_stage"] == "Prebill edit / hold":
            assert row["aging_clock_start_ts"] == latest_completion_ts[row["encounter_id"]] + pd.Timedelta(hours=4)
        elif row["current_prebill_stage"] == "Correction / rebill pending":
            assert row["aging_clock_start_ts"] == encounter["final_bill_datetime"] + pd.Timedelta(days=2)

    explanation_lookup = exception_queue.set_index("encounter_id")["why_not_billable_explanation"].to_dict()
    for encounter_id in {"INF004", "INF006", "RAD003", "IR001", "OR007"}:
        assert explanation_lookup[encounter_id] != ""

    latest_history = (
        queue_history.sort_values(["encounter_id", "transition_event_index"])
        .drop_duplicates("encounter_id", keep="last")
        .copy()
    )
    rerouted = queue_history.loc[queue_history["reroute_count"] > 0]
    assert not rerouted.empty
    assert rerouted["ever_rerouted_flag"].all()
    assert (rerouted["prior_queue"] != "").all()
    assert (rerouted["prior_stage"] != "").all()
    assert (rerouted["prior_queue"] != rerouted["current_queue"]).all()
    assert rerouted["latest_reroute_ts"].notna().all()
    assert queue_history["routing_reason"].str.len().gt(0).all()
    assert queue_history["current_record_flag"].sum() == len(exception_queue)
    assert latest_history["reroute_count"].max() >= 3
    assert latest_history["transition_event_index"].max() >= 4


def test_stage_specific_sla_thresholds_can_diverge_for_similar_stage_age() -> None:
    processed_dir = _generate_queue_outputs()
    exception_queue = pd.read_parquet(processed_dir / "exception_queue.parquet")

    charge_capture_row = exception_queue.loc[
        (exception_queue["current_stage"] == "Charge capture pending")
        & (exception_queue["days_in_stage"] == 6)
    ].iloc[0]
    correction_rebill_row = exception_queue.loc[
        (exception_queue["current_stage"] == "Correction / rebill pending")
        & (exception_queue["days_in_stage"] == 6)
    ].iloc[0]

    assert charge_capture_row["sla_status"] == "Overdue"
    assert charge_capture_row["overdue_threshold_days"] == 4
    assert correction_rebill_row["sla_status"] == "At risk"
    assert correction_rebill_row["overdue_threshold_days"] == 10
