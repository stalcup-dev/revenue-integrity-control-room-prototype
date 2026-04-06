from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.build_pipeline import build_operating_artifacts
from ri_control_room.io import get_repo_root

DEFAULT_MODERATE_VOLUME_REPEATS = 4
MODERATE_VOLUME_TABLES = (
    "documentation_events",
    "claims_or_account_status",
    "expected_charge_opportunities",
    "priority_scores",
)


def _resolve_repo_root(repo_root: Path | None = None) -> Path:
    return repo_root.resolve() if repo_root is not None else get_repo_root()


def _identifier_columns(frame: pd.DataFrame) -> tuple[str, ...]:
    return tuple(
        column
        for column in frame.columns
        if (
            column.endswith("_id")
            or column in {"account_id", "claim_id", "patient_id"}
        )
        and pd.api.types.is_object_dtype(frame[column])
    )


def _datetime_columns(frame: pd.DataFrame) -> tuple[str, ...]:
    return tuple(
        column
        for column in frame.columns
        if pd.api.types.is_datetime64_any_dtype(frame[column])
    )


def _clone_frame(frame: pd.DataFrame, replica_index: int) -> pd.DataFrame:
    if replica_index == 0:
        return frame.copy()

    clone = frame.copy()
    suffix = f"-MV{replica_index + 1}"
    for column in _identifier_columns(clone):
        clone[column] = clone[column].map(
            lambda value: value if pd.isna(value) else f"{value}{suffix}"
        )

    time_offset = pd.Timedelta(days=replica_index * 2)
    for column in _datetime_columns(clone):
        clone[column] = clone[column] + time_offset

    return clone


def _rebuild_priority_rank(priority_scores: pd.DataFrame) -> pd.DataFrame:
    ranked = priority_scores.sort_values(
        ["priority_score", "estimated_gross_dollars", "encounter_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    ranked["priority_rank"] = range(1, len(ranked) + 1)
    return ranked


def build_moderate_volume_scenario_pack(
    repo_root: Path | None = None,
    repeats: int = DEFAULT_MODERATE_VOLUME_REPEATS,
) -> dict[str, pd.DataFrame]:
    root = _resolve_repo_root(repo_root)
    build_operating_artifacts(root)

    base_tables = {
        table_name: load_processed_artifact(table_name, root)
        for table_name in MODERATE_VOLUME_TABLES
    }
    packed_tables: dict[str, pd.DataFrame] = {}
    for table_name, frame in base_tables.items():
        replicas = [_clone_frame(frame, replica_index) for replica_index in range(repeats)]
        packed = pd.concat(replicas, ignore_index=True)
        packed_tables[table_name] = packed

    packed_tables["priority_scores"] = _rebuild_priority_rank(packed_tables["priority_scores"])
    return packed_tables
