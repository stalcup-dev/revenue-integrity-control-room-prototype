from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_reference_tables_contract() -> None:
    from ri_control_room.constants import (
        FROZEN_V1_DEPARTMENTS,
        RECOVERABILITY_STATES,
        WORKFLOW_STAGE_LADDER,
    )
    from ri_control_room.reference_loader import (
        REFERENCE_TABLE_SPECS,
        load_reference_tables,
    )

    tables = load_reference_tables(ROOT)

    for table_name, spec in REFERENCE_TABLE_SPECS.items():
        rows = getattr(tables, table_name)
        assert rows, f"{table_name} should not be empty"
        assert set(spec.required_columns).issubset(rows[0].keys())

    departments = {row["department"] for row in tables.department_charge_logic_map}
    assert departments == set(FROZEN_V1_DEPARTMENTS)
    assert len(departments) == 3

    active_queue_definitions = [
        row for row in tables.queue_definitions if row["active_flag"] == "true"
    ]
    assert len(active_queue_definitions) == 5
    assert {
        row["queue_name"] for row in active_queue_definitions
    } == {
        "Charge Reconciliation Monitor",
        "Documentation Support Exceptions",
        "Coding Pending Review",
        "Modifiers / Edits / Prebill Holds",
        "Correction / Rebill Pending",
    }

    recoverability_states = tuple(
        row["recoverability_state"] for row in tables.recoverability_rules
    )
    assert recoverability_states == RECOVERABILITY_STATES

    stage_names = {row["stage_name"] for row in tables.stage_aging_rules}
    assert set(WORKFLOW_STAGE_LADDER).issubset(stage_names)
    assert "denial_feedback_backlog" in stage_names

    assert all(
        row["separately_billable_flag"] in {"true", "false"}
        and row["packaged_or_integral_flag"] in {"true", "false"}
        for row in tables.department_charge_logic_map
    )
