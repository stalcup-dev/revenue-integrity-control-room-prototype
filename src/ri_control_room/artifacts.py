from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ri_control_room.io import get_repo_root
from ri_control_room.synthetic.generate_encounters import get_processed_dir

PRIORITY_SCORES_FILENAME = "priority_scores.parquet"
RUN_MANIFEST_FILENAME = "run_manifest.json"
MANUAL_AUDIT_SAMPLE_CSV_FILENAME = "manual_audit_sample.csv"
MANUAL_AUDIT_SAMPLE_MARKDOWN_FILENAME = "MANUAL_AUDIT_SAMPLE.md"

PROCESSED_ARTIFACT_FILENAMES: dict[str, str] = {
    "encounters": "encounters.parquet",
    "orders": "orders.parquet",
    "documentation_events": "documentation_events.parquet",
    "upstream_activity_signals": "upstream_activity_signals.parquet",
    "claims_or_account_status": "claims_or_account_status.parquet",
    "charge_events": "charge_events.parquet",
    "claim_lines": "claim_lines.parquet",
    "edits_bill_holds": "edits_bill_holds.parquet",
    "corrections_rebills": "corrections_rebills.parquet",
    "denials_feedback": "denials_feedback.parquet",
    "expected_charge_opportunities": "expected_charge_opportunities.parquet",
    "exception_queue": "exception_queue.parquet",
    "queue_history": "queue_history.parquet",
    "priority_scores": PRIORITY_SCORES_FILENAME,
    "intervention_tracking": "intervention_tracking.parquet",
    "kpi_snapshot": "kpi_snapshot.parquet",
    "manual_audit_sample": MANUAL_AUDIT_SAMPLE_CSV_FILENAME,
    "run_manifest": RUN_MANIFEST_FILENAME,
}

VALIDATION_TABLE_NAMES: tuple[str, ...] = (
    "encounters",
    "claims_or_account_status",
    "documentation_events",
    "upstream_activity_signals",
    "charge_events",
    "expected_charge_opportunities",
    "exception_queue",
    "queue_history",
    "intervention_tracking",
    "kpi_snapshot",
)


def resolve_repo_root(repo_root: Path | None = None) -> Path:
    return repo_root.resolve() if repo_root is not None else get_repo_root()


def get_docs_dir(repo_root: Path | None = None) -> Path:
    return resolve_repo_root(repo_root) / "docs"


def get_processed_artifact_path(artifact_name: str, repo_root: Path | None = None) -> Path:
    try:
        filename = PROCESSED_ARTIFACT_FILENAMES[artifact_name]
    except KeyError as exc:
        raise KeyError(f"Unknown processed artifact: {artifact_name}") from exc
    return get_processed_dir(resolve_repo_root(repo_root)) / filename


def get_manual_audit_markdown_path(repo_root: Path | None = None) -> Path:
    return get_docs_dir(repo_root) / MANUAL_AUDIT_SAMPLE_MARKDOWN_FILENAME


def _require_existing_artifact(path: Path, description: str) -> Path:
    if path.exists():
        return path
    raise FileNotFoundError(
        f"Missing required artifact for {description}: {path}. "
        "Run an explicit build first."
    )


def load_processed_artifact(artifact_name: str, repo_root: Path | None = None) -> pd.DataFrame:
    path = _require_existing_artifact(
        get_processed_artifact_path(artifact_name, repo_root),
        artifact_name,
    )
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported artifact format for {path.name}")


def load_existing_validation_tables(repo_root: Path | None = None) -> dict[str, pd.DataFrame]:
    return {
        table_name: load_processed_artifact(table_name, repo_root)
        for table_name in VALIDATION_TABLE_NAMES
    }


def load_existing_priority_scores(repo_root: Path | None = None) -> pd.DataFrame:
    return load_processed_artifact("priority_scores", repo_root)


def read_run_manifest(repo_root: Path | None = None) -> dict[str, object]:
    path = _require_existing_artifact(
        get_processed_artifact_path("run_manifest", repo_root),
        "run_manifest",
    )
    return json.loads(path.read_text(encoding="utf-8"))
