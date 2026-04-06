from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.synthetic.generate_claims_account_status import (
    OUTPUT_FILENAME as STATUS_FILENAME,
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_encounters import (
    OUTPUT_FILENAME as ENCOUNTERS_FILENAME,
    get_processed_dir,
    write_encounters_parquet,
)
from ri_control_room.synthetic.workflow_profiles import get_workflow_profile
from ri_control_room.synthetic.generate_upstream_activity_signals import (
    OUTPUT_FILENAME as SIGNALS_FILENAME,
    write_upstream_activity_signals_parquet,
)


OUTPUT_FILENAME = "charge_events.parquet"


def _load_required_tables(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    encounters_path = processed_dir / ENCOUNTERS_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    signals_path = processed_dir / SIGNALS_FILENAME
    if not encounters_path.exists():
        write_encounters_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    if not signals_path.exists():
        write_upstream_activity_signals_parquet(repo_root)
    return (
        pd.read_parquet(encounters_path),
        pd.read_parquet(status_path),
        pd.read_parquet(signals_path),
    )


def _charge_status_for_stage(stage_name: str, scenario_code: str) -> str:
    if stage_name == "Charge capture pending":
        return "missing"
    if stage_name == "Documentation pending":
        return "posted_pending_support"
    if stage_name == "Coding pending":
        return "posted_pending_coding"
    if stage_name == "Prebill edit / hold":
        return "posted_held_prebill"
    if stage_name == "Correction / rebill pending":
        return "posted_needs_correction"
    if "packaged" in scenario_code or "integral" in scenario_code or "nonbillable" in scenario_code:
        return "suppressed_nonbillable"
    return "posted"


def generate_charge_events_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters, statuses, signals = _load_required_tables(repo_root)
    status_lookup = statuses.set_index("encounter_id").to_dict("index")
    rows: list[dict[str, object]] = []

    for _, signal in signals.iterrows():
        encounter = encounters.loc[encounters["encounter_id"] == signal["encounter_id"]].iloc[0]
        status = status_lookup[signal["encounter_id"]]
        workflow_profile = get_workflow_profile(str(encounter["scenario_code"]))
        scenario_code = str(signal.get("scenario_code", ""))
        activity_role = str(signal.get("activity_role", ""))
        if (scenario_code, activity_role) in {
            ("iv_push_only", "primary_infusion"),
            ("site_specific_clean", "primary_study"),
            ("implant_linked_clean", "implant_supply"),
        }:
            continue
        charge_status = _charge_status_for_stage(
            status["current_prebill_stage"], encounter["scenario_code"]
        )
        if charge_status == "missing":
            continue

        charge_post_ts = signal["activity_ts"] + timedelta(hours=6)
        late_charge_days = int(workflow_profile["late_charge_days_after_service"])
        if late_charge_days > 0:
            charge_post_ts = encounter["service_end_ts"] + timedelta(days=late_charge_days)
        if status["current_prebill_stage"] == "Correction / rebill pending":
            charge_post_ts = encounter["final_bill_datetime"] + timedelta(days=1)

        units = float(signal["unit_hint"]) if signal["unit_hint"] else 1.0
        if encounter["department"].startswith("Outpatient Infusion"):
            if bool(signal.get("unit_conversion_required_flag", False)):
                units = float(signal["expected_duration_unit_count"])
            if scenario_code in {"missing_stop_time", "late_charge_risk"} and activity_role in {
                "primary_infusion",
                "sequential_infusion",
            }:
                units = max(float(signal["expected_duration_unit_count"]) - 1.0, 1.0)
        gross_amount = 150.0
        if encounter["department"].startswith("Outpatient Infusion"):
            gross_amount = 225.0
        elif encounter["department"].startswith("Radiology"):
            gross_amount = 340.0
        elif encounter["department"].startswith("OR /"):
            gross_amount = 1250.0

        rows.append(
            {
                "charge_event_id": f"CHG-{signal['activity_signal_id']}",
                "encounter_id": signal["encounter_id"],
                "claim_id": status["claim_id"],
                "account_id": status["account_id"],
                "activity_signal_id": signal["activity_signal_id"],
                "department": signal["department"],
                "service_line": signal["service_line"],
                "charge_code": signal["activity_code"],
                "charge_description": signal["activity_description"],
                "charge_event_type": "posted",
                "charge_status": charge_status,
                "service_date": encounter["service_start_ts"].date(),
                "charge_post_ts": charge_post_ts,
                "units": units,
                "gross_charge_amount": gross_amount,
                "expected_flag": charge_status != "suppressed_nonbillable",
                "packaged_or_integral_flag": bool(signal["packaged_or_integral_candidate_flag"]),
                "non_billable_candidate_flag": bool(signal["non_billable_candidate_flag"]),
                "support_status": signal["support_status"],
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "charge_event_id"]).reset_index(drop=True)
    if not df.empty:
        df["charge_post_ts"] = pd.to_datetime(df["charge_post_ts"])
        df["service_date"] = pd.to_datetime(df["service_date"])
    return df


def write_charge_events_parquet(repo_root: Path | None = None) -> Path:
    df = generate_charge_events_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_charge_events_parquet()


if __name__ == "__main__":
    main()
