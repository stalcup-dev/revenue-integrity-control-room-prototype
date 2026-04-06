from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.ui.shared import (
    PageStoryCue,
    RECOVERABLE_STATES,
    StoryCallout,
    SummaryFilters,
    apply_filters,
    format_count,
    format_currency,
    get_global_filter_options,
    get_global_filters,
    get_filter_options,
    load_work_population,
    normalize_filters,
    render_active_filter_summary,
    render_page_story_cue,
)
from ri_control_room.ui.theme import (
    KpiCard,
    render_kpi_row,
    render_page_shell,
    render_section_header,
    render_table_section,
)


ALL_SETTINGS_LABEL = "All frozen V1 departments"
PREBILL_QUEUE = "Modifiers / Edits / Prebill Holds"
CORRECTION_QUEUE = "Correction / Rebill Pending"
PREBILL_TOUCHED_STAGES = {"Prebill edit / hold", "Correction / rebill pending"}
CLEARANCE_GAIN_CAP = 0.20
TURNAROUND_GAIN_CAP = 0.35
ROUTING_GAIN_CAP = 0.25
BACKLOG_REDUCTION_CAP = 0.30
DOLLAR_LIFT_CAP = 0.35


@dataclass(frozen=True)
class ScenarioLeverConfig:
    key: str
    label: str
    baseline_value: float
    default_target_value: float
    min_value: float
    max_value: float
    step: float
    unit_label: str
    delta_label: str
    assumption_note: str


@dataclass(frozen=True)
class ScenarioLabView:
    filters: SummaryFilters
    filter_options: dict[str, tuple[str, ...]]
    filtered_population: pd.DataFrame
    baseline_inputs: pd.DataFrame
    lever_configs: tuple[ScenarioLeverConfig, ...]
    story_cue: PageStoryCue


@dataclass(frozen=True)
class ScenarioProjection:
    output_summary: pd.DataFrame
    lever_summary: pd.DataFrame
    formula_summary: pd.DataFrame
    projected_recoverable_dollar_lift: float
    projected_backlog_reduction: int
    projected_sla_improvement_points: float
    ninety_day_impact_estimate: float
    implementation_effort: str


def _load_population(repo_root: Path | None = None) -> pd.DataFrame:
    population = load_work_population(repo_root)
    queue_history = load_processed_artifact("queue_history", repo_root)
    current_history = queue_history.loc[
        queue_history["current_record_flag"],
        [
            "claim_id",
            "account_id",
            "encounter_id",
            "current_queue",
            "prior_queue",
            "days_in_prior_queue",
            "transition_event_type",
        ],
    ].copy()
    merged = population.merge(
        current_history,
        on=["claim_id", "account_id", "encounter_id", "current_queue"],
        how="left",
    )
    merged["prior_queue"] = merged["prior_queue"].fillna("")
    merged["days_in_prior_queue"] = pd.to_numeric(
        merged["days_in_prior_queue"], errors="coerce"
    ).fillna(0.0)
    merged["transition_event_type"] = merged["transition_event_type"].fillna("Initial queue placement")
    return merged


def _load_corrections(repo_root: Path | None = None) -> pd.DataFrame:
    return load_processed_artifact("corrections_rebills", repo_root)


def _load_governed_kpis(repo_root: Path | None = None) -> pd.DataFrame:
    kpis = load_processed_artifact("kpi_snapshot", repo_root)
    return kpis.loc[kpis["record_type"] == "kpi"].copy()


def _safe_mean(series: pd.Series) -> float:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0.0
    return round(float(numeric.mean()), 2)


def _safe_percent(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 1)


def _recoverable_slice(filtered: pd.DataFrame) -> pd.DataFrame:
    return filtered.loc[filtered["recoverability_status"].isin(RECOVERABLE_STATES)].copy()


def _handoff_slice(filtered: pd.DataFrame) -> pd.DataFrame:
    return filtered.loc[filtered["prior_queue"].fillna("") != ""].copy()


def _prebill_touched_slice(filtered: pd.DataFrame) -> pd.DataFrame:
    return filtered.loc[
        filtered["current_prebill_stage"].isin(PREBILL_TOUCHED_STAGES)
    ].copy()


def _prebill_clearance_rate_baseline(filtered: pd.DataFrame) -> float:
    touched = _prebill_touched_slice(filtered)
    if touched.empty:
        return 0.0
    numerator = float((touched["recoverability_status"] == "Pre-final-bill recoverable").sum())
    return _safe_percent(numerator, float(len(touched)))


def _correction_turnaround_days_baseline(
    filtered: pd.DataFrame,
    corrections: pd.DataFrame,
) -> float:
    correction_scope = filtered.loc[filtered["current_queue"] == CORRECTION_QUEUE, [
        "claim_id",
        "account_id",
        "encounter_id",
    ]].drop_duplicates()
    if correction_scope.empty:
        return 0.0
    scoped_corrections = corrections.merge(
        correction_scope,
        on=["claim_id", "account_id", "encounter_id"],
        how="inner",
    )
    return _safe_mean(scoped_corrections["turnaround_days"])


def _routing_speed_days_baseline(filtered: pd.DataFrame) -> float:
    handoffs = _handoff_slice(filtered)
    return _safe_mean(handoffs["days_in_prior_queue"])


def _scoped_governed_kpi_value(
    kpi_rows: pd.DataFrame,
    *,
    filters: SummaryFilters,
    kpi_name: str,
) -> float:
    scoped = kpi_rows.loc[kpi_rows["kpi_name"] == kpi_name].copy()
    if scoped.empty:
        return 0.0
    if filters.departments:
        department_rows = scoped.loc[scoped["department"].isin(filters.departments)].copy()
        if not department_rows.empty:
            return round(float(department_rows["kpi_value"].fillna(0.0).sum()), 2)
    all_scope_rows = scoped.loc[scoped["setting_name"] == ALL_SETTINGS_LABEL].copy()
    if not all_scope_rows.empty:
        return round(float(all_scope_rows.iloc[0]["kpi_value"] or 0.0), 2)
    return round(float(scoped["kpi_value"].fillna(0.0).sum()), 2)


def _baseline_inputs(
    filtered: pd.DataFrame,
    kpi_rows: pd.DataFrame,
    corrections: pd.DataFrame,
    filters: SummaryFilters,
) -> pd.DataFrame:
    recoverable = _recoverable_slice(filtered)
    handoffs = _handoff_slice(filtered)
    aged_recoverable = recoverable.loc[recoverable["sla_status"] != "Within SLA"].copy()
    rows = [
        {
            "baseline_metric": "Open exceptions in current slice",
            "value": int(len(filtered)),
            "source": "priority_scores.parquet",
            "note": "Current active filtered backlog used for backlog and SLA scenario outputs.",
        },
        {
            "baseline_metric": "Non-within-SLA exceptions",
            "value": int((filtered["sla_status"] != "Within SLA").sum()),
            "source": "priority_scores.parquet",
            "note": "Current at-risk plus overdue exceptions used for SLA improvement math.",
        },
        {
            "baseline_metric": "Governed prebill edit aging",
            "value": _scoped_governed_kpi_value(
                kpi_rows,
                filters=filters,
                kpi_name="Prebill edit aging",
            ),
            "source": "kpi_snapshot.parquet",
            "note": "Department-governed KPI reference kept visible for context; service-line and queue filters do not restate KPI publication grain.",
        },
        {
            "baseline_metric": "Governed recoverable dollars still open",
            "value": _scoped_governed_kpi_value(
                kpi_rows,
                filters=filters,
                kpi_name="Recoverable dollars still open",
            ),
            "source": "kpi_snapshot.parquet",
            "note": "Governed gross exposure reference from the published KPI snapshot.",
        },
        {
            "baseline_metric": "Aged recoverable dollars in current slice",
            "value": round(float(aged_recoverable["estimated_gross_dollars"].sum()), 2),
            "source": "priority_scores.parquet",
            "note": "Current recoverable dollars already carrying at-risk or overdue pressure.",
        },
        {
            "baseline_metric": "Active owner-handoff items",
            "value": int(len(handoffs)),
            "source": "queue_history.parquet + priority_scores.parquet",
            "note": "Current queue items with a prior queue already recorded in governed routing history.",
        },
        {
            "baseline_metric": "Correction turnaround baseline",
            "value": _correction_turnaround_days_baseline(filtered, corrections),
            "source": "corrections_rebills.parquet",
            "note": "Average observed turnaround days on current open correction / rebill items in the filtered slice.",
        },
        {
            "baseline_metric": "Routing speed to owner teams baseline",
            "value": _routing_speed_days_baseline(filtered),
            "source": "queue_history.parquet",
            "note": "Average days spent in the prior queue before handoff into the current accountable owner queue.",
        },
        {
            "baseline_metric": "Prebill edit clearance rate baseline proxy",
            "value": _prebill_clearance_rate_baseline(filtered),
            "source": "priority_scores.parquet",
            "note": "V0 proxy: share of prebill-touched items still kept on a pre-final-bill recoverable path instead of spilling to correction or loss.",
        },
    ]
    return pd.DataFrame(rows)


def _default_target_percent(baseline: float) -> float:
    return round(min(90.0, baseline + 10.0), 1)


def _default_target_days(baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return round(max(0.5, baseline - 0.5), 1)


def _lever_configs(
    filtered: pd.DataFrame,
    corrections: pd.DataFrame,
) -> tuple[ScenarioLeverConfig, ...]:
    clearance_baseline = _prebill_clearance_rate_baseline(filtered)
    correction_baseline = _correction_turnaround_days_baseline(filtered, corrections)
    routing_baseline = _routing_speed_days_baseline(filtered)
    return (
        ScenarioLeverConfig(
            key="prebill_clearance_rate",
            label="Prebill edit clearance rate",
            baseline_value=clearance_baseline,
            default_target_value=_default_target_percent(clearance_baseline),
            min_value=clearance_baseline,
            max_value=95.0,
            step=1.0,
            unit_label="%",
            delta_label="pts",
            assumption_note=(
                "Improvement only; capped so prebill clearance cannot claim more than 20% of current backlog release in 90 days."
            ),
        ),
        ScenarioLeverConfig(
            key="correction_turnaround_days",
            label="Correction turnaround days",
            baseline_value=correction_baseline,
            default_target_value=_default_target_days(correction_baseline),
            min_value=0.0 if correction_baseline == 0 else 0.5,
            max_value=max(correction_baseline, 0.5),
            step=0.5,
            unit_label="days",
            delta_label="days faster",
            assumption_note=(
                "Improvement only; faster correction turnaround is capped at 35% of current open correction impact."
            ),
        ),
        ScenarioLeverConfig(
            key="routing_speed_to_owner_teams",
            label="Routing speed to owner teams",
            baseline_value=routing_baseline,
            default_target_value=_default_target_days(routing_baseline),
            min_value=0.0 if routing_baseline == 0 else 0.5,
            max_value=max(routing_baseline, 0.5),
            step=0.1,
            unit_label="days",
            delta_label="days faster",
            assumption_note=(
                "Improvement only; routing relief is capped at 25% of active handoff pressure to avoid treating every handoff day as removable."
            ),
        ),
    )


def _story_cue(
    filtered: pd.DataFrame,
    lever_configs: tuple[ScenarioLeverConfig, ...],
) -> PageStoryCue:
    if filtered.empty:
        return PageStoryCue(
            sentence=(
                "This page stays thin on purpose: it tests operational what-if assumptions only, "
                "and no active routed work matches the current filters."
            ),
            callouts=(
                StoryCallout("Control", "Deterministic what-if only."),
                StoryCallout("Current pressure", "No active backlog is in scope for scenario testing."),
                StoryCallout("Lever test", "Three capped levers remain available when active work re-enters scope."),
            ),
            note="No queue routing, KPI definition, or forecast model changes are introduced here.",
        )

    open_exceptions = int(len(filtered))
    non_within_sla = int((filtered["sla_status"] != "Within SLA").sum())
    lever_labels = ", ".join(lever.label for lever in lever_configs)
    return PageStoryCue(
        sentence=(
            "This page is a thin deterministic what-if surface, not a queue narrative hub or forecast engine."
        ),
        callouts=(
            StoryCallout(
                "Control",
                "Transparent testing of operational levers against the current filtered slice.",
            ),
            StoryCallout(
                "Current pressure",
                f"{open_exceptions} open exception(s) and {non_within_sla} non-within-SLA item(s) shape the current baseline.",
            ),
            StoryCallout(
                "Lever test",
                f"{lever_labels} move projected backlog, SLA, and recoverable-dollar outputs.",
            ),
        ),
        note="Kept intentionally thinner because this page supports the operating story; it does not replace it.",
    )


def build_scenario_lab_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> ScenarioLabView:
    population = _load_population(repo_root)
    normalized_filters = normalize_filters(filters)
    filter_options = get_filter_options(population)
    filtered = apply_filters(population, normalized_filters)
    corrections = _load_corrections(repo_root)
    kpi_rows = _load_governed_kpis(repo_root)
    lever_configs = _lever_configs(filtered, corrections)
    return ScenarioLabView(
        filters=normalized_filters,
        filter_options=filter_options,
        filtered_population=filtered,
        baseline_inputs=_baseline_inputs(filtered, kpi_rows, corrections, normalized_filters),
        lever_configs=lever_configs,
        story_cue=_story_cue(filtered, lever_configs),
    )


def _lever_config_map(view: ScenarioLabView) -> dict[str, ScenarioLeverConfig]:
    return {lever.key: lever for lever in view.lever_configs}


def _gain_ratio(current: float, target: float, cap: float) -> float:
    if current <= 0:
        return 0.0
    improvement = max(current - target, 0.0)
    return round(min(improvement / current, cap), 4)


def _gain_points(current: float, target: float, cap: float) -> float:
    improvement = max(target - current, 0.0)
    return round(min(improvement / 100.0, cap), 4)


def _implementation_effort(
    clearance_delta_points: float,
    turnaround_days_saved: float,
    routing_days_saved: float,
) -> str:
    effort_score = 0
    if clearance_delta_points >= 10:
        effort_score += 1
    if turnaround_days_saved >= 1:
        effort_score += 1
    if routing_days_saved >= 0.5:
        effort_score += 1
    if effort_score <= 1:
        return "Low"
    if effort_score == 2:
        return "Moderate"
    return "Moderate-high"


def project_scenario_lab(
    view: ScenarioLabView,
    *,
    target_prebill_clearance_rate: float,
    target_correction_turnaround_days: float,
    target_routing_speed_days: float,
) -> ScenarioProjection:
    filtered = view.filtered_population
    levers = _lever_config_map(view)

    prebill_open = filtered.loc[filtered["current_queue"] == PREBILL_QUEUE].copy()
    correction_open = filtered.loc[filtered["current_queue"] == CORRECTION_QUEUE].copy()
    handoff_open = _handoff_slice(filtered)
    recoverable = _recoverable_slice(filtered)
    aged_recoverable = recoverable.loc[recoverable["sla_status"] != "Within SLA"].copy()
    non_within_sla = filtered.loc[filtered["sla_status"] != "Within SLA"].copy()

    clearance_baseline = levers["prebill_clearance_rate"].baseline_value
    correction_baseline = levers["correction_turnaround_days"].baseline_value
    routing_baseline = levers["routing_speed_to_owner_teams"].baseline_value

    clearance_delta_points = round(max(target_prebill_clearance_rate - clearance_baseline, 0.0), 1)
    turnaround_days_saved = round(max(correction_baseline - target_correction_turnaround_days, 0.0), 1)
    routing_days_saved = round(max(routing_baseline - target_routing_speed_days, 0.0), 1)

    clearance_gain = _gain_points(
        clearance_baseline,
        target_prebill_clearance_rate,
        CLEARANCE_GAIN_CAP,
    )
    turnaround_gain = _gain_ratio(
        correction_baseline,
        target_correction_turnaround_days,
        TURNAROUND_GAIN_CAP,
    )
    routing_gain = _gain_ratio(
        routing_baseline,
        target_routing_speed_days,
        ROUTING_GAIN_CAP,
    )

    backlog_reduction_raw = (
        (len(prebill_open) * clearance_gain)
        + (len(handoff_open) * routing_gain)
    )
    projected_backlog_reduction = int(
        round(
            min(
                len(filtered) * BACKLOG_REDUCTION_CAP,
                backlog_reduction_raw,
            )
        )
    )

    improved_sla_cases_raw = (
        (int((prebill_open["sla_status"] != "Within SLA").sum()) * clearance_gain)
        + (int((handoff_open["sla_status"] != "Within SLA").sum()) * routing_gain)
        + (int((correction_open["sla_status"] != "Within SLA").sum()) * turnaround_gain)
    )
    improved_sla_cases = int(round(min(len(non_within_sla), improved_sla_cases_raw)))

    baseline_within_sla_rate = _safe_percent(
        float((filtered["sla_status"] == "Within SLA").sum()),
        float(len(filtered)),
    )
    scenario_within_sla_rate = _safe_percent(
        float((filtered["sla_status"] == "Within SLA").sum() + improved_sla_cases),
        float(len(filtered)),
    )
    projected_sla_improvement_points = round(
        scenario_within_sla_rate - baseline_within_sla_rate,
        1,
    )

    projected_recoverable_dollar_lift = round(
        min(
            float(aged_recoverable["estimated_gross_dollars"].sum()) * DOLLAR_LIFT_CAP,
            (
                float(
                    prebill_open.loc[
                        prebill_open["recoverability_status"].isin(RECOVERABLE_STATES),
                        "estimated_gross_dollars",
                    ].sum()
                )
                * clearance_gain
            )
            + (
                float(
                    correction_open.loc[
                        correction_open["recoverability_status"].isin(RECOVERABLE_STATES),
                        "estimated_gross_dollars",
                    ].sum()
                )
                * turnaround_gain
            )
            + (
                float(
                    handoff_open.loc[
                        handoff_open["recoverability_status"].isin(RECOVERABLE_STATES),
                        "estimated_gross_dollars",
                    ].sum()
                )
                * routing_gain
            ),
        ),
        2,
    )
    ninety_day_impact_estimate = round(projected_recoverable_dollar_lift * 3.0, 2)
    implementation_effort = _implementation_effort(
        clearance_delta_points,
        turnaround_days_saved,
        routing_days_saved,
    )

    output_summary = pd.DataFrame(
        [
            {
                "output": "Projected recoverable dollar lift",
                "baseline": format_currency(float(aged_recoverable["estimated_gross_dollars"].sum())),
                "scenario": format_currency(projected_recoverable_dollar_lift),
                "change": format_currency(projected_recoverable_dollar_lift),
                "assumption_note": "Monthly directional lift, capped at 35% of current aged recoverable dollars.",
            },
            {
                "output": "Projected open-exception / backlog reduction",
                "baseline": format_count(len(filtered)),
                "scenario": format_count(max(len(filtered) - projected_backlog_reduction, 0)),
                "change": f"-{format_count(projected_backlog_reduction)}",
                "assumption_note": "90-day reduction from current prebill backlog plus active owner-handoff pressure, capped at 30% of current open exceptions.",
            },
            {
                "output": "Projected SLA improvement",
                "baseline": f"{baseline_within_sla_rate:.1f}% within SLA",
                "scenario": f"{scenario_within_sla_rate:.1f}% within SLA",
                "change": f"+{projected_sla_improvement_points:.1f} pts",
                "assumption_note": "Only current non-within-SLA items are eligible to improve; no hidden queue-priority formula changes are introduced.",
            },
            {
                "output": "90-day impact estimate",
                "baseline": format_currency(float(aged_recoverable["estimated_gross_dollars"].sum())),
                "scenario": format_currency(ninety_day_impact_estimate),
                "change": format_currency(ninety_day_impact_estimate),
                "assumption_note": "Three months of the projected monthly lift with steady current mix; framed as what-if operational impact, not certainty.",
            },
            {
                "output": "Implementation effort framing",
                "baseline": "Current operating baseline",
                "scenario": implementation_effort,
                "change": implementation_effort,
                "assumption_note": "Simple framing only: larger lever shifts imply broader operational follow-through.",
            },
        ]
    )

    lever_summary = pd.DataFrame(
        [
            {
                "lever": levers["prebill_clearance_rate"].label,
                "baseline": f"{clearance_baseline:.1f}%",
                "target": f"{target_prebill_clearance_rate:.1f}%",
                "delta": f"+{clearance_delta_points:.1f} pts",
                "assumption_note": levers["prebill_clearance_rate"].assumption_note,
            },
            {
                "lever": levers["correction_turnaround_days"].label,
                "baseline": f"{correction_baseline:.1f} days",
                "target": f"{target_correction_turnaround_days:.1f} days",
                "delta": f"{turnaround_days_saved:.1f} days faster",
                "assumption_note": levers["correction_turnaround_days"].assumption_note,
            },
            {
                "lever": levers["routing_speed_to_owner_teams"].label,
                "baseline": f"{routing_baseline:.1f} days",
                "target": f"{target_routing_speed_days:.1f} days",
                "delta": f"{routing_days_saved:.1f} days faster",
                "assumption_note": levers["routing_speed_to_owner_teams"].assumption_note,
            },
        ]
    )

    formula_summary = pd.DataFrame(
        [
            {
                "step": "Backlog reduction",
                "formula": (
                    "min(30% of current open exceptions, "
                    "prebill open * clearance gain + active handoff items * routing gain)"
                ),
                "result": f"{projected_backlog_reduction} fewer open exceptions",
                "guardrail": "Prebill clearance gain capped at 20%; routing gain capped at 25%.",
            },
            {
                "step": "SLA improvement",
                "formula": (
                    "Baseline within-SLA rate plus improved cases from prebill, routing, and correction levers."
                ),
                "result": f"+{projected_sla_improvement_points:.1f} within-SLA pts",
                "guardrail": "Only current at-risk / overdue items can improve; no case can improve twice beyond the current non-within-SLA pool.",
            },
            {
                "step": "Recoverable dollar lift",
                "formula": (
                    "min(35% of aged recoverable dollars, "
                    "prebill recoverable $ * clearance gain + correction recoverable $ * turnaround gain + handoff recoverable $ * routing gain)"
                ),
                "result": format_currency(projected_recoverable_dollar_lift),
                "guardrail": "Not every open exception dollar is treated as recoverable or equally achievable.",
            },
            {
                "step": "90-day impact",
                "formula": "Projected monthly recoverable dollar lift * 3 months",
                "result": format_currency(ninety_day_impact_estimate),
                "guardrail": "Simple roll-forward only; this is not a predictive forecast.",
            },
        ]
    )

    return ScenarioProjection(
        output_summary=output_summary,
        lever_summary=lever_summary,
        formula_summary=formula_summary,
        projected_recoverable_dollar_lift=projected_recoverable_dollar_lift,
        projected_backlog_reduction=projected_backlog_reduction,
        projected_sla_improvement_points=projected_sla_improvement_points,
        ninety_day_impact_estimate=ninety_day_impact_estimate,
        implementation_effort=implementation_effort,
    )


def _baseline_display(value: float, unit_label: str) -> str:
    if unit_label == "%":
        return f"{value:.1f}%"
    return f"{value:.1f} {unit_label}"


def render_scenario_lab_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        (
            "Thin what-if page for operational improvement levers only. "
            "Results stay deterministic, facility-side, outpatient-first, and visibly capped."
        ),
        scope_note,
        badges=(
            "Facility-side only",
            "Outpatient-first",
            "What-if only",
        ),
    )
    selected_filters = get_global_filters(global_filter_options)
    view = build_scenario_lab_view(repo_root=repo_root, filters=selected_filters)
    render_active_filter_summary(view.filters)
    render_page_story_cue(view.story_cue)

    render_section_header(
        "Operational Levers",
        "Exactly three transparent levers. Baselines come from current governed queue, routing, correction, and KPI outputs.",
    )

    if view.filtered_population.empty:
        st.warning("No active routed work matches the current filters.")
        return

    lever_targets: dict[str, float] = {}
    for column, lever in zip(st.columns(3), view.lever_configs, strict=False):
        with column:
            st.caption(f"Baseline: {_baseline_display(lever.baseline_value, lever.unit_label)}")
            lever_targets[lever.key] = float(
                st.number_input(
                    lever.label,
                    min_value=float(lever.min_value),
                    max_value=float(lever.max_value),
                    value=float(lever.default_target_value),
                    step=float(lever.step),
                )
            )
            delta_value = round(
                lever_targets[lever.key] - lever.baseline_value,
                1,
            )
            if lever.unit_label == "%":
                st.caption(f"Delta from baseline: {delta_value:+.1f} {lever.delta_label}")
            else:
                st.caption(f"Delta from baseline: {-delta_value:+.1f} {lever.delta_label}")
            st.caption(lever.assumption_note)

    projection = project_scenario_lab(
        view,
        target_prebill_clearance_rate=lever_targets["prebill_clearance_rate"],
        target_correction_turnaround_days=lever_targets["correction_turnaround_days"],
        target_routing_speed_days=lever_targets["routing_speed_to_owner_teams"],
    )

    st.info(
        "What-if operational improvement only. This page does not change queue routing logic, priority formulas, denials workflows, or introduce any predictive model."
    )

    render_section_header(
        "Projected Impact",
        "Directional operating impact from the current filtered slice. Displayed as a what-if estimate, not forecast certainty.",
    )
    render_kpi_row(
        [
            KpiCard(
                "Projected recoverable dollar lift",
                format_currency(projection.projected_recoverable_dollar_lift),
                "Monthly directional lift after conservative caps.",
            ),
            KpiCard(
                "Projected open-exception / backlog reduction",
                f"{projection.projected_backlog_reduction} fewer",
                "Estimated 90-day backlog reduction from current prebill and routing pressure.",
            ),
            KpiCard(
                "Projected SLA improvement",
                f"+{projection.projected_sla_improvement_points:.1f} pts",
                "Within-SLA rate improvement from current non-within-SLA work only.",
            ),
            KpiCard(
                "90-day impact estimate",
                format_currency(projection.ninety_day_impact_estimate),
                "Three-month roll-forward of the projected monthly dollar lift.",
            ),
            KpiCard(
                "Implementation effort framing",
                projection.implementation_effort,
                "Simple framing only; larger lever movement implies broader operational effort.",
            ),
        ]
    )

    render_table_section(
        "Scenario Output Detail",
        "Baseline, scenario, change, and assumption note for each leader-facing output.",
        projection.output_summary,
        column_labels={
            "output": "Output",
            "baseline": "Baseline",
            "scenario": "Scenario",
            "change": "Change",
            "assumption_note": "Assumption note",
        },
        height=290,
    )

    left, right = st.columns(2)
    with left:
        render_table_section(
            "Baseline Metric Inputs Used",
            "Current deterministic inputs pulled from governed repo outputs and the filtered active slice.",
            view.baseline_inputs,
            column_labels={
                "baseline_metric": "Baseline metric",
                "value": "Value",
                "source": "Source",
                "note": "Note",
            },
            height=360,
        )
    with right:
        render_table_section(
            "Scenario Deltas",
            "Baseline, target, and delta for the three current levers only.",
            projection.lever_summary,
            column_labels={
                "lever": "Lever",
                "baseline": "Baseline",
                "target": "Target",
                "delta": "Delta",
                "assumption_note": "Assumption note",
            },
            height=360,
        )

    render_table_section(
        "How this is calculated",
        "Formulas, assumptions, and caps are shown directly. No hidden weights, opaque score blending, or fake confidence precision are used.",
        projection.formula_summary,
        column_labels={
            "step": "Step",
            "formula": "Formula",
            "result": "Result",
            "guardrail": "Caps / guardrails",
        },
        height=280,
    )
