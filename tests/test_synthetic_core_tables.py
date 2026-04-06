from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _generate_processed_tables() -> Path:
    from ri_control_room.synthetic.generate_documentation_events import (
        write_documentation_events_parquet,
    )
    from ri_control_room.synthetic.generate_encounters import write_encounters_parquet
    from ri_control_room.synthetic.generate_orders import write_orders_parquet
    from ri_control_room.synthetic.generate_upstream_activity_signals import (
        write_upstream_activity_signals_parquet,
    )

    write_encounters_parquet(ROOT)
    write_orders_parquet(ROOT)
    write_documentation_events_parquet(ROOT)
    write_upstream_activity_signals_parquet(ROOT)
    return ROOT / "data" / "processed"


def test_synthetic_core_tables_contract() -> None:
    from ri_control_room.constants import FROZEN_V1_DEPARTMENTS

    processed_dir = _generate_processed_tables()
    encounters = pd.read_parquet(processed_dir / "encounters.parquet")
    orders = pd.read_parquet(processed_dir / "orders.parquet")
    documentation_events = pd.read_parquet(processed_dir / "documentation_events.parquet")
    upstream_activity_signals = pd.read_parquet(
        processed_dir / "upstream_activity_signals.parquet"
    )

    assert set(encounters["department"]) == set(FROZEN_V1_DEPARTMENTS)
    assert set(encounters["encounter_setting"]) == {"Outpatient"}
    assert set(encounters["patient_type"]) == {"Hospital Outpatient"}

    infusion_docs = documentation_events[
        documentation_events["department"] == "Outpatient Infusion / Oncology Infusion"
    ]
    assert infusion_docs["start_time"].notna().any()
    assert infusion_docs["stop_time"].isna().any()

    radiology_docs = documentation_events[
        documentation_events["department"] == "Radiology / Interventional Radiology"
    ]
    assert radiology_docs["start_time"].isna().all()
    assert radiology_docs["laterality_documented_flag"].isin([True, False]).all()

    procedural_docs = documentation_events[
        documentation_events["department"]
        == "OR / Hospital Outpatient Surgery / Procedural Areas"
    ]
    assert procedural_docs["timestamp_complete_flag"].isin([True, False]).all()
    assert procedural_docs["stop_time"].isna().any()

    assert documentation_events["packaged_or_integral_candidate_flag"].any()
    assert upstream_activity_signals["non_billable_candidate_flag"].any()
    assert upstream_activity_signals["traceable_to_documentation_flag"].all()
    assert (upstream_activity_signals["signal_basis"] != "order_only").all()
    assert upstream_activity_signals["documentation_event_id"].notna().all()

    professional_fee_like_fields = {
        "professional_fee_flag",
        "pro_fee_code",
        "wRVU",
        "rendering_provider_npi",
        "cpt_professional_component",
    }
    all_columns = (
        set(encounters.columns)
        | set(orders.columns)
        | set(documentation_events.columns)
        | set(upstream_activity_signals.columns)
    )
    assert professional_fee_like_fields.isdisjoint(all_columns)
