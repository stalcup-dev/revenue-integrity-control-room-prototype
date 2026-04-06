from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_existing_validation_tables

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "encounters": (
        "encounter_id",
        "department",
        "service_line",
        "scenario_code",
        "service_end_ts",
        "final_bill_datetime",
    ),
    "claims_or_account_status": (
        "account_status_id",
        "encounter_id",
        "current_prebill_stage",
        "issue_domain",
        "current_primary_blocker_state",
        "current_queue_active_flag",
        "recoverability_status",
    ),
    "documentation_events": (
        "documentation_event_id",
        "encounter_id",
        "order_id",
        "documentation_status",
        "supports_charge_flag",
        "documentation_gap_type",
    ),
    "upstream_activity_signals": (
        "activity_signal_id",
        "encounter_id",
        "order_id",
        "documentation_event_id",
        "activity_description",
        "signal_basis",
        "performed_flag",
    ),
    "charge_events": (
        "charge_event_id",
        "encounter_id",
        "activity_signal_id",
        "charge_code",
        "charge_status",
        "gross_charge_amount",
    ),
    "expected_charge_opportunities": (
        "expected_opportunity_id",
        "encounter_id",
        "documentation_event_id",
        "activity_signal_id",
        "expected_facility_charge_opportunity",
        "opportunity_status",
        "recoverability_status",
        "documented_performed_activity_flag",
    ),
    "exception_queue": (
        "queue_item_id",
        "account_status_id",
        "encounter_id",
        "current_prebill_stage",
        "current_queue",
        "current_primary_blocker_state",
        "accountable_owner",
        "recoverability_status",
    ),
    "queue_history": (
        "queue_history_id",
        "encounter_id",
        "current_queue",
        "prior_queue",
        "reroute_count",
        "stage_transition_path",
    ),
    "intervention_tracking": (
        "intervention_tracking_id",
        "queue_item_id",
        "encounter_id",
        "intervention_owner",
        "checkpoint_status",
        "baseline_metric",
        "current_metric",
        "hold_expand_revise_recommendation",
    ),
    "kpi_snapshot": (
        "record_type",
        "snapshot_ts",
        "setting_name",
        "kpi_name",
        "numerator_value",
        "denominator_value",
        "kpi_value",
    ),
}

UNIQUE_KEYS: dict[str, tuple[str, ...]] = {
    "encounters": ("encounter_id",),
    "claims_or_account_status": ("account_status_id",),
    "documentation_events": ("documentation_event_id",),
    "upstream_activity_signals": ("activity_signal_id",),
    "charge_events": ("charge_event_id",),
    "expected_charge_opportunities": ("expected_opportunity_id",),
    "exception_queue": ("queue_item_id",),
    "queue_history": ("queue_history_id",),
    "intervention_tracking": ("intervention_tracking_id",),
}

NON_NULL_FIELDS: dict[str, tuple[str, ...]] = {
    "encounters": ("encounter_id", "department", "scenario_code", "service_end_ts"),
    "claims_or_account_status": (
        "account_status_id",
        "encounter_id",
        "current_prebill_stage",
        "issue_domain",
        "recoverability_status",
    ),
    "documentation_events": (
        "documentation_event_id",
        "encounter_id",
        "documentation_status",
    ),
    "upstream_activity_signals": (
        "activity_signal_id",
        "encounter_id",
        "activity_description",
        "signal_basis",
    ),
    "charge_events": (
        "charge_event_id",
        "encounter_id",
        "charge_status",
        "gross_charge_amount",
    ),
    "expected_charge_opportunities": (
        "expected_opportunity_id",
        "encounter_id",
        "expected_facility_charge_opportunity",
        "opportunity_status",
        "recoverability_status",
    ),
    "exception_queue": (
        "queue_item_id",
        "account_status_id",
        "encounter_id",
        "current_queue",
        "accountable_owner",
        "recoverability_status",
    ),
    "queue_history": (
        "queue_history_id",
        "encounter_id",
        "current_queue",
        "reroute_count",
    ),
    "intervention_tracking": (
        "intervention_tracking_id",
        "queue_item_id",
        "encounter_id",
        "intervention_owner",
        "checkpoint_status",
        "hold_expand_revise_recommendation",
    ),
    "kpi_snapshot": ("record_type", "snapshot_ts", "setting_name", "kpi_name"),
}


def refresh_validation_outputs(repo_root: Path | None = None) -> Path:
    from ri_control_room.build_pipeline import build_operating_artifacts

    return build_operating_artifacts(repo_root)


def load_validation_tables(repo_root: Path | None = None) -> dict[str, pd.DataFrame]:
    return load_existing_validation_tables(repo_root)


def _result_row(
    dataset: str,
    check_name: str,
    passed: bool,
    rows_examined: int,
    failure_count: int,
    detail: str,
) -> dict[str, object]:
    return {
        "dataset": dataset,
        "check_name": check_name,
        "passed": bool(passed),
        "rows_examined": int(rows_examined),
        "failure_count": int(failure_count),
        "detail": detail,
    }


def run_schema_checks(repo_root: Path | None = None) -> pd.DataFrame:
    tables = load_validation_tables(repo_root)
    results: list[dict[str, object]] = []

    for dataset, frame in tables.items():
        row_count = int(len(frame))
        results.append(
            _result_row(
                dataset,
                "non_empty",
                row_count > 0,
                row_count,
                0 if row_count > 0 else 1,
                "Output contains rows." if row_count > 0 else "Output is empty.",
            )
        )

        required_columns = REQUIRED_COLUMNS[dataset]
        missing_columns = [column for column in required_columns if column not in frame.columns]
        results.append(
            _result_row(
                dataset,
                "required_columns_present",
                not missing_columns,
                row_count,
                len(missing_columns),
                "All required columns present."
                if not missing_columns
                else "Missing columns: " + ", ".join(missing_columns),
            )
        )

        unique_key = UNIQUE_KEYS.get(dataset, ())
        duplicate_count = 0
        if unique_key and all(column in frame.columns for column in unique_key):
            duplicate_count = int(frame.duplicated(list(unique_key)).sum())
        results.append(
            _result_row(
                dataset,
                "key_uniqueness",
                duplicate_count == 0,
                row_count,
                duplicate_count,
                "Key columns are unique."
                if duplicate_count == 0
                else "Duplicate key rows detected for " + ", ".join(unique_key),
            )
        )

        required_non_null = NON_NULL_FIELDS[dataset]
        null_failure_count = 0
        if all(column in frame.columns for column in required_non_null):
            null_failure_count = int(frame[list(required_non_null)].isna().any(axis=1).sum())
        results.append(
            _result_row(
                dataset,
                "required_non_null_fields",
                null_failure_count == 0,
                row_count,
                null_failure_count,
                "Required fields are populated."
                if null_failure_count == 0
                else "Nulls found in required fields: " + ", ".join(required_non_null),
            )
        )

    return pd.DataFrame(results).sort_values(
        ["passed", "dataset", "check_name"],
        ascending=[True, True, True],
    ).reset_index(drop=True)


def assert_schema_checks_pass(repo_root: Path | None = None) -> pd.DataFrame:
    results = run_schema_checks(repo_root)
    failures = results.loc[~results["passed"]]
    if not failures.empty:
        failure_summary = " | ".join(
            f"{row.dataset}:{row.check_name}:{row.detail}" for row in failures.itertuples()
        )
        raise AssertionError("Schema checks failed: " + failure_summary)
    return results
