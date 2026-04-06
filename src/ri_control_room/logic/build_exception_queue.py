from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.logic.derive_expected_charge_opportunities import (
    OUTPUT_FILENAME as EXPECTED_OPPORTUNITIES_FILENAME,
    write_expected_charge_opportunities_parquet,
)
from ri_control_room.reference_loader import load_reference_csv
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
from ri_control_room.synthetic.workflow_profiles import get_workflow_profile


OUTPUT_FILENAME = "exception_queue.parquet"

ACTIVE_STAGE_QUEUE_MAP = {
    "Charge capture pending": "Charge Reconciliation Monitor",
    "Documentation pending": "Documentation Support Exceptions",
    "Coding pending": "Coding Pending Review",
    "Prebill edit / hold": "Modifiers / Edits / Prebill Holds",
    "Correction / rebill pending": "Correction / Rebill Pending",
}

ACTIVE_STAGE_ISSUE_DOMAIN_MAP = {
    "Charge capture pending": "Charge capture failure",
    "Documentation pending": "Documentation support failure",
    "Coding pending": "Coding failure",
    "Prebill edit / hold": "Billing / claim-edit failure",
    "Correction / rebill pending": "Billing / claim-edit failure",
}


def _index_reference_rows(
    rows: list[dict[str, str]],
    *,
    key: str,
    table_name: str,
) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in indexed:
            raise ValueError(f"{table_name} has multiple rows for {key}={value}")
        indexed[value] = row
    return indexed


def _load_inputs(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    encounter_path = processed_dir / ENCOUNTERS_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    documentation_path = processed_dir / DOCUMENTATION_FILENAME
    expected_path = processed_dir / EXPECTED_OPPORTUNITIES_FILENAME

    if not encounter_path.exists():
        write_encounters_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    if not documentation_path.exists():
        write_documentation_events_parquet(repo_root)
    if not expected_path.exists():
        write_expected_charge_opportunities_parquet(repo_root)

    return (
        pd.read_parquet(encounter_path),
        pd.read_parquet(status_path),
        pd.read_parquet(documentation_path),
        pd.read_parquet(expected_path),
    )


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() == "true"


def _int_value(value: object) -> int:
    if isinstance(value, int):
        return value
    return int(str(value).strip())


def _documentation_subset(
    documentation_groups: dict[str, pd.DataFrame], encounter_id: str
) -> pd.DataFrame:
    return documentation_groups.get(encounter_id, pd.DataFrame())


def derive_stage_entry_ts(
    stage_name: str,
    encounter_row: pd.Series,
    documentation_events: pd.DataFrame,
) -> pd.Timestamp:
    service_end_ts = pd.Timestamp(encounter_row["service_end_ts"])

    if stage_name == "Charge capture pending":
        return service_end_ts

    if stage_name == "Documentation pending":
        deficient_docs = documentation_events.loc[
            documentation_events["documentation_gap_type"].fillna("") != ""
        ]
        if deficient_docs.empty:
            deficient_docs = documentation_events.loc[
                ~documentation_events["supports_charge_flag"].fillna(False)
            ]
        candidate_ts = deficient_docs["event_ts"].dropna()
        return pd.Timestamp(candidate_ts.min()) if not candidate_ts.empty else service_end_ts

    if stage_name == "Coding pending":
        completion_ts = documentation_events["completion_ts"].dropna()
        if not completion_ts.empty:
            return pd.Timestamp(completion_ts.max()) + timedelta(hours=2)
        return service_end_ts + timedelta(hours=2)

    if stage_name == "Prebill edit / hold":
        completion_ts = documentation_events["completion_ts"].dropna()
        if not completion_ts.empty:
            return pd.Timestamp(completion_ts.max()) + timedelta(hours=4)
        return service_end_ts + timedelta(hours=4)

    if stage_name == "Correction / rebill pending":
        final_bill_ts = encounter_row.get("final_bill_datetime")
        if pd.notna(final_bill_ts):
            return pd.Timestamp(final_bill_ts) + timedelta(days=2)
        return service_end_ts + timedelta(days=2)

    if stage_name == "Ready to final bill":
        completion_ts = documentation_events["completion_ts"].dropna()
        if not completion_ts.empty:
            return pd.Timestamp(completion_ts.max()) + timedelta(hours=1)
        return service_end_ts + timedelta(hours=1)

    if stage_name == "Final billed" and pd.notna(encounter_row.get("final_bill_datetime")):
        return pd.Timestamp(encounter_row["final_bill_datetime"])

    return pd.Timestamp(encounter_row.get("encounter_open_ts", service_end_ts))


def _queue_snapshot_ts(
    stage_entry_ts: pd.Timestamp,
    stage_age_days: int,
) -> pd.Timestamp:
    return stage_entry_ts + timedelta(days=max(stage_age_days, 0))


def _aging_bucket(age_days: int, sla_target_days: int, overdue_threshold_days: int) -> str:
    if age_days <= sla_target_days:
        return f"0-{sla_target_days} days"
    if age_days <= overdue_threshold_days:
        return f"{sla_target_days + 1}-{overdue_threshold_days} days"
    return f"{overdue_threshold_days + 1}+ days"


def _sla_status(age_days: int, sla_target_days: int, overdue_threshold_days: int) -> str:
    if age_days <= sla_target_days:
        return "Within SLA"
    if age_days <= overdue_threshold_days:
        return "At risk"
    return "Overdue"


def _recoverability_status(
    stage_name: str,
    encounter_row: pd.Series,
    snapshot_ts: pd.Timestamp,
) -> str:
    policy_window_end_ts = pd.Timestamp(encounter_row["service_end_ts"]) + timedelta(days=5)
    final_bill_ts = encounter_row.get("final_bill_datetime")

    if stage_name in ACTIVE_STAGE_QUEUE_MAP and stage_name != "Correction / rebill pending":
        if snapshot_ts <= policy_window_end_ts:
            return "Pre-final-bill recoverable"
        return "Post-window financially lost"

    if stage_name == "Correction / rebill pending" and pd.notna(final_bill_ts):
        correction_window_end_ts = pd.Timestamp(final_bill_ts) + timedelta(days=10)
        if snapshot_ts <= correction_window_end_ts:
            return "Post-final-bill recoverable by correction / rebill"
        return "Post-window financially lost"

    if stage_name == "Closed / monitored through denial feedback only":
        return "Financially closed but still compliance-relevant"

    if stage_name == "Final billed":
        return "Post-window financially lost"

    return "Pre-final-bill recoverable"


def _build_explanation_map(
    documentation_events: pd.DataFrame,
    expected_opportunities: pd.DataFrame,
) -> dict[str, str]:
    explanations: dict[str, list[str]] = {}
    expected_nonempty = expected_opportunities.loc[
        expected_opportunities["why_not_billable_explanation"].fillna("") != ""
    ]

    for encounter_id, group in expected_nonempty.groupby("encounter_id"):
        ordered_values: list[str] = []
        for value in group["why_not_billable_explanation"]:
            cleaned = str(value).strip()
            if cleaned and cleaned not in ordered_values:
                ordered_values.append(cleaned)
        if ordered_values:
            explanations[encounter_id] = ordered_values

    doc_gap_rows = documentation_events.loc[
        documentation_events["documentation_gap_type"].fillna("") != ""
    ]
    for encounter_id, group in doc_gap_rows.groupby("encounter_id"):
        values = explanations.setdefault(encounter_id, [])
        for value in group["documentation_gap_type"]:
            cleaned = str(value).strip()
            if cleaned and cleaned not in values:
                values.append(cleaned)

    return {encounter_id: "; ".join(values[:2]) for encounter_id, values in explanations.items()}


def _resolve_current_queue(stage_name: str, issue_domain: str) -> str:
    queue_name = ACTIVE_STAGE_QUEUE_MAP.get(stage_name, "")
    expected_issue_domain = ACTIVE_STAGE_ISSUE_DOMAIN_MAP.get(stage_name, "")
    if queue_name == "" or expected_issue_domain == "":
        return ""
    if issue_domain != expected_issue_domain:
        raise ValueError(
            f"Unsupported stage and issue-domain combination: {stage_name} / {issue_domain}"
        )
    return queue_name


def build_exception_queue_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters, statuses, documentation_events, expected_opportunities = _load_inputs(repo_root)
    queue_definitions = _index_reference_rows(
        load_reference_csv("queue_definitions", repo_root),
        key="queue_name",
        table_name="queue_definitions",
    )
    stage_rules = _index_reference_rows(
        load_reference_csv("stage_aging_rules", repo_root),
        key="stage_name",
        table_name="stage_aging_rules",
    )
    recoverability_rules = _index_reference_rows(
        load_reference_csv("recoverability_rules", repo_root),
        key="recoverability_state",
        table_name="recoverability_rules",
    )

    encounter_lookup = encounters.set_index("encounter_id").to_dict("index")
    documentation_groups = {
        encounter_id: group.copy()
        for encounter_id, group in documentation_events.groupby("encounter_id")
    }
    explanation_map = _build_explanation_map(documentation_events, expected_opportunities)

    active_statuses = statuses.loc[statuses["current_queue_active_flag"]].copy()
    rows: list[dict[str, object]] = []
    for _, status in active_statuses.iterrows():
        encounter = pd.Series(encounter_lookup[status["encounter_id"]])
        workflow_profile = get_workflow_profile(str(encounter["scenario_code"]))
        documentation_subset = _documentation_subset(documentation_groups, status["encounter_id"])
        stage_name = status["current_prebill_stage"]
        queue_name = _resolve_current_queue(stage_name, status["issue_domain"])
        stage_rule = stage_rules[stage_name]
        queue_definition = queue_definitions[queue_name]
        if not _as_bool(queue_definition["active_flag"]):
            raise ValueError(f"Queue definition for active queue '{queue_name}' is not marked active")

        sla_target_days = _int_value(stage_rule["sla_target_days"])
        overdue_threshold_days = _int_value(stage_rule["overdue_threshold_days"])
        stage_entry_ts = derive_stage_entry_ts(stage_name, encounter, documentation_subset)
        stage_age_days = int(workflow_profile["current_stage_age_days"])
        snapshot_ts = _queue_snapshot_ts(stage_entry_ts, stage_age_days)
        recoverability_status = _recoverability_status(stage_name, encounter, snapshot_ts)
        recoverability_rule = recoverability_rules[recoverability_status]
        aging_basis_label = stage_rule["aging_basis"]
        clock_start_event = stage_rule["clock_start_event"]

        rows.append(
            {
                "queue_item_id": f"QUEUE-{status['account_id']}",
                "account_status_id": status["account_status_id"],
                "claim_id": status["claim_id"],
                "account_id": status["account_id"],
                "encounter_id": status["encounter_id"],
                "department": status["department"],
                "service_line": status["service_line"],
                "payer_group": status["payer_group"],
                "current_stage": stage_name,
                "current_prebill_stage": stage_name,
                "issue_domain": status["issue_domain"],
                "root_cause_mechanism": status["root_cause_mechanism"],
                "current_primary_blocker_state": status["current_primary_blocker_state"],
                "current_primary_blocker_code": status["current_primary_blocker_code"],
                "current_queue": queue_name,
                "current_queue_active_flag": True,
                "queue_business_purpose": queue_definition["business_purpose"],
                "queue_entry_rule": queue_definition["entry_rule"],
                "queue_exit_rule": queue_definition["exit_rule"],
                "queue_aging_clock_start_basis": queue_definition["aging_clock_start_basis"],
                "accountable_owner": queue_definition["accountable_owner"],
                "supporting_owner": queue_definition["supporting_owner"],
                "escalation_owner": queue_definition["escalation_owner"],
                "escalation_trigger": queue_definition["escalation_trigger"],
                "aging_basis_label": aging_basis_label,
                "clock_start_event": clock_start_event,
                "aging_clock_start_event": clock_start_event,
                "aging_clock_start_ts": stage_entry_ts,
                "queue_snapshot_ts": snapshot_ts,
                "days_in_stage": stage_age_days,
                "stage_age_days": stage_age_days,
                "sla_target_days": sla_target_days,
                "overdue_threshold_days": overdue_threshold_days,
                "aging_bucket": _aging_bucket(
                    stage_age_days,
                    sla_target_days,
                    overdue_threshold_days,
                ),
                "sla_status": _sla_status(
                    stage_age_days,
                    sla_target_days,
                    overdue_threshold_days,
                ),
                "recoverability_status": recoverability_status,
                "recoverability_window_rule": recoverability_rule["window_rule"],
                "recoverability_financial_meaning": recoverability_rule["financial_meaning"],
                "recoverability_active_queue_allowed": _as_bool(
                    recoverability_rule["active_queue_allowed"]
                ),
                "active_issue_tag_count": status["active_issue_tag_count"],
                "why_not_billable_explanation": explanation_map.get(status["encounter_id"], ""),
            }
        )

    df = pd.DataFrame(rows).sort_values(["current_queue", "encounter_id"]).reset_index(drop=True)
    for column in ("aging_clock_start_ts", "queue_snapshot_ts"):
        df[column] = pd.to_datetime(df[column])
    return df


def write_exception_queue_parquet(repo_root: Path | None = None) -> Path:
    df = build_exception_queue_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_exception_queue_parquet()


if __name__ == "__main__":
    main()
