from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.reference_loader import load_reference_csv
from ri_control_room.synthetic.generate_charge_events import (
    OUTPUT_FILENAME as CHARGE_EVENTS_FILENAME,
    write_charge_events_parquet,
)
from ri_control_room.synthetic.generate_claims_account_status import (
    OUTPUT_FILENAME as STATUS_FILENAME,
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_documentation_events import (
    OUTPUT_FILENAME as DOCUMENTATION_FILENAME,
    write_documentation_events_parquet,
)
from ri_control_room.synthetic.generate_encounters import get_processed_dir
from ri_control_room.synthetic.generate_upstream_activity_signals import (
    OUTPUT_FILENAME as SIGNALS_FILENAME,
    write_upstream_activity_signals_parquet,
)


OUTPUT_FILENAME = "expected_charge_opportunities.parquet"

INFUSION_DEPARTMENT = "Outpatient Infusion / Oncology Infusion"
RADIOLOGY_DEPARTMENT = "Radiology / Interventional Radiology"
PROCEDURAL_DEPARTMENT = "OR / Hospital Outpatient Surgery / Procedural Areas"


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() == "true"


def _merged_value(row: pd.Series, base_name: str) -> object:
    for candidate in (base_name, f"{base_name}_signal", f"{base_name}_doc"):
        if candidate in row.index:
            return row[candidate]
    return ""


def _load_inputs(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    documentation_path = processed_dir / DOCUMENTATION_FILENAME
    signals_path = processed_dir / SIGNALS_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    charge_events_path = processed_dir / CHARGE_EVENTS_FILENAME

    if not documentation_path.exists():
        write_documentation_events_parquet(repo_root)
    if not signals_path.exists():
        write_upstream_activity_signals_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    if not charge_events_path.exists():
        write_charge_events_parquet(repo_root)

    return (
        pd.read_parquet(documentation_path),
        pd.read_parquet(signals_path),
        pd.read_parquet(status_path),
        pd.read_parquet(charge_events_path),
    )


def _build_reference_map(repo_root: Path | None = None) -> dict[tuple[str, str], dict[str, str]]:
    rows = load_reference_csv("department_charge_logic_map", repo_root)
    return {(row["department"], row["clinical_event"]): row for row in rows}


def _map_clinical_event(row: pd.Series) -> str:
    department = row["department"]
    activity_role = str(_merged_value(row, "activity_role"))
    scenario_code = str(_merged_value(row, "scenario_code"))

    if department == INFUSION_DEPARTMENT:
        if activity_role == "waste_review" or _as_bool(row["waste_scenario_flag"]) or _as_bool(
            row["waste_documented_flag"]
        ):
            return "Drug waste scenario"
        if activity_role == "hydration" or str(_merged_value(row, "hydration_conditionality")) == "conditional":
            return "Hydration infusion distinct from therapy"
        if activity_role == "access_site" or _as_bool(_merged_value(row, "separate_access_site_flag")):
            return "Separate access-site administration"
        if activity_role in {"primary_infusion", "sequential_infusion"} and (
            _as_bool(_merged_value(row, "unit_conversion_required_flag"))
            or scenario_code in {"missing_stop_time", "late_charge_risk"}
        ):
            return "Timed infusion unit-conversion review"
        return "Initial therapeutic infusion"

    if department == RADIOLOGY_DEPARTMENT:
        if str(_merged_value(row, "study_completion_state")) == "incomplete":
            return "Incomplete or discontinued imaging study"
        if scenario_code in {"laterality_missing", "site_specific_clean"}:
            return "Laterality/site-dependent imaging study"
        if activity_role == "distinct_repeat" or _as_bool(_merged_value(row, "distinctness_support_flag")):
            return "Distinct same-day imaging study"
        if activity_role in {"contrast_support", "device_linkage"} or _as_bool(
            row["contrast_or_device_linked_flag_signal"]
        ):
            return "Interventional device or contrast linkage"
        return "Completed diagnostic imaging study"

    if scenario_code == "timestamp_missing" or (
        activity_role == "primary_procedure" and not _as_bool(row["timestamp_complete_flag"])
    ):
        return "Timestamp-dependent procedural support"
    if _as_bool(row["discontinued_state"]):
        return "Discontinued procedure"
    if activity_role == "implant_supply" or _as_bool(row["implant_supply_linked_flag"]):
        return "Implant or supply capture"
    return "Completed outpatient procedure"


def _expected_code_hint(clinical_event: str, activity_code: str) -> str:
    suffix_map = {
        "Initial therapeutic infusion": "EXP",
        "Hydration infusion distinct from therapy": "HYD",
        "Drug waste scenario": "WASTE",
        "Timed infusion unit-conversion review": "UNITS",
        "Separate access-site administration": "ACCESS",
        "Completed diagnostic imaging study": "TECH",
        "Incomplete or discontinued imaging study": "SUPPRESS",
        "Laterality/site-dependent imaging study": "LAT",
        "Distinct same-day imaging study": "DISTINCT",
        "Interventional device or contrast linkage": "SUPPLY",
        "Completed outpatient procedure": "PROC",
        "Discontinued procedure": "DISC",
        "Implant or supply capture": "IMPL",
        "Timestamp-dependent procedural support": "TIME",
    }
    return f"{activity_code}_{suffix_map[clinical_event]}"


def _expected_modifier_hint(row: pd.Series, clinical_event: str) -> str:
    if clinical_event == "Drug waste scenario":
        return "WASTE_REQ"
    if clinical_event == "Timed infusion unit-conversion review":
        return "UNITS_AUDIT"
    if clinical_event == "Separate access-site administration":
        return "ACCESS_DISTINCT_REQ"
    if clinical_event == "Laterality/site-dependent imaging study":
        return "SITE_LATERALITY_REQ"
    if clinical_event == "Distinct same-day imaging study":
        return "DISTINCT_REQ"
    if clinical_event == "Discontinued procedure":
        return "REDUCED_OR_DISC"
    if _as_bool(_merged_value(row, "distinctness_support_flag")) or row["hierarchy_bucket"] in {
        "concurrent",
        "sequential",
    }:
        return "DISTINCT_REQ"
    return ""


def _evidence_completeness_status(row: pd.Series) -> str:
    if not (
        row["signal_basis"] == "documentation_event"
        and _as_bool(row["traceable_to_documentation_flag"])
        and _as_bool(row["performed_flag"])
    ):
        return "no_documented_performed_support"
    if _as_bool(row["supports_charge_flag"]) and row["documentation_status"] == "complete":
        return "complete"
    if row["documentation_status"] == "partial":
        return "partial_support"
    return "incomplete_support"


def _suppression_reason(row: pd.Series, reference_row: dict[str, str]) -> str:
    if row["non_billable_reason"]:
        return row["non_billable_reason"]
    if row["documentation_gap_type"]:
        return row["documentation_gap_type"]
    return reference_row["why_it_may_not_be_billable"]


def _load_charge_summary(charge_events: pd.DataFrame) -> pd.DataFrame:
    if charge_events.empty:
        return pd.DataFrame(
            columns=[
                "activity_signal_id",
                "charge_event_exists_flag",
                "charge_status_example",
            ]
        )
    summary = (
        charge_events.groupby("activity_signal_id", as_index=False)
        .agg(
            charge_event_exists_flag=("charge_event_id", "size"),
            charge_status_example=("charge_status", "first"),
        )
        .assign(charge_event_exists_flag=lambda df: df["charge_event_exists_flag"] > 0)
    )
    return summary


def derive_expected_charge_opportunities_df(repo_root: Path | None = None) -> pd.DataFrame:
    documentation_events, upstream_signals, workflow_header, charge_events = _load_inputs(repo_root)
    reference_map = _build_reference_map(repo_root)
    charge_summary = _load_charge_summary(charge_events)

    merged = (
        upstream_signals.merge(
            documentation_events,
            on=["documentation_event_id", "encounter_id", "order_id", "department", "service_line"],
            suffixes=("_signal", "_doc"),
        )
        .merge(
            workflow_header[
                [
                    "encounter_id",
                    "claim_id",
                    "account_id",
                    "current_prebill_stage",
                    "current_queue",
                    "recoverability_status",
                    "current_primary_blocker_state",
                ]
            ],
            on="encounter_id",
            how="left",
        )
        .merge(charge_summary, on="activity_signal_id", how="left")
    )

    merged["charge_event_exists_flag"] = (
        merged["charge_event_exists_flag"].astype("boolean").fillna(False).astype(bool)
    )
    merged["charge_status_example"] = merged["charge_status_example"].fillna("")

    documented_support_mask = (
        (merged["signal_basis"] == "documentation_event")
        & merged["traceable_to_documentation_flag"].fillna(False)
        & merged["performed_flag"].fillna(False)
        & merged["documentation_event_id"].notna()
    )
    auditable = merged.loc[documented_support_mask].copy()

    rows: list[dict[str, object]] = []
    for _, row in auditable.iterrows():
        clinical_event = _map_clinical_event(row)
        reference_row = reference_map[(row["department"], clinical_event)]
        evidence_status = _evidence_completeness_status(row)
        expected_modifier_hint = _expected_modifier_hint(row, clinical_event)

        packaged_or_integral_flag = _as_bool(row["packaged_or_integral_candidate_flag_signal"]) or _as_bool(
            row["packaged_or_integral_candidate_flag_doc"]
        )
        non_billable_flag = _as_bool(row["non_billable_candidate_flag_signal"]) or _as_bool(
            row["non_billable_candidate_flag_doc"]
        )
        support_complete = _as_bool(row["supports_charge_flag"]) and evidence_status == "complete"
        charge_exists = _as_bool(row["charge_event_exists_flag"])
        reference_separately_billable = _as_bool(reference_row["separately_billable_flag"])

        suppression_flag = packaged_or_integral_flag or non_billable_flag
        opportunity_status = "expected_charge_supported"
        why_not_billable = ""

        if suppression_flag:
            opportunity_status = "packaged_or_nonbillable_suppressed"
            why_not_billable = _suppression_reason(row, reference_row)
        elif not support_complete and charge_exists:
            opportunity_status = "unsupported_charge_risk"
            why_not_billable = row["documentation_gap_type"] or reference_row["common_failure_mode"]
        elif (not charge_exists) and support_complete and row["current_prebill_stage"] in {
            "Charge capture pending",
            "Ready to final bill",
        }:
            opportunity_status = "recoverable_missed_charge"
        elif charge_exists and expected_modifier_hint and row["current_prebill_stage"] in {
            "Coding pending",
            "Prebill edit / hold",
            "Ready to final bill",
        }:
            opportunity_status = "modifier_dependency_case"
        elif not support_complete:
            opportunity_status = "documentation_support_pending"
            why_not_billable = row["documentation_gap_type"] or reference_row["common_failure_mode"]

        rows.append(
            {
                "expected_opportunity_id": f"ECO-{row['activity_signal_id']}",
                "encounter_id": row["encounter_id"],
                "claim_id": row["claim_id"],
                "account_id": row["account_id"],
                "order_id": row["order_id"],
                "documentation_event_id": row["documentation_event_id"],
                "activity_signal_id": row["activity_signal_id"],
                "department": row["department"],
                "service_line": row["service_line"],
                "clinical_event": clinical_event,
                "expected_facility_charge_opportunity": reference_row[
                    "expected_facility_charge_opportunity"
                ],
                "expected_code_hint": _expected_code_hint(clinical_event, row["activity_code"]),
                "expected_modifier_hint": expected_modifier_hint,
                "expected_units": float(row["unit_hint_signal"] or 1.0),
                "evidence_completeness_status": evidence_status,
                "separately_billable_flag": reference_separately_billable and not suppression_flag,
                "packaged_or_integral_flag": packaged_or_integral_flag,
                "documented_performed_activity_flag": True,
                "charge_event_exists_flag": charge_exists,
                "charge_status_example": row["charge_status_example"],
                "suppression_flag": suppression_flag,
                "opportunity_status": opportunity_status,
                "why_not_billable_explanation": why_not_billable,
                "recoverability_status": row["recoverability_status"],
                "current_prebill_stage": row["current_prebill_stage"],
                "current_queue": row["current_queue"],
                "current_primary_blocker_state": row["current_primary_blocker_state"],
                "signal_basis": row["signal_basis"],
                "support_status": row["support_status"],
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "expected_opportunity_id"]).reset_index(
        drop=True
    )
    return df


def write_expected_charge_opportunities_parquet(repo_root: Path | None = None) -> Path:
    df = derive_expected_charge_opportunities_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_expected_charge_opportunities_parquet()


if __name__ == "__main__":
    main()
