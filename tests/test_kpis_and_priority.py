from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _generate_kpi_snapshot() -> Path:
    from ri_control_room.metrics.kpis import write_kpi_snapshot_parquet

    write_kpi_snapshot_parquet(ROOT)
    return ROOT / "data" / "processed"


def test_kpis_and_priority_contract() -> None:
    from ri_control_room.constants import FROZEN_V1_DEPARTMENTS
    from ri_control_room.metrics.priority_score import (
        PRIORITY_SCORE_VERSION,
        REDUCED_V1_PRIORITY_FORMULA,
        compute_reduced_v1_priority_score,
    )

    processed_dir = _generate_kpi_snapshot()
    snapshot = pd.read_parquet(processed_dir / "kpi_snapshot.parquet")
    charge_events = pd.read_parquet(processed_dir / "charge_events.parquet")
    expected = pd.read_parquet(processed_dir / "expected_charge_opportunities.parquet")

    kpis = snapshot.loc[snapshot["record_type"] == "kpi"].copy()
    priority = snapshot.loc[snapshot["record_type"] == "priority_score"].copy()

    expected_kpis = {
        "Unreconciled encounter rate",
        "Late charge rate",
        "Charge reconciliation completion within policy window",
        "Time to charge entry",
        "Prebill edit aging",
        "Recoverable dollars still open",
        "Dollars already lost after timing window",
        "Department repeat exception rate",
        "Unsupported charge rate",
        "Edit first-pass clearance rate",
    }
    assert set(kpis["kpi_name"].unique()) == expected_kpis
    assert set(kpis["setting_name"]).issubset(
        {"All frozen V1 departments", *FROZEN_V1_DEPARTMENTS}
    )

    required_definition_columns = {
        "numerator_definition",
        "denominator_definition",
        "exclusions_text",
        "grain",
        "owner",
        "caveats_text",
    }
    assert required_definition_columns.issubset(kpis.columns)
    assert kpis["numerator_definition"].ne("").all()
    assert kpis["denominator_definition"].ne("").all()
    assert kpis["exclusions_text"].ne("").all()
    assert kpis["grain"].ne("").all()
    assert kpis["owner"].ne("").all()
    assert kpis["caveats_text"].ne("").all()

    overall_late = kpis.loc[
        (kpis["setting_name"] == "All frozen V1 departments")
        & (kpis["kpi_name"] == "Late charge rate")
    ].iloc[0]
    overall_unsupported = kpis.loc[
        (kpis["setting_name"] == "All frozen V1 departments")
        & (kpis["kpi_name"] == "Unsupported charge rate")
    ].iloc[0]

    eligible_charge_lines = charge_events.loc[
        charge_events["charge_status"] != "suppressed_nonbillable"
    ]
    assert overall_late["denominator_value"] == float(len(eligible_charge_lines))
    assert overall_unsupported["denominator_value"] == float(len(eligible_charge_lines))
    assert overall_unsupported["numerator_value"] == float(
        (eligible_charge_lines["charge_status"] == "posted_pending_support").sum()
    )

    overall_unreconciled = kpis.loc[
        (kpis["setting_name"] == "All frozen V1 departments")
        & (kpis["kpi_name"] == "Unreconciled encounter rate")
    ].iloc[0]
    chargeable_encounters = (
        expected.groupby("encounter_id")["suppression_flag"].apply(lambda values: (~values).any())
    )
    assert overall_unreconciled["denominator_value"] <= float(chargeable_encounters.sum())

    assert not priority.empty
    assert (priority["priority_score_version"] == PRIORITY_SCORE_VERSION).all()
    assert (priority["priority_formula"] == REDUCED_V1_PRIORITY_FORMULA).all()
    assert priority["priority_score"].between(0, 100).all()
    assert priority["normalized_recoverable_dollars"].between(0, 1).all()
    assert priority["department_repeat_exception_rate"].between(0, 1).all()
    assert priority["aging_severity"].between(0, 1).all()

    base_score = compute_reduced_v1_priority_score(0.2, 0.1, 0.3)
    higher_dollars_score = compute_reduced_v1_priority_score(0.6, 0.1, 0.3)
    higher_repeat_score = compute_reduced_v1_priority_score(0.2, 0.5, 0.3)
    higher_aging_score = compute_reduced_v1_priority_score(0.2, 0.1, 0.8)
    assert higher_dollars_score > base_score
    assert higher_repeat_score > base_score
    assert higher_aging_score > base_score

    null_first_pass = kpis.loc[
        kpis["kpi_name"] == "Edit first-pass clearance rate", "kpi_value"
    ]
    assert null_first_pass.isna().all()
    assert (
        kpis.loc[kpis["kpi_name"] == "Edit first-pass clearance rate", "denominator_value"] == 0
    ).all()
    assert not math.isnan(float(overall_late["kpi_value"]))
