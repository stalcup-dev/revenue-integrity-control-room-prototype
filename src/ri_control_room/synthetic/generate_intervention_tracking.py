from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.logic.build_queue_history import (
    OUTPUT_FILENAME as QUEUE_HISTORY_FILENAME,
    latest_queue_history_rows,
    write_queue_history_parquet,
)
from ri_control_room.metrics.priority_score import (
    OUTPUT_FILENAME as PRIORITY_SCORES_FILENAME,
    write_priority_scores_parquet,
)
from ri_control_room.synthetic.generate_corrections_rebills import (
    OUTPUT_FILENAME as CORRECTIONS_REBILLS_FILENAME,
    write_corrections_rebills_parquet,
)
from ri_control_room.synthetic.generate_encounters import get_processed_dir


OUTPUT_FILENAME = "intervention_tracking.parquet"

ACTION_METRIC_PROFILES = {
    "Education": {
        "metric_name": "Documentation support reroutes per 10 cases",
        "metric_unit": "per_10_cases",
        "note": "Compare documentation-support recurrence and queue aging on the next validation run.",
    },
    "Build": {
        "metric_name": "False-positive routing rate per 10 cases",
        "metric_unit": "per_10_cases",
        "note": "Rerun build and validate whether queue routing or rule behavior actually shifts.",
    },
    "Coding": {
        "metric_name": "Modifier review repeats per 10 cases",
        "metric_unit": "per_10_cases",
        "note": "Compare coding-review recurrence and modifier hold spillover after validation.",
    },
    "Billing": {
        "metric_name": "Median handoff turnaround days",
        "metric_unit": "days",
        "note": "Confirm handoff clearance and queue exit on the next validation run.",
    },
}


def _load_inputs(repo_root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    priority_scores_path = processed_dir / PRIORITY_SCORES_FILENAME
    queue_history_path = processed_dir / QUEUE_HISTORY_FILENAME
    corrections_rebills_path = processed_dir / CORRECTIONS_REBILLS_FILENAME

    if not priority_scores_path.exists():
        write_priority_scores_parquet(repo_root)
    if not queue_history_path.exists():
        write_queue_history_parquet(repo_root)
    if not corrections_rebills_path.exists():
        write_corrections_rebills_parquet(repo_root)

    return (
        pd.read_parquet(priority_scores_path),
        pd.read_parquet(queue_history_path),
        pd.read_parquet(corrections_rebills_path),
    )


def _action_path(root_cause_mechanism: str) -> str:
    mapping = {
        "Documentation behavior": "Education",
        "Workflow / handoff": "Billing",
        "Coding practice": "Coding",
        "Billing edit management": "Billing",
        "CDM / rule configuration": "Build",
    }
    return mapping.get(root_cause_mechanism, "Education")


def _intervention_owner(row: pd.Series) -> str:
    action_path = str(row["action_path"])
    if action_path == "Education":
        return str(row["supporting_owner"] or row["accountable_owner"])
    if action_path == "Build":
        return str(row["escalation_owner"] or row["supporting_owner"] or row["accountable_owner"])
    if action_path == "Coding":
        if row["current_queue"] == "Coding Pending Review":
            return str(row["accountable_owner"])
        return str(row["supporting_owner"] or row["accountable_owner"])
    return str(row["accountable_owner"])


def _intervention_type(action_path: str) -> str:
    return {
        "Education": "Education",
        "Build": "Build / configuration fix",
        "Coding": "Coding follow-up",
        "Billing": "Billing / correction action",
    }.get(action_path, action_path)


def _target_completion_date(row: pd.Series) -> str:
    snapshot_ts = pd.Timestamp(row["queue_snapshot_ts"]).normalize()
    if row["current_queue"] == "Correction / Rebill Pending":
        days_out = 2 if row["sla_status"] == "At risk" else 1
    elif row["sla_status"] == "Overdue":
        days_out = 1
    elif row["sla_status"] == "At risk":
        days_out = max(2, int(row["overdue_threshold_days"]) - int(row["stage_age_days"]))
    else:
        days_out = 5 + min(int(row["reroute_count"]), 2)
    return (snapshot_ts + pd.Timedelta(days=max(days_out, 1))).strftime("%Y-%m-%d")


def _progress_state(row: pd.Series) -> str:
    if row["sla_status"] == "Overdue" and int(row["reroute_count"]) >= 2:
        return "stalled"
    if row["current_queue"] == "Correction / Rebill Pending":
        return "turnaround_improving"
    if bool(row["repeat_exception_flag"]) and row["recoverability_status"] == "Pre-final-bill recoverable":
        return "validated"
    if row["sla_status"] == "Within SLA" and not bool(row["repeat_exception_flag"]):
        return "baseline"
    return "partial"


def _checkpoint_status(progress_state: str) -> str:
    return {
        "stalled": "Checkpoint overdue",
        "turnaround_improving": "Turnaround improving",
        "validated": "Pilot checkpoint complete",
        "baseline": "Baseline captured",
        "partial": "Monitor next checkpoint",
    }[progress_state]


def _improvement_rate(progress_state: str) -> float:
    return {
        "stalled": -0.06,
        "turnaround_improving": 0.12,
        "validated": 0.18,
        "baseline": 0.02,
        "partial": 0.07,
    }[progress_state]


def _baseline_metric_value(row: pd.Series) -> float:
    pattern_open_actions = float(row["pattern_open_actions"])
    pattern_repeat_rate = float(row["pattern_repeat_rate"])
    reroute_count = float(row["reroute_count"])
    stage_age_days = float(row["stage_age_days"])

    if row["action_path"] in {"Education", "Coding", "Build"}:
        return round(
            (pattern_repeat_rate * 10.0) + (pattern_open_actions * 0.6) + (reroute_count * 0.8),
            1,
        )
    return round(3.8 + (stage_age_days * 0.45) + (reroute_count * 0.9), 1)


def _current_metric_value(baseline_metric_value: float, progress_state: str) -> float:
    current_value = baseline_metric_value * (1.0 - _improvement_rate(progress_state))
    return round(max(current_value, 0.1), 1)


def _correction_turnaround(row: pd.Series, progress_state: str) -> tuple[float | None, float | None]:
    if row["action_path"] != "Billing":
        return None, None
    baseline_days = round(4.5 + (float(row["reroute_count"]) * 0.7) + (float(row["stage_age_days"]) * 0.2), 1)
    if row["current_queue"] == "Correction / Rebill Pending":
        baseline_days = round(baseline_days + 1.4, 1)
    current_days = round(max(baseline_days * (1.0 - _improvement_rate(progress_state)), 0.5), 1)
    return baseline_days, current_days


def _format_metric(metric_name: str, metric_value: float, metric_unit: str) -> str:
    if metric_unit == "days":
        return f"{metric_name}: {metric_value:.1f} days"
    return f"{metric_name}: {metric_value:.1f} per 10 cases"


def _latest_correction_rows(corrections_rebills: pd.DataFrame) -> pd.DataFrame:
    if corrections_rebills.empty:
        return corrections_rebills.copy()
    latest = (
        corrections_rebills.sort_values(
            ["encounter_id", "last_activity_datetime", "correction_open_datetime"],
            ascending=[True, False, False],
        )
        .drop_duplicates(subset=["encounter_id"], keep="first")
        .reset_index(drop=True)
    )
    return latest


def _downstream_outcome(
    row: pd.Series,
    *,
    correction_row: pd.Series | None,
    metric_name: str,
    metric_unit: str,
    baseline_metric_value: float,
    current_metric_value: float,
) -> tuple[str, str, str | None, float | None]:
    if correction_row is not None:
        outcome_status = (
            str(
                correction_row.get("observed_rebill_outcome_status")
                or correction_row.get("outcome_status")
                or ""
            ).strip()
            or None
        )
        turnaround_days = (
            correction_row.get("observed_correction_turnaround_days")
            if correction_row.get("observed_correction_turnaround_days") is not None
            else correction_row.get("turnaround_days")
        )
        turnaround_value = float(turnaround_days) if turnaround_days is not None else None
        outcome_label = (
            outcome_status.replace("_", " ") if outcome_status is not None else "status not captured"
        )
        turnaround_label = (
            f"{turnaround_value:.1f} days" if turnaround_value is not None else "turnaround not captured"
        )
        signal = f"Rebill outcome {outcome_label}; correction turnaround {turnaround_label}."
        return "Correction turnaround / rebill outcome", signal, outcome_status, turnaround_value

    if str(row["action_path"]) in {"Education", "Build", "Coding"}:
        if metric_unit == "days":
            signal = f"{metric_name}: {baseline_metric_value:.1f} -> {current_metric_value:.1f} days."
        else:
            signal = (
                f"{metric_name}: {baseline_metric_value:.1f} -> {current_metric_value:.1f} per 10 cases."
            )
        return "Repeat-exception reduction", signal, None, None

    signal = (
        f"{row['current_queue']}: {row['sla_status']} at {int(row['stage_age_days'])} days aged."
    )
    return "Queue / SLA improvement", signal, None, None


def _recommendation(
    row: pd.Series,
    *,
    progress_state: str,
    baseline_metric_value: float,
    current_metric_value: float,
    correction_baseline: float | None,
    correction_current: float | None,
    observed_outcome_status: str | None = None,
    observed_turnaround_days: float | None = None,
) -> tuple[str, str]:
    metric_delta = round(baseline_metric_value - current_metric_value, 1)
    if observed_outcome_status is not None:
        normalized_outcome = observed_outcome_status.strip().lower()
        if normalized_outcome in {"closed_successful", "rebilled_paid", "resolved_recovered"}:
            if observed_turnaround_days is not None and observed_turnaround_days <= 3.0 and metric_delta >= 1.0:
                return "Expand", "Recovered rebill outcome closed quickly and supports scaling the intervention."
            return "Hold", "Recovery closed, but the observed turnaround is not yet strong enough to expand."
        if normalized_outcome == "open_recoverable":
            if observed_turnaround_days is not None and observed_turnaround_days <= 2.5 and metric_delta >= 1.0:
                return "Revise", "Turnaround improved, but the rebill remains open so follow-through still needs tightening."
            return "Hold", "Rebill remains open and the observed turnaround is not yet strong enough to change course."
        if "monitoring" in normalized_outcome:
            return "Hold", "Recovery is closed for monitoring only, so hold until repeat volume confirms durable change."

    if progress_state == "validated" and metric_delta >= 1.0:
        return "Expand", "Checkpoint evidence shows recurring volume and measurable improvement."
    if progress_state == "baseline" or metric_delta < 0.5:
        return "Hold", "Impact is too early or too small to scale beyond the current intervention."
    if correction_baseline is not None and correction_current is not None:
        turnaround_delta = round(correction_baseline - correction_current, 1)
        if turnaround_delta < 1.0:
            return "Hold", "Turnaround is moving, but the gain is not yet strong enough to expand."
    return "Revise", "Progress is visible but the current intervention design needs adjustment."


def _before_after_note(row: pd.Series, recommendation: str) -> str:
    metric_profile = ACTION_METRIC_PROFILES[str(row["action_path"])]
    pattern_name = str(row["recurring_issue_pattern"])
    return (
        f"{metric_profile['note']} Pattern focus: {pattern_name}. "
        f"Recommendation remains {recommendation.lower()} until the next checkpoint confirms sustained change."
    )


def generate_intervention_tracking_df(repo_root: Path | None = None) -> pd.DataFrame:
    priority_scores, queue_history, corrections_rebills = _load_inputs(repo_root)
    if priority_scores.empty:
        return priority_scores.copy()

    latest_history = latest_queue_history_rows(queue_history)[
        ["encounter_id", "reroute_count", "transition_event_index", "routing_reason"]
    ].copy()
    tracker = priority_scores.merge(latest_history, on="encounter_id", how="left", suffixes=("", "_history"))
    if "reroute_count_history" in tracker.columns:
        tracker["reroute_count"] = tracker["reroute_count_history"].fillna(
            tracker.get("reroute_count", 0)
        )
        tracker = tracker.drop(columns=["reroute_count_history"])
    tracker["reroute_count"] = tracker["reroute_count"].fillna(0).astype(int)
    tracker["transition_event_index"] = tracker["transition_event_index"].fillna(1).astype(int)
    tracker["routing_reason"] = tracker["routing_reason"].fillna("").astype(str)
    tracker["action_path"] = tracker["root_cause_mechanism"].map(_action_path)
    tracker["intervention_type"] = tracker["action_path"].map(_intervention_type)
    tracker["intervention_owner"] = tracker.apply(_intervention_owner, axis=1)
    tracker["recurring_issue_pattern"] = tracker.apply(
        lambda row: f"{row['department']} | {row['current_queue']} | {row['root_cause_mechanism']}",
        axis=1,
    )

    pattern_metrics = (
        tracker.groupby(
            ["department", "current_queue", "root_cause_mechanism", "action_path"],
            as_index=False,
        )
        .agg(
            pattern_open_actions=("queue_item_id", "size"),
            pattern_repeat_exceptions=("repeat_exception_flag", "sum"),
            pattern_stage_age_median=("stage_age_days", "median"),
            pattern_reroute_mean=("reroute_count", "mean"),
        )
    )
    pattern_metrics["pattern_repeat_rate"] = (
        pattern_metrics["pattern_repeat_exceptions"] / pattern_metrics["pattern_open_actions"]
    ).fillna(0.0)
    tracker = tracker.merge(
        pattern_metrics,
        on=["department", "current_queue", "root_cause_mechanism", "action_path"],
        how="left",
    )
    latest_corrections = _latest_correction_rows(corrections_rebills)
    if not latest_corrections.empty:
        tracker = tracker.merge(
            latest_corrections[
                [
                    "encounter_id",
                    "correction_id",
                    "correction_type",
                    "turnaround_days",
                    "outcome_status",
                    "last_activity_datetime",
                    "rebill_required_flag",
                    "financial_recovery_pathway",
                ]
            ].rename(
                columns={
                    "turnaround_days": "observed_correction_turnaround_days",
                    "outcome_status": "observed_rebill_outcome_status",
                    "last_activity_datetime": "observed_rebill_last_activity_datetime",
                    "rebill_required_flag": "observed_rebill_required_flag",
                    "financial_recovery_pathway": "observed_financial_recovery_pathway",
                }
            ),
            on="encounter_id",
            how="left",
        )

    rows: list[dict[str, object]] = []
    for _, row in tracker.iterrows():
        metric_profile = ACTION_METRIC_PROFILES[str(row["action_path"])]
        progress_state = _progress_state(row)
        checkpoint_status = _checkpoint_status(progress_state)
        baseline_metric_value = _baseline_metric_value(row)
        current_metric_value = _current_metric_value(baseline_metric_value, progress_state)
        correction_baseline, correction_current = _correction_turnaround(row, progress_state)
        observed_outcome_status = row.get("observed_rebill_outcome_status")
        if observed_outcome_status is not None and pd.isna(observed_outcome_status):
            observed_outcome_status = None
        observed_turnaround_days = row.get("observed_correction_turnaround_days")
        if observed_turnaround_days is not None and pd.isna(observed_turnaround_days):
            observed_turnaround_days = None
        correction_row = None
        if observed_outcome_status is not None or observed_turnaround_days is not None:
            correction_row = row
        downstream_outcome_type, downstream_outcome_signal, _, _ = _downstream_outcome(
            row,
            correction_row=correction_row,
            metric_name=metric_profile["metric_name"],
            metric_unit=metric_profile["metric_unit"],
            baseline_metric_value=baseline_metric_value,
            current_metric_value=current_metric_value,
        )
        recommendation, recommendation_rationale = _recommendation(
            row,
            progress_state=progress_state,
            baseline_metric_value=baseline_metric_value,
            current_metric_value=current_metric_value,
            correction_baseline=correction_baseline,
            correction_current=correction_current,
            observed_outcome_status=(
                str(observed_outcome_status)
                if observed_outcome_status is not None
                else None
            ),
            observed_turnaround_days=(
                float(observed_turnaround_days)
                if observed_turnaround_days is not None
                else None
            ),
        )
        current_correction_turnaround = (
            float(observed_turnaround_days)
            if observed_turnaround_days is not None
            else correction_current
        )
        correction_turnaround_signal = "Not correction-led"
        if correction_baseline is not None and current_correction_turnaround is not None:
            correction_turnaround_signal = (
                f"{correction_baseline:.1f}d baseline -> {current_correction_turnaround:.1f}d observed"
            )
            if observed_outcome_status is not None:
                correction_turnaround_signal = (
                    f"{correction_turnaround_signal} ({str(observed_outcome_status).replace('_', ' ')})"
                )

        rows.append(
            {
                "intervention_tracking_id": f"INT-{row['account_id']}",
                "queue_item_id": row["queue_item_id"],
                "account_status_id": row["account_status_id"],
                "claim_id": row["claim_id"],
                "account_id": row["account_id"],
                "encounter_id": row["encounter_id"],
                "department": row["department"],
                "service_line": row["service_line"],
                "current_queue": row["current_queue"],
                "current_prebill_stage": row["current_prebill_stage"],
                "issue_domain": row["issue_domain"],
                "root_cause_mechanism": row["root_cause_mechanism"],
                "action_path": row["action_path"],
                "intervention_type": row["intervention_type"],
                "recurring_issue_pattern": row["recurring_issue_pattern"],
                "intervention_owner": row["intervention_owner"],
                "owner_context_match_flag": bool(
                    str(row["intervention_owner"]).strip()
                    and str(row["current_queue"]).strip()
                ),
                "target_completion_date": _target_completion_date(row),
                "checkpoint_status": checkpoint_status,
                "progress_state": progress_state,
                "baseline_metric_name": metric_profile["metric_name"],
                "baseline_metric_unit": metric_profile["metric_unit"],
                "baseline_metric_value": baseline_metric_value,
                "current_metric_value": current_metric_value,
                "metric_delta": round(baseline_metric_value - current_metric_value, 1),
                "baseline_metric": _format_metric(
                    metric_profile["metric_name"],
                    baseline_metric_value,
                    metric_profile["metric_unit"],
                ),
                "current_metric": _format_metric(
                    metric_profile["metric_name"],
                    current_metric_value,
                    metric_profile["metric_unit"],
                ),
                "correction_turnaround_baseline_days": correction_baseline,
                "correction_turnaround_current_days": current_correction_turnaround,
                "correction_turnaround_signal": correction_turnaround_signal,
                "downstream_outcome_type": downstream_outcome_type,
                "downstream_outcome_signal": downstream_outcome_signal,
                "correction_id": row.get("correction_id"),
                "correction_type": row.get("correction_type"),
                "observed_rebill_outcome_status": observed_outcome_status,
                "observed_rebill_last_activity_datetime": row.get("observed_rebill_last_activity_datetime"),
                "observed_rebill_required_flag": row.get("observed_rebill_required_flag"),
                "observed_financial_recovery_pathway": row.get("observed_financial_recovery_pathway"),
                "before_after_validation_note": _before_after_note(row, recommendation),
                "hold_expand_revise_recommendation": recommendation,
                "recommendation_rationale": recommendation_rationale,
                "routing_reason_context": row["routing_reason"],
                "reroute_count": int(row["reroute_count"]),
                "repeat_exception_flag": bool(row["repeat_exception_flag"]),
                "pattern_open_actions": int(row["pattern_open_actions"]),
                "pattern_repeat_rate": round(float(row["pattern_repeat_rate"]), 4),
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["queue_item_id", "encounter_id"]
    ).reset_index(drop=True)


def write_intervention_tracking_parquet(repo_root: Path | None = None) -> Path:
    df = generate_intervention_tracking_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_intervention_tracking_parquet()


if __name__ == "__main__":
    main()
