from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from ri_control_room.constants import (
    FROZEN_V1_DEPARTMENTS,
    RECOVERABILITY_STATES,
    WORKFLOW_STAGE_LADDER,
)
from ri_control_room.io import get_repo_root


@dataclass(frozen=True)
class ReferenceTableSpec:
    filename: str
    required_columns: tuple[str, ...]


REFERENCE_TABLE_SPECS = {
    "cdm_reference": ReferenceTableSpec(
        filename="cdm_reference.csv",
        required_columns=(
            "cdm_item_id",
            "department",
            "service_line",
            "expected_code",
            "expected_modifier",
            "default_units",
            "revenue_code",
            "active_flag",
            "rule_status",
            "last_update_datetime",
        ),
    ),
    "department_charge_logic_map": ReferenceTableSpec(
        filename="department_charge_logic_map.csv",
        required_columns=(
            "department",
            "clinical_event",
            "performed_activity_evidence",
            "required_documentation_elements",
            "expected_facility_charge_opportunity",
            "common_modifier_logic",
            "separately_billable_flag",
            "packaged_or_integral_flag",
            "common_failure_mode",
            "likely_queue_destination",
            "why_it_may_not_be_billable",
        ),
    ),
    "queue_definitions": ReferenceTableSpec(
        filename="queue_definitions.csv",
        required_columns=(
            "queue_name",
            "business_purpose",
            "entry_rule",
            "exit_rule",
            "aging_clock_start_basis",
            "sla_target_days",
            "overdue_threshold_days",
            "accountable_owner",
            "supporting_owner",
            "escalation_owner",
            "escalation_trigger",
            "active_flag",
        ),
    ),
    "stage_aging_rules": ReferenceTableSpec(
        filename="stage_aging_rules.csv",
        required_columns=(
            "stage_name",
            "aging_basis",
            "clock_start_event",
            "sla_target_days",
            "overdue_threshold_days",
            "aging_bucket_rule_note",
        ),
    ),
    "recoverability_rules": ReferenceTableSpec(
        filename="recoverability_rules.csv",
        required_columns=(
            "recoverability_state",
            "workflow_stage_pattern",
            "window_rule",
            "financial_meaning",
            "active_queue_allowed",
        ),
    ),
    "issue_domain_map": ReferenceTableSpec(
        filename="issue_domain_map.csv",
        required_columns=(
            "issue_domain",
            "domain_description",
            "included_in_v1",
            "notes",
        ),
    ),
    "root_cause_map": ReferenceTableSpec(
        filename="root_cause_map.csv",
        required_columns=(
            "root_cause_mechanism",
            "mechanism_description",
            "operational_owner_hint",
            "included_in_v1",
        ),
    ),
}


@dataclass(frozen=True)
class ReferenceTables:
    cdm_reference: list[dict[str, str]]
    department_charge_logic_map: list[dict[str, str]]
    queue_definitions: list[dict[str, str]]
    stage_aging_rules: list[dict[str, str]]
    recoverability_rules: list[dict[str, str]]
    issue_domain_map: list[dict[str, str]]
    root_cause_map: list[dict[str, str]]


def get_reference_dir(repo_root: Path | None = None) -> Path:
    root = repo_root.resolve() if repo_root is not None else get_repo_root()
    return root / "data" / "reference"


def load_reference_csv(table_name: str, repo_root: Path | None = None) -> list[dict[str, str]]:
    try:
        spec = REFERENCE_TABLE_SPECS[table_name]
    except KeyError as exc:
        raise KeyError(f"Unknown reference table: {table_name}") from exc

    path = get_reference_dir(repo_root) / spec.filename
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    return rows


def load_reference_tables(repo_root: Path | None = None) -> ReferenceTables:
    kwargs = {
        table_name: load_reference_csv(table_name, repo_root)
        for table_name in REFERENCE_TABLE_SPECS
    }
    tables = ReferenceTables(**kwargs)
    validate_reference_tables(tables)
    return tables


def validate_reference_tables(tables: ReferenceTables) -> None:
    for table_name, spec in REFERENCE_TABLE_SPECS.items():
        rows = getattr(tables, table_name)
        if not rows:
            raise ValueError(f"{table_name} is empty")

        columns = set(rows[0].keys())
        missing = [column for column in spec.required_columns if column not in columns]
        if missing:
            raise ValueError(f"{table_name} is missing required columns: {', '.join(missing)}")

        for row_number, row in enumerate(rows, start=2):
            for column in spec.required_columns:
                if row[column] == "":
                    raise ValueError(
                        f"{table_name} has an empty required value in column '{column}' on data row {row_number}"
                    )

    for table_name, rows, key in (
        ("queue_definitions", tables.queue_definitions, "queue_name"),
        ("stage_aging_rules", tables.stage_aging_rules, "stage_name"),
    ):
        seen: set[str] = set()
        for row in rows:
            value = row[key]
            if value in seen:
                raise ValueError(f"{table_name} has a duplicate {key}: {value}")
            seen.add(value)

    departments = {row["department"] for row in tables.department_charge_logic_map}
    if departments != set(FROZEN_V1_DEPARTMENTS):
        raise ValueError(
            "department_charge_logic_map departments do not match the frozen V1 set"
        )

    recoverability_states = tuple(
        row["recoverability_state"] for row in tables.recoverability_rules
    )
    if recoverability_states != RECOVERABILITY_STATES:
        raise ValueError("recoverability_rules states do not match the locked V1 set")

    stage_names = {row["stage_name"] for row in tables.stage_aging_rules}
    required_stage_names = set(WORKFLOW_STAGE_LADDER) | {"denial_feedback_backlog"}
    if not required_stage_names.issubset(stage_names):
        raise ValueError("stage_aging_rules is missing required governed workflow stages")

    for row in tables.queue_definitions:
        if row["active_flag"] not in {"true", "false"}:
            raise ValueError("queue_definitions active_flag must be true or false")
