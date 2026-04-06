from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _generate_downstream_tables() -> Path:
    from ri_control_room.synthetic.generate_charge_events import write_charge_events_parquet
    from ri_control_room.synthetic.generate_claim_lines import write_claim_lines_parquet
    from ri_control_room.synthetic.generate_claims_account_status import (
        write_claims_account_status_parquet,
    )
    from ri_control_room.synthetic.generate_edits_bill_holds import (
        write_edits_bill_holds_parquet,
    )

    write_claims_account_status_parquet(ROOT)
    write_charge_events_parquet(ROOT)
    write_claim_lines_parquet(ROOT)
    write_edits_bill_holds_parquet(ROOT)
    return ROOT / "data" / "processed"


def test_workflow_header_and_downstream_tables_contract() -> None:
    from ri_control_room.reference_loader import load_reference_csv

    processed_dir = _generate_downstream_tables()
    encounters = pd.read_parquet(processed_dir / "encounters.parquet")
    status = pd.read_parquet(processed_dir / "claims_or_account_status.parquet")
    charge_events = pd.read_parquet(processed_dir / "charge_events.parquet")
    claim_lines = pd.read_parquet(processed_dir / "claim_lines.parquet")
    edits = pd.read_parquet(processed_dir / "edits_bill_holds.parquet")

    assert encounters["encounter_id"].nunique() == len(encounters)
    assert status["claim_id"].is_unique
    assert status["account_id"].is_unique
    assert len(status) == len(encounters)
    assert set(status["encounter_id"]) == set(encounters["encounter_id"])

    active_exceptions = status[status["current_queue_active_flag"]]
    assert active_exceptions["current_primary_blocker_state"].notna().all()
    assert (active_exceptions["current_primary_blocker_state"] != "").all()
    assert active_exceptions["current_primary_blocker_code"].notna().all()

    queue_definitions = load_reference_csv("queue_definitions", ROOT)
    valid_queues = {row["queue_name"] for row in queue_definitions}
    assert set(active_exceptions["current_queue"]).issubset(valid_queues)

    allowed_stage_queue_pairs = {
        ("Charge capture pending", "Charge Reconciliation Monitor"),
        ("Documentation pending", "Documentation Support Exceptions"),
        ("Coding pending", "Coding Pending Review"),
        ("Prebill edit / hold", "Modifiers / Edits / Prebill Holds"),
        ("Correction / rebill pending", "Correction / Rebill Pending"),
    }
    observed_pairs = {
        (row["current_prebill_stage"], row["current_queue"])
        for _, row in active_exceptions.iterrows()
    }
    assert observed_pairs.issubset(allowed_stage_queue_pairs)

    assert edits["encounter_id"].isin(
        status.loc[status["current_prebill_stage"] == "Prebill edit / hold", "encounter_id"]
    ).all()
    assert (
        status.loc[status["current_prebill_stage"] == "Prebill edit / hold", "current_queue"]
        == "Modifiers / Edits / Prebill Holds"
    ).all()

    assert set(charge_events["encounter_id"]).issubset(set(status["encounter_id"]))
    assert set(claim_lines["encounter_id"]).issubset(set(status["encounter_id"]))
