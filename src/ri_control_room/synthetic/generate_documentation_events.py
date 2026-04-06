from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.synthetic.generate_encounters import (
    OUTPUT_FILENAME as ENCOUNTERS_FILENAME,
    get_processed_dir,
    write_encounters_parquet,
)
from ri_control_room.synthetic.generate_orders import (
    OUTPUT_FILENAME as ORDERS_FILENAME,
    write_orders_parquet,
)


OUTPUT_FILENAME = "documentation_events.parquet"


def _load_required_tables(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    encounters_path = processed_dir / ENCOUNTERS_FILENAME
    orders_path = processed_dir / ORDERS_FILENAME
    if not encounters_path.exists():
        write_encounters_parquet(repo_root)
    if not orders_path.exists():
        write_orders_parquet(repo_root)
    return pd.read_parquet(encounters_path), pd.read_parquet(orders_path)


def generate_documentation_events_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters, orders = _load_required_tables(repo_root)
    encounter_lookup = encounters.set_index("encounter_id").to_dict("index")
    rows: list[dict[str, object]] = []

    for _, order in orders.iterrows():
        encounter = encounter_lookup[order["encounter_id"]]
        scenario = encounter["scenario_code"]
        activity_role = str(order.get("activity_role", "primary"))
        start_time = encounter["service_start_ts"]
        stop_time = encounter["service_end_ts"]
        documentation_type = "procedure_note"
        documentation_status = "complete"
        supports_charge_flag = True
        documentation_gap_type = ""
        sequence_bucket = ""
        hydration_conditionality = "not_applicable"
        separate_access_site_flag = False
        unit_hint = 1.0
        waste_documented_flag = False
        study_completion_state = "not_applicable"
        site_documented_flag = False
        laterality_documented_flag = False
        distinctness_support_flag = False
        contrast_or_device_linked_flag = False
        case_completion_state = "completed"
        discontinued_state = False
        implant_supply_linked_flag = False
        timestamp_complete_flag = True
        unit_conversion_required_flag = False
        documented_duration_minutes = 0
        expected_duration_unit_count = 1.0
        packaged_or_integral_candidate_flag = False
        non_billable_candidate_flag = False

        if encounter["department"].startswith("Outpatient Infusion"):
            documentation_type = "infusion_administration"
            sequence_bucket = {
                "concurrent_infusion": "concurrent" if activity_role == "concurrent_infusion" else "primary",
                "sequential_infusion": "sequential" if activity_role == "sequential_infusion" else "primary",
            }.get(scenario, "primary")
            hydration_conditionality = (
                "conditional" if activity_role == "hydration" else "not_applicable"
            )
            separate_access_site_flag = activity_role == "access_site"
            documented_duration_minutes = 95 if activity_role == "primary_infusion" else 45
            if activity_role == "sequential_infusion":
                documented_duration_minutes = 65
            if activity_role == "concurrent_infusion":
                documented_duration_minutes = 35
            unit_conversion_required_flag = activity_role in {
                "primary_infusion",
                "sequential_infusion",
                "concurrent_infusion",
            }
            expected_duration_unit_count = max(documented_duration_minutes / 30.0, 1.0)
            unit_hint = float(round(expected_duration_unit_count, 1))
            waste_documented_flag = activity_role == "waste_review" and scenario == "waste_documented"
            if activity_role == "hydration":
                documentation_type = "hydration_administration"
                documented_duration_minutes = 40
                unit_hint = 1.0
                supports_charge_flag = False
                packaged_or_integral_candidate_flag = True
                non_billable_candidate_flag = True
            if activity_role == "access_site":
                documentation_type = "access_site_administration"
                documented_duration_minutes = 15
                unit_hint = 1.0
                supports_charge_flag = False
                packaged_or_integral_candidate_flag = True
                non_billable_candidate_flag = True
            if activity_role == "waste_review":
                documentation_type = "waste_support_record"
                documented_duration_minutes = 0
                unit_hint = 1.0
            if scenario == "missing_stop_time":
                stop_time = pd.NaT
                documentation_status = "incomplete"
                supports_charge_flag = False
                documentation_gap_type = "missing_stop_time"
                timestamp_complete_flag = False
                unit_hint = 2.0
            if scenario == "waste_missing":
                if activity_role == "waste_review":
                    documentation_status = "incomplete"
                    supports_charge_flag = False
                    documentation_gap_type = "undocumented_waste"
                    waste_documented_flag = False
            if scenario == "iv_push_only":
                start_time = pd.NaT
                stop_time = pd.NaT
                documentation_type = "iv_push_administration"
                unit_conversion_required_flag = False
                documented_duration_minutes = 0
                unit_hint = 1.0
                non_billable_candidate_flag = True
            if scenario == "hydration_conditional" and activity_role == "primary_infusion":
                unit_hint = 2.0
            if scenario == "access_site_integral" and activity_role == "primary_infusion":
                unit_hint = 2.0
            if scenario == "late_charge_risk":
                unit_hint = 2.5

        elif encounter["department"].startswith("Radiology"):
            documentation_type = "study_completion"
            start_time = pd.NaT
            stop_time = pd.NaT
            study_completion_state = "completed"
            site_documented_flag = scenario in {"site_specific_clean", "laterality_missing"}
            laterality_documented_flag = scenario == "site_specific_clean"
            distinctness_support_flag = scenario == "distinctness_required" and activity_role == "distinct_repeat"
            contrast_or_device_linked_flag = activity_role in {"contrast_support", "device_linkage"}
            if activity_role == "contrast_support":
                documentation_type = "contrast_support_record"
            if activity_role == "device_linkage":
                documentation_type = "device_linkage_record"
            if scenario in {"incomplete_study_nonbillable", "incomplete_ir_case"}:
                documentation_status = "partial"
                supports_charge_flag = False
                study_completion_state = "incomplete"
                documentation_gap_type = "incomplete_study"
                if activity_role != "primary_study":
                    supports_charge_flag = False
            if scenario == "laterality_missing":
                documentation_status = "incomplete"
                supports_charge_flag = False
                site_documented_flag = True
                laterality_documented_flag = False
                documentation_gap_type = "missing_laterality"
            if scenario == "site_specific_clean":
                site_documented_flag = True
                laterality_documented_flag = True
            if scenario == "contrast_packaged":
                if activity_role == "contrast_support":
                    supports_charge_flag = False
                    packaged_or_integral_candidate_flag = True
                    non_billable_candidate_flag = True
            if scenario == "device_link_gap":
                if activity_role == "device_linkage":
                    documentation_status = "incomplete"
                    supports_charge_flag = False
                    contrast_or_device_linked_flag = False
                    documentation_gap_type = "missing_device_linkage"

        else:
            documentation_type = "operative_case_record"
            implant_supply_linked_flag = activity_role == "implant_supply" and scenario in {
                "implant_linked_clean",
                "device_supply_clean",
                "late_post_risk",
            }
            contrast_or_device_linked_flag = implant_supply_linked_flag
            if activity_role == "implant_supply":
                documentation_type = "implant_supply_log"
            if scenario in {"discontinued_partial", "discontinued_no_charge"}:
                documentation_status = "partial"
                case_completion_state = "discontinued"
                discontinued_state = True
            if scenario == "implant_link_gap":
                if activity_role == "implant_supply":
                    documentation_status = "incomplete"
                    supports_charge_flag = False
                    implant_supply_linked_flag = False
                    contrast_or_device_linked_flag = False
                    documentation_gap_type = "missing_implant_linkage"
            if scenario == "timestamp_missing":
                stop_time = pd.NaT
                documentation_status = "incomplete"
                supports_charge_flag = False
                documentation_gap_type = "missing_case_timestamp"
                timestamp_complete_flag = False
                documented_duration_minutes = 90
                unit_hint = 1.0
            if scenario in {"supply_integral", "discontinued_no_charge"}:
                if activity_role == "implant_supply" or scenario == "discontinued_no_charge":
                    supports_charge_flag = False
                    packaged_or_integral_candidate_flag = True
                    non_billable_candidate_flag = True
            if scenario == "late_post_risk" and activity_role == "implant_supply":
                implant_supply_linked_flag = True
                documented_duration_minutes = 0
                unit_hint = 1.0

        role_scoped_packaging_scenarios = {
            ("hydration_conditional", "primary_infusion"),
            ("access_site_integral", "primary_infusion"),
            ("contrast_packaged", "primary_study"),
            ("supply_integral", "primary_procedure"),
        }
        if (
            scenario,
            activity_role,
        ) not in role_scoped_packaging_scenarios:
            if not packaged_or_integral_candidate_flag:
                packaged_or_integral_candidate_flag = bool(encounter["packaged_candidate_flag"])
            if not non_billable_candidate_flag:
                non_billable_candidate_flag = bool(encounter["non_billable_candidate_flag"])

        event_ts = encounter["service_end_ts"] - timedelta(minutes=10)
        completion_ts = encounter["service_end_ts"] + timedelta(minutes=15)
        if documentation_status != "complete":
            completion_ts = encounter["service_end_ts"] + timedelta(hours=6)

        rows.append(
            {
                "documentation_event_id": f"DOC-{order['order_id']}",
                "encounter_id": order["encounter_id"],
                "order_id": order["order_id"],
                "department": order["department"],
                "service_line": order["service_line"],
                "scenario_code": scenario,
                "activity_role": activity_role,
                "documentation_type": documentation_type,
                "documentation_status": documentation_status,
                "event_ts": event_ts,
                "completion_ts": completion_ts,
                "start_time": start_time,
                "stop_time": stop_time,
                "performed_activity_code": order["procedure_code"],
                "performed_activity_description": order["procedure_description"],
                "supports_charge_flag": supports_charge_flag,
                "documentation_gap_type": documentation_gap_type,
                "sequence_bucket": sequence_bucket,
                "hydration_conditionality": hydration_conditionality,
                "separate_access_site_flag": separate_access_site_flag,
                "unit_hint": unit_hint,
                "waste_documented_flag": waste_documented_flag,
                "study_completion_state": study_completion_state,
                "site_documented_flag": site_documented_flag,
                "laterality_documented_flag": laterality_documented_flag,
                "distinctness_support_flag": distinctness_support_flag,
                "contrast_or_device_linked_flag": contrast_or_device_linked_flag,
                "case_completion_state": case_completion_state,
                "discontinued_state": discontinued_state,
                "implant_supply_linked_flag": implant_supply_linked_flag,
                "timestamp_complete_flag": timestamp_complete_flag,
                "unit_conversion_required_flag": unit_conversion_required_flag,
                "documented_duration_minutes": documented_duration_minutes,
                "expected_duration_unit_count": float(round(expected_duration_unit_count, 1)),
                "packaged_or_integral_candidate_flag": packaged_or_integral_candidate_flag,
                "non_billable_candidate_flag": non_billable_candidate_flag,
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "documentation_event_id"]).reset_index(drop=True)
    for column in ("event_ts", "completion_ts", "start_time", "stop_time"):
        df[column] = pd.to_datetime(df[column])
    return df


def write_documentation_events_parquet(repo_root: Path | None = None) -> Path:
    df = generate_documentation_events_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_documentation_events_parquet()


if __name__ == "__main__":
    main()
