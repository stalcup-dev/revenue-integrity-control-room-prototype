from __future__ import annotations

from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from html import escape
from typing import Any, Iterable

import pandas as pd

_THEME_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(28, 76, 120, 0.08), transparent 26%),
            linear-gradient(180deg, rgba(16, 42, 67, 0.04) 0%, transparent 220px);
    }

    .block-container {
        max-width: min(1880px, 97vw);
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(16, 42, 67, 0.98) 0%, rgba(12, 33, 51, 0.96) 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f3f7fb;
    }

    .cr-sidebar-title {
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.45;
        letter-spacing: 0.01em;
        margin-bottom: 1rem;
    }

    .cr-sidebar-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 0.95rem 1rem;
        margin-bottom: 0.9rem;
    }

    .cr-sidebar-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
        opacity: 0.86;
        text-transform: uppercase;
    }

    .cr-sidebar-text {
        font-size: 0.9rem;
        line-height: 1.45;
        opacity: 0.96;
    }

    .cr-sidebar-list {
        margin: 0;
        padding-left: 1rem;
    }

    .cr-sidebar-list li {
        margin: 0.2rem 0;
    }

    .cr-page-eyebrow {
        color: var(--text-color);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin-bottom: 0.35rem;
        opacity: 0.78;
        text-transform: uppercase;
    }

    .cr-page-subtitle {
        color: var(--text-color);
        font-size: 1.02rem;
        line-height: 1.55;
        margin: -0.35rem 0 0.95rem 0;
        max-width: 980px;
        opacity: 0.9;
    }

    .cr-note-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0 0 1.25rem 0;
    }

    .cr-note-pill {
        background: linear-gradient(180deg, rgba(232, 240, 248, 0.98) 0%, rgba(222, 233, 244, 0.98) 100%);
        border: 1px solid rgba(23, 50, 77, 0.14);
        border-radius: 999px;
        color: #17324d;
        display: inline-flex;
        font-size: 0.79rem;
        font-weight: 600;
        line-height: 1.2;
        opacity: 1;
        padding: 0.42rem 0.8rem;
    }

    .cr-story-card {
        background:
            linear-gradient(
                180deg,
                color-mix(in srgb, var(--secondary-background-color) 97%, #1c4c78 3%) 0%,
                color-mix(in srgb, var(--secondary-background-color) 93%, #1c4c78 7%) 100%
            );
        border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
        border-radius: 22px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.04);
        margin: 0.15rem 0 1.15rem 0;
        padding: 1rem 1.05rem 1.05rem 1.05rem;
    }

    .cr-story-lead {
        color: var(--text-color);
        font-size: 0.96rem;
        font-weight: 600;
        line-height: 1.55;
        margin-bottom: 0.85rem;
        max-width: 1100px;
    }

    .cr-story-grid {
        display: grid;
        gap: 0.7rem;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    }

    .cr-story-item {
        background: rgba(255, 255, 255, 0.48);
        border: 1px solid rgba(23, 50, 77, 0.1);
        border-radius: 16px;
        padding: 0.8rem 0.85rem;
    }

    .cr-story-label {
        color: var(--text-color);
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        line-height: 1.3;
        margin-bottom: 0.35rem;
        opacity: 0.72;
        text-transform: uppercase;
    }

    .cr-story-value {
        color: var(--text-color);
        font-size: 0.91rem;
        font-weight: 600;
        line-height: 1.5;
    }

    .cr-story-note {
        color: var(--text-color);
        font-size: 0.82rem;
        line-height: 1.5;
        margin-top: 0.8rem;
        opacity: 0.8;
    }

    .cr-section-heading {
        color: var(--text-color);
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        margin-bottom: 0.15rem;
    }

    .cr-section-subtitle {
        color: var(--text-color);
        font-size: 0.88rem;
        line-height: 1.5;
        margin-bottom: 0.8rem;
        opacity: 0.84;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                180deg,
                color-mix(in srgb, var(--secondary-background-color) 96%, #1c4c78 4%) 0%,
                color-mix(in srgb, var(--secondary-background-color) 92%, #1c4c78 8%) 100%
            );
        border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
        border-radius: 18px;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
        min-height: 142px;
        padding: 1rem 1.05rem;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--text-color);
        font-size: 0.73rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        opacity: 0.78;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text-color);
        font-size: 2.3rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    div[data-testid="stMetricDelta"] {
        color: var(--text-color);
        opacity: 0.82;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(
                180deg,
                color-mix(in srgb, var(--secondary-background-color) 96%, #1c4c78 4%) 0%,
                color-mix(in srgb, var(--secondary-background-color) 93%, #1c4c78 7%) 100%
            );
        border-radius: 20px;
        border: 1px solid color-mix(in srgb, var(--text-color) 10%, transparent);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMultiSelect"] label p {
        color: var(--text-color);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        opacity: 0.86;
        text-transform: uppercase;
    }

    div[data-testid="stMultiSelect"] [data-baseweb="select"] {
        background: color-mix(in srgb, var(--secondary-background-color) 90%, #285d8a 10%);
        border-color: color-mix(in srgb, var(--text-color) 14%, transparent);
        border-radius: 16px;
    }

    div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: color-mix(in srgb, var(--secondary-background-color) 66%, #2c6ea6 34%);
        border: 1px solid color-mix(in srgb, var(--text-color) 18%, transparent);
        color: var(--text-color);
        opacity: 0.96;
    }

    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] {
        background: transparent !important;
        background-color: transparent !important;
        border-color: rgba(255, 255, 255, 0.16) !important;
    }

    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] > div,
    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: linear-gradient(180deg, rgba(23, 55, 86, 0.98) 0%, rgba(16, 42, 67, 0.98) 100%) !important;
        background-color: rgba(16, 42, 67, 0.98) !important;
        border-radius: 16px !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] span[data-baseweb="tag"] {
        background: rgba(255, 255, 255, 0.08) !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #f3f7fb !important;
        -webkit-text-fill-color: #f3f7fb !important;
    }

    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] span[data-baseweb="tag"] *,
    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] input,
    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] input::placeholder,
    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] svg {
        color: #f3f7fb !important;
        fill: #f3f7fb !important;
        -webkit-text-fill-color: #f3f7fb !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: linear-gradient(180deg, rgba(23, 55, 86, 0.98) 0%, rgba(16, 42, 67, 0.98) 100%) !important;
        background-color: rgba(16, 42, 67, 0.98) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        color: #f3f7fb !important;
        -webkit-text-fill-color: #f3f7fb !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        border-color: rgba(255, 255, 255, 0.28) !important;
        background: linear-gradient(180deg, rgba(27, 62, 96, 0.98) 0%, rgba(18, 46, 73, 0.98) 100%) !important;
        background-color: rgba(18, 46, 73, 0.98) !important;
        color: #ffffff !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    div[data-testid="stDataFrame"] [role="columnheader"] {
        background: color-mix(in srgb, var(--secondary-background-color) 74%, #295e8d 26%) !important;
        color: var(--text-color) !important;
        font-weight: 700 !important;
    }

    div[data-testid="stDataFrame"] [role="gridcell"] {
        color: var(--text-color) !important;
    }

    div[data-testid="stDataFrame"] [role="gridcell"] span,
    div[data-testid="stDataFrame"] [role="columnheader"] span {
        color: var(--text-color) !important;
    }

    [data-testid="stCaptionContainer"] {
        margin-top: 0.15rem;
        color: var(--text-color);
        opacity: 0.82;
    }
</style>
"""


@dataclass(frozen=True)
class KpiCard:
    label: str
    value: str | int | float
    help_text: str = ""


def _call_if_present(target: Any, method_name: str, *args: Any, **kwargs: Any) -> Any:
    method = getattr(target, method_name, None)
    if callable(method):
        return method(*args, **kwargs)
    return None


def apply_theme() -> None:
    import streamlit as st

    if not hasattr(st, "markdown"):
        return
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


@contextmanager
def panel(border: bool = True):
    import streamlit as st

    apply_theme()
    container = getattr(st, "container", None)
    if not callable(container):
        with nullcontext():
            yield
        return
    try:
        with container(border=border):
            yield
        return
    except TypeError:
        with container():
            yield


def render_page_header(
    title: str,
    subtitle: str,
    scope_note: str,
    badges: Iterable[str] = (),
) -> None:
    import streamlit as st

    apply_theme()
    _call_if_present(
        st,
        "markdown",
        "<div class='cr-page-eyebrow'>Hospital Revenue Integrity Control Room</div>",
        unsafe_allow_html=True,
    )
    st.title(title)
    _call_if_present(
        st,
        "markdown",
        f"<div class='cr-page-subtitle'>{escape(subtitle)}</div>",
        unsafe_allow_html=True,
    )
    note_pills = [scope_note, *badges]
    if note_pills:
        pills = "".join(
            f"<span class='cr-note-pill'>{escape(note)}</span>"
            for note in note_pills
        )
        _call_if_present(
            st,
            "markdown",
            f"<div class='cr-note-row'>{pills}</div>",
            unsafe_allow_html=True,
        )


def render_page_shell(
    title: str,
    subtitle: str,
    scope_note: str,
    badges: Iterable[str] = (),
) -> None:
    apply_theme()
    render_page_header(title, subtitle, scope_note, badges=badges)


def render_section_header(title: str, subtitle: str = "") -> None:
    import streamlit as st

    apply_theme()
    if hasattr(st, "markdown"):
        st.markdown(
            f"<div class='cr-section-heading'>{escape(title)}</div>",
            unsafe_allow_html=True,
        )
        if subtitle:
            st.markdown(
                f"<div class='cr-section-subtitle'>{escape(subtitle)}</div>",
                unsafe_allow_html=True,
            )
        return
    st.subheader(title)
    if subtitle:
        _call_if_present(st, "caption", subtitle)


def render_kpi_row(cards: list[KpiCard]) -> None:
    import streamlit as st

    apply_theme()
    for column, card in zip(st.columns(len(cards)), cards, strict=False):
        with column:
            st.metric(card.label, card.value)
            if card.help_text:
                _call_if_present(st, "caption", card.help_text)


def render_sidebar_shell(
    sidebar: Any,
    app_title: str,
    scope_note: str,
    departments: Iterable[str],
) -> None:
    apply_theme()
    if hasattr(sidebar, "markdown"):
        sidebar.markdown(
            f"<div class='cr-sidebar-title'>{escape(app_title)}</div>",
            unsafe_allow_html=True,
        )
        sidebar.markdown(
            (
                "<div class='cr-sidebar-card'>"
                "<div class='cr-sidebar-label'>Scope</div>"
                f"<div class='cr-sidebar-text'>{escape(scope_note)}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        department_list = "".join(
            f"<li>{escape(department)}</li>"
            for department in departments
        )
        sidebar.markdown(
            (
                "<div class='cr-sidebar-card'>"
                "<div class='cr-sidebar-label'>Current In-Scope Departments</div>"
                f"<ul class='cr-sidebar-text cr-sidebar-list'>{department_list}</ul>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        return
    _call_if_present(sidebar, "title", app_title)
    _call_if_present(sidebar, "caption", "Scope")
    _call_if_present(sidebar, "write", scope_note)
    _call_if_present(sidebar, "caption", "Current in-scope departments")
    for department in departments:
        _call_if_present(sidebar, "write", f"- {department}")


def render_filter_header(title: str, subtitle: str) -> None:
    render_section_header(title, subtitle)


def _status_cell_style(value: Any) -> str:
    if value is None:
        return ""
    normalized = str(value).lower()
    if "overdue" in normalized or "lost" in normalized or "escalate" in normalized:
        return "background-color: rgba(153, 27, 27, 0.08); color: #7f1d1d;"
    if "at risk" in normalized or "review" in normalized:
        return "background-color: rgba(180, 83, 9, 0.1); color: #8a4b08;"
    if "recoverable" in normalized or "queued" in normalized or "within sla" in normalized:
        return "background-color: rgba(3, 105, 96, 0.09); color: #0f5f59;"
    return ""


def render_dataframe(
    dataframe: pd.DataFrame,
    *,
    column_labels: dict[str, str] | None = None,
    currency_columns: Iterable[str] = (),
    integer_columns: Iterable[str] = (),
    decimal_columns: Iterable[str] = (),
    percent_columns: Iterable[str] = (),
    status_columns: Iterable[str] = (),
    column_widths: dict[str, str] | None = None,
    height: int | None = None,
) -> None:
    import streamlit as st

    apply_theme()
    if dataframe.empty:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
        return

    column_labels = column_labels or {}
    currency_columns = tuple(currency_columns)
    integer_columns = tuple(integer_columns)
    decimal_columns = tuple(decimal_columns)
    percent_columns = tuple(percent_columns)
    status_columns = tuple(status_columns)
    column_widths = column_widths or {}

    styled = dataframe.style
    format_map: dict[str, Any] = {}
    format_map.update({column: "${:,.0f}" for column in currency_columns})
    format_map.update({column: "{:,.0f}" for column in integer_columns})
    format_map.update({column: "{:,.1f}" for column in decimal_columns})
    format_map.update({column: "{:.1%}" for column in percent_columns})
    if format_map:
        styled = styled.format(format_map)
    for column in status_columns:
        if column in dataframe.columns:
            styled = styled.map(_status_cell_style, subset=[column])

    column_config: dict[str, Any] | None = None
    if hasattr(st, "column_config"):
        column_config = {}
        for column in dataframe.columns:
            label = column_labels.get(column, column.replace("_", " ").title())
            width = column_widths.get(column)
            if column in currency_columns or column in integer_columns or column in decimal_columns:
                column_config[column] = st.column_config.NumberColumn(label, width=width)
            elif column in percent_columns:
                column_config[column] = st.column_config.NumberColumn(label, width=width)
            else:
                column_config[column] = st.column_config.TextColumn(label, width=width)

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        height=height,
        column_config=column_config,
    )


def render_table_section(
    title: str,
    subtitle: str,
    dataframe: pd.DataFrame,
    **table_kwargs: Any,
) -> None:
    with panel():
        render_section_header(title, subtitle)
        render_dataframe(dataframe, **table_kwargs)
