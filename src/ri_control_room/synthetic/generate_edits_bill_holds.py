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


OUTPUT_FILENAME = "edits_bill_holds.parquet"


def _load_required_tables(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    claim_lines_path = processed_dir / CLAIM_LINES_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    if not claim_lines_path.exists():
        write_claim_lines_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    return pd.read_parquet(claim_lines_path), pd.read_parquet(status_path)


def generate_edits_bill_holds_df(repo_root: Path | None = None) -> pd.DataFrame:
    claim_lines, statuses = _load_required_tables(repo_root)
    status_lookup = statuses.set_index("encounter_id").to_dict("index")
    rows: list[dict[str, object]] = []

    active_stage_encounters = statuses[
        statuses["current_prebill_stage"] == "Prebill edit / hold"
    ]["encounter_id"]
    for encounter_id in active_stage_encounters:
        status = status_lookup[encounter_id]
        claim_line = claim_lines.loc[claim_lines["encounter_id"] == encounter_id].head(1)
        if claim_line.empty:
            continue
        line = claim_line.iloc[0]
        rows.append(
            {
                "edit_id": f"EDIT-{line['claim_line_id']}",
                "claim_id": status["claim_id"],
                "encounter_id": encounter_id,
                "issue_domain": status["issue_domain"],
                "edit_type": "modifier_edit",
                "opened_datetime": status["claim_create_datetime"] + timedelta(hours=8),
                "resolved_datetime": pd.NaT,
                "age_days": max(int(status["stage_age_days"]), 1),
                "current_owner_team": status["accountable_owner"],
                "resolution_status": "open",
                "current_primary_blocker_state": status["current_primary_blocker_state"],
                "claim_line_id": line["claim_line_id"],
                "modifier_related_flag": True,
                "preventable_flag": True,
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "edit_id"]).reset_index(drop=True)
    if not df.empty:
        df["opened_datetime"] = pd.to_datetime(df["opened_datetime"])
        df["resolved_datetime"] = pd.to_datetime(df["resolved_datetime"])
    return df


def write_edits_bill_holds_parquet(repo_root: Path | None = None) -> Path:
    df = generate_edits_bill_holds_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_edits_bill_holds_parquet()


if __name__ == "__main__":
    main()
