from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_existing_priority_scores
from ri_control_room.ui.theme import apply_theme


RECOVERABLE_STATES = {
    "Pre-final-bill recoverable",
    "Post-final-bill recoverable by correction / rebill",
}
GLOBAL_FILTER_STATE_KEY = "ri_global_filters"

FILTER_LABELS = {
    "departments": "Department",
    "service_lines": "Service line",
    "queues": "Queue",
    "recoverability_states": "Recoverability",
}

FILTER_ALL_LABELS = {
    "departments": "All departments",
    "service_lines": "All service lines",
    "queues": "All queues",
    "recoverability_states": "All recoverability states",
}


@dataclass(frozen=True)
class SummaryFilters:
    departments: tuple[str, ...] = ()
    service_lines: tuple[str, ...] = ()
    queues: tuple[str, ...] = ()
    recoverability_states: tuple[str, ...] = ()


@dataclass(frozen=True)
class StoryCallout:
    label: str
    value: str


@dataclass(frozen=True)
class PageStoryCue:
    sentence: str
    callouts: tuple[StoryCallout, ...]
    note: str = ""
    title: str = "What This Page Is Telling You"


def load_work_population(repo_root: Path | None = None) -> pd.DataFrame:
    return load_existing_priority_scores(repo_root)


def normalize_filters(filters: SummaryFilters | None) -> SummaryFilters:
    if filters is None:
        return SummaryFilters()
    return SummaryFilters(
        departments=tuple(filters.departments),
        service_lines=tuple(filters.service_lines),
        queues=tuple(filters.queues),
        recoverability_states=tuple(filters.recoverability_states),
    )


def get_filter_options(population: pd.DataFrame) -> dict[str, tuple[str, ...]]:
    return {
        "departments": tuple(sorted(population["department"].dropna().unique())),
        "service_lines": tuple(sorted(population["service_line"].dropna().unique())),
        "queues": tuple(sorted(population["current_queue"].dropna().unique())),
        "recoverability_states": tuple(sorted(population["recoverability_status"].dropna().unique())),
    }


def get_global_filter_options(repo_root: Path | None = None) -> dict[str, tuple[str, ...]]:
    return get_filter_options(load_work_population(repo_root))


def apply_filters(population: pd.DataFrame, filters: SummaryFilters) -> pd.DataFrame:
    filtered = population.copy()
    if filters.departments:
        filtered = filtered.loc[filtered["department"].isin(filters.departments)]
    if filters.service_lines:
        filtered = filtered.loc[filtered["service_line"].isin(filters.service_lines)]
    if filters.queues:
        filtered = filtered.loc[filtered["current_queue"].isin(filters.queues)]
    if filters.recoverability_states:
        filtered = filtered.loc[
            filtered["recoverability_status"].isin(filters.recoverability_states)
        ]
    return filtered.sort_values(["priority_rank", "encounter_id"]).reset_index(drop=True)


def empty_summary(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_count(value: int) -> str:
    return f"{value:,}"


def _get_session_state() -> dict[str, object]:
    import streamlit as st

    session_state = getattr(st, "session_state", None)
    if session_state is None:
        fallback = getattr(st, "_ri_session_state", None)
        if fallback is None:
            fallback = {}
            setattr(st, "_ri_session_state", fallback)
        return fallback
    return session_state


def _default_filter_state(
    filter_options: dict[str, tuple[str, ...]],
) -> dict[str, tuple[str, ...]]:
    return {
        key: tuple(values)
        for key, values in filter_options.items()
    }


def _sanitize_filter_selection(
    selected_values: object,
    options: tuple[str, ...],
) -> tuple[str, ...]:
    if selected_values is None:
        return tuple(options)
    return tuple(
        value for value in tuple(selected_values) if value in options
    )


def _initialize_global_filter_state(
    filter_options: dict[str, tuple[str, ...]],
) -> None:
    session_state = _get_session_state()
    defaults = _default_filter_state(filter_options)
    existing = session_state.get(GLOBAL_FILTER_STATE_KEY)
    if not isinstance(existing, dict):
        session_state[GLOBAL_FILTER_STATE_KEY] = defaults
        return

    normalized_state: dict[str, tuple[str, ...]] = {}
    for key, options in filter_options.items():
        if key not in existing:
            normalized_state[key] = defaults[key]
            continue
        normalized_state[key] = _sanitize_filter_selection(existing.get(key), options)
    session_state[GLOBAL_FILTER_STATE_KEY] = normalized_state


def get_global_filters(
    filter_options: dict[str, tuple[str, ...]] | None = None,
) -> SummaryFilters:
    session_state = _get_session_state()
    if filter_options is not None:
        _initialize_global_filter_state(filter_options)

    existing = session_state.get(GLOBAL_FILTER_STATE_KEY)
    if not isinstance(existing, dict):
        return SummaryFilters()
    return SummaryFilters(
        departments=tuple(existing.get("departments", ())),
        service_lines=tuple(existing.get("service_lines", ())),
        queues=tuple(existing.get("queues", ())),
        recoverability_states=tuple(existing.get("recoverability_states", ())),
    )


def scope_global_filters(
    filters: SummaryFilters,
    *,
    departments: bool = True,
    service_lines: bool = True,
    queues: bool = True,
    recoverability_states: bool = True,
) -> SummaryFilters:
    return SummaryFilters(
        departments=filters.departments if departments else (),
        service_lines=filters.service_lines if service_lines else (),
        queues=filters.queues if queues else (),
        recoverability_states=(
            filters.recoverability_states if recoverability_states else ()
        ),
    )


def render_global_sidebar_filters(
    filter_options: dict[str, tuple[str, ...]],
) -> SummaryFilters:
    import streamlit as st

    _initialize_global_filter_state(filter_options)
    session_state = _get_session_state()
    state = get_global_filters(filter_options)

    st.sidebar.markdown("### Global Control Filters")
    if hasattr(st.sidebar, "caption"):
        st.sidebar.caption(
            "Persistent app-level filters for the current operating pages."
        )

    selected_departments = st.sidebar.multiselect(
        "Department",
        options=list(filter_options["departments"]),
        default=list(state.departments),
    )
    selected_service_lines = st.sidebar.multiselect(
        "Service line",
        options=list(filter_options["service_lines"]),
        default=list(state.service_lines),
    )
    selected_queues = st.sidebar.multiselect(
        "Queue",
        options=list(filter_options["queues"]),
        default=list(state.queues),
    )
    selected_recoverability = st.sidebar.multiselect(
        "Recoverability",
        options=list(filter_options["recoverability_states"]),
        default=list(state.recoverability_states),
    )

    updated_filters = SummaryFilters(
        departments=tuple(selected_departments),
        service_lines=tuple(selected_service_lines),
        queues=tuple(selected_queues),
        recoverability_states=tuple(selected_recoverability),
    )
    session_state[GLOBAL_FILTER_STATE_KEY] = {
        "departments": updated_filters.departments,
        "service_lines": updated_filters.service_lines,
        "queues": updated_filters.queues,
        "recoverability_states": updated_filters.recoverability_states,
    }

    if st.sidebar.button("Reset filters"):
        session_state[GLOBAL_FILTER_STATE_KEY] = _default_filter_state(filter_options)
        rerun = getattr(st, "rerun", None)
        if callable(rerun):
            rerun()
        return get_global_filters(filter_options)

    return updated_filters


def _summarize_filter_values(values: tuple[str, ...], key: str) -> str:
    if not values:
        return FILTER_ALL_LABELS[key]
    if len(values) == 1:
        return values[0]
    return f"{len(values)} selected"


def render_active_filter_summary(
    filters: SummaryFilters,
    *,
    inactive_reasons: dict[str, str] | None = None,
) -> None:
    import streamlit as st

    apply_theme()
    inactive_reasons = inactive_reasons or {}
    pills: list[str] = []
    ordered_keys = (
        "departments",
        "service_lines",
        "queues",
        "recoverability_states",
    )
    values_by_key = {
        "departments": filters.departments,
        "service_lines": filters.service_lines,
        "queues": filters.queues,
        "recoverability_states": filters.recoverability_states,
    }
    for key in ordered_keys:
        if key in inactive_reasons:
            pills.append(f"{FILTER_LABELS[key]}: {inactive_reasons[key]}")
            continue
        pills.append(
            f"{FILTER_LABELS[key]}: {_summarize_filter_values(values_by_key[key], key)}"
        )

    if hasattr(st, "markdown"):
        st.markdown(
            "<div class='cr-page-eyebrow'>Active Filters</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='cr-note-row'>"
            + "".join(
                f"<span class='cr-note-pill'>{escape(pill)}</span>"
                for pill in pills
            )
            + "</div>",
            unsafe_allow_html=True,
        )
        return
    if hasattr(st, "caption"):
        st.caption(" | ".join(pills))


def render_page_story_cue(cue: PageStoryCue) -> None:
    import streamlit as st

    apply_theme()
    if hasattr(st, "markdown"):
        callouts = "".join(
            (
                "<div class='cr-story-item'>"
                f"<div class='cr-story-label'>{escape(callout.label)}</div>"
                f"<div class='cr-story-value'>{escape(callout.value)}</div>"
                "</div>"
            )
            for callout in cue.callouts
        )
        note_html = (
            f"<div class='cr-story-note'>{escape(cue.note)}</div>"
            if cue.note
            else ""
        )
        st.markdown(
            (
                "<div class='cr-story-card'>"
                f"<div class='cr-page-eyebrow'>{escape(cue.title)}</div>"
                f"<div class='cr-story-lead'>{escape(cue.sentence)}</div>"
                f"<div class='cr-story-grid'>{callouts}</div>"
                f"{note_html}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        return

    if hasattr(st, "subheader"):
        st.subheader(cue.title)
    if hasattr(st, "caption"):
        st.caption(cue.sentence)
        for callout in cue.callouts:
            st.caption(f"{callout.label}: {callout.value}")
        if cue.note:
            st.caption(cue.note)
