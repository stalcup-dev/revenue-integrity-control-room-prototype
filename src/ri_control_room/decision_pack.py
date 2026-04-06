from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.control_story import (
    DeterministicControlStory,
    render_control_story_lines,
)
from ri_control_room.ui.shared import RECOVERABLE_STATES, SummaryFilters, format_count, format_currency
from ri_control_room.ui.theme import panel, render_section_header


DECISION_PACK_TITLE = "Revenue Integrity Decision Pack"
DECISION_PACK_FILENAME = "revenue_integrity_decision_pack.md"
SCENARIO_LAB_DEFAULT_NOTE = (
    "Scenario snapshot uses the current Scenario Lab v0 default lever targets for the same filtered slice."
)
GUARDRAILS = (
    "Facility-side only.",
    "Outpatient-first.",
    "Deterministic-first.",
    "Synthetic/public-safe data.",
    "Scenario results are what-if estimates, not forecasts.",
    "Denials are evidence-only, not the product center.",
)
SLA_PRIORITY = {
    "Overdue": 0,
    "At risk": 1,
    "Within SLA": 2,
}


@dataclass(frozen=True)
class DecisionPackPayload:
    title: str
    build_timestamp_utc: str
    validation_status: str
    filters: SummaryFilters
    executive_summary: dict[str, object]
    top_priority_work_queues: pd.DataFrame
    control_story: DeterministicControlStory
    intervention_update: dict[str, object]
    scenario_snapshot: dict[str, object]
    guardrails: tuple[str, ...]


def _mode_text(values: pd.Series, *, fallback: str = "") -> str:
    cleaned = values.fillna("").astype(str).str.strip()
    cleaned = cleaned.loc[cleaned != ""]
    if cleaned.empty:
        return fallback
    modes = cleaned.mode()
    if modes.empty:
        return fallback
    return str(sorted(modes.astype(str).tolist())[0])


def _worst_sla_status(values: pd.Series) -> str:
    cleaned = values.fillna("Within SLA").astype(str)
    return min(
        cleaned.tolist(),
        key=lambda value: SLA_PRIORITY.get(str(value), 99),
    )


def _queue_filename_prefix(filters: SummaryFilters) -> str:
    scoped = any(
        (
            filters.departments,
            filters.service_lines,
            filters.queues,
            filters.recoverability_states,
        )
    )
    return "filtered_" if scoped else ""


def _top_service_line_department(filtered: pd.DataFrame) -> str:
    if filtered.empty:
        return "No active slice"
    summary = (
        filtered.assign(breach_flag=lambda df: df["sla_status"] != "Within SLA")
        .groupby(["service_line", "department"], as_index=False)
        .agg(
            exceptions=("queue_item_id", "size"),
            breaching_sla=("breach_flag", "sum"),
            dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(
            ["breaching_sla", "exceptions", "dollars", "service_line", "department"],
            ascending=[False, False, False, True, True],
        )
        .reset_index(drop=True)
    )
    if summary.empty:
        return "No active slice"
    top_row = summary.iloc[0]
    return f"{top_row['service_line']} | {top_row['department']}"


def _build_executive_summary(
    summary_view,
    top_priority_work_queues: pd.DataFrame,
) -> dict[str, object]:
    top_owner_queue = "No active queue"
    if not top_priority_work_queues.empty:
        top_row = top_priority_work_queues.iloc[0]
        top_owner_queue = f"{top_row['owner_team']} | {top_row['queue_name']}"
    return {
        "total_open_exceptions": int(summary_view.open_exception_count),
        "recoverable_now_dollars": float(summary_view.recoverable_now_dollars),
        "already_lost_dollars": float(summary_view.lost_dollars_now),
        "exceptions_breaching_sla": int(summary_view.urgent_exception_count),
        "top_owner_queue": top_owner_queue,
        "top_service_line_department": _top_service_line_department(
            summary_view.filtered_population
        ),
    }


def _build_top_priority_work_queues(
    filtered: pd.DataFrame,
    action_tracker: pd.DataFrame,
    *,
    limit: int = 3,
) -> pd.DataFrame:
    if filtered.empty:
        return pd.DataFrame(
            columns=[
                "rank",
                "issue_domain",
                "owner_team",
                "queue_name",
                "sla_status",
                "recoverability",
                "dollars_at_risk",
                "recoverable_dollars",
                "recommended_next_step",
            ]
        )

    queue_rows = filtered.merge(
        action_tracker[["queue_item_id", "next_action"]],
        on="queue_item_id",
        how="left",
    ).copy()
    queue_rows["breach_flag"] = queue_rows["sla_status"] != "Within SLA"
    queue_rows["recoverable_dollars_component"] = queue_rows["estimated_gross_dollars"].where(
        queue_rows["recoverability_status"].isin(RECOVERABLE_STATES),
        0.0,
    )
    summary = (
        queue_rows.groupby(["issue_domain", "accountable_owner", "current_queue"], as_index=False)
        .agg(
            open_exceptions=("queue_item_id", "size"),
            breaching_sla=("breach_flag", "sum"),
            sla_status=("sla_status", _worst_sla_status),
            recoverability=("recoverability_status", _mode_text),
            dollars_at_risk=("estimated_gross_dollars", "sum"),
            recoverable_dollars=("recoverable_dollars_component", "sum"),
            recommended_next_step=(
                "next_action",
                lambda values: _mode_text(
                    values,
                    fallback="Work the accountable queue and confirm the next governed handoff.",
                ),
            ),
        )
        .sort_values(
            [
                "breaching_sla",
                "recoverable_dollars",
                "dollars_at_risk",
                "open_exceptions",
                "issue_domain",
            ],
            ascending=[False, False, False, False, True],
        )
        .head(limit)
        .reset_index(drop=True)
    )
    if summary.empty:
        return summary
    summary["rank"] = range(1, len(summary) + 1)
    summary["dollars_at_risk"] = summary["dollars_at_risk"].round(2)
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    summary = summary.rename(
        columns={
            "accountable_owner": "owner_team",
            "current_queue": "queue_name",
        }
    )
    return summary[
        [
            "rank",
            "issue_domain",
            "owner_team",
            "queue_name",
            "sla_status",
            "recoverability",
            "dollars_at_risk",
            "recoverable_dollars",
            "recommended_next_step",
        ]
    ].copy()


def _build_intervention_update(
    repo_root: Path | None,
    tracker_view,
) -> dict[str, object]:
    if tracker_view.action_tracker.empty:
        return {
            "queue_item_id": "No active intervention",
            "intervention_type": "No active intervention",
            "owner": "No active owner",
            "baseline_metric": "No current action-tracker rows in the selected slice.",
            "current_metric": "No current action-tracker rows in the selected slice.",
            "downstream_outcome_signal": "No downstream signal available.",
            "recommendation": "Hold",
        }

    from ri_control_room.case_detail import build_case_detail_payload

    selected_row = tracker_view.action_tracker.iloc[0]
    queue_item_id = str(selected_row["queue_item_id"])
    case_payload = build_case_detail_payload(queue_item_id, repo_root)
    intervention = case_payload.intervention_follow_through
    downstream = case_payload.downstream_outcome
    return {
        "queue_item_id": queue_item_id,
        "intervention_type": str(
            intervention.get("intervention_type") or selected_row["intervention_type"]
        ),
        "owner": str(intervention.get("intervention_owner") or selected_row["intervention_owner"]),
        "baseline_metric": str(
            intervention.get("baseline_metric") or selected_row["baseline_metric"]
        ),
        "current_metric": str(intervention.get("current_metric") or selected_row["current_metric"]),
        "downstream_outcome_signal": str(
            downstream.get("downstream_outcome_signal")
            or selected_row["downstream_outcome_signal"]
        ),
        "recommendation": str(
            intervention.get("hold_expand_revise_recommendation")
            or selected_row["hold_expand_revise_recommendation"]
        ),
    }


def _build_scenario_snapshot(repo_root: Path | None, filters: SummaryFilters) -> dict[str, object]:
    from ri_control_room.ui.scenario_lab import build_scenario_lab_view, project_scenario_lab

    scenario_view = build_scenario_lab_view(repo_root=repo_root, filters=filters)
    if len(scenario_view.lever_configs) < 3:
        return {
            "lever_settings_used": ("Scenario Lab v0 defaults unavailable.",),
            "projected_backlog_reduction": 0,
            "projected_sla_improvement_points": 0.0,
            "projected_recoverable_dollar_lift": 0.0,
            "ninety_day_impact_estimate": 0.0,
            "note": SCENARIO_LAB_DEFAULT_NOTE,
        }

    lever_map = {lever.key: lever for lever in scenario_view.lever_configs}
    projection = project_scenario_lab(
        scenario_view,
        target_prebill_clearance_rate=lever_map["prebill_clearance_rate"].default_target_value,
        target_correction_turnaround_days=lever_map["correction_turnaround_days"].default_target_value,
        target_routing_speed_days=lever_map["routing_speed_to_owner_teams"].default_target_value,
    )
    lever_settings_used = (
        (
            f"Prebill edit clearance rate: {lever_map['prebill_clearance_rate'].baseline_value:.1f}% "
            f"to {lever_map['prebill_clearance_rate'].default_target_value:.1f}%."
        ),
        (
            f"Correction turnaround days: {lever_map['correction_turnaround_days'].baseline_value:.1f} "
            f"to {lever_map['correction_turnaround_days'].default_target_value:.1f}."
        ),
        (
            f"Routing speed to owner teams: {lever_map['routing_speed_to_owner_teams'].baseline_value:.1f} "
            f"to {lever_map['routing_speed_to_owner_teams'].default_target_value:.1f} days."
        ),
    )
    return {
        "lever_settings_used": lever_settings_used,
        "projected_backlog_reduction": int(projection.projected_backlog_reduction),
        "projected_sla_improvement_points": float(projection.projected_sla_improvement_points),
        "projected_recoverable_dollar_lift": float(projection.projected_recoverable_dollar_lift),
        "ninety_day_impact_estimate": float(projection.ninety_day_impact_estimate),
        "note": SCENARIO_LAB_DEFAULT_NOTE,
    }


def build_revenue_integrity_decision_pack(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> DecisionPackPayload:
    from ri_control_room.ui.control_room_summary import build_control_room_summary_view
    from ri_control_room.ui.opportunity_action_tracker import build_opportunity_action_tracker_view

    summary_view = build_control_room_summary_view(repo_root=repo_root, filters=filters)
    tracker_view = build_opportunity_action_tracker_view(repo_root=repo_root, filters=filters)
    top_priority_work_queues = _build_top_priority_work_queues(
        summary_view.filtered_population,
        tracker_view.action_tracker,
    )
    return DecisionPackPayload(
        title=DECISION_PACK_TITLE,
        build_timestamp_utc=summary_view.artifact_lineage.build_timestamp_utc,
        validation_status=summary_view.artifact_lineage.overall_validation_status,
        filters=summary_view.filters,
        executive_summary=_build_executive_summary(summary_view, top_priority_work_queues),
        top_priority_work_queues=top_priority_work_queues,
        control_story=summary_view.control_story,
        intervention_update=_build_intervention_update(repo_root, tracker_view),
        scenario_snapshot=_build_scenario_snapshot(repo_root, summary_view.filters),
        guardrails=GUARDRAILS,
    )


def render_revenue_integrity_decision_pack_markdown(payload: DecisionPackPayload) -> str:
    lines = [
        f"# {payload.title}",
        "",
        f"- Build timestamp (UTC): {payload.build_timestamp_utc}",
        f"- Validation status: {payload.validation_status}",
        "",
        "## Executive summary",
        "",
        f"- Total open exceptions: {format_count(int(payload.executive_summary['total_open_exceptions']))}",
        (
            f"- Recoverable now vs already lost: "
            f"{format_currency(float(payload.executive_summary['recoverable_now_dollars']))} vs "
            f"{format_currency(float(payload.executive_summary['already_lost_dollars']))}"
        ),
        (
            f"- Exceptions breaching SLA: "
            f"{format_count(int(payload.executive_summary['exceptions_breaching_sla']))}"
        ),
        f"- Top owner queue: {payload.executive_summary['top_owner_queue']}",
        (
            f"- Top service line / department of concern: "
            f"{payload.executive_summary['top_service_line_department']}"
        ),
        "",
        "## Top priority work queues",
        "",
    ]

    if payload.top_priority_work_queues.empty:
        lines.append("- No active routed queue groupings match the current filters.")
    else:
        for row in payload.top_priority_work_queues.itertuples(index=False):
            lines.extend(
                [
                    (
                        f"- #{row.rank} {row.queue_name} | {row.issue_domain} | {row.owner_team}"
                    ),
                    f"  SLA status: {row.sla_status}.",
                    f"  Recoverability: {row.recoverability}.",
                    (
                        f"  Dollars at risk / recoverable: "
                        f"{format_currency(float(row.dollars_at_risk))} / "
                        f"{format_currency(float(row.recoverable_dollars))}."
                    ),
                    f"  Recommended next step: {row.recommended_next_step}",
                ]
            )

    intervention = payload.intervention_update
    scenario = payload.scenario_snapshot
    control_story_lines = render_control_story_lines(payload.control_story, memo_tight=True)

    lines.extend(
        [
            "",
            "## Current control story",
            "",
        ]
    )
    lines.extend(control_story_lines)
    lines.extend(
        [
            "",
            "## Intervention update",
            "",
            f"- Intervention type: {intervention['intervention_type']}",
            f"- Owner: {intervention['owner']}",
            f"- Baseline metric: {intervention['baseline_metric']}",
            f"- Current metric: {intervention['current_metric']}",
            f"- Downstream outcome signal: {intervention['downstream_outcome_signal']}",
            f"- Hold / expand / revise recommendation: {intervention['recommendation']}",
            "",
            "## Scenario snapshot",
            "",
            "- Lever settings used:",
        ]
    )
    for lever_setting in scenario["lever_settings_used"]:
        lines.append(f"  - {lever_setting}")
    lines.extend(
        [
            (
                f"- Projected backlog reduction: "
                f"{format_count(int(scenario['projected_backlog_reduction']))}"
            ),
            (
                f"- Projected SLA improvement: "
                f"+{float(scenario['projected_sla_improvement_points']):.1f} points"
            ),
            (
                f"- Projected recoverable dollar lift: "
                f"{format_currency(float(scenario['projected_recoverable_dollar_lift']))}"
            ),
            (
                f"- 90-day impact estimate: "
                f"{format_currency(float(scenario['ninety_day_impact_estimate']))}"
            ),
            f"- Note: {scenario['note']}",
            "",
            "## Guardrails / caveats",
            "",
        ]
    )
    for guardrail in payload.guardrails:
        lines.append(f"- {guardrail}")
    lines.append("")
    return "\n".join(lines)


def export_revenue_integrity_decision_pack(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
    output_path: Path | None = None,
) -> Path:
    root = repo_root.resolve() if repo_root is not None else Path.cwd().resolve()
    payload = build_revenue_integrity_decision_pack(root, filters=filters)
    if output_path is None:
        output_dir = root / "artifacts" / "decision_pack"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{_queue_filename_prefix(payload.filters)}{DECISION_PACK_FILENAME}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_revenue_integrity_decision_pack_markdown(payload),
        encoding="utf-8",
    )
    return output_path


def render_revenue_integrity_decision_pack_panel(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> None:
    import streamlit as st

    payload = build_revenue_integrity_decision_pack(repo_root=repo_root, filters=filters)
    markdown = render_revenue_integrity_decision_pack_markdown(payload)
    with st.expander(DECISION_PACK_TITLE, expanded=False):
        with panel():
            render_section_header(
                DECISION_PACK_TITLE,
                (
                    "Thin leadership-facing memo assembled from the current governed control-room, "
                    "action-tracker, and scenario outputs for this filtered slice."
                ),
            )
            if hasattr(st, "caption"):
                st.caption(
                    "Trigger from Control Room Summary. Export stays facility-side, outpatient-first, "
                    "deterministic-first, and uses the current filtered app state."
                )
            download_button = getattr(st, "download_button", None)
            if callable(download_button):
                download_button(
                    "Download markdown",
                    data=markdown,
                    file_name=f"{_queue_filename_prefix(payload.filters)}{DECISION_PACK_FILENAME}",
                    mime="text/markdown",
                )
            if hasattr(st, "markdown"):
                st.markdown(markdown)
