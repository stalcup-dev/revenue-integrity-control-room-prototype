from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_validation_harness_and_manual_audit_pack() -> None:
    from ri_control_room.build_pipeline import (
        build_operating_artifacts,
        update_run_manifest_validation_status,
    )
    from ri_control_room.validation.business_rule_checks import run_business_rule_checks
    from ri_control_room.validation.manual_audit_sample import (
        AUDIT_SAMPLE_CSV_FILENAME,
        AUDIT_SAMPLE_MARKDOWN_FILENAME,
        build_manual_audit_sample_df,
    )
    from ri_control_room.validation.realism_scorecard import build_realism_scorecard
    from ri_control_room.validation.schema_checks import run_schema_checks

    manifest_path = build_operating_artifacts(ROOT)
    manifest_before = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_before["validation_status"]["overall_passed"] is None
    assert manifest_before["artifact_row_counts"]["denials_feedback.parquet"] > 0

    schema_results = run_schema_checks(ROOT)
    assert not schema_results.empty
    assert schema_results["passed"].all()

    business_results = run_business_rule_checks(ROOT)
    assert not business_results.empty
    assert business_results["passed"].all()
    realism_report = build_realism_scorecard(ROOT)
    assert realism_report["overall_status"] == "pass"
    assert set(business_results["check_name"]) >= {
        "order_only_expectation_blocked",
        "timestamp_dependency_blocked",
        "partial_documentation_not_promoted",
        "contradictory_charge_support_flagged",
        "universal_workflow_drift_blocked",
        "packaged_suppression_holds",
        "multiple_current_blockers_blocked",
        "unsupported_charge_risk_distinct_from_undercapture",
        "correction_rebill_requires_postbill_context",
        "recoverability_logic_present",
        "suppressed_billable_lookalikes_explained",
        "duplicate_transition_paths_blocked",
    }

    updated_manifest_path = update_run_manifest_validation_status(
        ROOT,
        schema_passed=bool(schema_results["passed"].all()),
        business_passed=bool(business_results["passed"].all()),
    )
    manifest_after = json.loads(updated_manifest_path.read_text(encoding="utf-8"))
    assert manifest_after["validation_status"]["overall_passed"] is True
    assert manifest_after["validation_status"]["last_validated_at_utc"] is not None
    assert manifest_after["artifact_row_counts"]["denials_feedback.parquet"] > 0

    baseline_realism_path = ROOT / "artifacts" / "realism" / "baseline_realism_report.json"
    post_tuning_realism_path = ROOT / "artifacts" / "realism" / "post_tuning_realism_report.json"
    realism_diff_path = ROOT / "artifacts" / "realism" / "realism_before_after_diff.md"
    for path in (baseline_realism_path, post_tuning_realism_path, realism_diff_path):
        assert path.exists()

    baseline_realism = json.loads(baseline_realism_path.read_text(encoding="utf-8"))
    assert baseline_realism["overall_status"] == "pass"
    assert (
        baseline_realism["dimensions"]["workflow_state_realism"]["metrics"][
            "stage_age_median_range_days"
        ]
        > 0
    )
    assert (
        baseline_realism["dimensions"]["queue_history_realism"]["metrics"][
            "routing_reason_populated_count"
        ]
        > 0
    )
    assert (
        baseline_realism["dimensions"]["financial_consequence_realism"]["metrics"][
            "late_charge_rate"
        ]
        > 0
    )
    assert (
        baseline_realism["dimensions"]["financial_consequence_realism"]["metrics"][
            "lost_dollars_after_timing_window"
        ]
        > 0
    )
    assert baseline_realism["dimensions"]["correction_history_realism"]["metrics"][
        "postbill_cases_with_correction_history"
    ] == baseline_realism["dimensions"]["correction_history_realism"]["metrics"][
        "postbill_recoverable_case_count"
    ]

    realism_diff_text = realism_diff_path.read_text(encoding="utf-8")
    assert "Resolved: Routing reasons are absent." in realism_diff_text
    assert (
        "Resolved: Stage-specific aging is effectively flat across the active workflow."
        in realism_diff_text
    )

    sample = build_manual_audit_sample_df(ROOT)
    csv_path = ROOT / "data" / "processed" / AUDIT_SAMPLE_CSV_FILENAME
    markdown_path = ROOT / "docs" / AUDIT_SAMPLE_MARKDOWN_FILENAME
    assert 15 <= len(sample) <= 25
    assert sample["encounter_id"].is_unique
    assert sample["owner_queue"].str.len().gt(0).all()
    assert sample["recoverability"].str.len().gt(0).all()
    assert sample["expected_opportunity"].str.contains("status=").all()
    assert sample["documentation_evidence"].str.contains("status=").all()
    assert sample["billed_state"].str.contains("charge_status=").all()
    assert csv_path == ROOT / "data" / "processed" / AUDIT_SAMPLE_CSV_FILENAME
    assert markdown_path == ROOT / "docs" / AUDIT_SAMPLE_MARKDOWN_FILENAME
    assert csv_path.exists()
    assert markdown_path.exists()

    csv_sample = pd.read_csv(csv_path)
    assert len(csv_sample) == len(sample)

    markdown_text = markdown_path.read_text(encoding="utf-8")
    assert "# Manual Audit Sample" in markdown_text
    assert "## OR010" in markdown_text
    assert "Audit focus" in markdown_text

    rubric_text = (ROOT / "docs" / "MANUAL_AUDIT_RUBRIC.md").read_text(encoding="utf-8")
    checklist_text = (ROOT / "docs" / "V1_VALIDATION_CHECKLIST.md").read_text(encoding="utf-8")
    assert "packaged" in rubric_text.lower()
    assert "30-day" in checklist_text.lower()
    assert "manual sampled audit review" in checklist_text.lower()


def test_validation_reads_existing_artifacts_without_rebuild() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.validation.schema_checks import run_schema_checks

    build_operating_artifacts(ROOT)
    target_path = ROOT / "data" / "processed" / "kpi_snapshot.parquet"
    backup_path = ROOT / "data" / "processed" / "kpi_snapshot.parquet.bak"
    target_path.replace(backup_path)
    try:
        try:
            run_schema_checks(ROOT)
        except FileNotFoundError as exc:
            assert "Run an explicit build first." in str(exc)
        else:
            raise AssertionError("Validation unexpectedly rebuilt missing artifacts.")
    finally:
        backup_path.replace(target_path)
