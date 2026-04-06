from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.reference_loader import load_reference_csv
from ri_control_room.synthetic.generate_documentation_events import (
    OUTPUT_FILENAME as DOCUMENTATION_FILENAME,
    write_documentation_events_parquet,
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


OUTPUT_FILENAME = "claims_or_account_status.parquet"


def _load_required_tables(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    encounters_path = processed_dir / ENCOUNTERS_FILENAME
    documentation_path = processed_dir / DOCUMENTATION_FILENAME
    signals_path = processed_dir / SIGNALS_FILENAME
    if not encounters_path.exists():
        write_encounters_parquet(repo_root)
    if not documentation_path.exists():
        write_documentation_events_parquet(repo_root)
    if not signals_path.exists():
        write_upstream_activity_signals_parquet(repo_root)
    return (
        pd.read_parquet(encounters_path),
        pd.read_parquet(documentation_path),
        pd.read_parquet(signals_path),
    )


def _queue_for_stage(stage_name: str, scenario_code: str) -> str:
    if stage_name == "Charge capture pending":
        return "Charge Reconciliation Monitor"
    if stage_name == "Documentation pending":
        return "Documentation Support Exceptions"
    if stage_name == "Coding pending":
        return "Coding Pending Review"
    if stage_name == "Prebill edit / hold":
        return "Modifiers / Edits / Prebill Holds"
    if stage_name == "Correction / rebill pending":
        return "Correction / Rebill Pending"
    return ""


def _blocker_for_stage(stage_name: str, scenario_code: str) -> tuple[str, str]:
    if stage_name == "Charge capture pending":
        return ("Charge capture failure", "Missing or late charge capture")
    if stage_name == "Documentation pending":
        return ("Documentation support failure", "Documentation support incomplete")
    if stage_name == "Coding pending":
        return ("Coding failure", "Coding or modifier review pending")
    if stage_name == "Prebill edit / hold":
        return ("Billing / claim-edit failure", "Prebill edit or hold unresolved")
    if stage_name == "Correction / rebill pending":
        return ("Billing / claim-edit failure", "Correction or rebill pending")
    if stage_name == "Ready to final bill":
        return ("Charge capture failure", "Final reconciliation release pending")
    if "packaged" in scenario_code or "integral" in scenario_code or "nonbillable" in scenario_code:
        return ("Packaged / non-billable / false-positive classification", "Suppressed as nonbillable")
    return ("No active exception", "No active blocker")


def _recoverability_for_stage(stage_name: str) -> str:
    if stage_name in {
        "Open encounter",
        "Charge capture pending",
        "Documentation pending",
        "Coding pending",
        "Prebill edit / hold",
        "Ready to final bill",
    }:
        return "Pre-final-bill recoverable"
    if stage_name == "Correction / rebill pending":
        return "Post-final-bill recoverable by correction / rebill"
    if stage_name == "Closed / monitored through denial feedback only":
        return "Financially closed but still compliance-relevant"
    return "Post-window financially lost" if stage_name == "Final billed" else "Pre-final-bill recoverable"


def _recoverability_for_context(
    stage_name: str,
    encounter: pd.Series,
    stage_entry_ts: pd.Timestamp,
    stage_age_days: int,
) -> str:
    snapshot_ts = pd.Timestamp(stage_entry_ts) + timedelta(days=max(stage_age_days, 0))
    policy_window_end_ts = pd.Timestamp(encounter["service_end_ts"]) + timedelta(days=5)
    final_bill_ts = encounter.get("final_bill_datetime")

    if stage_name in {
        "Charge capture pending",
        "Documentation pending",
        "Coding pending",
        "Prebill edit / hold",
        "Ready to final bill",
    }:
        if snapshot_ts <= policy_window_end_ts:
            return "Pre-final-bill recoverable"
        return "Post-window financially lost"

    if stage_name == "Correction / rebill pending" and pd.notna(final_bill_ts):
        correction_window_end_ts = pd.Timestamp(final_bill_ts) + timedelta(days=10)
        if snapshot_ts <= correction_window_end_ts:
            return "Post-final-bill recoverable by correction / rebill"
        return "Post-window financially lost"

    if stage_name == "Closed / monitored through denial feedback only":
        return "Financially closed but still compliance-relevant"

    return _recoverability_for_stage(stage_name)


def _root_cause_for_scenario(scenario_code: str) -> str:
    if any(key in scenario_code for key in ("missing", "gap", "timestamp", "laterality")):
        return "Documentation behavior"
    if any(key in scenario_code for key in ("late_charge", "late_post")):
        return "Workflow / handoff"
    if any(key in scenario_code for key in ("waste", "concurrent", "sequential", "distinctness")):
        return "Coding practice"
    if any(key in scenario_code for key in ("packaged", "integral", "nonbillable")):
        return "CDM / rule configuration"
    if "correction_rebill" in scenario_code:
        return "Billing edit management"
    return "Workflow / handoff"


def generate_claims_account_status_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters, documentation_events, upstream_signals = _load_required_tables(repo_root)
    queue_definitions = {
        row["queue_name"]: row for row in load_reference_csv("queue_definitions", repo_root)
    }
    doc_by_encounter = documentation_events.groupby("encounter_id")
    signal_by_encounter = upstream_signals.groupby("encounter_id")

    rows: list[dict[str, object]] = []
    for _, encounter in encounters.iterrows():
        workflow_profile = get_workflow_profile(str(encounter["scenario_code"]))
        stage_name = encounter["workflow_stage"]
        queue_name = _queue_for_stage(stage_name, encounter["scenario_code"])
        issue_domain, blocker_state = _blocker_for_stage(stage_name, encounter["scenario_code"])
        group_docs = doc_by_encounter.get_group(encounter["encounter_id"])
        group_signals = signal_by_encounter.get_group(encounter["encounter_id"])

        stage_entry_ts = encounter["service_end_ts"]
        if stage_name == "Documentation pending":
            stage_entry_ts = group_docs["completion_ts"].min()
        elif stage_name == "Coding pending":
            stage_entry_ts = group_docs["event_ts"].max() + timedelta(hours=2)
        elif stage_name == "Prebill edit / hold":
            stage_entry_ts = group_docs["completion_ts"].max() + timedelta(hours=4)
        elif stage_name == "Ready to final bill":
            stage_entry_ts = group_docs["completion_ts"].max() + timedelta(hours=1)
        elif stage_name == "Correction / rebill pending":
            stage_entry_ts = encounter["final_bill_datetime"] + timedelta(days=2)

        active_exception = queue_name != ""
        current_owner = queue_definitions[queue_name]["accountable_owner"] if active_exception else ""
        supporting_owner = queue_definitions[queue_name]["supporting_owner"] if active_exception else ""
        escalation_owner = queue_definitions[queue_name]["escalation_owner"] if active_exception else ""
        days_open = int(workflow_profile["current_stage_age_days"])
        recoverability_state = _recoverability_for_context(
            stage_name,
            encounter,
            pd.Timestamp(stage_entry_ts),
            days_open,
        )
        rows.append(
            {
                "account_status_id": f"CAS-{encounter['account_id']}",
                "claim_id": f"CLM-{encounter['account_id']}",
                "encounter_id": encounter["encounter_id"],
                "account_id": encounter["account_id"],
                "patient_type": encounter["patient_type"],
                "department": encounter["department"],
                "service_line": encounter["service_line"],
                "payer_group": encounter["payer_group"],
                "workflow_unit_type": "account",
                "current_prebill_stage": stage_name,
                "account_status": stage_name,
                "claim_status_code": encounter["final_bill_status"],
                "billing_status_code": encounter["final_bill_status"],
                "reconciliation_status": (
                    "reconciled"
                    if stage_name in {"Final billed", "Closed / monitored through denial feedback only"}
                    else "pending"
                ),
                "current_primary_blocker_state": blocker_state,
                "current_primary_blocker_code": blocker_state.lower().replace(" ", "_").replace("/", "_"),
                "issue_domain": issue_domain,
                "root_cause_mechanism": _root_cause_for_scenario(encounter["scenario_code"]),
                "current_queue": queue_name,
                "accountable_owner": current_owner,
                "supporting_owner": supporting_owner,
                "escalation_owner": escalation_owner,
                "recoverability_status": recoverability_state,
                "policy_window_start_ts": encounter["service_end_ts"],
                "policy_window_end_ts": encounter["service_end_ts"] + timedelta(days=5),
                "claim_create_datetime": encounter["service_end_ts"] + timedelta(hours=8),
                "bill_hold_start_datetime": stage_entry_ts if stage_name == "Prebill edit / hold" else pd.NaT,
                "scrubber_release_datetime": (
                    encounter["service_end_ts"] + timedelta(days=1)
                    if stage_name in {"Ready to final bill", "Final billed"}
                    else pd.NaT
                ),
                "final_bill_datetime": encounter["final_bill_datetime"],
                "first_submit_datetime": (
                    encounter["final_bill_datetime"] + timedelta(hours=6)
                    if pd.notna(encounter["final_bill_datetime"])
                    and encounter["final_bill_status"] == "final_billed"
                    else pd.NaT
                ),
                "rebill_flag": bool(workflow_profile["rebill_flag"]),
                "corrected_claim_flag": bool(workflow_profile["corrected_claim_flag"]),
                "current_flag": True,
                "current_queue_active_flag": active_exception,
                "active_issue_tag_count": int(
                    max(1, group_docs["documentation_gap_type"].replace("", pd.NA).notna().sum())
                    + group_signals["non_billable_candidate_flag"].sum()
                )
                if active_exception
                else int(group_signals["non_billable_candidate_flag"].sum()),
                "stage_age_days": max(days_open, 0),
                "evidence_completeness_status": (
                    "complete" if bool(group_docs["supports_charge_flag"].all()) else "incomplete"
                ),
            }
        )

    df = pd.DataFrame(rows).sort_values("claim_id").reset_index(drop=True)
    for column in (
        "policy_window_start_ts",
        "policy_window_end_ts",
        "claim_create_datetime",
        "bill_hold_start_datetime",
        "scrubber_release_datetime",
        "final_bill_datetime",
        "first_submit_datetime",
    ):
        df[column] = pd.to_datetime(df[column])
    return df


def write_claims_account_status_parquet(repo_root: Path | None = None) -> Path:
    df = generate_claims_account_status_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_claims_account_status_parquet()


if __name__ == "__main__":
    main()
