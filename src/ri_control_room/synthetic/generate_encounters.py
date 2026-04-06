from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.io import get_repo_root


OUTPUT_FILENAME = "encounters.parquet"


def get_processed_dir(repo_root: Path | None = None) -> Path:
    root = repo_root.resolve() if repo_root is not None else get_repo_root()
    path = root / "data" / "processed"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _scenario_rows() -> list[dict[str, object]]:
    base_ts = datetime(2026, 2, 3, 7, 30)
    payer_groups = (
        "Medicare",
        "Commercial",
        "Managed Medicaid",
        "Blue Cross",
        "Self Pay",
    )
    scenarios = [
        ("INF001", "Outpatient Infusion / Oncology Infusion", "Infusion", "infusion_primary_clean", "Therapeutic infusion", "final_billed", "Final billed", False, False, False),
        ("INF002", "Outpatient Infusion / Oncology Infusion", "Infusion", "hydration_conditional", "Hydration support", "final_billed", "Final billed", True, True, False),
        ("INF003", "Outpatient Infusion / Oncology Infusion", "Infusion", "iv_push_only", "IV push administration", "final_billed", "Final billed", False, False, False),
        ("INF004", "Outpatient Infusion / Oncology Infusion", "Infusion", "missing_stop_time", "Timed infusion with missing stop", "not_final_billed", "Documentation pending", False, False, False),
        ("INF005", "Outpatient Infusion / Oncology Infusion", "Infusion", "waste_documented", "Drug administration with documented waste", "not_final_billed", "Charge capture pending", False, False, False),
        ("INF006", "Outpatient Infusion / Oncology Infusion", "Infusion", "waste_missing", "Drug administration with undocumented waste", "not_final_billed", "Prebill edit / hold", False, False, False),
        ("INF007", "Outpatient Infusion / Oncology Infusion", "Infusion", "sequential_infusion", "Sequential infusion", "final_billed", "Final billed", False, False, False),
        ("INF008", "Outpatient Infusion / Oncology Infusion", "Infusion", "access_site_integral", "Separate access-site candidate", "final_billed", "Final billed", True, True, False),
        ("INF009", "Outpatient Infusion / Oncology Infusion", "Infusion", "concurrent_infusion", "Concurrent infusion", "not_final_billed", "Coding pending", False, False, False),
        ("INF010", "Outpatient Infusion / Oncology Infusion", "Infusion", "late_charge_risk", "Infusion with late-post risk", "not_final_billed", "Charge capture pending", False, False, True),
        ("RAD001", "Radiology / Interventional Radiology", "Radiology", "completed_study_clean", "Completed diagnostic study", "final_billed", "Final billed", False, False, False),
        ("RAD002", "Radiology / Interventional Radiology", "Radiology", "incomplete_study_nonbillable", "Incomplete study", "final_billed", "Final billed", True, True, False),
        ("RAD003", "Radiology / Interventional Radiology", "Radiology", "laterality_missing", "Laterality-dependent study", "not_final_billed", "Documentation pending", False, False, False),
        ("RAD004", "Radiology / Interventional Radiology", "Radiology", "contrast_linked_clean", "Contrast-supported imaging", "final_billed", "Final billed", False, False, False),
        ("RAD005", "Radiology / Interventional Radiology", "Radiology", "contrast_packaged", "Contrast packaged scenario", "final_billed", "Final billed", True, True, False),
        ("IR001", "Radiology / Interventional Radiology", "Interventional Radiology", "device_link_gap", "IR device linkage gap", "not_final_billed", "Documentation pending", False, False, False),
        ("RAD006", "Radiology / Interventional Radiology", "Radiology", "distinctness_required", "Same-day distinct imaging", "not_final_billed", "Coding pending", False, False, False),
        ("IR002", "Radiology / Interventional Radiology", "Interventional Radiology", "incomplete_ir_case", "Incomplete IR case", "final_billed", "Closed / monitored through denial feedback only", False, False, False),
        ("RAD007", "Radiology / Interventional Radiology", "Radiology", "late_post_risk", "Radiology late-post risk", "final_billed", "Final billed", False, False, True),
        ("RAD008", "Radiology / Interventional Radiology", "Radiology", "site_specific_clean", "Site-specific completed study", "ready_to_final_bill", "Ready to final bill", False, False, False),
        ("OR001", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "completed_case_clean", "Completed outpatient procedure", "final_billed", "Final billed", False, False, False),
        ("OR002", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "discontinued_partial", "Discontinued procedure", "not_final_billed", "Prebill edit / hold", True, True, False),
        ("OR003", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "implant_linked_clean", "Implant linked cleanly", "ready_to_final_bill", "Ready to final bill", False, False, False),
        ("OR004", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "implant_link_gap", "Implant linkage gap", "final_billed", "Final billed", False, False, False),
        ("OR005", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "supply_integral", "Supply integral scenario", "final_billed", "Final billed", True, True, False),
        ("OR006", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "late_post_risk", "Late-post procedural case", "not_final_billed", "Prebill edit / hold", False, False, True),
        ("OR007", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "timestamp_missing", "Procedure with missing timestamp support", "not_final_billed", "Documentation pending", False, False, False),
        ("OR008", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "discontinued_no_charge", "Discontinued nonbillable case", "final_billed", "Final billed", True, True, False),
        ("OR009", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "device_supply_clean", "Device and supply capture", "final_billed", "Final billed", False, False, False),
        ("OR010", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "correction_rebill_pending", "Post-bill correction case", "correction_rebill_pending", "Correction / rebill pending", False, False, True),
        ("INF011", "Outpatient Infusion / Oncology Infusion", "Infusion", "missing_stop_time", "Timed infusion with missing stop", "not_final_billed", "Documentation pending", False, False, False),
        ("INF012", "Outpatient Infusion / Oncology Infusion", "Infusion", "waste_documented", "Drug administration with documented waste", "not_final_billed", "Charge capture pending", False, False, False),
        ("INF013", "Outpatient Infusion / Oncology Infusion", "Infusion", "waste_missing", "Drug administration with undocumented waste", "not_final_billed", "Prebill edit / hold", False, False, False),
        ("INF014", "Outpatient Infusion / Oncology Infusion", "Infusion", "concurrent_infusion", "Concurrent infusion add-on review", "not_final_billed", "Coding pending", False, False, False),
        ("INF015", "Outpatient Infusion / Oncology Infusion", "Infusion", "late_charge_risk", "Infusion late-post follow-up", "not_final_billed", "Charge capture pending", False, False, True),
        ("INF016", "Outpatient Infusion / Oncology Infusion", "Infusion", "hydration_conditional", "Hydration packaged same-day", "final_billed", "Final billed", True, True, False),
        ("INF017", "Outpatient Infusion / Oncology Infusion", "Infusion", "access_site_integral", "Access-site packaged same-day", "final_billed", "Final billed", True, True, False),
        ("INF018", "Outpatient Infusion / Oncology Infusion", "Infusion", "missing_stop_time", "Final-billed infusion with missing stop", "final_billed", "Final billed", False, False, False),
        ("INF019", "Outpatient Infusion / Oncology Infusion", "Infusion", "late_charge_risk", "Final-billed infusion late charge", "final_billed", "Final billed", False, False, True),
        ("INF020", "Outpatient Infusion / Oncology Infusion", "Infusion", "sequential_infusion", "Sequential infusion add-on review", "not_final_billed", "Coding pending", False, False, False),
        ("INF021", "Outpatient Infusion / Oncology Infusion", "Infusion", "missing_stop_time", "Closed monitored infusion support risk", "final_billed", "Closed / monitored through denial feedback only", False, False, False),
        ("RAD009", "Radiology / Interventional Radiology", "Radiology", "laterality_missing", "Laterality-dependent follow-up study", "not_final_billed", "Documentation pending", False, False, False),
        ("RAD010", "Radiology / Interventional Radiology", "Radiology", "distinctness_required", "Distinct same-day imaging review", "not_final_billed", "Coding pending", False, False, False),
        ("RAD011", "Radiology / Interventional Radiology", "Radiology", "contrast_packaged", "Contrast packaged into technical service", "final_billed", "Final billed", True, True, False),
        ("RAD012", "Radiology / Interventional Radiology", "Radiology", "site_specific_clean", "Ready-to-bill site-specific study", "ready_to_final_bill", "Ready to final bill", False, False, False),
        ("RAD013", "Radiology / Interventional Radiology", "Radiology", "completed_study_clean", "Clean completed diagnostic study", "final_billed", "Final billed", False, False, False),
        ("IR003", "Radiology / Interventional Radiology", "Interventional Radiology", "device_link_gap", "Final-billed IR device linkage gap", "final_billed", "Final billed", False, False, False),
        ("IR004", "Radiology / Interventional Radiology", "Interventional Radiology", "incomplete_ir_case", "Closed monitored incomplete IR case", "final_billed", "Closed / monitored through denial feedback only", False, False, False),
        ("RAD014", "Radiology / Interventional Radiology", "Radiology", "late_post_risk", "Radiology late-post variance", "final_billed", "Final billed", False, False, True),
        ("RAD015", "Radiology / Interventional Radiology", "Radiology", "incomplete_study_nonbillable", "Final-billed incomplete study", "final_billed", "Final billed", True, True, False),
        ("RAD016", "Radiology / Interventional Radiology", "Radiology", "contrast_linked_clean", "Clean contrast-supported study", "final_billed", "Final billed", False, False, False),
        ("OR011", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "discontinued_partial", "Discontinued procedural hold", "not_final_billed", "Prebill edit / hold", True, True, False),
        ("OR012", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "implant_link_gap", "Final-billed implant linkage gap", "final_billed", "Final billed", False, False, False),
        ("OR013", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "late_post_risk", "Procedural late-post hold", "not_final_billed", "Prebill edit / hold", False, False, True),
        ("OR014", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "timestamp_missing", "Procedural timestamp follow-up", "not_final_billed", "Documentation pending", False, False, False),
        ("OR015", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "supply_integral", "Supply packaged into procedural service", "final_billed", "Final billed", True, True, False),
        ("OR016", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "correction_rebill_pending", "Second post-bill correction case", "correction_rebill_pending", "Correction / rebill pending", False, False, True),
        ("OR017", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "implant_linked_clean", "Ready-to-bill implant case", "ready_to_final_bill", "Ready to final bill", False, False, False),
        ("OR018", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "discontinued_no_charge", "Final-billed discontinued nonbillable case", "final_billed", "Final billed", True, True, False),
        ("OR019", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "device_supply_clean", "Clean device and supply capture", "final_billed", "Final billed", False, False, False),
        ("OR020", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "late_post_risk", "Final-billed late-post procedural case", "final_billed", "Final billed", False, False, True),
        ("OR021", "OR / Hospital Outpatient Surgery / Procedural Areas", "Outpatient Surgery", "implant_link_gap", "Closed monitored implant linkage risk", "final_billed", "Closed / monitored through denial feedback only", False, False, False),
    ]

    rows: list[dict[str, object]] = []
    for index, scenario in enumerate(scenarios):
        (
            encounter_code,
            department,
            service_line,
            scenario_code,
            primary_event,
            final_bill_status,
            workflow_stage,
            packaged_candidate_flag,
            non_billable_candidate_flag,
            late_post_risk_flag,
        ) = scenario
        start_ts = base_ts + timedelta(hours=index * 3)
        duration_minutes = 45 if department.startswith("Outpatient Infusion") else 75
        if department.startswith("OR /"):
            duration_minutes = 95
        service_end_ts = start_ts + timedelta(minutes=duration_minutes)
        final_bill_ts = (
            service_end_ts + timedelta(days=1)
            if final_bill_status in {"final_billed", "correction_rebill_pending"}
            else pd.NaT
        )
        rows.append(
            {
                "encounter_id": encounter_code,
                "account_id": f"ACC-{1000 + index}",
                "patient_id": f"PT-{2000 + index}",
                "encounter_setting": "Outpatient",
                "patient_type": "Hospital Outpatient",
                "department": department,
                "service_line": service_line,
                "payer_group": payer_groups[index % len(payer_groups)],
                "scenario_code": scenario_code,
                "primary_clinical_event": primary_event,
                "encounter_status": "Completed",
                "workflow_stage": workflow_stage,
                "final_bill_status": final_bill_status,
                "encounter_open_ts": start_ts - timedelta(hours=2),
                "scheduled_service_ts": start_ts - timedelta(days=1, hours=2),
                "service_start_ts": start_ts,
                "service_end_ts": service_end_ts,
                "final_bill_datetime": final_bill_ts,
                "packaged_candidate_flag": packaged_candidate_flag,
                "non_billable_candidate_flag": non_billable_candidate_flag,
                "late_post_risk_flag": late_post_risk_flag,
            }
        )
    return rows


def generate_encounters_df() -> pd.DataFrame:
    df = pd.DataFrame(_scenario_rows())
    for column in (
        "encounter_open_ts",
        "scheduled_service_ts",
        "service_start_ts",
        "service_end_ts",
        "final_bill_datetime",
    ):
        df[column] = pd.to_datetime(df[column])
    return df.sort_values("encounter_id").reset_index(drop=True)


def write_encounters_parquet(repo_root: Path | None = None) -> Path:
    df = generate_encounters_df()
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_encounters_parquet()


if __name__ == "__main__":
    main()
