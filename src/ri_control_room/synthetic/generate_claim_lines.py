from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.synthetic.generate_charge_events import (
    OUTPUT_FILENAME as CHARGE_EVENTS_FILENAME,
    write_charge_events_parquet,
)
from ri_control_room.synthetic.generate_claims_account_status import (
    OUTPUT_FILENAME as STATUS_FILENAME,
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_encounters import get_processed_dir


OUTPUT_FILENAME = "claim_lines.parquet"


def _load_required_tables(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    charge_path = processed_dir / CHARGE_EVENTS_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    if not charge_path.exists():
        write_charge_events_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    return pd.read_parquet(charge_path), pd.read_parquet(status_path)


def generate_claim_lines_df(repo_root: Path | None = None) -> pd.DataFrame:
    charge_events, statuses = _load_required_tables(repo_root)
    status_lookup = statuses.set_index("encounter_id").to_dict("index")
    rows: list[dict[str, object]] = []

    for _, charge in charge_events.iterrows():
        status = status_lookup[charge["encounter_id"]]
        stage_name = status["current_prebill_stage"]
        if charge["charge_status"] == "suppressed_nonbillable":
            continue

        line_status = "prebill"
        if stage_name == "Prebill edit / hold":
            line_status = "held"
        elif stage_name in {"Final billed", "Closed / monitored through denial feedback only"}:
            line_status = "billed"
        elif stage_name == "Correction / rebill pending":
            line_status = "corrected"
        elif stage_name == "Ready to final bill":
            line_status = "ready"

        rows.append(
            {
                "claim_line_id": f"CL-{charge['charge_event_id']}",
                "claim_id": charge["claim_id"],
                "encounter_id": charge["encounter_id"],
                "account_id": charge["account_id"],
                "charge_event_id": charge["charge_event_id"],
                "department": charge["department"],
                "service_line": charge["service_line"],
                "line_status": line_status,
                "bill_type": "131",
                "line_code": charge["charge_code"],
                "modifier_code": "" if stage_name != "Prebill edit / hold" else "MODCHK",
                "billed_units": charge["units"],
                "billed_amount": charge["gross_charge_amount"],
                "final_billed_flag": stage_name == "Final billed",
                "bill_drop_datetime": (
                    charge["charge_post_ts"] + timedelta(hours=12)
                    if stage_name in {"Final billed", "Correction / rebill pending"}
                    else pd.NaT
                ),
            }
        )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "claim_line_id"]).reset_index(drop=True)
    if not df.empty:
        df["bill_drop_datetime"] = pd.to_datetime(df["bill_drop_datetime"])
    return df


def write_claim_lines_parquet(repo_root: Path | None = None) -> Path:
    df = generate_claim_lines_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_claim_lines_parquet()


if __name__ == "__main__":
    main()
