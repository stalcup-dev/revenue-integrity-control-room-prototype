from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.synthetic.generate_claim_lines import (
    OUTPUT_FILENAME as CLAIM_LINES_FILENAME,
    write_claim_lines_parquet,
)
from ri_control_room.synthetic.generate_claims_account_status import (
    OUTPUT_FILENAME as STATUS_FILENAME,
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_encounters import get_processed_dir


OUTPUT_FILENAME = "corrections_rebills.parquet"


def _load_required_tables(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    claim_lines_path = processed_dir / CLAIM_LINES_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    if not claim_lines_path.exists():
        write_claim_lines_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    return pd.read_parquet(claim_lines_path), pd.read_parquet(status_path)


def generate_corrections_rebills_df(repo_root: Path | None = None) -> pd.DataFrame:
    claim_lines, statuses = _load_required_tables(repo_root)
    rows: list[dict[str, object]] = []

    correction_cases = statuses.loc[
        statuses["current_prebill_stage"] == "Correction / rebill pending"
    ].copy()
    for _, status in correction_cases.iterrows():
        claim_line = claim_lines.loc[claim_lines["encounter_id"] == status["encounter_id"]].head(1)
        if claim_line.empty or pd.isna(status["final_bill_datetime"]):
            continue

        line = claim_line.iloc[0]
        correction_open_datetime = pd.Timestamp(status["final_bill_datetime"]) + timedelta(days=1)
        last_activity_datetime = correction_open_datetime + timedelta(days=2)
        rows.append(
            {
                "correction_id": f"CRB-{status['claim_id']}",
                "claim_id": status["claim_id"],
                "account_id": status["account_id"],
                "encounter_id": status["encounter_id"],
                "claim_line_id": line["claim_line_id"],
                "correction_type": "late_charge_correction"
                if status["root_cause_mechanism"] == "Workflow / handoff"
                else "technical_rebill_review",
                "correction_open_datetime": correction_open_datetime,
                "last_activity_datetime": last_activity_datetime,
                "correction_close_datetime": pd.NaT,
                "turnaround_days": float((last_activity_datetime - correction_open_datetime).days),
                "outcome_status": "open_recoverable",
                "correction_reason": status["current_primary_blocker_state"],
                "source_claim_status": status["claim_status_code"],
                "rebill_required_flag": bool(status["rebill_flag"]),
                "financial_recovery_pathway": "Post-final-bill recoverable by correction / rebill",
            }
        )

    monitored_cases = statuses.loc[
        statuses["current_prebill_stage"] == "Closed / monitored through denial feedback only"
    ].copy()
    for _, status in monitored_cases.iterrows():
        if not bool(status.get("corrected_claim_flag", False)) or pd.isna(status["final_bill_datetime"]):
            continue

        claim_line = claim_lines.loc[claim_lines["encounter_id"] == status["encounter_id"]].head(1)
        if claim_line.empty:
            continue

        line = claim_line.iloc[0]
        correction_open_datetime = pd.Timestamp(status["final_bill_datetime"]) + timedelta(days=1)
        correction_close_datetime = correction_open_datetime + timedelta(days=4)
        rows.append(
            {
                "correction_id": f"CRB-{status['claim_id']}-HIST",
                "claim_id": status["claim_id"],
                "account_id": status["account_id"],
                "encounter_id": status["encounter_id"],
                "claim_line_id": line["claim_line_id"],
                "correction_type": "historical_support_review",
                "correction_open_datetime": correction_open_datetime,
                "last_activity_datetime": correction_close_datetime,
                "correction_close_datetime": correction_close_datetime,
                "turnaround_days": float((correction_close_datetime - correction_open_datetime).days),
                "outcome_status": "closed_monitoring_only",
                "correction_reason": status["current_primary_blocker_state"],
                "source_claim_status": status["claim_status_code"],
                "rebill_required_flag": bool(status["rebill_flag"]),
                "financial_recovery_pathway": "Financially closed but still compliance-relevant",
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "correction_id"]).reset_index(drop=True)
    for column in (
        "correction_open_datetime",
        "last_activity_datetime",
        "correction_close_datetime",
    ):
        if column in df.columns:
            df[column] = pd.to_datetime(df[column])
    return df


def write_corrections_rebills_parquet(repo_root: Path | None = None) -> Path:
    df = generate_corrections_rebills_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_corrections_rebills_parquet()


if __name__ == "__main__":
    main()
