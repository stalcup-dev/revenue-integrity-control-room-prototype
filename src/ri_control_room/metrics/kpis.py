from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.constants import FROZEN_V1_DEPARTMENTS
from ri_control_room.logic.build_exception_queue import derive_stage_entry_ts
from ri_control_room.logic.derive_expected_charge_opportunities import (
    OUTPUT_FILENAME as EXPECTED_OPPORTUNITIES_FILENAME,
    write_expected_charge_opportunities_parquet,
)
from ri_control_room.metrics.priority_score import build_priority_scores_df
from ri_control_room.synthetic.generate_charge_events import (
    OUTPUT_FILENAME as CHARGE_EVENTS_FILENAME,
    write_charge_events_parquet,
)
from ri_control_room.synthetic.generate_claims_account_status import (
    OUTPUT_FILENAME as STATUS_FILENAME,
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_documentation_events import (
    OUTPUT_FILENAME as DOCUMENTATION_FILENAME,
    write_documentation_events_parquet,
)
from ri_control_room.synthetic.generate_encounters import (
    OUTPUT_FILENAME as ENCOUNTERS_FILENAME,
    get_processed_dir,
    write_encounters_parquet,
)


OUTPUT_FILENAME = "kpi_snapshot.parquet"
ALL_SETTINGS_LABEL = "All frozen V1 departments"

KPI_METADATA: dict[str, dict[str, str]] = {
    "Unreconciled encounter rate": {
        "unit": "rate",
        "grain": "Encounter snapshot",
        "owner": "Revenue Integrity operations",
        "numerator_definition": (
            "Eligible chargeable encounters past the current report cutoff that remain unreconciled."
        ),
        "denominator_definition": (
            "Eligible chargeable encounters that have reached the point where reconciliation should be complete."
        ),
        "exclusions_text": (
            "Cancelled, no-show, test, training, non-chargeable, and still-too-early encounters are excluded."
        ),
        "caveats_text": (
            "Snapshot rate only. Denominator includes only encounters that should already be complete."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Late charge rate": {
        "unit": "rate",
        "grain": "Charge line",
        "owner": "Department operations with Revenue Integrity support",
        "numerator_definition": (
            "Posted charge lines entered after the governed policy window end timestamp."
        ),
        "denominator_definition": (
            "Eligible posted charge lines in scope, excluding suppressed nonbillable lines."
        ),
        "exclusions_text": (
            "Suppressed nonbillable lines, cancelled activity, tests, and approved backdated exceptions are excluded."
        ),
        "caveats_text": (
            "Do not use one universal late threshold across departments; timing follows governed policy windows."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Charge reconciliation completion within policy window": {
        "unit": "rate",
        "grain": "Encounter",
        "owner": "Revenue Integrity operations",
        "numerator_definition": (
            "Eligible chargeable encounters completed as reconciled on or before the governed policy window."
        ),
        "denominator_definition": (
            "Eligible chargeable encounters whose reconciliation outcome can be evaluated at the current cutoff."
        ),
        "exclusions_text": (
            "Cancelled, no-show, non-chargeable, test, and still-inside-window encounters are excluded."
        ),
        "caveats_text": (
            "Completion requires no active primary blocker, not just bill existence."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Time to charge entry": {
        "unit": "hours",
        "grain": "Encounter",
        "owner": "Department operations",
        "numerator_definition": (
            "Total elapsed hours from service completion to first eligible posted charge."
        ),
        "denominator_definition": (
            "Eligible chargeable encounters with at least one eligible posted charge."
        ),
        "exclusions_text": (
            "Cancelled, non-chargeable, suppressed-only, and timestamp-invalid encounters are excluded."
        ),
        "caveats_text": (
            "Average elapsed-time KPI only. It measures charge entry, not final billing."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Prebill edit aging": {
        "unit": "days",
        "grain": "Active blocker item snapshot",
        "owner": "Revenue Integrity operations",
        "numerator_definition": "Total open age in days for active prebill edit or hold blocker items.",
        "denominator_definition": "Count of active prebill edit or hold blocker items.",
        "exclusions_text": (
            "Closed edits, approved out-of-band holds, tests, and out-of-scope departments are excluded."
        ),
        "caveats_text": (
            "Snapshot aging KPI only. It does not measure turnaround for already resolved edits."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Recoverable dollars still open": {
        "unit": "dollars",
        "grain": "Active blocker item snapshot",
        "owner": "Revenue Integrity leadership",
        "numerator_definition": (
            "Estimated gross dollars on active recoverable blocker items in the current queue snapshot."
        ),
        "denominator_definition": (
            "Estimated gross dollars tied to active recoverable items plus currently identified lost items."
        ),
        "exclusions_text": (
            "Lost items, tests, out-of-scope departments, and items with no governed estimation basis are excluded."
        ),
        "caveats_text": (
            "The headline KPI value is the numerator dollars. It is gross exposure, not cash or net revenue."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Dollars already lost after timing window": {
        "unit": "dollars",
        "grain": "Encounter period total",
        "owner": "Revenue Integrity leadership",
        "numerator_definition": (
            "Estimated gross dollars tied to unresolved chargeable encounters already beyond recoverability."
        ),
        "denominator_definition": (
            "Estimated gross dollars tied to active recoverable items plus currently identified lost items."
        ),
        "exclusions_text": (
            "Suppressed nonbillable encounters, reopened items, tests, and items without governed estimation logic are excluded."
        ),
        "caveats_text": (
            "This is a governed gross-loss exposure metric. It is not denials, write-offs, or cash loss."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Department repeat exception rate": {
        "unit": "rate",
        "grain": "Active blocker item by department",
        "owner": "Department operations leader",
        "numerator_definition": (
            "Current blocker items with queue-history reroute evidence under the reduced V1 repeat rule."
        ),
        "denominator_definition": "Current active blocker items in the same department snapshot.",
        "exclusions_text": (
            "Departments with no active blocker items and blocker items lacking queue history are excluded from the rate."
        ),
        "caveats_text": (
            "Reduced V1 repeat logic uses reroute history because a separate resolved-repeat ledger is not yet modeled."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Unsupported charge rate": {
        "unit": "rate",
        "grain": "Charge line",
        "owner": "Revenue Integrity with department leadership",
        "numerator_definition": (
            "Eligible posted charge lines flagged as pending support under governed rules."
        ),
        "denominator_definition": (
            "Eligible posted charge lines in scope, excluding suppressed nonbillable lines."
        ),
        "exclusions_text": (
            "Suppressed nonbillable lines, cancelled activity, tests, and approved delayed-linkage exceptions are excluded."
        ),
        "caveats_text": (
            "Operational support-quality KPI only. It is not a fraud or intent indicator."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
    "Edit first-pass clearance rate": {
        "unit": "rate",
        "grain": "Resolved prebill edit or bill-hold item",
        "owner": "Revenue Integrity operations with billing operations support",
        "numerator_definition": (
            "Prebill edit or hold items closed without reroute, reopen, or secondary escalation."
        ),
        "denominator_definition": "Closed prebill edit or hold items in the reporting period.",
        "exclusions_text": (
            "Still-open items, cancelled closures, tests, and items without enough history to judge first-pass behavior are excluded."
        ),
        "caveats_text": (
            "This metric can be null when the current synthetic snapshot contains no resolved eligible edit closures."
        ),
        "applicable_settings": ALL_SETTINGS_LABEL,
    },
}


def _load_inputs(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    encounter_path = processed_dir / ENCOUNTERS_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    documentation_path = processed_dir / DOCUMENTATION_FILENAME
    charge_events_path = processed_dir / CHARGE_EVENTS_FILENAME
    expected_path = processed_dir / EXPECTED_OPPORTUNITIES_FILENAME

    if not encounter_path.exists():
        write_encounters_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    if not documentation_path.exists():
        write_documentation_events_parquet(repo_root)
    if not charge_events_path.exists():
        write_charge_events_parquet(repo_root)
    if not expected_path.exists():
        write_expected_charge_opportunities_parquet(repo_root)

    return (
        pd.read_parquet(encounter_path),
        pd.read_parquet(status_path),
        pd.read_parquet(documentation_path),
        pd.read_parquet(charge_events_path),
        pd.read_parquet(expected_path),
    )


def _safe_rate(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _safe_average(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _report_cutoff_ts(
    encounters: pd.DataFrame,
    statuses: pd.DataFrame,
    charge_events: pd.DataFrame,
    priority_scores: pd.DataFrame,
) -> pd.Timestamp:
    candidates = [
        encounters["service_end_ts"].max(),
        statuses["policy_window_end_ts"].max(),
        statuses["final_bill_datetime"].max(),
        charge_events["charge_post_ts"].max() if not charge_events.empty else pd.NaT,
        priority_scores["queue_snapshot_ts"].max() if not priority_scores.empty else pd.NaT,
    ]
    valid_candidates = [pd.Timestamp(value) for value in candidates if pd.notna(value)]
    return max(valid_candidates)


def _build_encounter_summary(
    encounters: pd.DataFrame,
    statuses: pd.DataFrame,
    documentation_events: pd.DataFrame,
    expected_opportunities: pd.DataFrame,
) -> pd.DataFrame:
    encounter_lookup = encounters.set_index("encounter_id").to_dict("index")
    documentation_groups = {
        encounter_id: group.copy()
        for encounter_id, group in documentation_events.groupby("encounter_id")
    }
    expected_by_encounter = (
        expected_opportunities.groupby("encounter_id", as_index=False)
        .agg(
            has_expected_chargeable_activity=("suppression_flag", lambda values: (~values).any()),
            has_lost_candidate_issue=(
                "opportunity_status",
                lambda values: any(
                    value in {"recoverable_missed_charge", "unsupported_charge_risk", "modifier_dependency_case"}
                    for value in values
                ),
            ),
        )
    )

    summary = statuses.merge(expected_by_encounter, on="encounter_id", how="left")
    summary["has_expected_chargeable_activity"] = (
        summary["has_expected_chargeable_activity"].fillna(False).astype(bool)
    )
    summary["has_lost_candidate_issue"] = summary["has_lost_candidate_issue"].fillna(False).astype(bool)

    completion_ts: list[pd.Timestamp | pd.NaT] = []
    completion_flag: list[bool] = []
    for _, row in summary.iterrows():
        documentation_subset = documentation_groups.get(row["encounter_id"], pd.DataFrame())
        encounter = pd.Series(encounter_lookup[row["encounter_id"]])
        stage_name = row["current_prebill_stage"]

        if row["current_queue_active_flag"]:
            completion_ts.append(pd.NaT)
            completion_flag.append(False)
            continue

        if stage_name == "Ready to final bill":
            completion_ts.append(
                derive_stage_entry_ts(stage_name, encounter, documentation_subset)
            )
            completion_flag.append(True)
            continue

        if stage_name in {"Final billed", "Closed / monitored through denial feedback only"}:
            if pd.notna(row["final_bill_datetime"]):
                completion_ts.append(pd.Timestamp(row["final_bill_datetime"]))
            else:
                completion_ts.append(
                    derive_stage_entry_ts("Ready to final bill", encounter, documentation_subset)
                )
            completion_flag.append(True)
            continue

        completion_ts.append(pd.NaT)
        completion_flag.append(False)

    summary["reconciliation_complete_ts"] = pd.to_datetime(completion_ts)
    summary["reconciliation_complete_flag"] = completion_flag
    return summary


def _department_filter(df: pd.DataFrame, setting_name: str) -> pd.DataFrame:
    if setting_name == ALL_SETTINGS_LABEL:
        return df.copy()
    return df.loc[df["department"] == setting_name].copy()


def _build_lost_dollars_frame(
    encounter_summary: pd.DataFrame,
    priority_scores: pd.DataFrame,
) -> pd.DataFrame:
    lost_candidates = encounter_summary.loc[
        encounter_summary["has_expected_chargeable_activity"]
        & encounter_summary["has_lost_candidate_issue"]
        & ~encounter_summary["current_queue_active_flag"]
        & (
            encounter_summary["recoverability_status"]
            == "Post-window financially lost"
        )
    ][["encounter_id", "department"]].copy()
    if lost_candidates.empty:
        lost_candidates["estimated_gross_dollars"] = pd.Series(dtype=float)
        return lost_candidates

    encounter_dollars = priority_scores.groupby(
        ["encounter_id", "department"], as_index=False
    ).agg(estimated_gross_dollars=("estimated_gross_dollars", "first"))
    department_defaults = priority_scores.groupby("department", as_index=False).agg(
        department_default_gross_dollars=("estimated_gross_dollars", "median")
    )
    lost_candidates = lost_candidates.merge(
        encounter_dollars,
        on=["encounter_id", "department"],
        how="left",
    ).merge(
        department_defaults,
        on="department",
        how="left",
    )
    lost_candidates["estimated_gross_dollars"] = lost_candidates["estimated_gross_dollars"].fillna(
        lost_candidates["department_default_gross_dollars"]
    )
    return lost_candidates[["encounter_id", "department", "estimated_gross_dollars"]]


def _metric_row(
    snapshot_ts: pd.Timestamp,
    setting_name: str,
    kpi_name: str,
    numerator_value: float,
    denominator_value: float,
    kpi_value: float | None,
) -> dict[str, object]:
    metadata = KPI_METADATA[kpi_name]
    return {
        "record_type": "kpi",
        "snapshot_ts": snapshot_ts,
        "setting_name": setting_name,
        "department": "" if setting_name == ALL_SETTINGS_LABEL else setting_name,
        "kpi_name": kpi_name,
        "unit": metadata["unit"],
        "grain": metadata["grain"],
        "owner": metadata["owner"],
        "numerator_definition": metadata["numerator_definition"],
        "denominator_definition": metadata["denominator_definition"],
        "exclusions_text": metadata["exclusions_text"],
        "caveats_text": metadata["caveats_text"],
        "applicable_settings": metadata["applicable_settings"],
        "numerator_value": float(numerator_value),
        "denominator_value": float(denominator_value),
        "kpi_value": kpi_value,
        "priority_score_version": "",
        "priority_formula": "",
        "queue_item_id": "",
        "claim_id": "",
        "account_id": "",
        "encounter_id": "",
        "current_queue": "",
        "recoverability_status": "",
        "estimated_gross_dollars": pd.NA,
        "normalized_recoverable_dollars": pd.NA,
        "department_repeat_exception_rate": pd.NA,
        "aging_severity": pd.NA,
        "priority_score": pd.NA,
        "priority_rank": pd.NA,
    }


def _priority_rows_for_snapshot(priority_scores: pd.DataFrame) -> pd.DataFrame:
    if priority_scores.empty:
        return pd.DataFrame()

    rows = priority_scores[
        [
            "queue_snapshot_ts",
            "department",
            "queue_item_id",
            "claim_id",
            "account_id",
            "encounter_id",
            "current_queue",
            "recoverability_status",
            "estimated_gross_dollars",
            "normalized_recoverable_dollars",
            "department_repeat_exception_rate",
            "aging_severity",
            "priority_score",
            "priority_rank",
            "priority_score_version",
            "priority_formula",
        ]
    ].copy()
    rows = rows.rename(columns={"queue_snapshot_ts": "snapshot_ts", "department": "setting_name"})
    rows["record_type"] = "priority_score"
    rows["department"] = rows["setting_name"]
    rows["kpi_name"] = "Transparent reduced V1 priority score"
    rows["unit"] = "score_0_to_100"
    rows["grain"] = "Active queue item"
    rows["owner"] = "Revenue Integrity operations"
    rows["numerator_definition"] = ""
    rows["denominator_definition"] = ""
    rows["exclusions_text"] = ""
    rows["caveats_text"] = (
        "Reduced V1 score only. Undefined components such as preventable_share, fixability_score, and sla_breach_risk are intentionally excluded."
    )
    rows["applicable_settings"] = ALL_SETTINGS_LABEL
    rows["numerator_value"] = pd.NA
    rows["denominator_value"] = pd.NA
    rows["kpi_value"] = rows["priority_score"]
    return rows


def _align_snapshot_frames(
    kpi_rows: pd.DataFrame,
    priority_rows: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    snapshot_columns = [
        "record_type",
        "snapshot_ts",
        "setting_name",
        "department",
        "kpi_name",
        "unit",
        "grain",
        "owner",
        "numerator_definition",
        "denominator_definition",
        "exclusions_text",
        "caveats_text",
        "applicable_settings",
        "numerator_value",
        "denominator_value",
        "kpi_value",
        "priority_score_version",
        "priority_formula",
        "queue_item_id",
        "claim_id",
        "account_id",
        "encounter_id",
        "current_queue",
        "recoverability_status",
        "estimated_gross_dollars",
        "normalized_recoverable_dollars",
        "department_repeat_exception_rate",
        "aging_severity",
        "priority_score",
        "priority_rank",
    ]
    numeric_columns = [
        "numerator_value",
        "denominator_value",
        "kpi_value",
        "estimated_gross_dollars",
        "normalized_recoverable_dollars",
        "department_repeat_exception_rate",
        "aging_severity",
        "priority_score",
        "priority_rank",
    ]

    left = kpi_rows.reindex(columns=snapshot_columns).copy()
    right = priority_rows.reindex(columns=snapshot_columns).copy()
    for column in numeric_columns:
        left[column] = pd.to_numeric(left[column], errors="coerce")
        right[column] = pd.to_numeric(right[column], errors="coerce")
    return left, right


def build_kpi_snapshot_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters, statuses, documentation_events, charge_events, expected_opportunities = _load_inputs(
        repo_root
    )
    priority_scores = build_priority_scores_df(repo_root)
    report_cutoff = _report_cutoff_ts(encounters, statuses, charge_events, priority_scores)
    encounter_summary = _build_encounter_summary(
        encounters,
        statuses,
        documentation_events,
        expected_opportunities,
    )
    lost_dollars = _build_lost_dollars_frame(encounter_summary, priority_scores)

    charge_lines = charge_events.merge(
        statuses[["encounter_id", "policy_window_end_ts"]],
        on="encounter_id",
        how="left",
    )
    charge_lines = charge_lines.loc[charge_lines["charge_status"] != "suppressed_nonbillable"].copy()
    charge_lines["late_charge_flag"] = charge_lines["charge_post_ts"] > charge_lines["policy_window_end_ts"]

    first_charge = (
        charge_lines.groupby("encounter_id", as_index=False)
        .agg(first_charge_post_ts=("charge_post_ts", "min"))
        .merge(encounters[["encounter_id", "department", "service_end_ts"]], on="encounter_id", how="left")
    )
    first_charge["hours_to_charge_entry"] = (
        first_charge["first_charge_post_ts"] - first_charge["service_end_ts"]
    ).dt.total_seconds() / 3600

    prebill_queue = priority_scores.loc[
        priority_scores["current_prebill_stage"] == "Prebill edit / hold"
    ].copy()
    repeat_queue = priority_scores[
        [
            "department",
            "queue_item_id",
            "repeat_exception_flag",
        ]
    ].copy()
    recoverable_queue = priority_scores.loc[
        priority_scores["recoverability_status"].isin(
            {
                "Pre-final-bill recoverable",
                "Post-final-bill recoverable by correction / rebill",
            }
        )
    ].copy()

    settings = [ALL_SETTINGS_LABEL, *FROZEN_V1_DEPARTMENTS]
    rows: list[dict[str, object]] = []
    for setting_name in settings:
        encounter_scope = _department_filter(encounter_summary, setting_name)
        charge_scope = _department_filter(charge_lines, setting_name)
        first_charge_scope = _department_filter(first_charge, setting_name)
        prebill_scope = _department_filter(prebill_queue, setting_name)
        repeat_scope = _department_filter(repeat_queue, setting_name)
        recoverable_scope = _department_filter(recoverable_queue, setting_name)
        lost_scope = _department_filter(lost_dollars, setting_name)

        eligible_encounters = encounter_scope.loc[
            encounter_scope["has_expected_chargeable_activity"]
            & (encounter_scope["policy_window_end_ts"] <= report_cutoff)
        ].copy()
        unreconciled_numerator = float((~eligible_encounters["reconciliation_complete_flag"]).sum())
        unreconciled_denominator = float(len(eligible_encounters))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Unreconciled encounter rate",
                unreconciled_numerator,
                unreconciled_denominator,
                _safe_rate(unreconciled_numerator, unreconciled_denominator),
            )
        )

        late_charge_numerator = float(charge_scope["late_charge_flag"].sum())
        late_charge_denominator = float(len(charge_scope))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Late charge rate",
                late_charge_numerator,
                late_charge_denominator,
                _safe_rate(late_charge_numerator, late_charge_denominator),
            )
        )

        completion_numerator = float(
            (
                eligible_encounters["reconciliation_complete_flag"]
                & (
                    eligible_encounters["reconciliation_complete_ts"]
                    <= eligible_encounters["policy_window_end_ts"]
                )
            ).sum()
        )
        completion_denominator = float(len(eligible_encounters))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Charge reconciliation completion within policy window",
                completion_numerator,
                completion_denominator,
                _safe_rate(completion_numerator, completion_denominator),
            )
        )

        time_to_charge_numerator = float(first_charge_scope["hours_to_charge_entry"].sum())
        time_to_charge_denominator = float(len(first_charge_scope))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Time to charge entry",
                time_to_charge_numerator,
                time_to_charge_denominator,
                _safe_average(time_to_charge_numerator, time_to_charge_denominator),
            )
        )

        prebill_aging_numerator = float(prebill_scope["stage_age_days"].sum())
        prebill_aging_denominator = float(len(prebill_scope))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Prebill edit aging",
                prebill_aging_numerator,
                prebill_aging_denominator,
                _safe_average(prebill_aging_numerator, prebill_aging_denominator),
            )
        )

        recoverable_dollars_numerator = float(recoverable_scope["estimated_gross_dollars"].sum())
        lost_dollars_total = float(lost_scope["estimated_gross_dollars"].sum())
        exposure_denominator = recoverable_dollars_numerator + lost_dollars_total
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Recoverable dollars still open",
                recoverable_dollars_numerator,
                exposure_denominator,
                round(recoverable_dollars_numerator, 2),
            )
        )
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Dollars already lost after timing window",
                lost_dollars_total,
                exposure_denominator,
                round(lost_dollars_total, 2),
            )
        )

        repeat_numerator = float(repeat_scope["repeat_exception_flag"].sum())
        repeat_denominator = float(len(repeat_scope))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Department repeat exception rate",
                repeat_numerator,
                repeat_denominator,
                _safe_rate(repeat_numerator, repeat_denominator),
            )
        )

        unsupported_scope = charge_scope.loc[
            charge_scope["charge_status"] == "posted_pending_support"
        ].copy()
        unsupported_numerator = float(len(unsupported_scope))
        unsupported_denominator = float(len(charge_scope))
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Unsupported charge rate",
                unsupported_numerator,
                unsupported_denominator,
                _safe_rate(unsupported_numerator, unsupported_denominator),
            )
        )

        edit_first_pass_numerator = 0.0
        edit_first_pass_denominator = 0.0
        rows.append(
            _metric_row(
                report_cutoff,
                setting_name,
                "Edit first-pass clearance rate",
                edit_first_pass_numerator,
                edit_first_pass_denominator,
                _safe_rate(edit_first_pass_numerator, edit_first_pass_denominator),
            )
        )

    kpi_rows = pd.DataFrame(rows)
    priority_rows = _priority_rows_for_snapshot(priority_scores)
    kpi_rows, priority_rows = _align_snapshot_frames(kpi_rows, priority_rows)
    snapshot = pd.concat([kpi_rows, priority_rows], ignore_index=True)
    snapshot["snapshot_ts"] = pd.to_datetime(snapshot["snapshot_ts"])
    return snapshot.sort_values(
        ["record_type", "setting_name", "kpi_name", "priority_rank", "encounter_id"],
        na_position="last",
    ).reset_index(drop=True)


def write_kpi_snapshot_parquet(repo_root: Path | None = None) -> Path:
    df = build_kpi_snapshot_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_kpi_snapshot_parquet()


if __name__ == "__main__":
    main()
