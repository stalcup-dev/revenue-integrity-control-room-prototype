from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.logic.derive_expected_charge_opportunities import (
    OUTPUT_FILENAME as EXPECTED_FILENAME,
    write_expected_charge_opportunities_parquet,
)
from ri_control_room.synthetic.generate_claim_lines import (
    OUTPUT_FILENAME as CLAIM_LINES_FILENAME,
    write_claim_lines_parquet,
)
from ri_control_room.synthetic.generate_claims_account_status import (
    OUTPUT_FILENAME as STATUS_FILENAME,
    write_claims_account_status_parquet,
)
from ri_control_room.synthetic.generate_corrections_rebills import (
    OUTPUT_FILENAME as CORRECTIONS_FILENAME,
    write_corrections_rebills_parquet,
)
from ri_control_room.synthetic.generate_encounters import get_processed_dir


OUTPUT_FILENAME = "denials_feedback.parquet"


def _load_required_tables(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    expected_path = processed_dir / EXPECTED_FILENAME
    status_path = processed_dir / STATUS_FILENAME
    claim_lines_path = processed_dir / CLAIM_LINES_FILENAME
    corrections_path = processed_dir / CORRECTIONS_FILENAME

    if not expected_path.exists():
        write_expected_charge_opportunities_parquet(repo_root)
    if not status_path.exists():
        write_claims_account_status_parquet(repo_root)
    if not claim_lines_path.exists():
        write_claim_lines_parquet(repo_root)
    if not corrections_path.exists():
        write_corrections_rebills_parquet(repo_root)

    return (
        pd.read_parquet(expected_path),
        pd.read_parquet(status_path),
        pd.read_parquet(claim_lines_path),
        pd.read_parquet(corrections_path),
    )


def _linked_issue_domain(expected_row: pd.Series) -> str:
    blocker_state = str(expected_row.get("current_primary_blocker_state", ""))
    opportunity_status = str(expected_row.get("opportunity_status", ""))

    if opportunity_status == "packaged_or_nonbillable_suppressed":
        return "Packaged / non-billable / false-positive classification"
    if opportunity_status == "recoverable_missed_charge":
        return "Charge capture failure"
    if opportunity_status == "modifier_dependency_case":
        return "Billing / claim-edit failure"
    if "Documentation" in blocker_state or "support" in blocker_state.lower():
        return "Documentation support failure"
    if "Coding" in blocker_state or "modifier" in blocker_state.lower():
        return "Billing / claim-edit failure"
    if "Charge capture" in blocker_state:
        return "Charge capture failure"
    return "Documentation support failure"


def _denial_category(expected_row: pd.Series) -> str:
    reason = str(expected_row.get("why_not_billable_explanation", ""))
    modifier_hint = str(expected_row.get("expected_modifier_hint", ""))
    clinical_event = str(expected_row.get("clinical_event", ""))

    if modifier_hint:
        return "technical_denial"
    if "incomplete_study" in reason or clinical_event == "Incomplete or discontinued imaging study":
        return "medical_necessity_denial"
    return "documentation_support_denial"


def _denial_reason_group(expected_row: pd.Series) -> str:
    reason = str(expected_row.get("why_not_billable_explanation", ""))
    modifier_hint = str(expected_row.get("expected_modifier_hint", ""))

    if modifier_hint:
        return "modifier_validation"
    if "laterality" in reason or "site" in reason:
        return "laterality_site_support"
    if "device_linkage" in reason or "implant_linkage" in reason:
        return "device_implant_support"
    if "timestamp" in reason or "stop_time" in reason:
        return "timestamp_time_support"
    if "incomplete_study" in reason:
        return "technical_completion"
    return "documentation_integrity"


def _denial_amount(base_amount: float, category: str) -> float:
    denial_share = {
        "technical_denial": 0.35,
        "medical_necessity_denial": 0.5,
        "documentation_support_denial": 0.4,
    }[category]
    return round(base_amount * denial_share, 2)


def generate_denials_feedback_df(repo_root: Path | None = None) -> pd.DataFrame:
    expected, statuses, claim_lines, corrections = _load_required_tables(repo_root)
    if expected.empty or statuses.empty:
        return pd.DataFrame()

    status_lookup = statuses.set_index("encounter_id").to_dict("index")
    claim_summary = (
        claim_lines.groupby(["encounter_id", "claim_id"], as_index=False)
        .agg(
            denial_base_amount=("billed_amount", "sum"),
            denial_signal_datetime=("bill_drop_datetime", "max"),
        )
        .sort_values(["encounter_id", "claim_id"])
    )
    claim_lookup = claim_summary.set_index("encounter_id").to_dict("index")

    rows: list[dict[str, object]] = []
    used_encounters: set[str] = set()

    correction_expected = (
        expected.sort_values(["encounter_id", "expected_opportunity_id"])
        .groupby("encounter_id", as_index=False)
        .first()
    )
    correction_expected_lookup = correction_expected.set_index("encounter_id").to_dict("index")

    for _, correction in corrections.iterrows():
        encounter_id = str(correction["encounter_id"])
        status = status_lookup.get(encounter_id)
        if status is None or str(status.get("payer_group", "")) == "Self Pay":
            continue

        claim_context = claim_lookup.get(encounter_id, {})
        expected_context = correction_expected_lookup.get(encounter_id, {})
        signal_ts = claim_context.get("denial_signal_datetime", pd.NaT)
        if pd.isna(signal_ts):
            signal_ts = pd.Timestamp(status["final_bill_datetime"]) + timedelta(days=12)

        correction_type = str(correction.get("correction_type", ""))
        denial_category = (
            "technical_denial"
            if correction_type in {"late_charge_correction", "technical_rebill_review"}
            else "documentation_support_denial"
        )
        denial_reason_group = (
            "postbill_rebill_variance"
            if correction_type == "late_charge_correction"
            else "technical_rebill_review"
            if correction_type == "technical_rebill_review"
            else "historical_support_review"
        )
        base_amount = float(claim_context.get("denial_base_amount", 0.0) or 0.0)
        rows.append(
            {
                "denial_id": f"DEN-{correction['claim_id']}",
                "encounter_id": encounter_id,
                "claim_id": correction["claim_id"],
                "denial_signal_datetime": pd.Timestamp(signal_ts),
                "denial_category": denial_category,
                "denial_reason_group": denial_reason_group,
                "payer_group": status["payer_group"],
                "denial_amount": _denial_amount(max(base_amount, 150.0), denial_category),
                "linked_upstream_issue_domain": (
                    "Billing / claim-edit failure"
                    if correction_type in {"late_charge_correction", "technical_rebill_review"}
                    else "Documentation support failure"
                ),
                "linked_recoverability_status": status["recoverability_status"],
                "source_expected_opportunity_id": expected_context.get(
                    "expected_opportunity_id", ""
                ),
                "evidence_only_flag": True,
            }
        )
        used_encounters.add(encounter_id)

    expected_candidates = expected.merge(
        statuses[
            [
                "encounter_id",
                "payer_group",
                "current_prebill_stage",
                "recoverability_status",
                "final_bill_datetime",
            ]
        ],
        on=["encounter_id", "current_prebill_stage", "recoverability_status"],
        how="left",
        suffixes=("", "_status"),
    )
    expected_candidates = expected_candidates.merge(
        claim_summary[["encounter_id", "denial_base_amount", "denial_signal_datetime"]],
        on="encounter_id",
        how="left",
    )
    expected_candidates = expected_candidates.loc[
        expected_candidates["opportunity_status"].isin(
            {"unsupported_charge_risk", "modifier_dependency_case"}
        )
        & expected_candidates["current_prebill_stage"].isin(
            {"Final billed", "Closed / monitored through denial feedback only"}
        )
        & expected_candidates["charge_event_exists_flag"]
        & expected_candidates["payer_group"].fillna("").ne("Self Pay")
    ].copy()
    expected_candidates["priority"] = expected_candidates["opportunity_status"].map(
        {"unsupported_charge_risk": 0, "modifier_dependency_case": 1}
    )
    expected_candidates = expected_candidates.sort_values(
        ["priority", "encounter_id", "expected_opportunity_id"]
    )

    for _, candidate in expected_candidates.iterrows():
        encounter_id = str(candidate["encounter_id"])
        if encounter_id in used_encounters:
            continue

        signal_ts = candidate["denial_signal_datetime"]
        if pd.isna(signal_ts):
            signal_ts = pd.Timestamp(candidate["final_bill_datetime"]) + timedelta(days=14)
        denial_category = _denial_category(candidate)
        rows.append(
            {
                "denial_id": f"DEN-{candidate['claim_id']}-{len(rows) + 1}",
                "encounter_id": encounter_id,
                "claim_id": candidate["claim_id"],
                "denial_signal_datetime": pd.Timestamp(signal_ts),
                "denial_category": denial_category,
                "denial_reason_group": _denial_reason_group(candidate),
                "payer_group": candidate["payer_group"],
                "denial_amount": _denial_amount(
                    float(candidate.get("denial_base_amount", 0.0) or 150.0),
                    denial_category,
                ),
                "linked_upstream_issue_domain": _linked_issue_domain(candidate),
                "linked_recoverability_status": candidate["recoverability_status"],
                "source_expected_opportunity_id": candidate["expected_opportunity_id"],
                "evidence_only_flag": True,
            }
        )
        used_encounters.add(encounter_id)

    df = pd.DataFrame(rows).sort_values(
        ["denial_signal_datetime", "encounter_id", "denial_id"]
    ).reset_index(drop=True)
    if not df.empty:
        df["denial_signal_datetime"] = pd.to_datetime(df["denial_signal_datetime"])
    return df


def write_denials_feedback_parquet(repo_root: Path | None = None) -> Path:
    df = generate_denials_feedback_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_denials_feedback_parquet()


if __name__ == "__main__":
    main()
