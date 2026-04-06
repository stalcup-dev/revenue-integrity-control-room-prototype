from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import (
    MANUAL_AUDIT_SAMPLE_CSV_FILENAME,
    MANUAL_AUDIT_SAMPLE_MARKDOWN_FILENAME,
    get_manual_audit_markdown_path,
    get_processed_artifact_path,
    load_existing_validation_tables,
)
from ri_control_room.io import get_repo_root
from ri_control_room.logic.build_queue_history import latest_queue_history_rows

AUDIT_SAMPLE_CSV_FILENAME = MANUAL_AUDIT_SAMPLE_CSV_FILENAME
AUDIT_SAMPLE_MARKDOWN_FILENAME = MANUAL_AUDIT_SAMPLE_MARKDOWN_FILENAME

HANDPICKED_AUDIT_CASES = (
    "INF001",
    "INF002",
    "INF004",
    "INF005",
    "INF006",
    "INF009",
    "INF010",
    "IR001",
    "IR002",
    "OR001",
    "OR002",
    "OR004",
    "OR005",
    "OR006",
    "OR007",
    "OR010",
    "RAD001",
    "RAD002",
    "RAD003",
    "RAD006",
    "RAD007",
)


def _resolved_root(repo_root: Path | None = None) -> Path:
    return repo_root.resolve() if repo_root is not None else get_repo_root()


def _join_unique(values: pd.Series, *, fallback: str = "") -> str:
    ordered_values: list[str] = []
    for value in values.fillna(""):
        cleaned = str(value).strip()
        if cleaned and cleaned not in ordered_values:
            ordered_values.append(cleaned)
    return "; ".join(ordered_values) if ordered_values else fallback


def _documentation_evidence(group: pd.DataFrame) -> str:
    if group.empty:
        return "No documentation events found."
    parts = [
        "types=" + _join_unique(group["documentation_type"], fallback="unknown"),
        "status=" + _join_unique(group["documentation_status"], fallback="unknown"),
        "gaps=" + _join_unique(group["documentation_gap_type"], fallback="none"),
    ]
    support_true_count = int(group["supports_charge_flag"].fillna(False).sum())
    parts.append(f"supports_charge_true={support_true_count}/{len(group)}")
    return "; ".join(parts)


def _upstream_activity(group: pd.DataFrame) -> str:
    if group.empty:
        return "No upstream activity signals found."
    return "; ".join(
        [
            "activities=" + _join_unique(group["activity_description"], fallback="unknown"),
            "support=" + _join_unique(group["support_status"], fallback="unknown"),
            "basis=" + _join_unique(group["signal_basis"], fallback="unknown"),
        ]
    )


def _expected_opportunity(group: pd.DataFrame) -> str:
    if group.empty:
        return "No expected opportunity rows found."
    return "; ".join(
        [
            "targets="
            + _join_unique(group["expected_facility_charge_opportunity"], fallback="none"),
            "status=" + _join_unique(group["opportunity_status"], fallback="unknown"),
            "why_not_billable="
            + _join_unique(group["why_not_billable_explanation"], fallback="none"),
        ]
    )


def _billed_state(
    charge_group: pd.DataFrame,
    status_row: pd.Series,
    encounter_row: pd.Series,
) -> str:
    charge_status = _join_unique(charge_group["charge_status"], fallback="no charge rows")
    charge_codes = _join_unique(charge_group["charge_code"], fallback="none")
    final_bill_text = (
        pd.Timestamp(encounter_row["final_bill_datetime"]).strftime("%Y-%m-%d %H:%M")
        if pd.notna(encounter_row["final_bill_datetime"])
        else "not final billed"
    )
    return "; ".join(
        [
            "charge_status=" + charge_status,
            "charge_codes=" + charge_codes,
            "current_stage=" + str(status_row["current_prebill_stage"]),
            "final_bill=" + final_bill_text,
        ]
    )


def _queue_owner(status_row: pd.Series, queue_row: pd.Series | None) -> tuple[str, str]:
    if queue_row is not None:
        queue_name = str(queue_row["current_queue"]).strip() or "No active queue"
        owner_name = str(queue_row["accountable_owner"]).strip() or "No active owner"
        return queue_name, owner_name
    queue_name = str(status_row.get("current_queue", "")).strip() or "No active queue"
    owner_name = str(status_row.get("accountable_owner", "")).strip() or "No active owner"
    return queue_name, owner_name


def _audit_focus(status_row: pd.Series, expected_group: pd.DataFrame, queue_name: str) -> str:
    if queue_name == "Charge Reconciliation Monitor":
        return "Confirm a true missed-charge or late-post story, not a packaged false positive."
    if queue_name == "Documentation Support Exceptions":
        return "Confirm the documented activity exists but the support gap blocks clean billing."
    if queue_name == "Modifiers / Edits / Prebill Holds":
        return "Confirm the issue is a governed edit or hold path with real billing ownership."
    if queue_name == "Coding Pending Review":
        return "Confirm modifier or coding review is the true current blocker."
    if queue_name == "Correction / Rebill Pending":
        return "Confirm the account left prebill, entered correction, and remains financially recoverable."
    if (expected_group["opportunity_status"] == "packaged_or_nonbillable_suppressed").any():
        return "Confirm the case suppresses to packaged or non-billable and should not become leakage."
    return "Confirm the clean control case does not create an active exception."


def build_manual_audit_sample_df(repo_root: Path | None = None) -> pd.DataFrame:
    tables = load_existing_validation_tables(repo_root)
    encounters = tables["encounters"].set_index("encounter_id")
    statuses = tables["claims_or_account_status"].set_index("encounter_id")
    documentation = tables["documentation_events"]
    signals = tables["upstream_activity_signals"]
    expected = tables["expected_charge_opportunities"]
    charges = tables["charge_events"]
    queue = tables["exception_queue"].set_index("encounter_id")
    queue_history = tables["queue_history"].copy()

    rows: list[dict[str, object]] = []
    for case_rank, encounter_id in enumerate(HANDPICKED_AUDIT_CASES, start=1):
        encounter_row = encounters.loc[encounter_id]
        status_row = statuses.loc[encounter_id]
        documentation_group = documentation.loc[documentation["encounter_id"] == encounter_id].copy()
        signal_group = signals.loc[signals["encounter_id"] == encounter_id].copy()
        expected_group = expected.loc[expected["encounter_id"] == encounter_id].copy()
        charge_group = charges.loc[charges["encounter_id"] == encounter_id].copy()
        queue_row = queue.loc[encounter_id] if encounter_id in queue.index else None
        history_subset = queue_history.loc[queue_history["encounter_id"] == encounter_id].copy()
        history_row = latest_queue_history_rows(history_subset).iloc[0] if not history_subset.empty else None
        queue_name, owner_name = _queue_owner(status_row, queue_row)

        reroute_text = "No reroute history."
        if history_row is not None:
            reroute_text = (
                f"transition_events={len(history_subset)}; "
                f"reroute_count={int(history_row['reroute_count'])}; "
                f"prior_queue={str(history_row['prior_queue']).strip() or 'none'}; "
                f"path={history_row['queue_transition_path']}"
            )

        rows.append(
            {
                "case_rank": case_rank,
                "encounter_id": encounter_id,
                "department": encounter_row["department"],
                "service_line": encounter_row["service_line"],
                "scenario_code": encounter_row["scenario_code"],
                "current_prebill_stage": status_row["current_prebill_stage"],
                "upstream_activity": _upstream_activity(signal_group),
                "documentation_evidence": _documentation_evidence(documentation_group),
                "expected_opportunity": _expected_opportunity(expected_group),
                "billed_state": _billed_state(charge_group, status_row, encounter_row),
                "exception_classification": "; ".join(
                    [
                        "issue_domain=" + str(status_row["issue_domain"]),
                        "blocker=" + str(status_row["current_primary_blocker_state"]),
                    ]
                ),
                "owner_queue": queue_name,
                "accountable_owner": owner_name,
                "recoverability": status_row["recoverability_status"],
                "queue_history": reroute_text,
                "audit_focus": _audit_focus(status_row, expected_group, queue_name),
            }
        )

    return pd.DataFrame(rows)


def _write_markdown(df: pd.DataFrame, output_path: Path) -> Path:
    lines = [
        "# Manual Audit Sample",
        "",
        "Deterministic 21-case audit pack exported from the current V1 synthetic control-room outputs.",
        "",
    ]
    for row in df.itertuples(index=False):
        lines.extend(
            [
                f"## {row.encounter_id}",
                "",
                f"- Case rank: {row.case_rank}",
                f"- Department: {row.department}",
                f"- Service line: {row.service_line}",
                f"- Scenario code: {row.scenario_code}",
                f"- Current prebill stage: {row.current_prebill_stage}",
                f"- Upstream activity: {row.upstream_activity}",
                f"- Documentation evidence: {row.documentation_evidence}",
                f"- Expected opportunity: {row.expected_opportunity}",
                f"- Billed state: {row.billed_state}",
                f"- Exception classification: {row.exception_classification}",
                f"- Owner queue: {row.owner_queue}",
                f"- Accountable owner: {row.accountable_owner}",
                f"- Recoverability: {row.recoverability}",
                f"- Queue history: {row.queue_history}",
                f"- Audit focus: {row.audit_focus}",
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def export_manual_audit_pack(repo_root: Path | None = None) -> tuple[pd.DataFrame, Path, Path]:
    root = _resolved_root(repo_root)
    sample = build_manual_audit_sample_df(root)
    csv_path = get_processed_artifact_path("manual_audit_sample", root)
    markdown_path = get_manual_audit_markdown_path(root)
    sample.to_csv(csv_path, index=False)
    _write_markdown(sample, markdown_path)
    return sample, csv_path, markdown_path


def main() -> tuple[Path, Path]:
    _, csv_path, markdown_path = export_manual_audit_pack()
    return csv_path, markdown_path


if __name__ == "__main__":
    main()
