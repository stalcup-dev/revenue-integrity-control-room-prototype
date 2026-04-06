from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.synthetic.generate_documentation_events import (
    OUTPUT_FILENAME as DOCUMENTATION_FILENAME,
    write_documentation_events_parquet,
)
from ri_control_room.synthetic.generate_encounters import (
    OUTPUT_FILENAME as ENCOUNTERS_FILENAME,
    get_processed_dir,
    write_encounters_parquet,
)
from ri_control_room.synthetic.generate_orders import (
    OUTPUT_FILENAME as ORDERS_FILENAME,
    write_orders_parquet,
)


OUTPUT_FILENAME = "upstream_activity_signals.parquet"


def _load_required_tables(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    encounters_path = processed_dir / ENCOUNTERS_FILENAME
    orders_path = processed_dir / ORDERS_FILENAME
    documentation_path = processed_dir / DOCUMENTATION_FILENAME
    if not encounters_path.exists():
        write_encounters_parquet(repo_root)
    if not orders_path.exists():
        write_orders_parquet(repo_root)
    if not documentation_path.exists():
        write_documentation_events_parquet(repo_root)
    return pd.read_parquet(encounters_path), pd.read_parquet(documentation_path)


def _non_billable_reason(event: pd.Series, scenario: str) -> str:
    activity_role = str(event["activity_role"])
    department = str(event["department"])

    if department.startswith("Outpatient Infusion"):
        if scenario == "hydration_conditional" and activity_role == "hydration":
            return "same_day_hydration_integral_to_primary_infusion"
        if scenario == "access_site_integral" and activity_role == "access_site":
            return "access_site_integral_to_primary_infusion"
        if scenario == "iv_push_only" and activity_role == "primary_infusion":
            return "iv_push_documented_without_infusion_duration"

    if department.startswith("Radiology"):
        if scenario in {"incomplete_study_nonbillable", "incomplete_ir_case"} and activity_role == "primary_study":
            return "incomplete_study_without_technical_completion"
        if scenario == "contrast_packaged" and activity_role == "contrast_support":
            return "contrast_packaged_into_primary_technical_service"

    if department.startswith("OR /"):
        if scenario == "supply_integral" and activity_role == "implant_supply":
            return "supply_integral_to_procedural_package"
        if scenario in {"discontinued_partial", "discontinued_no_charge"}:
            return "discontinued_before_billable_procedure_threshold"

    return "packaged_or_integral"


def generate_upstream_activity_signals_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters, documentation_events = _load_required_tables(repo_root)
    encounter_lookup = encounters.set_index("encounter_id").to_dict("index")
    rows: list[dict[str, object]] = []

    for _, event in documentation_events.iterrows():
        encounter = encounter_lookup[event["encounter_id"]]
        scenario = encounter["scenario_code"]

        signal_type = "performed_activity"
        if encounter["department"].startswith("Outpatient Infusion"):
            signal_type = "medication_administration"
        elif encounter["department"].startswith("Radiology"):
            signal_type = "study_completion"
        elif encounter["department"].startswith("OR /"):
            signal_type = "case_activity"

        separately_billable_candidate_flag = bool(event["supports_charge_flag"]) and not bool(
            event["packaged_or_integral_candidate_flag"]
        )
        non_billable_reason = ""
        if bool(event["non_billable_candidate_flag"]):
            non_billable_reason = event["documentation_gap_type"] or _non_billable_reason(
                event, scenario
            )
        elif not bool(event["supports_charge_flag"]):
            non_billable_reason = event["documentation_gap_type"] or "support_incomplete"

        rows.append(
            {
                "activity_signal_id": f"SIG-{event['documentation_event_id']}",
                "encounter_id": event["encounter_id"],
                "order_id": event["order_id"],
                "documentation_event_id": event["documentation_event_id"],
                "department": event["department"],
                "service_line": event["service_line"],
                "scenario_code": event["scenario_code"],
                "activity_role": event["activity_role"],
                "signal_type": signal_type,
                "activity_code": event["performed_activity_code"],
                "activity_description": event["performed_activity_description"],
                "activity_ts": event["event_ts"],
                "performed_flag": True,
                "support_status": event["documentation_status"],
                "signal_basis": "documentation_event",
                "traceable_to_documentation_flag": True,
                "separately_billable_candidate_flag": separately_billable_candidate_flag,
                "packaged_or_integral_candidate_flag": bool(
                    event["packaged_or_integral_candidate_flag"]
                ),
                "non_billable_candidate_flag": bool(event["non_billable_candidate_flag"]),
                "non_billable_reason": non_billable_reason,
                "hierarchy_bucket": event["sequence_bucket"],
                "unit_hint": event["unit_hint"],
                "unit_conversion_required_flag": bool(event["unit_conversion_required_flag"]),
                "expected_duration_unit_count": float(event["expected_duration_unit_count"]),
                "documented_duration_minutes": int(event["documented_duration_minutes"]),
                "separate_access_site_flag": bool(event["separate_access_site_flag"]),
                "hydration_conditionality": event["hydration_conditionality"],
                "distinctness_support_flag": bool(event["distinctness_support_flag"]),
                "study_completion_state": event["study_completion_state"],
                "case_completion_state": event["case_completion_state"],
                "waste_scenario_flag": bool(event["waste_documented_flag"])
                or scenario == "waste_missing",
                "contrast_or_device_linked_flag": bool(
                    event["contrast_or_device_linked_flag"]
                ),
                "late_post_risk_flag": bool(encounter["late_post_risk_flag"]),
                "timestamp_dependency_flag": encounter["department"].startswith(
                    "Outpatient Infusion"
                )
                or encounter["department"].startswith("OR /"),
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "activity_signal_id"]).reset_index(
        drop=True
    )
    df["activity_ts"] = pd.to_datetime(df["activity_ts"])
    return df


def write_upstream_activity_signals_parquet(repo_root: Path | None = None) -> Path:
    df = generate_upstream_activity_signals_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_upstream_activity_signals_parquet()


if __name__ == "__main__":
    main()
