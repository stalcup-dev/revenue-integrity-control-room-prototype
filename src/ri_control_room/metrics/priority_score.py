from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.logic.build_exception_queue import (
    OUTPUT_FILENAME as EXCEPTION_QUEUE_FILENAME,
    write_exception_queue_parquet,
)
from ri_control_room.logic.build_queue_history import (
    OUTPUT_FILENAME as QUEUE_HISTORY_FILENAME,
    latest_queue_history_rows,
    write_queue_history_parquet,
)
from ri_control_room.synthetic.generate_charge_events import (
    OUTPUT_FILENAME as CHARGE_EVENTS_FILENAME,
    write_charge_events_parquet,
)
from ri_control_room.synthetic.generate_encounters import get_processed_dir


OUTPUT_FILENAME = "priority_scores.parquet"
REDUCED_V1_PRIORITY_FORMULA = (
    "100 * (0.50 * normalized_recoverable_dollars + "
    "0.30 * department_repeat_exception_rate + 0.20 * aging_severity)"
)
PRIORITY_SCORE_VERSION = "reduced_v1"


def _load_inputs(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    exception_queue_path = processed_dir / EXCEPTION_QUEUE_FILENAME
    queue_history_path = processed_dir / QUEUE_HISTORY_FILENAME
    charge_events_path = processed_dir / CHARGE_EVENTS_FILENAME

    if not exception_queue_path.exists():
        write_exception_queue_parquet(repo_root)
    if not queue_history_path.exists():
        write_queue_history_parquet(repo_root)
    if not charge_events_path.exists():
        write_charge_events_parquet(repo_root)

    return (
        pd.read_parquet(exception_queue_path),
        pd.read_parquet(queue_history_path),
        pd.read_parquet(charge_events_path),
    )


def _build_estimated_dollars(
    exception_queue: pd.DataFrame,
    charge_events: pd.DataFrame,
) -> pd.DataFrame:
    eligible_charge_events = charge_events.loc[
        charge_events["charge_status"] != "suppressed_nonbillable"
    ].copy()
    encounter_dollars = (
        eligible_charge_events.groupby(["encounter_id", "department"], as_index=False)
        .agg(estimated_gross_dollars=("gross_charge_amount", "sum"))
    )
    department_defaults = (
        encounter_dollars.groupby("department", as_index=False)
        .agg(department_default_gross_dollars=("estimated_gross_dollars", "median"))
    )

    merged = (
        exception_queue.merge(
            encounter_dollars[["encounter_id", "estimated_gross_dollars"]],
            on="encounter_id",
            how="left",
        )
        .merge(
            department_defaults,
            on="department",
            how="left",
        )
    )
    merged["estimated_gross_dollars"] = merged["estimated_gross_dollars"].fillna(
        merged["department_default_gross_dollars"]
    )
    merged["estimated_gross_dollars"] = merged["estimated_gross_dollars"].fillna(0.0)
    return merged


def compute_reduced_v1_priority_score(
    normalized_recoverable_dollars: float,
    department_repeat_exception_rate: float,
    aging_severity: float,
) -> float:
    score = 100 * (
        0.50 * normalized_recoverable_dollars
        + 0.30 * department_repeat_exception_rate
        + 0.20 * aging_severity
    )
    return round(score, 2)


def build_priority_scores_df(repo_root: Path | None = None) -> pd.DataFrame:
    exception_queue, queue_history, charge_events = _load_inputs(repo_root)
    if exception_queue.empty:
        return exception_queue.copy()

    scored = _build_estimated_dollars(exception_queue, charge_events)
    reroute_flags = latest_queue_history_rows(queue_history)[["encounter_id", "reroute_count"]].copy()
    reroute_flags["repeat_exception_flag"] = reroute_flags["reroute_count"] > 0
    scored = scored.merge(
        reroute_flags[["encounter_id", "reroute_count", "repeat_exception_flag"]],
        on="encounter_id",
        how="left",
    )
    scored["reroute_count"] = scored["reroute_count"].fillna(0).astype(int)
    scored["repeat_exception_flag"] = scored["repeat_exception_flag"].fillna(False).astype(bool)

    department_repeat_rates = (
        scored.groupby("department", as_index=False)
        .agg(
            department_repeat_exception_numerator=("repeat_exception_flag", "sum"),
            department_repeat_exception_denominator=("queue_item_id", "size"),
        )
    )
    department_repeat_rates["department_repeat_exception_rate"] = (
        department_repeat_rates["department_repeat_exception_numerator"]
        / department_repeat_rates["department_repeat_exception_denominator"]
    )
    scored = scored.merge(
        department_repeat_rates[
            [
                "department",
                "department_repeat_exception_numerator",
                "department_repeat_exception_denominator",
                "department_repeat_exception_rate",
            ]
        ],
        on="department",
        how="left",
    )

    max_dollars = float(scored["estimated_gross_dollars"].max() or 0.0)
    if max_dollars <= 0:
        scored["normalized_recoverable_dollars"] = 0.0
    else:
        scored["normalized_recoverable_dollars"] = scored["estimated_gross_dollars"] / max_dollars

    scored["aging_severity"] = (
        scored["stage_age_days"] / scored["overdue_threshold_days"].replace(0, pd.NA)
    ).fillna(0.0)
    scored["aging_severity"] = scored["aging_severity"].clip(lower=0.0, upper=1.0)

    scored["priority_score"] = scored.apply(
        lambda row: compute_reduced_v1_priority_score(
            float(row["normalized_recoverable_dollars"]),
            float(row["department_repeat_exception_rate"]),
            float(row["aging_severity"]),
        ),
        axis=1,
    )
    scored["priority_rank"] = (
        scored["priority_score"].rank(method="dense", ascending=False).astype(int)
    )
    scored["priority_score_version"] = PRIORITY_SCORE_VERSION
    scored["priority_formula"] = REDUCED_V1_PRIORITY_FORMULA
    return scored.sort_values(
        ["priority_score", "estimated_gross_dollars", "encounter_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def write_priority_scores_parquet(repo_root: Path | None = None) -> Path:
    df = build_priority_scores_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_priority_scores_parquet()


if __name__ == "__main__":
    main()
