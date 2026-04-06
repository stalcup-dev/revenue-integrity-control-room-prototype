from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact, resolve_repo_root
from ri_control_room.logic.build_queue_history import latest_queue_history_rows


ARTIFACT_DIR = Path("artifacts") / "realism"
REPORT_FIELDS = ("pass", "warn", "fail")

INFUSION_DEPARTMENT = "Outpatient Infusion / Oncology Infusion"
RADIOLOGY_DEPARTMENT = "Radiology / Interventional Radiology"
PROCEDURAL_DEPARTMENT = "OR / Hospital Outpatient Surgery / Procedural Areas"

DEPARTMENT_STORY_ORDER = ("infusion", "radiology_ir", "or_procedural")
DEPARTMENT_STORY_LABELS = {
    "infusion": "Infusion / Oncology Infusion",
    "radiology_ir": "Radiology / Interventional Radiology",
    "or_procedural": "OR / Procedural",
}
DEPARTMENT_TO_STORY_KEY = {
    INFUSION_DEPARTMENT: "infusion",
    RADIOLOGY_DEPARTMENT: "radiology_ir",
    PROCEDURAL_DEPARTMENT: "or_procedural",
}
ALLOWED_MODIFIER_EVENTS = {
    "infusion": {
        "Drug waste scenario",
        "Initial therapeutic infusion",
        "Separate access-site administration",
        "Timed infusion unit-conversion review",
    },
    "radiology_ir": {
        "Distinct same-day imaging study",
        "Laterality/site-dependent imaging study",
    },
    "or_procedural": {
        "Discontinued procedure",
        "Timestamp-dependent procedural support",
    },
}
BALANCE_STATUS_NAMES = (
    "recoverable_missed_charge",
    "unsupported_charge_risk",
    "packaged_or_nonbillable_suppressed",
    "modifier_dependency_case",
)
GENERIC_SUPPRESSION_REASONS = {"", "packaged_or_integral", "support_incomplete"}


def _safe_rate(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return float(numerator) / float(denominator)


def _status_from_flags(*, failed: bool, warned: bool) -> str:
    if failed:
        return "fail"
    if warned:
        return "warn"
    return "pass"


def _int_dict(series: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in series.to_dict().items()}


def _float_dict(frame: pd.DataFrame, columns: tuple[str, ...]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for index, row in frame.iterrows():
        result[str(index)] = {column: float(row[column]) for column in columns}
    return result


def _load_table(artifact_name: str, repo_root: Path) -> pd.DataFrame:
    return load_processed_artifact(artifact_name, repo_root)


def _load_optional_table(artifact_name: str, repo_root: Path) -> pd.DataFrame:
    try:
        return load_processed_artifact(artifact_name, repo_root)
    except FileNotFoundError:
        return pd.DataFrame()


def _find_kpi_value(kpis: pd.DataFrame, kpi_name: str) -> float:
    row = kpis.loc[
        (kpis["record_type"] == "kpi")
        & (kpis["setting_name"] == "All frozen V1 departments")
        & (kpis["kpi_name"] == kpi_name)
    ]
    if row.empty:
        return 0.0
    value = row.iloc[0]["kpi_value"]
    return 0.0 if pd.isna(value) else float(value)


def _department_queue_mix(queue: pd.DataFrame) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for department, group in queue.groupby("department"):
        result[str(department)] = _int_dict(group["current_queue"].value_counts())
    return result


def _latest_history(queue_history: pd.DataFrame) -> pd.DataFrame:
    return latest_queue_history_rows(queue_history)


def _bucket_reroutes(reroute_count: int) -> str:
    if reroute_count >= 3:
        return "3+"
    return str(int(reroute_count))


def _transition_pair_counts(queue_history: pd.DataFrame) -> pd.Series:
    transitions = queue_history.loc[
        queue_history["prior_queue"].fillna("").ne("")
        & queue_history["current_queue"].fillna("").ne("")
    ].copy()
    if transitions.empty:
        return pd.Series(dtype=int)
    pairs = transitions["prior_queue"] + " -> " + transitions["current_queue"]
    return pairs.value_counts()


def _active_stage_age_summary(queue: pd.DataFrame) -> pd.DataFrame:
    if queue.empty:
        return pd.DataFrame(columns=["min", "median", "max", "nunique"])
    return queue.groupby("current_prebill_stage")["stage_age_days"].agg(["min", "median", "max", "nunique"])


def _story_key_from_department(department: object) -> str:
    return DEPARTMENT_TO_STORY_KEY.get(str(department), "unknown")


def _encounter_gap_counts(documentation: pd.DataFrame) -> dict[str, int]:
    if documentation.empty:
        return {}
    encounter_gaps = documentation.groupby("encounter_id")["documentation_gap_type"].apply(
        lambda values: next((str(value) for value in values if str(value)), "<blank>")
    )
    return _int_dict(encounter_gaps.value_counts())


def _nonblank_gap_values(documentation: pd.DataFrame) -> list[str]:
    if documentation.empty:
        return []
    values = documentation["documentation_gap_type"].fillna("").astype(str)
    return sorted(value for value in values.unique().tolist() if value)


def _department_failure_mode_mix(expected: pd.DataFrame, documentation_events: pd.DataFrame) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for department, story_key in DEPARTMENT_TO_STORY_KEY.items():
        expected_subset = expected.loc[expected["department"] == department].copy()
        documentation_subset = documentation_events.loc[
            documentation_events["department"] == department
        ].copy()
        result[story_key] = {
            "department_label": DEPARTMENT_STORY_LABELS[story_key],
            "opportunity_status_counts": _int_dict(
                expected_subset["opportunity_status"].value_counts()
            ),
            "clinical_event_counts": _int_dict(expected_subset["clinical_event"].value_counts()),
            "documentation_gap_counts": _encounter_gap_counts(documentation_subset),
        }
    return result


def _finalize_dimension_report(
    dimensions: dict[str, dict[str, object]],
    *,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    anti_pattern_flags = [
        flag for dimension in dimensions.values() for flag in dimension["anti_pattern_flags"]
    ]
    summary_counts = {
        field: sum(1 for dimension in dimensions.values() if dimension["status"] == field)
        for field in REPORT_FIELDS
    }
    overall_status = "pass" if summary_counts["fail"] == 0 else "fail"
    if summary_counts["fail"] == 0 and summary_counts["warn"] > 0:
        overall_status = "warn"

    report = {
        "overall_status": overall_status,
        "summary_counts": summary_counts,
        "dimensions": dimensions,
        "anti_pattern_flags": anti_pattern_flags,
        "what_still_feels_fake": [flag for flag in anti_pattern_flags if flag],
    }
    if extra:
        report.update(extra)
    return report


def build_department_story_snapshot_from_tables(
    *,
    documentation_events: pd.DataFrame,
    expected: pd.DataFrame,
    queue: pd.DataFrame,
    corrections: pd.DataFrame | None = None,
    encounters: pd.DataFrame | None = None,
) -> dict[str, dict[str, object]]:
    corrections = pd.DataFrame() if corrections is None else corrections.copy()
    encounters = pd.DataFrame() if encounters is None else encounters.copy()

    correction_departments = pd.DataFrame(columns=["encounter_id", "department"])
    if not corrections.empty and not encounters.empty:
        correction_departments = corrections.merge(
            encounters[["encounter_id", "department"]].drop_duplicates(),
            on="encounter_id",
            how="left",
        )

    infusion_docs = documentation_events.loc[
        documentation_events["department"] == INFUSION_DEPARTMENT
    ].copy()
    radiology_docs = documentation_events.loc[
        documentation_events["department"] == RADIOLOGY_DEPARTMENT
    ].copy()
    procedural_docs = documentation_events.loc[
        documentation_events["department"] == PROCEDURAL_DEPARTMENT
    ].copy()

    return {
        "infusion": {
            "start_stop_dependency_count": int(
                infusion_docs["start_time"].notna().sum()
            ),
            "sequence_non_primary_count": int(
                infusion_docs["activity_role"].isin(
                    ["sequential_infusion", "concurrent_infusion"]
                ).sum()
            ),
            "hydration_conditional_count": int(
                (infusion_docs["hydration_conditionality"] == "conditional").sum()
            ),
            "waste_case_count": int((infusion_docs["activity_role"] == "waste_review").sum()),
            "access_site_case_count": int(infusion_docs["separate_access_site_flag"].sum()),
            "documentation_gap_counts": _int_dict(
                infusion_docs["documentation_gap_type"].replace("", "<blank>").value_counts()
            ),
        },
        "radiology_ir": {
            "completed_study_count": int(
                (radiology_docs["study_completion_state"] == "completed").sum()
            ),
            "incomplete_study_count": int(
                (radiology_docs["study_completion_state"] == "incomplete").sum()
            ),
            "laterality_site_count": int(
                radiology_docs["scenario_code"].isin(
                    ["laterality_missing", "site_specific_clean"]
                ).sum()
            ),
            "distinctness_case_count": int(
                (radiology_docs["activity_role"] == "distinct_repeat").sum()
            ),
            "contrast_device_count": int(
                radiology_docs["activity_role"].isin(
                    ["contrast_support", "device_linkage"]
                ).sum()
            ),
            "unsupported_count": int(
                (
                    expected.loc[expected["department"] == RADIOLOGY_DEPARTMENT, "opportunity_status"]
                    == "unsupported_charge_risk"
                ).sum()
            ),
        },
        "or_procedural": {
            "discontinued_case_count": int(procedural_docs["discontinued_state"].sum()),
            "implant_supply_count": int(
                (procedural_docs["activity_role"] == "implant_supply").sum()
            ),
            "timestamp_gap_count": int((~procedural_docs["timestamp_complete_flag"]).sum()),
            "late_post_risk_count": int(
                encounters.loc[
                    encounters["department"] == PROCEDURAL_DEPARTMENT, "late_post_risk_flag"
                ].sum()
            )
            if not encounters.empty
            else 0,
            "postbill_recoverable_queue_count": int(
                (
                    queue.loc[queue["department"] == PROCEDURAL_DEPARTMENT, "recoverability_status"]
                    == "Post-final-bill recoverable by correction / rebill"
                ).sum()
            ),
            "correction_history_count": int(
                correction_departments["department"].eq(PROCEDURAL_DEPARTMENT).sum()
            )
            if not correction_departments.empty
            else 0,
        },
    }


def build_department_story_snapshot(repo_root: Path | None = None) -> dict[str, dict[str, object]]:
    root = resolve_repo_root(repo_root)
    return build_department_story_snapshot_from_tables(
        documentation_events=_load_table("documentation_events", root),
        expected=_load_table("expected_charge_opportunities", root),
        queue=_load_table("exception_queue", root),
        corrections=_load_optional_table("corrections_rebills", root),
        encounters=_load_table("encounters", root),
    )


def build_department_story_report_from_tables(
    *,
    encounters: pd.DataFrame,
    documentation_events: pd.DataFrame,
    upstream_signals: pd.DataFrame,
    expected: pd.DataFrame,
    queue: pd.DataFrame,
    queue_history: pd.DataFrame,
    corrections: pd.DataFrame | None = None,
) -> dict[str, object]:
    del upstream_signals
    corrections = pd.DataFrame() if corrections is None else corrections.copy()
    encounter_departments = encounters[["encounter_id", "department"]].drop_duplicates()
    queue_history_with_department = queue_history.merge(
        encounter_departments,
        on="encounter_id",
        how="left",
    )
    correction_departments = pd.DataFrame(columns=["encounter_id", "department"])
    if not corrections.empty:
        correction_departments = corrections.merge(
            encounter_departments,
            on="encounter_id",
            how="left",
        )

    infusion_docs = documentation_events.loc[
        documentation_events["department"] == INFUSION_DEPARTMENT
    ].copy()
    infusion_expected = expected.loc[expected["department"] == INFUSION_DEPARTMENT].copy()
    infusion_encounters = encounters.loc[encounters["department"] == INFUSION_DEPARTMENT].copy()
    infusion_gap_counts = _encounter_gap_counts(infusion_docs)
    infusion_case_count = int(len(infusion_encounters))
    infusion_start_stop_case_count = int(
        infusion_docs.loc[
            infusion_docs["activity_role"].isin(
                ["primary_infusion", "sequential_infusion", "concurrent_infusion"]
            )
            & infusion_docs["unit_conversion_required_flag"],
            "encounter_id",
        ].nunique()
    )
    infusion_sequence_case_count = int(
        infusion_docs.loc[
            infusion_docs["activity_role"].isin(["sequential_infusion", "concurrent_infusion"]),
            "encounter_id",
        ].nunique()
    )
    infusion_hydration_case_count = int(
        infusion_docs.loc[infusion_docs["activity_role"] == "hydration", "encounter_id"].nunique()
    )
    infusion_waste_case_count = int(
        infusion_docs.loc[infusion_docs["activity_role"] == "waste_review", "encounter_id"].nunique()
    )
    infusion_access_case_count = int(
        infusion_docs.loc[infusion_docs["separate_access_site_flag"], "encounter_id"].nunique()
    )
    infusion_metrics = {
        "encounter_count": infusion_case_count,
        "start_stop_dependency_case_count": infusion_start_stop_case_count,
        "start_stop_dependency_rate": round(
            _safe_rate(infusion_start_stop_case_count, infusion_case_count), 4
        ),
        "sequence_non_primary_case_count": infusion_sequence_case_count,
        "hydration_conditional_case_count": infusion_hydration_case_count,
        "waste_support_case_count": infusion_waste_case_count,
        "access_site_case_count": infusion_access_case_count,
        "documentation_gap_counts": infusion_gap_counts,
        "clinical_event_counts": _int_dict(infusion_expected["clinical_event"].value_counts()),
    }
    infusion_flags = []
    if infusion_start_stop_case_count == 0:
        infusion_flags.append("Infusion lacks start/stop-dependent timed administration cases.")
    if infusion_sequence_case_count == 0:
        infusion_flags.append("Infusion lacks sequencing or concurrent administration cases.")
    if infusion_hydration_case_count == 0:
        infusion_flags.append("Infusion lacks hydration conditionality scenarios.")
    if infusion_waste_case_count == 0:
        infusion_flags.append("Infusion lacks waste-support scenarios.")
    if infusion_access_case_count == 0:
        infusion_flags.append("Infusion lacks separate access-site logic.")
    if infusion_gap_counts.get("missing_stop_time", 0) == 0:
        infusion_flags.append("Infusion lacks a stop-time-driven documentation failure.")
    if infusion_gap_counts.get("undocumented_waste", 0) == 0:
        infusion_flags.append("Infusion lacks a waste-support documentation failure.")
    infusion_status = _status_from_flags(
        failed=bool(infusion_flags),
        warned=infusion_metrics["start_stop_dependency_rate"] < 0.7,
    )

    radiology_docs = documentation_events.loc[
        documentation_events["department"] == RADIOLOGY_DEPARTMENT
    ].copy()
    radiology_expected = expected.loc[expected["department"] == RADIOLOGY_DEPARTMENT].copy()
    radiology_encounters = encounters.loc[encounters["department"] == RADIOLOGY_DEPARTMENT].copy()
    radiology_primary_docs = radiology_docs.loc[radiology_docs["activity_role"] == "primary_study"].copy()
    radiology_case_count = int(len(radiology_encounters))
    radiology_completed_count = int(
        radiology_primary_docs.loc[
            radiology_primary_docs["study_completion_state"] == "completed", "encounter_id"
        ].nunique()
    )
    radiology_incomplete_count = int(
        radiology_primary_docs.loc[
            radiology_primary_docs["study_completion_state"] == "incomplete", "encounter_id"
        ].nunique()
    )
    radiology_laterality_site_count = int(
        radiology_docs.loc[
            radiology_docs["scenario_code"].isin(["laterality_missing", "site_specific_clean"]),
            "encounter_id",
        ].nunique()
    )
    radiology_distinctness_count = int(
        radiology_docs.loc[radiology_docs["activity_role"] == "distinct_repeat", "encounter_id"].nunique()
    )
    radiology_contrast_device_count = int(
        radiology_docs.loc[
            radiology_docs["activity_role"].isin(["contrast_support", "device_linkage"]),
            "encounter_id",
        ].nunique()
    )
    radiology_unsupported_count = int(
        (radiology_expected["opportunity_status"] == "unsupported_charge_risk").sum()
    )
    radiology_metrics = {
        "encounter_count": radiology_case_count,
        "completed_study_case_count": radiology_completed_count,
        "incomplete_study_case_count": radiology_incomplete_count,
        "laterality_site_case_count": radiology_laterality_site_count,
        "distinctness_case_count": radiology_distinctness_count,
        "contrast_device_case_count": radiology_contrast_device_count,
        "unsupported_case_count": radiology_unsupported_count,
        "documentation_gap_counts": _encounter_gap_counts(radiology_docs),
        "clinical_event_counts": _int_dict(radiology_expected["clinical_event"].value_counts()),
    }
    radiology_flags = []
    if radiology_completed_count == 0 or radiology_incomplete_count == 0:
        radiology_flags.append("Radiology lacks a believable completed-versus-incomplete study mix.")
    if radiology_laterality_site_count == 0:
        radiology_flags.append("Radiology lacks laterality or site-dependent support scenarios.")
    if radiology_distinctness_count == 0:
        radiology_flags.append("Radiology lacks distinct same-day study scenarios.")
    if radiology_contrast_device_count == 0:
        radiology_flags.append("Radiology lacks contrast or device-linked support scenarios.")
    if radiology_unsupported_count == 0:
        radiology_flags.append("Radiology lacks unsupported or compliance-risk cases.")
    radiology_status = _status_from_flags(
        failed=bool(radiology_flags),
        warned=radiology_expected["clinical_event"].nunique() < 4,
    )

    procedural_docs = documentation_events.loc[
        documentation_events["department"] == PROCEDURAL_DEPARTMENT
    ].copy()
    procedural_expected = expected.loc[expected["department"] == PROCEDURAL_DEPARTMENT].copy()
    procedural_encounters = encounters.loc[encounters["department"] == PROCEDURAL_DEPARTMENT].copy()
    procedural_queue = queue.loc[queue["department"] == PROCEDURAL_DEPARTMENT].copy()
    procedural_case_count = int(len(procedural_encounters))
    procedural_discontinued_count = int(
        procedural_docs.loc[procedural_docs["discontinued_state"], "encounter_id"].nunique()
    )
    procedural_implant_supply_count = int(
        procedural_docs.loc[procedural_docs["activity_role"] == "implant_supply", "encounter_id"].nunique()
    )
    procedural_timestamp_gap_count = int(
        procedural_docs.loc[~procedural_docs["timestamp_complete_flag"], "encounter_id"].nunique()
    )
    procedural_late_post_risk_count = int(procedural_encounters["late_post_risk_flag"].sum())
    procedural_postbill_recoverable_count = int(
        (
            procedural_queue["recoverability_status"]
            == "Post-final-bill recoverable by correction / rebill"
        ).sum()
    )
    procedural_correction_history_case_count = int(
        correction_departments.loc[
            correction_departments["department"] == PROCEDURAL_DEPARTMENT, "encounter_id"
        ].nunique()
    )
    mean_reroute_by_department = {
        _story_key_from_department(department): round(float(value), 4)
        for department, value in queue_history_with_department.groupby("department")["reroute_count"].mean().items()
        if _story_key_from_department(department) != "unknown"
    }
    procedural_metrics = {
        "encounter_count": procedural_case_count,
        "discontinued_case_count": procedural_discontinued_count,
        "implant_supply_case_count": procedural_implant_supply_count,
        "timestamp_gap_case_count": procedural_timestamp_gap_count,
        "late_post_risk_case_count": procedural_late_post_risk_count,
        "postbill_recoverable_case_count": procedural_postbill_recoverable_count,
        "correction_history_case_count": procedural_correction_history_case_count,
        "mean_reroute_count_by_department": mean_reroute_by_department,
        "clinical_event_counts": _int_dict(procedural_expected["clinical_event"].value_counts()),
    }
    procedural_flags = []
    if procedural_discontinued_count == 0:
        procedural_flags.append("OR / procedural lacks discontinued-procedure states.")
    if procedural_implant_supply_count == 0:
        procedural_flags.append("OR / procedural lacks implant or supply-linked scenarios.")
    if procedural_timestamp_gap_count == 0:
        procedural_flags.append("OR / procedural lacks timestamp-dependent failures.")
    if procedural_late_post_risk_count == 0:
        procedural_flags.append("OR / procedural lacks late-charge-risk scenarios.")
    if procedural_postbill_recoverable_count == 0:
        procedural_flags.append("OR / procedural lacks post-final-bill correction-path cases.")
    if procedural_correction_history_case_count == 0:
        procedural_flags.append("OR / procedural lacks correction-history support.")
    if mean_reroute_by_department:
        procedural_mean_reroute = mean_reroute_by_department.get("or_procedural", 0.0)
        if procedural_mean_reroute <= max(
            mean_reroute_by_department.get("infusion", 0.0),
            mean_reroute_by_department.get("radiology_ir", 0.0),
        ):
            procedural_flags.append(
                "OR / procedural is not more handoff-heavy than the other frozen V1 departments."
            )
    procedural_status = _status_from_flags(
        failed=bool(procedural_flags),
        warned=procedural_expected["clinical_event"].nunique() < 4,
    )

    expected_story_keys = expected["department"].map(_story_key_from_department)
    modifier_cases = expected.loc[expected["opportunity_status"] == "modifier_dependency_case"].copy()
    modifier_cases["story_key"] = modifier_cases["department"].map(_story_key_from_department)
    invalid_modifier_cases = modifier_cases.loc[
        ~modifier_cases.apply(
            lambda row: row["clinical_event"] in ALLOWED_MODIFIER_EVENTS.get(row["story_key"], set()),
            axis=1,
        )
    ]
    modifier_case_event_map = {
        story_key: _int_dict(group["clinical_event"].value_counts())
        for story_key, group in modifier_cases.groupby("story_key")
        if story_key != "unknown"
    }
    failure_categories = [
        "recoverable_missed_charge",
        "unsupported_charge_risk",
        "packaged_or_nonbillable_suppressed",
        "modifier_dependency_case",
    ]
    failure_category_dominance: dict[str, dict[str, object]] = {}
    dominant_departments: list[str] = []
    for category in failure_categories:
        category_subset = expected.loc[expected["opportunity_status"] == category].copy()
        if category_subset.empty:
            continue
        by_department = category_subset["department"].value_counts()
        dominant_department = str(by_department.idxmax())
        dominant_share = round(float(by_department.max()) / float(by_department.sum()), 4)
        failure_category_dominance[category] = {
            "department": dominant_department,
            "share": dominant_share,
        }
        if dominant_share >= 0.6:
            dominant_departments.append(dominant_department)

    gap_signatures = {
        story_key: _nonblank_gap_values(
            documentation_events.loc[documentation_events["department"] == department]
        )
        for department, story_key in DEPARTMENT_TO_STORY_KEY.items()
    }
    top_failure_status_by_department: dict[str, str] = {}
    for department, story_key in DEPARTMENT_TO_STORY_KEY.items():
        failure_subset = expected.loc[
            (expected["department"] == department)
            & (expected["opportunity_status"] != "expected_charge_supported")
        ]
        if not failure_subset.empty:
            top_failure_status_by_department[story_key] = str(
                failure_subset["opportunity_status"].value_counts().idxmax()
            )

    anti_pattern_metrics = {
        "documented_performed_support_rate": round(
            _safe_rate(
                int(
                    (
                        expected["documented_performed_activity_flag"]
                        & expected["signal_basis"].eq("documentation_event")
                    ).sum()
                ),
                len(expected),
            ),
            4,
        ),
        "department_documentation_gap_signatures": gap_signatures,
        "modifier_case_event_map": modifier_case_event_map,
        "invalid_modifier_case_count": int(len(invalid_modifier_cases)),
        "failure_category_dominance": failure_category_dominance,
        "top_failure_status_by_department": top_failure_status_by_department,
        "top_clinical_event_by_department": {
            story_key: str(group["clinical_event"].value_counts().idxmax())
            for story_key, group in expected.assign(story_key=expected_story_keys).groupby("story_key")
            if story_key in DEPARTMENT_STORY_ORDER and not group.empty
        },
    }
    anti_pattern_flags = []
    if anti_pattern_metrics["documented_performed_support_rate"] < 1.0:
        anti_pattern_flags.append(
            "Expected opportunities are no longer grounded only in documented performed activity."
        )
    if len({tuple(values) for values in gap_signatures.values()}) < len(DEPARTMENT_STORY_ORDER):
        anti_pattern_flags.append(
            "Departments exhibit near-identical documentation gap patterns."
        )
    if anti_pattern_metrics["invalid_modifier_case_count"] > 0:
        anti_pattern_flags.append(
            "Modifier dependency cases are not patterned to believable department-specific scenarios."
        )
    if len(set(dominant_departments)) == 1 and len(dominant_departments) >= 3:
        anti_pattern_flags.append(
            "One department dominates nearly every failure category in an artificial way."
        )
    if len(set(top_failure_status_by_department.values())) < 2:
        anti_pattern_flags.append(
            "Service-line failure clustering is too uniform across departments."
        )
    anti_pattern_status = _status_from_flags(
        failed=bool(anti_pattern_flags),
        warned=False,
    )

    snapshot = build_department_story_snapshot_from_tables(
        documentation_events=documentation_events,
        expected=expected,
        queue=queue,
        corrections=corrections,
        encounters=encounters,
    )
    failure_mode_mix = _department_failure_mode_mix(expected, documentation_events)
    return _finalize_dimension_report(
        {
            "infusion_story_realism": {
                "status": infusion_status,
                "metrics": infusion_metrics,
                "anti_pattern_flags": infusion_flags,
            },
            "radiology_story_realism": {
                "status": radiology_status,
                "metrics": radiology_metrics,
                "anti_pattern_flags": radiology_flags,
            },
            "or_procedural_story_realism": {
                "status": procedural_status,
                "metrics": procedural_metrics,
                "anti_pattern_flags": procedural_flags,
            },
            "department_story_antipatterns": {
                "status": anti_pattern_status,
                "metrics": anti_pattern_metrics,
                "anti_pattern_flags": anti_pattern_flags,
            },
        },
        extra={
            "department_scenario_counts": snapshot,
            "department_failure_mode_mix": failure_mode_mix,
            "what_still_feels_fake_by_department": {
                "infusion": infusion_flags,
                "radiology_ir": radiology_flags,
                "or_procedural": procedural_flags,
                "cross_department": anti_pattern_flags,
            },
        },
    )


def build_department_story_report(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_department_story_report_from_tables(
        encounters=_load_table("encounters", root),
        documentation_events=_load_table("documentation_events", root),
        upstream_signals=_load_table("upstream_activity_signals", root),
        expected=_load_table("expected_charge_opportunities", root),
        queue=_load_table("exception_queue", root),
        queue_history=_load_table("queue_history", root),
        corrections=_load_optional_table("corrections_rebills", root),
    )


def build_suppression_balance_snapshot_from_tables(
    *,
    expected: pd.DataFrame,
) -> dict[str, object]:
    snapshot = {
        "overall": {
            "status_counts": {
                status_name: int((expected["opportunity_status"] == status_name).sum())
                for status_name in BALANCE_STATUS_NAMES
            },
            "status_rates": {
                status_name: round(float((expected["opportunity_status"] == status_name).mean()), 4)
                for status_name in BALANCE_STATUS_NAMES
            },
        },
        "by_department": {},
    }
    for department, story_key in DEPARTMENT_TO_STORY_KEY.items():
        subset = expected.loc[expected["department"] == department].copy()
        failure_subset = subset.loc[subset["opportunity_status"] != "expected_charge_supported"].copy()
        snapshot["by_department"][story_key] = {
            "status_counts": {
                status_name: int((subset["opportunity_status"] == status_name).sum())
                for status_name in BALANCE_STATUS_NAMES
            },
            "status_rates": {
                status_name: round(float((subset["opportunity_status"] == status_name).mean()), 4)
                for status_name in BALANCE_STATUS_NAMES
            },
            "top_failure_class": ""
            if failure_subset.empty
            else str(failure_subset["opportunity_status"].value_counts().idxmax()),
            "suppression_reason_counts": _int_dict(
                subset.loc[
                    subset["opportunity_status"] == "packaged_or_nonbillable_suppressed",
                    "why_not_billable_explanation",
                ].value_counts()
            ),
            "unsupported_reason_counts": _int_dict(
                subset.loc[
                    subset["opportunity_status"] == "unsupported_charge_risk",
                    "why_not_billable_explanation",
                ].value_counts()
            ),
        }
    return snapshot


def build_suppression_balance_snapshot(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_suppression_balance_snapshot_from_tables(
        expected=_load_table("expected_charge_opportunities", root),
    )


def build_suppression_balance_report_from_tables(
    *,
    expected: pd.DataFrame,
) -> dict[str, object]:
    undercapture = expected.loc[expected["opportunity_status"] == "recoverable_missed_charge"].copy()
    unsupported = expected.loc[expected["opportunity_status"] == "unsupported_charge_risk"].copy()
    suppressed = expected.loc[
        expected["opportunity_status"] == "packaged_or_nonbillable_suppressed"
    ].copy()

    top_failure_class_by_department: dict[str, str] = {}
    for department, story_key in DEPARTMENT_TO_STORY_KEY.items():
        failure_subset = expected.loc[
            (expected["department"] == department)
            & (expected["opportunity_status"] != "expected_charge_supported")
        ].copy()
        if not failure_subset.empty:
            top_failure_class_by_department[story_key] = str(
                failure_subset["opportunity_status"].value_counts().idxmax()
            )

    undercapture_metrics = {
        "overall_count": int(len(undercapture)),
        "overall_rate": round(_safe_rate(len(undercapture), len(expected)), 4),
        "department_counts": _int_dict(undercapture["department"].value_counts()),
        "department_rates": {
            department: round(
                _safe_rate(
                    int((expected["department"] == department).mul(
                        expected["opportunity_status"] == "recoverable_missed_charge",
                        fill_value=False,
                    ).sum()),
                    int((expected["department"] == department).sum()),
                ),
                4,
            )
            for department in DEPARTMENT_TO_STORY_KEY
        },
        "departments_with_undercapture_count": int(undercapture["department"].nunique()),
        "top_failure_class_by_department": top_failure_class_by_department,
    }
    undercapture_flags = []
    if undercapture_metrics["overall_count"] == 0:
        undercapture_flags.append("Recoverable missed-charge cases are absent.")
    if undercapture_metrics["departments_with_undercapture_count"] < 2:
        undercapture_flags.append("Undercapture is isolated to too few departments.")
    if top_failure_class_by_department and len(set(top_failure_class_by_department.values())) == 1 and (
        next(iter(top_failure_class_by_department.values())) == "recoverable_missed_charge"
    ):
        undercapture_flags.append("Undercapture dominates every department in the same way.")
    undercapture_status = _status_from_flags(
        failed=undercapture_metrics["overall_count"] == 0
        or any("dominates every department" in flag for flag in undercapture_flags),
        warned=undercapture_metrics["departments_with_undercapture_count"] < 2,
    )

    unsupported_with_charge_count = int(unsupported["charge_event_exists_flag"].sum())
    unsupported_metrics = {
        "overall_count": int(len(unsupported)),
        "overall_rate": round(_safe_rate(len(unsupported), len(expected)), 4),
        "department_counts": _int_dict(unsupported["department"].value_counts()),
        "unsupported_with_charge_count": unsupported_with_charge_count,
        "unsupported_with_charge_rate": round(
            _safe_rate(unsupported_with_charge_count, len(unsupported)), 4
        ),
        "closed_compliance_unsupported_count": int(
            (
                unsupported["recoverability_status"]
                == "Financially closed but still compliance-relevant"
            ).sum()
        ),
        "charge_status_distribution": _int_dict(unsupported["charge_status_example"].value_counts()),
    }
    unsupported_flags = []
    if unsupported_metrics["overall_count"] == 0:
        unsupported_flags.append("Unsupported or compliance-risk cases are absent.")
    if unsupported_metrics["unsupported_with_charge_rate"] < 1.0:
        unsupported_flags.append("Unsupported cases are collapsing into missing-charge stories.")
    if unsupported_metrics["closed_compliance_unsupported_count"] == 0:
        unsupported_flags.append(
            "Unsupported cases never persist as financially closed but compliance-relevant."
        )
    unsupported_status = _status_from_flags(
        failed=unsupported_metrics["overall_count"] == 0
        or unsupported_metrics["unsupported_with_charge_rate"] < 1.0,
        warned=unsupported_metrics["closed_compliance_unsupported_count"] == 0,
    )

    meaningful_suppression_explanations = suppressed["why_not_billable_explanation"].fillna("").astype(str)
    generic_suppression_reason_count = int(
        meaningful_suppression_explanations.isin(GENERIC_SUPPRESSION_REASONS).sum()
    )
    suppression_metrics = {
        "overall_count": int(len(suppressed)),
        "overall_rate": round(_safe_rate(len(suppressed), len(expected)), 4),
        "department_counts": _int_dict(suppressed["department"].value_counts()),
        "meaningful_explanation_rate": round(
            _safe_rate(
                int((meaningful_suppression_explanations != "").sum()),
                len(suppressed),
            ),
            4,
        ),
        "generic_explanation_rate": round(
            _safe_rate(generic_suppression_reason_count, len(suppressed)),
            4,
        ),
        "department_reason_counts": {
            story_key: _int_dict(
                expected.loc[
                    (expected["department"] == department)
                    & (expected["opportunity_status"] == "packaged_or_nonbillable_suppressed"),
                    "why_not_billable_explanation",
                ].value_counts()
            )
            for department, story_key in DEPARTMENT_TO_STORY_KEY.items()
        },
        "suppressed_charge_capture_queue_count": int(
            (
                expected["opportunity_status"].eq("packaged_or_nonbillable_suppressed")
                & expected["current_prebill_stage"].eq("Charge capture pending")
            ).sum()
        ),
    }
    suppression_flags = []
    if suppression_metrics["overall_count"] == 0:
        suppression_flags.append("Suppressed packaged or non-billable cases are absent.")
    if suppression_metrics["meaningful_explanation_rate"] < 1.0:
        suppression_flags.append("Suppression explanations are missing.")
    if suppression_metrics["generic_explanation_rate"] > 0.25:
        suppression_flags.append("Suppression explanations are still too generic.")
    if suppression_metrics["suppressed_charge_capture_queue_count"] > 0:
        suppression_flags.append("Suppressed cases are still being represented as leakage.")
    suppression_status = _status_from_flags(
        failed=suppression_metrics["overall_count"] == 0
        or suppression_metrics["meaningful_explanation_rate"] < 1.0
        or suppression_metrics["suppressed_charge_capture_queue_count"] > 0,
        warned=suppression_metrics["generic_explanation_rate"] > 0.25,
    )

    snapshot = build_suppression_balance_snapshot_from_tables(expected=expected)
    dominant_department_by_class: dict[str, dict[str, object]] = {}
    dominant_departments: list[str] = []
    for status_name in BALANCE_STATUS_NAMES:
        subset = expected.loc[expected["opportunity_status"] == status_name].copy()
        if subset.empty:
            continue
        counts = subset["department"].value_counts()
        dominant_department = str(counts.idxmax())
        dominant_share = round(float(counts.max()) / float(counts.sum()), 4)
        dominant_department_by_class[status_name] = {
            "department": dominant_department,
            "share": dominant_share,
        }
        if dominant_share >= 0.6:
            dominant_departments.append(dominant_department)

    suppression_signatures = {
        story_key: sorted(department_snapshot["suppression_reason_counts"].keys())
        for story_key, department_snapshot in snapshot["by_department"].items()
        if department_snapshot["suppression_reason_counts"]
    }
    unsupported_signatures = {
        story_key: sorted(department_snapshot["unsupported_reason_counts"].keys())
        for story_key, department_snapshot in snapshot["by_department"].items()
        if department_snapshot["unsupported_reason_counts"]
    }
    anti_pattern_metrics = {
        "overall_status_counts": snapshot["overall"]["status_counts"],
        "overall_status_rates": snapshot["overall"]["status_rates"],
        "top_failure_class_by_department": top_failure_class_by_department,
        "separately_billable_rate": round(float(expected["separately_billable_flag"].mean()), 4),
        "dominant_department_by_class": dominant_department_by_class,
        "suppression_reason_signatures": suppression_signatures,
        "unsupported_reason_signatures": unsupported_signatures,
    }
    anti_pattern_flags = []
    if undercapture_metrics["overall_count"] > 0 and unsupported_metrics["overall_count"] == 0 and suppression_metrics["overall_count"] == 0:
        anti_pattern_flags.append("Only underbilling stories remain.")
    if suppression_metrics["overall_count"] == 0 or suppression_metrics["generic_explanation_rate"] > 0.5:
        anti_pattern_flags.append("Suppression is too rare or too generic.")
    if unsupported_metrics["unsupported_with_charge_rate"] < 1.0:
        anti_pattern_flags.append("Unsupported cases are just relabeled missed charges.")
    if anti_pattern_metrics["separately_billable_rate"] > 0.8:
        anti_pattern_flags.append(
            "Too many documented activities still trend toward separately billable expectation."
        )
    if len(set(dominant_departments)) == 1 and len(dominant_departments) >= 3:
        anti_pattern_flags.append("One department dominates every balance class in an artificial way.")
    if suppression_signatures and len({tuple(values) for values in suppression_signatures.values()}) < len(suppression_signatures):
        anti_pattern_flags.append(
            "Department-specific suppression signatures have become too uniform."
        )
    if unsupported_signatures and len({tuple(values) for values in unsupported_signatures.values()}) < len(unsupported_signatures):
        anti_pattern_flags.append(
            "Department-specific unsupported signatures have become too uniform."
        )
    anti_pattern_status = _status_from_flags(
        failed=bool(anti_pattern_flags),
        warned=False,
    )

    return _finalize_dimension_report(
        {
            "undercapture_balance_realism": {
                "status": undercapture_status,
                "metrics": undercapture_metrics,
                "anti_pattern_flags": undercapture_flags,
            },
            "unsupported_balance_realism": {
                "status": unsupported_status,
                "metrics": unsupported_metrics,
                "anti_pattern_flags": unsupported_flags,
            },
            "suppression_balance_realism": {
                "status": suppression_status,
                "metrics": suppression_metrics,
                "anti_pattern_flags": suppression_flags,
            },
            "suppression_balance_antipatterns": {
                "status": anti_pattern_status,
                "metrics": anti_pattern_metrics,
                "anti_pattern_flags": anti_pattern_flags,
            },
        },
        extra={"balance_snapshot": snapshot},
    )


def build_suppression_balance_report(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_suppression_balance_report_from_tables(
        expected=_load_table("expected_charge_opportunities", root),
    )


def build_ops_mix_snapshot_from_tables(
    *,
    encounters: pd.DataFrame,
    statuses: pd.DataFrame,
    expected: pd.DataFrame,
    queue: pd.DataFrame,
    queue_history: pd.DataFrame,
    priority_scores: pd.DataFrame,
    denials_feedback: pd.DataFrame | None = None,
) -> dict[str, object]:
    denials_feedback = pd.DataFrame() if denials_feedback is None else denials_feedback.copy()
    latest_history = _latest_history(queue_history)
    repeat_cluster_frame = (
        priority_scores.groupby(["department", "root_cause_mechanism"], as_index=False)
        .agg(open_exception_count=("queue_item_id", "size"))
        .sort_values(
            ["department", "open_exception_count", "root_cause_mechanism"],
            ascending=[True, False, True],
        )
    )
    repeat_clusters: dict[str, dict[str, int]] = {}
    for department, group in repeat_cluster_frame.groupby("department"):
        repeat_clusters[str(department)] = {
            str(row["root_cause_mechanism"]): int(row["open_exception_count"])
            for _, row in group.iterrows()
        }

    payer_group_counts = (
        _int_dict(denials_feedback["payer_group"].value_counts())
        if not denials_feedback.empty
        else {}
    )
    issue_domain_counts = (
        _int_dict(denials_feedback["linked_upstream_issue_domain"].value_counts())
        if not denials_feedback.empty
        else {}
    )
    denial_category_counts = (
        _int_dict(denials_feedback["denial_category"].value_counts())
        if not denials_feedback.empty
        else {}
    )

    return {
        "artifact_row_counts": {
            "encounters": int(len(encounters)),
            "claims_or_account_status": int(len(statuses)),
            "expected_charge_opportunities": int(len(expected)),
            "exception_queue": int(len(queue)),
            "queue_history": int(len(queue_history)),
            "priority_scores": int(len(priority_scores)),
            "denials_feedback": int(len(denials_feedback)),
        },
        "department_queue_mix": _department_queue_mix(queue),
        "reroute_distribution": _int_dict(
            latest_history["reroute_count"].value_counts().sort_index()
        ),
        "repeat_exception_rate_by_department": {
            str(index): round(float(value), 4)
            for index, value in priority_scores.groupby("department")[
                "repeat_exception_flag"
            ].mean().to_dict().items()
        }
        if not priority_scores.empty
        else {},
        "repeat_root_cause_clusters_by_department": repeat_clusters,
        "status_stage_counts": _int_dict(statuses["current_prebill_stage"].value_counts()),
        "closed_compliance_count": int(
            (
                statuses["recoverability_status"]
                == "Financially closed but still compliance-relevant"
            ).sum()
        ),
        "payable_signal_counts": {
            "denials_feedback_rows": int(len(denials_feedback)),
            "upstream_linked_rows": int(
                (
                    denials_feedback.get(
                        "linked_upstream_issue_domain", pd.Series(dtype=object)
                    )
                    .fillna("")
                    .ne("")
                ).sum()
            )
            if not denials_feedback.empty
            else 0,
            "payer_group_counts": payer_group_counts,
            "issue_domain_counts": issue_domain_counts,
            "denial_category_counts": denial_category_counts,
            "closed_compliance_signal_rows": int(
                (
                    denials_feedback.get(
                        "linked_recoverability_status", pd.Series(dtype=object)
                    )
                    == "Financially closed but still compliance-relevant"
                ).sum()
            )
            if not denials_feedback.empty
            else 0,
        },
    }


def build_ops_mix_snapshot(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_ops_mix_snapshot_from_tables(
        encounters=_load_table("encounters", root),
        statuses=_load_table("claims_or_account_status", root),
        expected=_load_table("expected_charge_opportunities", root),
        queue=_load_table("exception_queue", root),
        queue_history=_load_table("queue_history", root),
        priority_scores=_load_table("priority_scores", root),
        denials_feedback=_load_optional_table("denials_feedback", root),
    )


def build_ops_mix_report_from_tables(
    *,
    encounters: pd.DataFrame,
    statuses: pd.DataFrame,
    expected: pd.DataFrame,
    queue: pd.DataFrame,
    queue_history: pd.DataFrame,
    priority_scores: pd.DataFrame,
    denials_feedback: pd.DataFrame | None = None,
) -> dict[str, object]:
    denials_feedback = pd.DataFrame() if denials_feedback is None else denials_feedback.copy()
    snapshot = build_ops_mix_snapshot_from_tables(
        encounters=encounters,
        statuses=statuses,
        expected=expected,
        queue=queue,
        queue_history=queue_history,
        priority_scores=priority_scores,
        denials_feedback=denials_feedback,
    )

    department_queue_mix = snapshot["department_queue_mix"]
    dominant_queues = {
        department: max(queue_counts, key=queue_counts.get)
        for department, queue_counts in department_queue_mix.items()
        if queue_counts
    }
    reroute_distribution = snapshot["reroute_distribution"]
    repeat_cluster_frame = (
        priority_scores.groupby(["department", "root_cause_mechanism"], as_index=False)
        .agg(open_exception_count=("queue_item_id", "size"))
        .sort_values(
            ["department", "open_exception_count", "root_cause_mechanism"],
            ascending=[True, False, True],
        )
    )
    repeat_cluster_count = int((repeat_cluster_frame["open_exception_count"] >= 2).sum())
    latest_history = _latest_history(queue_history)
    rerouted_case_count = int((latest_history["reroute_count"] > 0).sum()) if not latest_history.empty else 0
    multi_reroute_count = int((latest_history["reroute_count"] >= 2).sum()) if not latest_history.empty else 0

    medium_volume_metrics = {
        "encounter_count": int(len(encounters)),
        "active_exception_count": int(len(queue)),
        "department_queue_mix": department_queue_mix,
        "distinct_dominant_queues": len(set(dominant_queues.values())),
        "reroute_distribution": reroute_distribution,
        "rerouted_case_count": rerouted_case_count,
        "multi_reroute_count": multi_reroute_count,
        "repeat_exception_rate_by_department": snapshot["repeat_exception_rate_by_department"],
        "repeat_root_cause_cluster_count_ge_2": repeat_cluster_count,
    }
    medium_volume_flags = []
    if medium_volume_metrics["encounter_count"] < 50:
        medium_volume_flags.append("Population still feels too small and catalog-like.")
    if medium_volume_metrics["active_exception_count"] < 18:
        medium_volume_flags.append("Active queue volume is still too thin for an ops mix.")
    if medium_volume_metrics["distinct_dominant_queues"] < 2:
        medium_volume_flags.append("Queue concentration has flattened into the same dominant queue.")
    if rerouted_case_count < 6:
        medium_volume_flags.append("Reroute churn is still too light at the expanded volume.")
    if multi_reroute_count < 2:
        medium_volume_flags.append("Multi-reroute cases remain too rare.")
    if repeat_cluster_count < 4:
        medium_volume_flags.append("Repeat-pattern clustering remains too thin.")
    medium_volume_status = _status_from_flags(
        failed=medium_volume_metrics["encounter_count"] < 50
        or medium_volume_metrics["distinct_dominant_queues"] < 2
        or repeat_cluster_count < 4,
        warned=medium_volume_metrics["active_exception_count"] < 18
        or rerouted_case_count < 6
        or multi_reroute_count < 2,
    )

    payable_counts = snapshot["payable_signal_counts"]
    linked_rows = int(payable_counts["upstream_linked_rows"])
    denial_row_count = int(payable_counts["denials_feedback_rows"])
    closed_compliance_count = int(snapshot["closed_compliance_count"])
    closed_compliance_signal_rows = int(payable_counts["closed_compliance_signal_rows"])
    payable_metrics = {
        "denials_feedback_row_count": denial_row_count,
        "linked_upstream_rate": round(_safe_rate(linked_rows, denial_row_count), 4),
        "payer_group_count": int(len(payable_counts["payer_group_counts"])),
        "denial_category_counts": payable_counts["denial_category_counts"],
        "issue_domain_counts": payable_counts["issue_domain_counts"],
        "closed_compliance_count": closed_compliance_count,
        "closed_compliance_signal_rows": closed_compliance_signal_rows,
    }
    payable_flags = []
    if denial_row_count == 0:
        payable_flags.append("Thin payable-state signal layer is absent.")
    if payable_metrics["linked_upstream_rate"] < 1.0:
        payable_flags.append("Downstream payable signals are not fully linked to upstream issue domains.")
    if closed_compliance_count < 2:
        payable_flags.append("Financially closed but compliance-relevant cases still look like a token one-off.")
    if closed_compliance_signal_rows == 0:
        payable_flags.append("Closed compliance cases still lack payable-state evidence.")
    if payable_metrics["payer_group_count"] < 2:
        payable_flags.append("Payable-state signals do not show any payer-group spread.")
    payable_status = _status_from_flags(
        failed=denial_row_count == 0
        or payable_metrics["linked_upstream_rate"] < 1.0
        or closed_compliance_signal_rows == 0,
        warned=closed_compliance_count < 2 or payable_metrics["payer_group_count"] < 2,
    )

    top_failure_class_by_department: dict[str, str] = {}
    for department, story_key in DEPARTMENT_TO_STORY_KEY.items():
        department_failures = expected.loc[
            (expected["department"] == department)
            & (expected["opportunity_status"] != "expected_charge_supported")
        ].copy()
        if not department_failures.empty:
            top_failure_class_by_department[story_key] = str(
                department_failures["opportunity_status"].value_counts().idxmax()
            )

    anti_pattern_metrics = {
        "denial_feedback_share_of_encounters": round(
            _safe_rate(denial_row_count, len(encounters)),
            4,
        ),
        "blank_upstream_issue_domain_count": int(
            (
                denials_feedback.get("linked_upstream_issue_domain", pd.Series(dtype=object))
                .fillna("")
                .eq("")
            ).sum()
        )
        if not denials_feedback.empty
        else 0,
        "top_failure_class_by_department": top_failure_class_by_department,
        "repeat_exception_rate_by_department": snapshot["repeat_exception_rate_by_department"],
        "distinct_dominant_queues": medium_volume_metrics["distinct_dominant_queues"],
    }
    anti_pattern_flags = []
    if anti_pattern_metrics["denial_feedback_share_of_encounters"] > 0.25:
        anti_pattern_flags.append("Denial feedback is becoming too central to the operating scope.")
    if anti_pattern_metrics["blank_upstream_issue_domain_count"] > 0:
        anti_pattern_flags.append("Some payable-state signals are disconnected from upstream issue domains.")
    if len(set(top_failure_class_by_department.values())) < 2:
        anti_pattern_flags.append("Expanded volume flattened department-specific failure signatures.")
    repeat_rates = list(snapshot["repeat_exception_rate_by_department"].values())
    if repeat_rates and len(set(repeat_rates)) == 1:
        anti_pattern_flags.append("Reroute and repeat-pattern distributions look flat instead of patterned.")
    anti_pattern_status = _status_from_flags(
        failed=bool(anti_pattern_flags),
        warned=False,
    )

    return _finalize_dimension_report(
        {
            "medium_volume_ops_realism": {
                "status": medium_volume_status,
                "metrics": medium_volume_metrics,
                "anti_pattern_flags": medium_volume_flags,
            },
            "payable_state_signal_realism": {
                "status": payable_status,
                "metrics": payable_metrics,
                "anti_pattern_flags": payable_flags,
            },
            "ops_mix_payable_antipatterns": {
                "status": anti_pattern_status,
                "metrics": anti_pattern_metrics,
                "anti_pattern_flags": anti_pattern_flags,
            },
        },
        extra={"ops_mix_snapshot": snapshot},
    )


def build_ops_mix_report(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_ops_mix_report_from_tables(
        encounters=_load_table("encounters", root),
        statuses=_load_table("claims_or_account_status", root),
        expected=_load_table("expected_charge_opportunities", root),
        queue=_load_table("exception_queue", root),
        queue_history=_load_table("queue_history", root),
        priority_scores=_load_table("priority_scores", root),
        denials_feedback=_load_optional_table("denials_feedback", root),
    )


def build_transition_ledger_snapshot_from_tables(
    *,
    queue: pd.DataFrame,
    queue_history: pd.DataFrame,
    intervention_tracking: pd.DataFrame | None = None,
    encounters: pd.DataFrame | None = None,
) -> dict[str, object]:
    intervention_tracking = (
        pd.DataFrame() if intervention_tracking is None else intervention_tracking.copy()
    )
    encounters = pd.DataFrame() if encounters is None else encounters.copy()
    latest_history = _latest_history(queue_history)
    latest_with_context = latest_history.copy()
    if not encounters.empty:
        latest_with_context = latest_with_context.merge(
            encounters[["encounter_id", "department", "service_line"]].drop_duplicates(),
            on="encounter_id",
            how="left",
        )
    elif not queue.empty:
        latest_with_context = latest_with_context.merge(
            queue[["encounter_id", "department", "service_line"]].drop_duplicates(),
            on="encounter_id",
            how="left",
        )

    transition_pairs = _transition_pair_counts(queue_history)
    routing_reasons = queue_history.get("routing_reason", pd.Series(dtype=object)).fillna("").astype(str)
    nonblank_routing_reasons = routing_reasons.loc[routing_reasons.ne("")]
    generic_routing_reasons = nonblank_routing_reasons.str.contains(
        "Initial queue placement under deterministic workflow rules.",
        regex=False,
    )
    days_in_prior_queue = queue_history.get("days_in_prior_queue", pd.Series(dtype=float)).dropna()
    reroute_buckets = (
        latest_history["reroute_count"].apply(_bucket_reroutes).value_counts().reindex(
            ["0", "1", "2", "3+"],
            fill_value=0,
        )
        if not latest_history.empty
        else pd.Series([0, 0, 0, 0], index=["0", "1", "2", "3+"])
    )

    checkpoint_distribution = (
        _int_dict(intervention_tracking["checkpoint_status"].value_counts())
        if not intervention_tracking.empty
        else {}
    )
    recommendation_distribution = (
        _int_dict(intervention_tracking["hold_expand_revise_recommendation"].value_counts())
        if not intervention_tracking.empty
        else {}
    )
    metric_delta_values = (
        intervention_tracking.get("metric_delta", pd.Series(dtype=float)).dropna()
        if not intervention_tracking.empty
        else pd.Series(dtype=float)
    )
    correction_turnaround_rows = (
        intervention_tracking.get("correction_turnaround_current_days", pd.Series(dtype=float))
        .dropna()
        .shape[0]
        if not intervention_tracking.empty
        else 0
    )
    owner_context_match_rate = round(
        float(
            intervention_tracking.get("owner_context_match_flag", pd.Series(dtype=bool))
            .fillna(False)
            .mean()
        ),
        4,
    ) if not intervention_tracking.empty else 0.0

    return {
        "queue_history_row_count": int(len(queue_history)),
        "exception_queue_row_count": int(len(queue)),
        "latest_history_row_count": int(len(latest_history)),
        "transition_event_density": round(_safe_rate(len(queue_history), len(queue)), 4),
        "multi_event_case_count": int(
            latest_history.get("transition_event_index", pd.Series(dtype=int)).gt(1).sum()
        )
        if not latest_history.empty
        else 0,
        "reroute_bucket_distribution": _int_dict(reroute_buckets),
        "distinct_transition_pair_count": int(len(transition_pairs)),
        "top_transition_pairs": _int_dict(transition_pairs.head(6)),
        "routing_reason_coverage": round(_safe_rate(len(nonblank_routing_reasons), len(queue_history)), 4),
        "generic_routing_reason_rate": round(
            _safe_rate(int(generic_routing_reasons.sum()), len(nonblank_routing_reasons)),
            4,
        ),
        "top_routing_reasons": _int_dict(nonblank_routing_reasons.value_counts().head(6)),
        "days_in_prior_queue_summary": {
            "min": float(days_in_prior_queue.min()) if not days_in_prior_queue.empty else 0.0,
            "median": float(days_in_prior_queue.median()) if not days_in_prior_queue.empty else 0.0,
            "max": float(days_in_prior_queue.max()) if not days_in_prior_queue.empty else 0.0,
            "nunique": int(days_in_prior_queue.nunique()) if not days_in_prior_queue.empty else 0,
        },
        "department_reroute_mean": {
            str(index): round(float(value), 4)
            for index, value in latest_with_context.groupby("department")["reroute_count"].mean().items()
        }
        if not latest_with_context.empty and "department" in latest_with_context.columns
        else {},
        "service_line_reroute_mean": {
            str(index): round(float(value), 4)
            for index, value in latest_with_context.groupby("service_line")["reroute_count"].mean().items()
        }
        if not latest_with_context.empty and "service_line" in latest_with_context.columns
        else {},
        "checkpoint_distribution": checkpoint_distribution,
        "recommendation_distribution": recommendation_distribution,
        "metric_delta_summary": {
            "nonzero_count": int(metric_delta_values.ne(0).sum()),
            "positive_count": int(metric_delta_values.gt(0).sum()),
            "median_delta": float(metric_delta_values.median()) if not metric_delta_values.empty else 0.0,
            "max_delta": float(metric_delta_values.max()) if not metric_delta_values.empty else 0.0,
        },
        "correction_turnaround_row_count": int(correction_turnaround_rows),
        "owner_context_match_rate": owner_context_match_rate,
        "recurring_pattern_coverage": round(
            _safe_rate(
                int(
                    intervention_tracking.get("recurring_issue_pattern", pd.Series(dtype=object))
                    .fillna("")
                    .ne("")
                    .sum()
                ),
                len(intervention_tracking),
            ),
            4,
        )
        if not intervention_tracking.empty
        else 0.0,
    }


def build_transition_ledger_report_from_tables(
    *,
    queue: pd.DataFrame,
    queue_history: pd.DataFrame,
    intervention_tracking: pd.DataFrame | None = None,
    encounters: pd.DataFrame | None = None,
) -> dict[str, object]:
    snapshot = build_transition_ledger_snapshot_from_tables(
        queue=queue,
        queue_history=queue_history,
        intervention_tracking=intervention_tracking,
        encounters=encounters,
    )
    department_reroute_mean = snapshot["department_reroute_mean"]
    reroute_buckets = snapshot["reroute_bucket_distribution"]
    checkpoint_distribution = snapshot["checkpoint_distribution"]
    recommendation_distribution = snapshot["recommendation_distribution"]
    metric_delta_summary = snapshot["metric_delta_summary"]

    transition_metrics = {
        "queue_history_row_count": snapshot["queue_history_row_count"],
        "exception_queue_row_count": snapshot["exception_queue_row_count"],
        "transition_event_density": snapshot["transition_event_density"],
        "multi_event_case_count": snapshot["multi_event_case_count"],
        "distinct_transition_pair_count": snapshot["distinct_transition_pair_count"],
        "routing_reason_coverage": snapshot["routing_reason_coverage"],
        "days_in_prior_queue_summary": snapshot["days_in_prior_queue_summary"],
    }
    transition_flags = []
    if snapshot["transition_event_density"] <= 1.1:
        transition_flags.append("Queue history still behaves too much like a one-row summary.")
    if snapshot["distinct_transition_pair_count"] < 5:
        transition_flags.append("Too few prior-to-current transition combinations are visible.")
    if snapshot["routing_reason_coverage"] < 0.95:
        transition_flags.append("Routing reasons are missing on too many transition rows.")
    if snapshot["days_in_prior_queue_summary"]["nunique"] < 4:
        transition_flags.append("Days in prior queue still looks too flat.")
    transition_status = _status_from_flags(
        failed=snapshot["transition_event_density"] <= 1.05
        or snapshot["routing_reason_coverage"] < 0.9
        or snapshot["distinct_transition_pair_count"] < 4,
        warned=snapshot["transition_event_density"] <= 1.2
        or snapshot["days_in_prior_queue_summary"]["nunique"] < 4,
    )

    procedural_mean = float(department_reroute_mean.get(PROCEDURAL_DEPARTMENT, 0.0))
    other_means = [
        float(value)
        for department, value in department_reroute_mean.items()
        if department != PROCEDURAL_DEPARTMENT
    ]
    handoff_metrics = {
        "reroute_bucket_distribution": reroute_buckets,
        "department_reroute_mean": department_reroute_mean,
        "service_line_reroute_mean": snapshot["service_line_reroute_mean"],
        "top_transition_pairs": snapshot["top_transition_pairs"],
    }
    handoff_flags = []
    if any(reroute_buckets.get(bucket, 0) == 0 for bucket in ("0", "1", "2")):
        handoff_flags.append("Encounter-level churn buckets do not cover 0, 1, and 2 reroutes.")
    if reroute_buckets.get("3+", 0) == 0:
        handoff_flags.append("No believable 3+ reroute cases are present.")
    if other_means and procedural_mean <= max(other_means):
        handoff_flags.append("Procedural work is not more handoff-heavy than the other V1 departments.")
    if len(set(department_reroute_mean.values())) <= 1:
        handoff_flags.append("Department churn patterns look flat instead of patterned.")
    handoff_status = _status_from_flags(
        failed=any(reroute_buckets.get(bucket, 0) == 0 for bucket in ("0", "1", "2"))
        or len(set(department_reroute_mean.values())) <= 1,
        warned=reroute_buckets.get("3+", 0) == 0
        or (other_means and procedural_mean <= max(other_means)),
    )

    intervention_metrics = {
        "checkpoint_distribution": checkpoint_distribution,
        "recommendation_distribution": recommendation_distribution,
        "metric_delta_summary": metric_delta_summary,
        "correction_turnaround_row_count": snapshot["correction_turnaround_row_count"],
        "owner_context_match_rate": snapshot["owner_context_match_rate"],
        "recurring_pattern_coverage": snapshot["recurring_pattern_coverage"],
    }
    intervention_flags = []
    if len(checkpoint_distribution) < 3:
        intervention_flags.append("Checkpoint states are still too degenerate.")
    if len(recommendation_distribution) < 3:
        intervention_flags.append("Hold / expand / revise distribution is too one-note.")
    if metric_delta_summary["positive_count"] == 0:
        intervention_flags.append("Baseline-versus-current deltas are not showing improvement anywhere.")
    if snapshot["correction_turnaround_row_count"] == 0:
        intervention_flags.append("Correction-turnaround evidence is absent from intervention support.")
    if snapshot["owner_context_match_rate"] < 1.0 or snapshot["recurring_pattern_coverage"] < 1.0:
        intervention_flags.append("Intervention evidence is disconnected from owner or recurring-pattern context.")
    intervention_status = _status_from_flags(
        failed=len(checkpoint_distribution) < 2
        or len(recommendation_distribution) < 2
        or snapshot["correction_turnaround_row_count"] == 0
        or snapshot["recurring_pattern_coverage"] < 1.0,
        warned=len(checkpoint_distribution) < 3
        or len(recommendation_distribution) < 3
        or metric_delta_summary["positive_count"] < max(snapshot["exception_queue_row_count"] // 4, 1),
    )

    anti_pattern_metrics = {
        "transition_event_density": snapshot["transition_event_density"],
        "generic_routing_reason_rate": snapshot["generic_routing_reason_rate"],
        "owner_context_match_rate": snapshot["owner_context_match_rate"],
        "recommendation_distribution": recommendation_distribution,
        "department_reroute_mean": department_reroute_mean,
    }
    anti_pattern_flags = []
    if snapshot["transition_event_density"] <= 1.05:
        anti_pattern_flags.append("Queue history still behaves like a one-row summary only.")
    if snapshot["generic_routing_reason_rate"] > 0.2:
        anti_pattern_flags.append("Routing reasons are still too generic.")
    if len(recommendation_distribution) <= 1:
        anti_pattern_flags.append("All interventions look equally successful or equally stagnant.")
    if snapshot["owner_context_match_rate"] < 1.0 or snapshot["recurring_pattern_coverage"] < 1.0:
        anti_pattern_flags.append("Intervention evidence is disconnected from recurring patterns or owner context.")
    if len(set(department_reroute_mean.values())) <= 1:
        anti_pattern_flags.append("Transition churn looks random or flat instead of service-line aware.")
    anti_pattern_status = _status_from_flags(
        failed=bool(anti_pattern_flags),
        warned=False,
    )

    return _finalize_dimension_report(
        {
            "transition_ledger_realism": {
                "status": transition_status,
                "metrics": transition_metrics,
                "anti_pattern_flags": transition_flags,
            },
            "handoff_churn_realism": {
                "status": handoff_status,
                "metrics": handoff_metrics,
                "anti_pattern_flags": handoff_flags,
            },
            "intervention_followthrough_realism": {
                "status": intervention_status,
                "metrics": intervention_metrics,
                "anti_pattern_flags": intervention_flags,
            },
            "transition_intervention_antipatterns": {
                "status": anti_pattern_status,
                "metrics": anti_pattern_metrics,
                "anti_pattern_flags": anti_pattern_flags,
            },
        },
        extra={"transition_ledger_snapshot": snapshot},
    )


def build_transition_ledger_snapshot(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_transition_ledger_snapshot_from_tables(
        queue=_load_table("exception_queue", root),
        queue_history=_load_table("queue_history", root),
        intervention_tracking=_load_optional_table("intervention_tracking", root),
        encounters=_load_table("encounters", root),
    )


def build_transition_ledger_report(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_transition_ledger_report_from_tables(
        queue=_load_table("exception_queue", root),
        queue_history=_load_table("queue_history", root),
        intervention_tracking=_load_optional_table("intervention_tracking", root),
        encounters=_load_table("encounters", root),
    )


def build_realism_scorecard_from_tables(
    *,
    statuses: pd.DataFrame,
    queue: pd.DataFrame,
    queue_history: pd.DataFrame,
    expected: pd.DataFrame,
    priority_scores: pd.DataFrame,
    kpis: pd.DataFrame,
    corrections: pd.DataFrame | None = None,
    intervention_tracking: pd.DataFrame | None = None,
    encounters: pd.DataFrame | None = None,
    documentation_events: pd.DataFrame | None = None,
    upstream_signals: pd.DataFrame | None = None,
    denials_feedback: pd.DataFrame | None = None,
) -> dict[str, object]:
    corrections = pd.DataFrame() if corrections is None else corrections.copy()
    intervention_tracking = (
        pd.DataFrame() if intervention_tracking is None else intervention_tracking.copy()
    )
    encounters = pd.DataFrame() if encounters is None else encounters.copy()
    documentation_events = (
        pd.DataFrame() if documentation_events is None else documentation_events.copy()
    )
    upstream_signals = pd.DataFrame() if upstream_signals is None else upstream_signals.copy()
    denials_feedback = pd.DataFrame() if denials_feedback is None else denials_feedback.copy()

    stage_age_summary = _active_stage_age_summary(queue)
    active_recoverability = statuses.loc[statuses["current_queue_active_flag"], "recoverability_status"]
    all_recoverability = statuses["recoverability_status"]

    recoverability_metrics = {
        "all_status_counts": _int_dict(all_recoverability.value_counts()),
        "active_counts": _int_dict(active_recoverability.value_counts()),
        "active_lost_rate": round(
            _safe_rate(
                int((active_recoverability == "Post-window financially lost").sum()),
                len(active_recoverability),
            ),
            4,
        ),
        "closed_compliance_count": int(
            (all_recoverability == "Financially closed but still compliance-relevant").sum()
        ),
    }
    missing_required_states = [
        state
        for state in (
            "Pre-final-bill recoverable",
            "Post-final-bill recoverable by correction / rebill",
            "Post-window financially lost",
            "Financially closed but still compliance-relevant",
        )
        if recoverability_metrics["all_status_counts"].get(state, 0) == 0
    ]
    active_lost_count = recoverability_metrics["active_counts"].get("Post-window financially lost", 0)
    recoverability_flags = []
    if missing_required_states:
        recoverability_flags.append(
            "Missing recoverability states: " + ", ".join(missing_required_states)
        )
    if active_lost_count == 0:
        recoverability_flags.append("No active post-window financially lost items are visible.")
    recoverability_status = _status_from_flags(
        failed=bool(missing_required_states or active_lost_count == 0),
        warned=recoverability_metrics["active_lost_rate"] < 0.12,
    )

    stage_counts = queue["current_prebill_stage"].value_counts()
    stage_medians = stage_age_summary["median"] if not stage_age_summary.empty else pd.Series(dtype=float)
    workflow_metrics = {
        "active_stage_counts": _int_dict(stage_counts),
        "active_stage_count": int(stage_counts.size),
        "stage_age_summary_days": _float_dict(stage_age_summary, ("min", "median", "max", "nunique")),
        "one_current_blocker_violations": int(
            queue.groupby("account_id")["current_primary_blocker_state"].nunique().ne(1).sum()
        ),
        "stage_age_median_range_days": float(stage_medians.max() - stage_medians.min())
        if not stage_medians.empty
        else 0.0,
    }
    flat_stage_ages = bool(not stage_medians.empty and workflow_metrics["stage_age_median_range_days"] < 1.0)
    workflow_flags = []
    if workflow_metrics["active_stage_count"] < 4:
        workflow_flags.append("Too few active stages are populated.")
    if workflow_metrics["one_current_blocker_violations"] > 0:
        workflow_flags.append("One-current-blocker rule is broken.")
    if flat_stage_ages:
        workflow_flags.append("Stage-specific aging is effectively flat across the active workflow.")
    workflow_status = _status_from_flags(
        failed=workflow_metrics["one_current_blocker_violations"] > 0 or flat_stage_ages,
        warned=workflow_metrics["active_stage_count"] < 5,
    )

    latest_history = _latest_history(queue_history)
    reroute_distribution = latest_history["reroute_count"].value_counts().sort_index()
    queue_history_metrics = {
        "queue_history_row_count": int(len(queue_history)),
        "encounter_level_row_count": int(len(latest_history)),
        "transition_event_density": round(_safe_rate(len(queue_history), len(queue)), 4),
        "reroute_count_distribution": _int_dict(reroute_distribution),
        "first_route_only_count": int((latest_history["reroute_count"] == 0).sum()),
        "rerouted_count": int((latest_history["reroute_count"] > 0).sum()),
        "multi_reroute_count": int((latest_history["reroute_count"] >= 2).sum()),
        "transition_count": int(
            ((queue_history["prior_queue"].fillna("") != "") & (queue_history["current_queue"].fillna("") != "")).sum()
        ),
        "routing_reason_populated_count": int(
            (queue_history.get("routing_reason", pd.Series(dtype=object)).fillna("") != "").sum()
        )
        if not queue_history.empty
        else 0,
    }
    queue_history_flags = []
    if queue_history_metrics["first_route_only_count"] == 0 or queue_history_metrics["rerouted_count"] == 0:
        queue_history_flags.append("Only one routing pattern is represented.")
    if queue_history_metrics["multi_reroute_count"] == 0:
        queue_history_flags.append("No multi-reroute cases are present.")
    if queue_history_metrics["transition_count"] == 0:
        queue_history_flags.append("No prior-to-current queue transitions are visible.")
    if queue_history_metrics["routing_reason_populated_count"] == 0:
        queue_history_flags.append("Routing reasons are absent.")
    if queue_history_metrics["transition_event_density"] <= 1.1:
        queue_history_flags.append("Queue history is still too close to a one-row summary.")
    queue_history_status = _status_from_flags(
        failed=queue_history_metrics["transition_count"] == 0
        or queue_history_metrics["routing_reason_populated_count"] == 0
        or queue_history_metrics["transition_event_density"] <= 1.05,
        warned=queue_history_metrics["multi_reroute_count"] == 0
        or queue_history_metrics["transition_event_density"] <= 1.2,
    )

    late_charge_rate = _find_kpi_value(kpis, "Late charge rate")
    lost_dollars = _find_kpi_value(kpis, "Dollars already lost after timing window")
    recoverable_dollars = _find_kpi_value(kpis, "Recoverable dollars still open")
    financial_metrics = {
        "late_charge_rate": round(late_charge_rate, 4),
        "lost_dollars_after_timing_window": round(lost_dollars, 2),
        "recoverable_dollars_still_open": round(recoverable_dollars, 2),
    }
    financial_flags = []
    if financial_metrics["late_charge_rate"] <= 0:
        financial_flags.append("Late charge rate is zero.")
    if financial_metrics["lost_dollars_after_timing_window"] <= 0:
        financial_flags.append("Lost dollars after timing window are zero.")
    if financial_metrics["recoverable_dollars_still_open"] <= 0:
        financial_flags.append("Recoverable dollars still open are zero.")
    financial_status = _status_from_flags(
        failed=bool(financial_flags),
        warned=financial_metrics["late_charge_rate"] < 0.05,
    )

    exception_metrics = {
        "recoverable_missed_charge_count": int(
            (expected["opportunity_status"] == "recoverable_missed_charge").sum()
        ),
        "unsupported_charge_risk_count": int(
            (expected["opportunity_status"] == "unsupported_charge_risk").sum()
        ),
        "suppressed_packaged_nonbillable_count": int(
            (expected["opportunity_status"] == "packaged_or_nonbillable_suppressed").sum()
        ),
    }
    exception_flags = []
    if exception_metrics["recoverable_missed_charge_count"] == 0:
        exception_flags.append("Undercapture cases are absent.")
    if exception_metrics["unsupported_charge_risk_count"] == 0:
        exception_flags.append("Unsupported or compliance-risk cases are absent.")
    if exception_metrics["suppressed_packaged_nonbillable_count"] == 0:
        exception_flags.append("Suppressed packaged or non-billable cases are absent.")
    exception_status = _status_from_flags(
        failed=bool(exception_flags),
        warned=False,
    )

    department_queue_mix = _department_queue_mix(queue)
    repeat_rates = priority_scores.groupby("department")["repeat_exception_flag"].mean()
    dominant_queues = {
        department: max(queue_counts, key=queue_counts.get)
        for department, queue_counts in department_queue_mix.items()
        if queue_counts
    }
    distribution_metrics = {
        "department_queue_mix": department_queue_mix,
        "department_repeat_exception_rate": {
            str(index): round(float(value), 4) for index, value in repeat_rates.to_dict().items()
        },
        "distinct_dominant_queues": len(set(dominant_queues.values())),
    }
    distribution_flags = []
    if distribution_metrics["distinct_dominant_queues"] < 2:
        distribution_flags.append("Departments collapse into the same dominant queue pattern.")
    if repeat_rates.nunique() <= 1:
        distribution_flags.append("Repeat exception patterns are flat across departments.")
    distribution_status = _status_from_flags(
        failed=bool(distribution_flags),
        warned=len(distribution_metrics["department_queue_mix"]) < 3,
    )

    postbill_recoverable_cases = statuses.loc[
        statuses["recoverability_status"] == "Post-final-bill recoverable by correction / rebill",
        ["encounter_id", "claim_id"],
    ].drop_duplicates()
    correction_supported = 0
    if not corrections.empty and not postbill_recoverable_cases.empty:
        correction_supported = int(
            corrections["encounter_id"].isin(postbill_recoverable_cases["encounter_id"]).sum()
        )
    correction_metrics = {
        "postbill_recoverable_case_count": int(len(postbill_recoverable_cases)),
        "correction_history_row_count": int(len(corrections)),
        "postbill_cases_with_correction_history": correction_supported,
    }
    correction_flags = []
    if correction_metrics["postbill_recoverable_case_count"] == 0:
        correction_flags.append("No post-final-bill recoverable cases are present.")
    if correction_metrics["postbill_cases_with_correction_history"] < correction_metrics["postbill_recoverable_case_count"]:
        correction_flags.append("Not every post-final-bill recoverable case has correction-history support.")
    correction_status = _status_from_flags(
        failed=bool(correction_flags),
        warned=correction_metrics["correction_history_row_count"] == 0,
    )

    department_story_report = build_department_story_report_from_tables(
        encounters=encounters,
        documentation_events=documentation_events,
        upstream_signals=upstream_signals,
        expected=expected,
        queue=queue,
        queue_history=queue_history,
        corrections=corrections,
    )
    suppression_balance_report = build_suppression_balance_report_from_tables(
        expected=expected,
    )
    ops_mix_report = build_ops_mix_report_from_tables(
        encounters=encounters,
        statuses=statuses,
        expected=expected,
        queue=queue,
        queue_history=queue_history,
        priority_scores=priority_scores,
        denials_feedback=denials_feedback,
    )
    transition_ledger_report = build_transition_ledger_report_from_tables(
        queue=queue,
        queue_history=queue_history,
        intervention_tracking=intervention_tracking,
        encounters=encounters,
    )

    return _finalize_dimension_report(
        {
            "recoverability_mix": {
                "status": recoverability_status,
                "metrics": recoverability_metrics,
                "anti_pattern_flags": recoverability_flags,
            },
            "workflow_state_realism": {
                "status": workflow_status,
                "metrics": workflow_metrics,
                "anti_pattern_flags": workflow_flags,
            },
            "queue_history_realism": {
                "status": queue_history_status,
                "metrics": queue_history_metrics,
                "anti_pattern_flags": queue_history_flags,
            },
            "financial_consequence_realism": {
                "status": financial_status,
                "metrics": financial_metrics,
                "anti_pattern_flags": financial_flags,
            },
            "exception_class_balance": {
                "status": exception_status,
                "metrics": exception_metrics,
                "anti_pattern_flags": exception_flags,
            },
            "distribution_realism": {
                "status": distribution_status,
                "metrics": distribution_metrics,
                "anti_pattern_flags": distribution_flags,
            },
            "correction_history_realism": {
                "status": correction_status,
                "metrics": correction_metrics,
                "anti_pattern_flags": correction_flags,
            },
            **transition_ledger_report["dimensions"],
            **department_story_report["dimensions"],
            **suppression_balance_report["dimensions"],
            **ops_mix_report["dimensions"],
        },
        extra={
            "department_scenario_counts": department_story_report["department_scenario_counts"],
            "department_failure_mode_mix": department_story_report["department_failure_mode_mix"],
            "what_still_feels_fake_by_department": department_story_report[
                "what_still_feels_fake_by_department"
            ],
            "balance_snapshot": suppression_balance_report["balance_snapshot"],
            "ops_mix_snapshot": ops_mix_report["ops_mix_snapshot"],
            "transition_ledger_snapshot": transition_ledger_report["transition_ledger_snapshot"],
        },
    )


def build_realism_scorecard(repo_root: Path | None = None) -> dict[str, object]:
    root = resolve_repo_root(repo_root)
    return build_realism_scorecard_from_tables(
        statuses=_load_table("claims_or_account_status", root),
        queue=_load_table("exception_queue", root),
        queue_history=_load_table("queue_history", root),
        expected=_load_table("expected_charge_opportunities", root),
        priority_scores=_load_table("priority_scores", root),
        kpis=_load_table("kpi_snapshot", root),
        corrections=_load_optional_table("corrections_rebills", root),
        intervention_tracking=_load_optional_table("intervention_tracking", root),
        encounters=_load_table("encounters", root),
        documentation_events=_load_table("documentation_events", root),
        upstream_signals=_load_table("upstream_activity_signals", root),
        denials_feedback=_load_optional_table("denials_feedback", root),
    )


def _format_metric_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _top_numeric_improvements(
    baseline: dict[str, object], current: dict[str, object], *, limit: int = 2
) -> list[str]:
    deltas: list[tuple[float, str]] = []
    for metric_name, current_value in current.items():
        baseline_value = baseline.get(metric_name)
        if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
            delta = float(current_value) - float(baseline_value)
            if delta > 0:
                deltas.append((delta, metric_name))
    deltas.sort(reverse=True)
    return [metric_name for _, metric_name in deltas[:limit]]


def render_markdown_report(report: dict[str, object], title: str) -> str:
    lines = [f"# {title}", "", f"Overall status: **{report['overall_status']}**", ""]
    lines.append("## Summary")
    counts = report["summary_counts"]
    lines.append(
        f"- pass: {counts['pass']} | warn: {counts['warn']} | fail: {counts['fail']}"
    )
    lines.append("")
    for dimension_name, dimension in report["dimensions"].items():
        lines.append(f"## {dimension_name.replace('_', ' ').title()}")
        lines.append(f"- status: **{dimension['status']}**")
        lines.append("- metrics:")
        for metric_name, metric_value in dimension["metrics"].items():
            lines.append(f"  - {metric_name}: {_format_metric_value(metric_value)}")
        if dimension["anti_pattern_flags"]:
            lines.append("- anti-pattern flags:")
            for flag in dimension["anti_pattern_flags"]:
                lines.append(f"  - {flag}")
        else:
            lines.append("- anti-pattern flags: none")
        lines.append("")
    lines.append("## What Still Feels Fake")
    if report["what_still_feels_fake"]:
        for flag in report["what_still_feels_fake"]:
            lines.append(f"- {flag}")
    else:
        lines.append("- No realism anti-pattern flags remain.")
    lines.append("")
    return "\n".join(lines)


def render_department_story_markdown_report(report: dict[str, object], title: str) -> str:
    lines = [f"# {title}", "", f"Overall status: **{report['overall_status']}**", ""]
    lines.append("## Summary")
    counts = report["summary_counts"]
    lines.append(
        f"- pass: {counts['pass']} | warn: {counts['warn']} | fail: {counts['fail']}"
    )
    lines.append("")

    for story_key in DEPARTMENT_STORY_ORDER:
        dimension_name = {
            "infusion": "infusion_story_realism",
            "radiology_ir": "radiology_story_realism",
            "or_procedural": "or_procedural_story_realism",
        }[story_key]
        dimension = report["dimensions"][dimension_name]
        lines.append(f"## {DEPARTMENT_STORY_LABELS[story_key]}")
        lines.append(f"- status: **{dimension['status']}**")
        lines.append(
            f"- scenario counts: {_format_metric_value(report['department_scenario_counts'][story_key])}"
        )
        lines.append(
            f"- failure-mode mix: {_format_metric_value(report['department_failure_mode_mix'][story_key])}"
        )
        if dimension["anti_pattern_flags"]:
            lines.append("- what still feels fake:")
            for flag in dimension["anti_pattern_flags"]:
                lines.append(f"  - {flag}")
        else:
            lines.append("- what still feels fake: none")
        lines.append("")

    cross_dimension = report["dimensions"]["department_story_antipatterns"]
    lines.append("## Cross-Department Anti-Patterns")
    lines.append(f"- status: **{cross_dimension['status']}**")
    lines.append(
        f"- metrics: {_format_metric_value(cross_dimension['metrics'])}"
    )
    if cross_dimension["anti_pattern_flags"]:
        lines.append("- anti-pattern flags:")
        for flag in cross_dimension["anti_pattern_flags"]:
            lines.append(f"  - {flag}")
    else:
        lines.append("- anti-pattern flags: none")
    lines.append("")
    return "\n".join(lines)


def write_realism_report(
    report: dict[str, object],
    *,
    report_basename: str,
    repo_root: Path | None = None,
    title: str | None = None,
) -> tuple[Path, Path]:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{report_basename}.json"
    markdown_path = output_dir / f"{report_basename}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_markdown_report(report, title or report_basename.replace("_", " ").title()),
        encoding="utf-8",
    )
    return markdown_path, json_path


def render_realism_before_after_diff(
    baseline_report: dict[str, object],
    current_report: dict[str, object],
) -> str:
    baseline_dimensions = baseline_report.get("dimensions", {})
    current_dimensions = current_report.get("dimensions", {})
    lines = ["# Realism Before/After Diff", ""]
    lines.append(
        f"Baseline overall status: **{baseline_report.get('overall_status', 'unknown')}**"
    )
    lines.append(
        f"Post-tuning overall status: **{current_report.get('overall_status', 'unknown')}**"
    )
    lines.append("")

    dimension_sections = (
        ("Recoverability", "recoverability_mix"),
        ("Workflow State", "workflow_state_realism"),
        ("Queue History", "queue_history_realism"),
        ("Financial Consequences", "financial_consequence_realism"),
        ("Correction History", "correction_history_realism"),
        ("Exception Balance", "exception_class_balance"),
        ("Distribution", "distribution_realism"),
    )
    for section_title, dimension_name in dimension_sections:
        baseline_dimension = baseline_dimensions.get(dimension_name, {})
        current_dimension = current_dimensions.get(dimension_name, {})
        baseline_metrics = baseline_dimension.get("metrics", {})
        current_metrics = current_dimension.get("metrics", {})
        if not baseline_metrics and not current_metrics:
            continue

        lines.append(f"## {section_title}")
        lines.append(
            f"- status: {_format_metric_value(baseline_dimension.get('status', 'unknown'))} -> {_format_metric_value(current_dimension.get('status', 'unknown'))}"
        )
        metric_names = sorted(set(baseline_metrics) | set(current_metrics))
        for metric_name in metric_names:
            lines.append(
                f"- {metric_name}: {_format_metric_value(baseline_metrics.get(metric_name, 0))} -> {_format_metric_value(current_metrics.get(metric_name, 0))}"
            )
        lines.append("")

    baseline_flags = set(baseline_report.get("what_still_feels_fake", []))
    current_flags = set(current_report.get("what_still_feels_fake", []))
    resolved_flags = sorted(baseline_flags - current_flags)
    remaining_flags = sorted(current_flags)

    lines.append("## Anti-Pattern Resolution")
    if resolved_flags:
        for flag in resolved_flags:
            lines.append(f"- Resolved: {flag}")
    else:
        lines.append("- Resolved: none")
    if remaining_flags:
        for flag in remaining_flags:
            lines.append(f"- Remaining: {flag}")
    else:
        lines.append("- Remaining: none")
    lines.append("")
    return "\n".join(lines)


def write_realism_before_after_diff(
    baseline_report: dict[str, object],
    current_report: dict[str, object],
    *,
    repo_root: Path | None = None,
    output_filename: str = "realism_before_after_diff.md",
) -> Path:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    output_path.write_text(
        render_realism_before_after_diff(baseline_report, current_report),
        encoding="utf-8",
    )
    return output_path


def render_transition_ledger_markdown_report(report: dict[str, object], title: str) -> str:
    snapshot = report["transition_ledger_snapshot"]
    lines = [f"# {title}", "", f"Overall status: **{report['overall_status']}**", ""]
    lines.append("## Queue History Shape")
    lines.append(
        f"- queue_history rows: {snapshot['queue_history_row_count']} vs exception_queue rows: {snapshot['exception_queue_row_count']}"
    )
    lines.append(f"- transition-event density: {snapshot['transition_event_density']}")
    lines.append(f"- multi-event cases: {snapshot['multi_event_case_count']}")
    lines.append(f"- reroute buckets: {_format_metric_value(snapshot['reroute_bucket_distribution'])}")
    lines.append("")
    lines.append("## Transition Evidence")
    lines.append(f"- top queue transitions: {_format_metric_value(snapshot['top_transition_pairs'])}")
    lines.append(f"- routing-reason coverage: {snapshot['routing_reason_coverage']}")
    lines.append(f"- top routing reasons: {_format_metric_value(snapshot['top_routing_reasons'])}")
    lines.append(
        f"- days in prior queue summary: {_format_metric_value(snapshot['days_in_prior_queue_summary'])}"
    )
    lines.append("")
    lines.append("## Intervention Follow-Through")
    lines.append(
        f"- checkpoint distribution: {_format_metric_value(snapshot['checkpoint_distribution'])}"
    )
    lines.append(
        f"- recommendation distribution: {_format_metric_value(snapshot['recommendation_distribution'])}"
    )
    lines.append(
        f"- metric delta summary: {_format_metric_value(snapshot['metric_delta_summary'])}"
    )
    lines.append(
        f"- correction turnaround rows: {_format_metric_value(snapshot['correction_turnaround_row_count'])}"
    )
    lines.append("")
    lines.append("## What Still Feels Fake")
    if report["what_still_feels_fake"]:
        for flag in report["what_still_feels_fake"]:
            lines.append(f"- {flag}")
    else:
        lines.append("- No transition-ledger or intervention follow-through flags remain.")
    lines.append("")
    return "\n".join(lines)


def write_transition_ledger_report(
    report: dict[str, object],
    *,
    report_basename: str = "transition_ledger_report",
    repo_root: Path | None = None,
    title: str = "Transition Ledger Report",
) -> tuple[Path, Path]:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{report_basename}.json"
    markdown_path = output_dir / f"{report_basename}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_transition_ledger_markdown_report(report, title),
        encoding="utf-8",
    )
    return markdown_path, json_path


def render_transition_ledger_before_after_diff(
    baseline_snapshot: dict[str, object],
    current_report: dict[str, object],
) -> str:
    current_snapshot = current_report["transition_ledger_snapshot"]
    lines = ["# Transition Ledger Before/After Diff", ""]
    lines.append("## Queue History Shape")
    for metric_name in (
        "queue_history_row_count",
        "exception_queue_row_count",
        "transition_event_density",
        "multi_event_case_count",
    ):
        lines.append(
            f"- {metric_name}: {_format_metric_value(baseline_snapshot.get(metric_name, 0))} -> {_format_metric_value(current_snapshot[metric_name])}"
        )
    lines.append(
        f"- reroute buckets: {_format_metric_value(baseline_snapshot.get('reroute_bucket_distribution', {}))} -> {_format_metric_value(current_snapshot['reroute_bucket_distribution'])}"
    )
    lines.append("")
    lines.append("## Transition Evidence")
    lines.append(
        f"- top transitions: {_format_metric_value(baseline_snapshot.get('top_transition_pairs', {}))} -> {_format_metric_value(current_snapshot['top_transition_pairs'])}"
    )
    lines.append(
        f"- routing-reason coverage: {_format_metric_value(baseline_snapshot.get('routing_reason_coverage', 0))} -> {_format_metric_value(current_snapshot['routing_reason_coverage'])}"
    )
    lines.append(
        f"- days in prior queue summary: {_format_metric_value(baseline_snapshot.get('days_in_prior_queue_summary', {}))} -> {_format_metric_value(current_snapshot['days_in_prior_queue_summary'])}"
    )
    lines.append("")
    lines.append("## Intervention Follow-Through")
    lines.append(
        f"- checkpoint distribution: {_format_metric_value(baseline_snapshot.get('checkpoint_distribution', {}))} -> {_format_metric_value(current_snapshot['checkpoint_distribution'])}"
    )
    lines.append(
        f"- recommendation distribution: {_format_metric_value(baseline_snapshot.get('recommendation_distribution', {}))} -> {_format_metric_value(current_snapshot['recommendation_distribution'])}"
    )
    lines.append(
        f"- metric delta summary: {_format_metric_value(baseline_snapshot.get('metric_delta_summary', {}))} -> {_format_metric_value(current_snapshot['metric_delta_summary'])}"
    )
    lines.append("")
    lines.append("## Remaining Notes")
    if current_report["what_still_feels_fake"]:
        for flag in current_report["what_still_feels_fake"]:
            lines.append(f"- {flag}")
    else:
        lines.append("- No transition-ledger or intervention follow-through flags remain.")
    lines.append("")
    return "\n".join(lines)


def write_transition_ledger_before_after_diff(
    baseline_snapshot: dict[str, object],
    current_report: dict[str, object],
    *,
    repo_root: Path | None = None,
    output_filename: str = "transition_ledger_before_after_diff.md",
) -> Path:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    output_path.write_text(
        render_transition_ledger_before_after_diff(baseline_snapshot, current_report),
        encoding="utf-8",
    )
    return output_path


def write_department_story_report(
    report: dict[str, object],
    *,
    report_basename: str,
    repo_root: Path | None = None,
    title: str | None = None,
) -> tuple[Path, Path]:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{report_basename}.json"
    markdown_path = output_dir / f"{report_basename}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_department_story_markdown_report(
            report, title or report_basename.replace("_", " ").title()
        ),
        encoding="utf-8",
    )
    return markdown_path, json_path


def render_suppression_balance_markdown_report(report: dict[str, object], title: str) -> str:
    lines = [f"# {title}", "", f"Overall status: **{report['overall_status']}**", ""]
    lines.append("## Summary")
    counts = report["summary_counts"]
    lines.append(f"- pass: {counts['pass']} | warn: {counts['warn']} | fail: {counts['fail']}")
    lines.append(
        f"- overall counts/rates: {_format_metric_value(report['balance_snapshot']['overall'])}"
    )
    lines.append("")
    for dimension_name in (
        "undercapture_balance_realism",
        "unsupported_balance_realism",
        "suppression_balance_realism",
        "suppression_balance_antipatterns",
    ):
        dimension = report["dimensions"][dimension_name]
        lines.append(f"## {dimension_name.replace('_', ' ').title()}")
        lines.append(f"- status: **{dimension['status']}**")
        lines.append(f"- metrics: {_format_metric_value(dimension['metrics'])}")
        if dimension["anti_pattern_flags"]:
            lines.append("- anti-pattern flags:")
            for flag in dimension["anti_pattern_flags"]:
                lines.append(f"  - {flag}")
        else:
            lines.append("- anti-pattern flags: none")
        lines.append("")
    return "\n".join(lines)


def write_suppression_balance_report(
    report: dict[str, object],
    *,
    report_basename: str,
    repo_root: Path | None = None,
    title: str | None = None,
) -> tuple[Path, Path]:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{report_basename}.json"
    markdown_path = output_dir / f"{report_basename}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_suppression_balance_markdown_report(
            report, title or report_basename.replace("_", " ").title()
        ),
        encoding="utf-8",
    )
    return markdown_path, json_path


def render_ops_mix_markdown_report(report: dict[str, object], title: str) -> str:
    lines = [f"# {title}", "", f"Overall status: **{report['overall_status']}**", ""]
    counts = report["summary_counts"]
    lines.append("## Summary")
    lines.append(f"- pass: {counts['pass']} | warn: {counts['warn']} | fail: {counts['fail']}")
    lines.append(
        f"- ops-mix snapshot: {_format_metric_value(report['ops_mix_snapshot'])}"
    )
    lines.append("")
    for dimension_name in (
        "medium_volume_ops_realism",
        "payable_state_signal_realism",
        "ops_mix_payable_antipatterns",
    ):
        dimension = report["dimensions"][dimension_name]
        lines.append(f"## {dimension_name.replace('_', ' ').title()}")
        lines.append(f"- status: **{dimension['status']}**")
        lines.append(f"- metrics: {_format_metric_value(dimension['metrics'])}")
        if dimension["anti_pattern_flags"]:
            lines.append("- anti-pattern flags:")
            for flag in dimension["anti_pattern_flags"]:
                lines.append(f"  - {flag}")
        else:
            lines.append("- anti-pattern flags: none")
        lines.append("")
    return "\n".join(lines)


def write_ops_mix_report(
    report: dict[str, object],
    *,
    report_basename: str,
    repo_root: Path | None = None,
    title: str | None = None,
) -> tuple[Path, Path]:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{report_basename}.json"
    markdown_path = output_dir / f"{report_basename}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_ops_mix_markdown_report(
            report, title or report_basename.replace("_", " ").title()
        ),
        encoding="utf-8",
    )
    return markdown_path, json_path


def render_department_story_before_after_diff(
    baseline_snapshot: dict[str, dict[str, object]],
    current_report: dict[str, object],
) -> str:
    current_snapshot = current_report["department_scenario_counts"]
    lines = ["# Department Story Before/After Diff", ""]

    for story_key in DEPARTMENT_STORY_ORDER:
        lines.append(f"## {DEPARTMENT_STORY_LABELS[story_key]}")
        baseline = baseline_snapshot.get(story_key, {})
        current = current_snapshot.get(story_key, {})
        top_improvements = _top_numeric_improvements(baseline, current)
        if top_improvements:
            lines.append(
                "- top realism improvements: "
                + ", ".join(top_improvements)
            )
        else:
            lines.append("- top realism improvements: no positive count deltas recorded")
        for metric_name, current_value in current.items():
            baseline_value = baseline.get(metric_name, 0 if not isinstance(current_value, dict) else {})
            lines.append(
                f"- {metric_name}: {_format_metric_value(baseline_value)} -> {_format_metric_value(current_value)}"
            )
        mix = current_report["department_failure_mode_mix"].get(story_key, {})
        lines.append(f"- current failure-mode mix: {_format_metric_value(mix)}")
        remaining = current_report["what_still_feels_fake_by_department"].get(story_key, [])
        if remaining:
            lines.append("- remaining realism gaps:")
            for flag in remaining:
                lines.append(f"  - {flag}")
        else:
            lines.append("- remaining realism gaps: none")
        lines.append("")

    cross_remaining = current_report["what_still_feels_fake_by_department"].get("cross_department", [])
    lines.append("## Cross-Department Notes")
    if cross_remaining:
        for flag in cross_remaining:
            lines.append(f"- {flag}")
    else:
        lines.append("- No cross-department anti-pattern flags remain.")
    lines.append("")
    return "\n".join(lines)


def write_department_story_before_after_diff(
    baseline_snapshot: dict[str, dict[str, object]],
    current_report: dict[str, object],
    *,
    repo_root: Path | None = None,
    output_filename: str = "department_story_before_after_diff.md",
) -> Path:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    output_path.write_text(
        render_department_story_before_after_diff(baseline_snapshot, current_report),
        encoding="utf-8",
    )
    return output_path


def render_suppression_balance_before_after_diff(
    baseline_snapshot: dict[str, object],
    current_report: dict[str, object],
) -> str:
    current_snapshot = current_report["balance_snapshot"]
    lines = ["# Suppression Balance Before/After Diff", ""]

    lines.append("## Overall Mix")
    lines.append(
        f"- status counts: {_format_metric_value(baseline_snapshot['overall']['status_counts'])} -> {_format_metric_value(current_snapshot['overall']['status_counts'])}"
    )
    lines.append(
        f"- status rates: {_format_metric_value(baseline_snapshot['overall']['status_rates'])} -> {_format_metric_value(current_snapshot['overall']['status_rates'])}"
    )
    lines.append("")

    for story_key in DEPARTMENT_STORY_ORDER:
        lines.append(f"## {DEPARTMENT_STORY_LABELS[story_key]}")
        baseline_department = baseline_snapshot["by_department"].get(story_key, {})
        current_department = current_snapshot["by_department"].get(story_key, {})
        lines.append(
            f"- status counts: {_format_metric_value(baseline_department.get('status_counts', {}))} -> {_format_metric_value(current_department.get('status_counts', {}))}"
        )
        lines.append(
            f"- top failure class: {_format_metric_value(baseline_department.get('top_failure_class', ''))} -> {_format_metric_value(current_department.get('top_failure_class', ''))}"
        )
        lines.append(
            f"- suppression reasons: {_format_metric_value(baseline_department.get('suppression_reason_counts', {}))} -> {_format_metric_value(current_department.get('suppression_reason_counts', {}))}"
        )
        lines.append(
            f"- unsupported reasons: {_format_metric_value(baseline_department.get('unsupported_reason_counts', {}))} -> {_format_metric_value(current_department.get('unsupported_reason_counts', {}))}"
        )
        lines.append("")

    lines.append("## Balance Notes")
    if current_report["what_still_feels_fake"]:
        for flag in current_report["what_still_feels_fake"]:
            lines.append(f"- {flag}")
    else:
        lines.append("- No balance anti-pattern flags remain.")
    lines.append("")
    return "\n".join(lines)


def write_suppression_balance_before_after_diff(
    baseline_snapshot: dict[str, object],
    current_report: dict[str, object],
    *,
    repo_root: Path | None = None,
    output_filename: str = "suppression_balance_before_after_diff.md",
) -> Path:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    output_path.write_text(
        render_suppression_balance_before_after_diff(baseline_snapshot, current_report),
        encoding="utf-8",
    )
    return output_path


def render_ops_mix_before_after_diff(
    baseline_snapshot: dict[str, object],
    current_report: dict[str, object],
) -> str:
    current_snapshot = current_report["ops_mix_snapshot"]
    lines = ["# Ops Mix Before/After Diff", ""]
    lines.append("## Row Counts")
    for metric_name, current_value in current_snapshot["artifact_row_counts"].items():
        baseline_value = baseline_snapshot.get("artifact_row_counts", {}).get(metric_name, 0)
        lines.append(
            f"- {metric_name}: {_format_metric_value(baseline_value)} -> {_format_metric_value(current_value)}"
        )
    lines.append("")
    lines.append("## Queue Concentration")
    lines.append(
        f"- department queue mix: {_format_metric_value(baseline_snapshot.get('department_queue_mix', {}))} -> {_format_metric_value(current_snapshot['department_queue_mix'])}"
    )
    lines.append("")
    lines.append("## Reroute Distribution")
    lines.append(
        f"- reroute distribution: {_format_metric_value(baseline_snapshot.get('reroute_distribution', {}))} -> {_format_metric_value(current_snapshot['reroute_distribution'])}"
    )
    lines.append("")
    lines.append("## Repeat Patterns")
    lines.append(
        f"- repeat exception rate by department: {_format_metric_value(baseline_snapshot.get('repeat_exception_rate_by_department', {}))} -> {_format_metric_value(current_snapshot['repeat_exception_rate_by_department'])}"
    )
    lines.append(
        f"- repeat root-cause clusters: {_format_metric_value(baseline_snapshot.get('repeat_root_cause_clusters_by_department', {}))} -> {_format_metric_value(current_snapshot['repeat_root_cause_clusters_by_department'])}"
    )
    lines.append("")
    lines.append("## Payable-State Signals")
    lines.append(
        f"- closed compliance count: {_format_metric_value(baseline_snapshot.get('closed_compliance_count', 0))} -> {_format_metric_value(current_snapshot['closed_compliance_count'])}"
    )
    lines.append(
        f"- payable signal counts: {_format_metric_value(baseline_snapshot.get('payable_signal_counts', {}))} -> {_format_metric_value(current_snapshot['payable_signal_counts'])}"
    )
    lines.append("")
    lines.append("## Remaining Notes")
    if current_report["what_still_feels_fake"]:
        for flag in current_report["what_still_feels_fake"]:
            lines.append(f"- {flag}")
    else:
        lines.append("- No ops-mix or payable-state anti-pattern flags remain.")
    lines.append("")
    return "\n".join(lines)


def write_ops_mix_before_after_diff(
    baseline_snapshot: dict[str, object],
    current_report: dict[str, object],
    *,
    repo_root: Path | None = None,
    output_filename: str = "ops_mix_before_after_diff.md",
) -> Path:
    root = resolve_repo_root(repo_root)
    output_dir = root / ARTIFACT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    output_path.write_text(
        render_ops_mix_before_after_diff(baseline_snapshot, current_report),
        encoding="utf-8",
    )
    return output_path
