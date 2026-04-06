from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.control_story import next_action_for_root_cause
from ri_control_room.ui.shared import (
    PageStoryCue,
    StoryCallout,
    SummaryFilters,
    apply_filters,
    empty_summary,
    format_count,
    format_currency,
    get_global_filter_options,
    get_global_filters,
    get_filter_options,
    load_work_population,
    normalize_filters,
    render_active_filter_summary,
    render_page_story_cue,
    scope_global_filters,
)
from ri_control_room.ui.theme import (
    KpiCard,
    render_kpi_row,
    render_page_shell,
    render_section_header,
    render_table_section,
)


QUEUE_NAME = "Modifiers / Edits / Prebill Holds"


@dataclass(frozen=True)
class ModifiersEditsView:
    filters: SummaryFilters
    filter_options: dict[str, tuple[str, ...]]
    filtered_population: pd.DataFrame
    story_cue: PageStoryCue
    unresolved_edits: pd.DataFrame
    prebill_aging_summary: pd.DataFrame
    repeat_patterns: pd.DataFrame
    unresolved_edit_count: int


def _load_edits(repo_root: Path | None = None) -> pd.DataFrame:
    return load_processed_artifact("edits_bill_holds", repo_root)


def _base_population(repo_root: Path | None = None) -> pd.DataFrame:
    population = load_work_population(repo_root)
    return population.loc[population["current_queue"] == QUEUE_NAME].copy()


def _unresolved_edits(filtered: pd.DataFrame, edits: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty or edits.empty:
        return empty_summary(
            [
                "encounter_id",
                "claim_id",
                "payer_group",
                "current_primary_blocker_state",
                "age_days",
                "current_owner_team",
                "preventable_flag",
            ]
        )
    merged = filtered.merge(
        edits[
            [
                "encounter_id",
                "claim_id",
                "age_days",
                "current_owner_team",
                "current_primary_blocker_state",
                "preventable_flag",
            ]
        ].rename(
            columns={
                "age_days": "edit_age_days",
                "current_owner_team": "edit_owner_team",
                "current_primary_blocker_state": "edit_blocker_state",
            }
        ),
        on=["encounter_id", "claim_id"],
        how="left",
    )
    return merged[
        [
            "encounter_id",
            "claim_id",
            "payer_group",
            "edit_blocker_state",
            "edit_age_days",
            "edit_owner_team",
            "preventable_flag",
        ]
    ].rename(
        columns={
            "edit_blocker_state": "current_primary_blocker_state",
            "edit_age_days": "age_days",
            "edit_owner_team": "current_owner_team",
        }
    ).copy()


def _prebill_aging_summary(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(["department", "open_edits", "average_age_days", "recoverable_dollars"])
    summary = (
        filtered.groupby("department", as_index=False)
        .agg(
            open_edits=("queue_item_id", "size"),
            average_age_days=("stage_age_days", "mean"),
            recoverable_dollars=("estimated_gross_dollars", "sum"),
        )
        .sort_values(["open_edits", "recoverable_dollars", "department"], ascending=[False, False, True])
        .reset_index(drop=True)
    )
    summary["average_age_days"] = summary["average_age_days"].round(2)
    summary["recoverable_dollars"] = summary["recoverable_dollars"].round(2)
    return summary


def _repeat_patterns(filtered: pd.DataFrame) -> pd.DataFrame:
    if filtered.empty:
        return empty_summary(["payer_group", "department", "open_edits", "repeat_exceptions", "repeat_rate"])
    summary = (
        filtered.groupby(["payer_group", "department"], as_index=False)
        .agg(
            open_edits=("queue_item_id", "size"),
            repeat_exceptions=("repeat_exception_flag", "sum"),
        )
        .sort_values(["repeat_exceptions", "open_edits", "payer_group", "department"], ascending=[False, False, True, True])
        .reset_index(drop=True)
    )
    summary["repeat_rate"] = (
        summary["repeat_exceptions"] / summary["open_edits"].replace(0, pd.NA)
    ).fillna(0.0).round(4)
    return summary


def _story_cue(
    filtered: pd.DataFrame,
    unresolved: pd.DataFrame,
    prebill_aging_summary: pd.DataFrame,
    repeat_patterns: pd.DataFrame,
) -> PageStoryCue:
    if filtered.empty:
        return PageStoryCue(
            sentence=(
                "This page tracks modifier-related edits and prebill holds, but no open edit work "
                "matches the current filters."
            ),
            callouts=(
                StoryCallout(
                    "Control",
                    "Modifier-driven edit resolution before accounts age deeper in prebill hold.",
                ),
                StoryCallout(
                    "Current pressure",
                    "No unresolved modifier edit pressure is in scope right now.",
                ),
                StoryCallout(
                    "Next move",
                    "No billing-owner follow-up is needed until a prebill hold re-enters scope.",
                ),
            ),
            note="Repeat payer and department patterns stay visible when open edit work exists.",
        )

    lead_row = filtered.sort_values(
        ["stage_age_days", "priority_rank", "queue_item_id"],
        ascending=[False, True, True],
        kind="mergesort",
    ).iloc[0]
    sentence = (
        "This page watches unresolved prebill edit pressure so modifier-driven holds do not stay "
        "hidden as passive aging metrics."
    )
    if not repeat_patterns.empty and int(repeat_patterns.iloc[0]["repeat_exceptions"]) > 0:
        repeat_row = repeat_patterns.iloc[0]
        pressure_text = (
            f"{repeat_row['department']} / {repeat_row['payer_group']} shows "
            f"{int(repeat_row['open_edits'])} open edits with "
            f"{int(repeat_row['repeat_exceptions'])} repeat handoff(s) "
            f"({float(repeat_row['repeat_rate']):.0%})."
        )
    else:
        aging_row = prebill_aging_summary.iloc[0]
        pressure_text = (
            f"{aging_row['department']} is carrying {int(aging_row['open_edits'])} open edit(s) at "
            f"{float(aging_row['average_age_days']):.1f} average days."
        )

    pre_final_bill_count = int(
        (filtered["recoverability_status"] == "Pre-final-bill recoverable").sum()
    )
    next_move = (
        f"{lead_row['accountable_owner']} owns the next hold-clearance move on {lead_row['encounter_id']}; "
        f"{next_action_for_root_cause(lead_row['root_cause_mechanism'])}"
    )
    return PageStoryCue(
        sentence=sentence,
        callouts=(
            StoryCallout(
                "Control",
                "Prebill edit resolution, unresolved hold visibility, and repeat handoff concentration.",
            ),
            StoryCallout("Current pressure", pressure_text),
            StoryCallout("Next move", next_move),
        ),
        note=(
            f"{pre_final_bill_count} open item(s) remain pre-final-bill recoverable in the current slice."
        ),
    )


def build_modifiers_edits_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> ModifiersEditsView:
    population = _base_population(repo_root)
    normalized_filters = normalize_filters(filters)
    filter_options = get_filter_options(population)
    filtered = apply_filters(population, normalized_filters)
    edits = _load_edits(repo_root)
    unresolved = _unresolved_edits(filtered, edits)
    prebill_aging_summary = _prebill_aging_summary(filtered)
    repeat_patterns = _repeat_patterns(filtered)
    return ModifiersEditsView(
        filters=normalized_filters,
        filter_options=filter_options,
        filtered_population=filtered,
        story_cue=_story_cue(
            filtered,
            unresolved,
            prebill_aging_summary,
            repeat_patterns,
        ),
        unresolved_edits=unresolved,
        prebill_aging_summary=prebill_aging_summary,
        repeat_patterns=repeat_patterns,
        unresolved_edit_count=int(len(unresolved)),
    )


def render_modifiers_edits_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        "Deterministic view of modifier-related edits, prebill aging, and repeat payer patterns in the active work queue.",
        scope_note,
        badges=("Facility-side only", "Outpatient-first", QUEUE_NAME),
    )
    selected_filters = scope_global_filters(
        get_global_filters(global_filter_options),
        queues=False,
    )
    view = build_modifiers_edits_view(repo_root=repo_root, filters=selected_filters)
    render_active_filter_summary(
        view.filters,
        inactive_reasons={
            "queues": f"Fixed to {QUEUE_NAME} on this page.",
        },
    )
    render_page_story_cue(view.story_cue)

    render_section_header(
        "Modifiers Snapshot",
        "Queue health for modifier-driven edit work and prebill holds.",
    )
    render_kpi_row(
        [
            KpiCard(
                "Unresolved modifier edits",
                format_count(view.unresolved_edit_count),
                "Open work items currently sitting in the modifier and edit queue.",
            ),
            KpiCard(
                "Prebill dollars open",
                format_currency(float(view.filtered_population["estimated_gross_dollars"].sum())),
                "Estimated gross dollars still blocked behind open edits or holds.",
            ),
            KpiCard(
                "Repeat edit patterns",
                format_count(
                    int(view.repeat_patterns["repeat_exceptions"].sum()) if not view.repeat_patterns.empty else 0
                ),
                "Repeat exceptions surfaced across payer and department combinations.",
            ),
        ]
    )

    if view.filtered_population.empty:
        st.warning("No modifier or prebill edit work matches the current filters.")
        return

    render_table_section(
        "Unresolved Modifier-Related Edits",
        "Detailed edit worklist with blocker state, age, and current owner team.",
        view.unresolved_edits,
        column_labels={
            "encounter_id": "Encounter",
            "claim_id": "Claim",
            "payer_group": "Payer group",
            "current_primary_blocker_state": "Primary blocker state",
            "age_days": "Age days",
            "current_owner_team": "Current owner team",
            "preventable_flag": "Preventable",
        },
        integer_columns=("age_days",),
        height=340,
    )
    render_table_section(
        "Prebill Aging",
        "Department-level scan of aging prebill edit pressure.",
        view.prebill_aging_summary,
        column_labels={
            "department": "Department",
            "open_edits": "Open edits",
            "average_age_days": "Average age days",
            "recoverable_dollars": "Recoverable dollars",
        },
        integer_columns=("open_edits",),
        decimal_columns=("average_age_days",),
        currency_columns=("recoverable_dollars",),
        height=250,
    )
    render_table_section(
        "Repeat Payer / Department Patterns",
        "Repeat-exception concentration by payer group and department.",
        view.repeat_patterns,
        column_labels={
            "payer_group": "Payer group",
            "department": "Department",
            "open_edits": "Open edits",
            "repeat_exceptions": "Repeat exceptions",
            "repeat_rate": "Repeat rate",
        },
        integer_columns=("open_edits", "repeat_exceptions"),
        percent_columns=("repeat_rate",),
        height=280,
    )
