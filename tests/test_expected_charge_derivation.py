from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _generate_expected_opportunities() -> Path:
    from ri_control_room.logic.derive_expected_charge_opportunities import (
        write_expected_charge_opportunities_parquet,
    )

    write_expected_charge_opportunities_parquet(ROOT)
    return ROOT / "data" / "processed"


def test_expected_charge_derivation_contract() -> None:
    from ri_control_room.constants import FROZEN_V1_DEPARTMENTS

    processed_dir = _generate_expected_opportunities()
    expected = pd.read_parquet(processed_dir / "expected_charge_opportunities.parquet")

    assert not expected.empty
    assert set(expected["department"]) == set(FROZEN_V1_DEPARTMENTS)

    required_columns = {
        "expected_code_hint",
        "expected_modifier_hint",
        "expected_units",
        "evidence_completeness_status",
        "separately_billable_flag",
        "packaged_or_integral_flag",
        "why_not_billable_explanation",
        "opportunity_status",
    }
    assert required_columns.issubset(expected.columns)

    assert expected["documentation_event_id"].notna().all()
    assert (expected["documentation_event_id"] != "").all()
    assert expected["documented_performed_activity_flag"].all()
    assert (expected["signal_basis"] == "documentation_event").all()
    assert (expected["signal_basis"] != "order_only").all()

    suppressed = expected[expected["suppression_flag"]]
    assert not suppressed.empty
    assert set(suppressed["department"]) == set(FROZEN_V1_DEPARTMENTS)
    assert suppressed["packaged_or_integral_flag"].any()
    assert (suppressed["why_not_billable_explanation"] != "").all()

    assert (expected["opportunity_status"] == "recoverable_missed_charge").any()
    recoverable = expected[expected["opportunity_status"] == "recoverable_missed_charge"]
    assert (~recoverable["charge_event_exists_flag"]).all()
    assert recoverable["department"].nunique() >= 2

    assert (expected["opportunity_status"] == "unsupported_charge_risk").any()
    unsupported = expected[expected["opportunity_status"] == "unsupported_charge_risk"]
    assert unsupported["why_not_billable_explanation"].notna().all()
    assert (unsupported["why_not_billable_explanation"] != "").all()
    assert unsupported["charge_event_exists_flag"].all()

    assert (expected["opportunity_status"] == "packaged_or_nonbillable_suppressed").any()
    assert (expected["opportunity_status"] == "modifier_dependency_case").any()
    assert suppressed["department"].nunique() == len(FROZEN_V1_DEPARTMENTS)
    assert not suppressed["why_not_billable_explanation"].isin({"", "packaged_or_integral"}).any()

    infusion_events = set(
        expected.loc[
            expected["department"] == "Outpatient Infusion / Oncology Infusion", "clinical_event"
        ]
    )
    radiology_events = set(
        expected.loc[
            expected["department"] == "Radiology / Interventional Radiology", "clinical_event"
        ]
    )
    procedural_events = set(
        expected.loc[
            expected["department"]
            == "OR / Hospital Outpatient Surgery / Procedural Areas",
            "clinical_event",
        ]
    )

    assert infusion_events.issubset(
        {
            "Initial therapeutic infusion",
            "Hydration infusion distinct from therapy",
            "Drug waste scenario",
            "Separate access-site administration",
            "Timed infusion unit-conversion review",
        }
    )
    assert radiology_events.issubset(
        {
            "Completed diagnostic imaging study",
            "Incomplete or discontinued imaging study",
            "Interventional device or contrast linkage",
            "Laterality/site-dependent imaging study",
            "Distinct same-day imaging study",
        }
    )
    assert procedural_events.issubset(
        {
            "Completed outpatient procedure",
            "Discontinued procedure",
            "Implant or supply capture",
            "Timestamp-dependent procedural support",
        }
    )

    assert len(infusion_events) >= 2
    assert len(radiology_events) >= 2
    assert len(procedural_events) >= 2
