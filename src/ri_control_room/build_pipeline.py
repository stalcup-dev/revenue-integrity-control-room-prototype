from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import (
    PROCESSED_ARTIFACT_FILENAMES,
    get_processed_artifact_path,
    get_processed_dir,
    read_run_manifest,
    resolve_repo_root,
)
from ri_control_room.logic.build_exception_queue import write_exception_queue_parquet
from ri_control_room.logic.build_queue_history import write_queue_history_parquet
from ri_control_room.logic.derive_expected_charge_opportunities import (
    write_expected_charge_opportunities_parquet,
)
from ri_control_room.metrics.kpis import write_kpi_snapshot_parquet
from ri_control_room.metrics.priority_score import (
    PRIORITY_SCORE_VERSION,
    write_priority_scores_parquet,
)
from ri_control_room.synthetic.generate_charge_events import write_charge_events_parquet
from ri_control_room.synthetic.generate_claim_lines import write_claim_lines_parquet
from ri_control_room.synthetic.generate_claims_account_status import (
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_corrections_rebills import (
    write_corrections_rebills_parquet,
)
from ri_control_room.synthetic.generate_documentation_events import (
    write_documentation_events_parquet,
)
from ri_control_room.synthetic.generate_denials_feedback import (
    write_denials_feedback_parquet,
)
from ri_control_room.synthetic.generate_edits_bill_holds import (
    write_edits_bill_holds_parquet,
)
from ri_control_room.synthetic.generate_encounters import write_encounters_parquet
from ri_control_room.synthetic.generate_intervention_tracking import (
    write_intervention_tracking_parquet,
)
from ri_control_room.synthetic.generate_orders import write_orders_parquet
from ri_control_room.synthetic.generate_upstream_activity_signals import (
    write_upstream_activity_signals_parquet,
)
from ri_control_room.validation.manual_audit_sample import export_manual_audit_pack
from ri_control_room.validation.realism_scorecard import (
    build_department_story_report,
    build_ops_mix_report,
    build_realism_scorecard,
    build_suppression_balance_report,
    build_transition_ledger_report,
    build_transition_ledger_snapshot_from_tables,
    write_department_story_before_after_diff,
    write_department_story_report,
    write_ops_mix_before_after_diff,
    write_ops_mix_report,
    write_realism_before_after_diff,
    write_realism_report,
    write_suppression_balance_before_after_diff,
    write_suppression_balance_report,
    write_transition_ledger_before_after_diff,
    write_transition_ledger_report,
)

SYNTHETIC_DATA_VERSION = "deterministic_v1"
RULESET_VERSION = "deterministic_v1"
SCHEMA_VERSION = "v1"

BUILD_SEQUENCE = (
    write_encounters_parquet,
    write_orders_parquet,
    write_documentation_events_parquet,
    write_upstream_activity_signals_parquet,
    write_claims_account_status_parquet,
    write_charge_events_parquet,
    write_claim_lines_parquet,
    write_edits_bill_holds_parquet,
    write_corrections_rebills_parquet,
    write_expected_charge_opportunities_parquet,
    write_denials_feedback_parquet,
    write_exception_queue_parquet,
    write_queue_history_parquet,
    write_priority_scores_parquet,
    write_intervention_tracking_parquet,
    write_kpi_snapshot_parquet,
)

MANIFEST_ARTIFACT_NAMES: tuple[str, ...] = (
    "encounters",
    "orders",
    "documentation_events",
    "upstream_activity_signals",
    "claims_or_account_status",
    "charge_events",
    "claim_lines",
    "edits_bill_holds",
    "corrections_rebills",
    "denials_feedback",
    "expected_charge_opportunities",
    "exception_queue",
    "queue_history",
    "priority_scores",
    "intervention_tracking",
    "kpi_snapshot",
    "manual_audit_sample",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _artifact_row_counts(repo_root: Path | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for artifact_name in MANIFEST_ARTIFACT_NAMES:
        path = get_processed_artifact_path(artifact_name, repo_root)
        if path.suffix == ".parquet":
            counts[PROCESSED_ARTIFACT_FILENAMES[artifact_name]] = int(len(pd.read_parquet(path)))
        elif path.suffix == ".csv":
            counts[PROCESSED_ARTIFACT_FILENAMES[artifact_name]] = int(len(pd.read_csv(path)))
    return counts


def _write_manifest(
    repo_root: Path | None,
    *,
    run_timestamp_utc: str,
    row_counts: dict[str, int],
    validation_status: dict[str, object],
) -> Path:
    manifest = {
        "run_timestamp_utc": run_timestamp_utc,
        "artifact_row_counts": row_counts,
        "validation_status": validation_status,
        "seed": None,
        "synthetic_data_version": SYNTHETIC_DATA_VERSION,
        "ruleset_version": RULESET_VERSION,
        "schema_version": SCHEMA_VERSION,
        "priority_score_version": PRIORITY_SCORE_VERSION,
    }
    manifest_path = get_processed_artifact_path("run_manifest", repo_root)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def _capture_transition_ledger_baseline(root: Path) -> dict[str, object]:
    required_artifacts = ("exception_queue", "queue_history", "encounters")
    if any(not get_processed_artifact_path(name, root).exists() for name in required_artifacts):
        return {}

    intervention_path = get_processed_artifact_path("intervention_tracking", root)
    intervention_tracking = (
        pd.read_parquet(intervention_path) if intervention_path.exists() else pd.DataFrame()
    )
    return build_transition_ledger_snapshot_from_tables(
        queue=pd.read_parquet(get_processed_artifact_path("exception_queue", root)),
        queue_history=pd.read_parquet(get_processed_artifact_path("queue_history", root)),
        intervention_tracking=intervention_tracking,
        encounters=pd.read_parquet(get_processed_artifact_path("encounters", root)),
    )


def _read_json_if_exists(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _publish_realism_artifacts(root: Path) -> None:
    realism_dir = root / "artifacts" / "realism"
    prior_baseline_report = _read_json_if_exists(
        realism_dir / "baseline_realism_snapshot.json"
    ) or _read_json_if_exists(realism_dir / "baseline_realism_report.json")
    department_story_baseline = _read_json_if_exists(
        realism_dir / "department_story_baseline_snapshot.json"
    )
    suppression_balance_baseline = _read_json_if_exists(
        realism_dir / "suppression_balance_baseline_snapshot.json"
    )
    ops_mix_baseline = _read_json_if_exists(realism_dir / "ops_mix_baseline_snapshot.json")

    realism_report = build_realism_scorecard(root)
    department_story_report = build_department_story_report(root)
    suppression_balance_report = build_suppression_balance_report(root)
    ops_mix_report = build_ops_mix_report(root)

    write_realism_report(
        realism_report,
        report_basename="baseline_realism_report",
        repo_root=root,
        title="Baseline Realism Report",
    )
    write_realism_report(
        realism_report,
        report_basename="post_tuning_realism_report",
        repo_root=root,
        title="Post Tuning Realism Report",
    )
    write_realism_before_after_diff(
        prior_baseline_report or realism_report,
        realism_report,
        repo_root=root,
    )

    write_department_story_report(
        department_story_report,
        report_basename="department_story_report",
        repo_root=root,
        title="Department Story Report",
    )
    write_suppression_balance_report(
        suppression_balance_report,
        report_basename="suppression_balance_report",
        repo_root=root,
        title="Suppression Balance Report",
    )
    write_ops_mix_report(
        ops_mix_report,
        report_basename="ops_mix_report",
        repo_root=root,
        title="Ops Mix Report",
    )
    if department_story_baseline:
        write_department_story_before_after_diff(
            department_story_baseline,
            department_story_report,
            repo_root=root,
        )
    if suppression_balance_baseline:
        write_suppression_balance_before_after_diff(
            suppression_balance_baseline,
            suppression_balance_report,
            repo_root=root,
        )
    if ops_mix_baseline:
        write_ops_mix_before_after_diff(
            ops_mix_baseline,
            ops_mix_report,
            repo_root=root,
        )


def build_operating_artifacts(repo_root: Path | None = None) -> Path:
    root = resolve_repo_root(repo_root)
    get_processed_dir(root)
    baseline_snapshot = _capture_transition_ledger_baseline(root)
    for writer in BUILD_SEQUENCE:
        writer(root)
    export_manual_audit_pack(root)
    transition_report = build_transition_ledger_report(root)
    write_transition_ledger_report(transition_report, repo_root=root)
    diff_path = root / "artifacts" / "realism" / "transition_ledger_before_after_diff.md"
    if baseline_snapshot != transition_report["transition_ledger_snapshot"] or not diff_path.exists():
        write_transition_ledger_before_after_diff(
            baseline_snapshot,
            transition_report,
            repo_root=root,
        )
    _publish_realism_artifacts(root)
    return _write_manifest(
        root,
        run_timestamp_utc=_utc_now_iso(),
        row_counts=_artifact_row_counts(root),
        validation_status={
            "last_validated_at_utc": None,
            "schema_checks_passed": None,
            "business_rule_checks_passed": None,
            "overall_passed": None,
        },
    )


def update_run_manifest_validation_status(
    repo_root: Path | None,
    *,
    schema_passed: bool,
    business_passed: bool,
) -> Path:
    root = resolve_repo_root(repo_root)
    manifest = read_run_manifest(root)
    manifest["artifact_row_counts"] = _artifact_row_counts(root)
    manifest["validation_status"] = {
        "last_validated_at_utc": _utc_now_iso(),
        "schema_checks_passed": schema_passed,
        "business_rule_checks_passed": business_passed,
        "overall_passed": schema_passed and business_passed,
    }
    manifest_path = get_processed_artifact_path("run_manifest", root)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
