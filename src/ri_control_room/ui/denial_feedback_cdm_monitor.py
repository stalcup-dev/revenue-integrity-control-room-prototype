from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_processed_artifact
from ri_control_room.ui.shared import (
    SummaryFilters,
    format_count,
    format_currency,
    get_global_filter_options,
    get_global_filters,
    render_active_filter_summary,
    scope_global_filters,
)
from ri_control_room.ui.theme import (
    KpiCard,
    render_kpi_row,
    render_page_shell,
    render_section_header,
    render_table_section,
)


ALL_SETTINGS_LABEL = "All frozen V1 departments"


@dataclass(frozen=True)
class DenialFeedbackCdmMonitorView:
    filters: SummaryFilters
    denial_signal_patterns: pd.DataFrame
    cdm_governance_monitor: pd.DataFrame
    linkage_detail: pd.DataFrame
    pattern_selector_options: tuple[str, ...]
    default_selected_pattern_id: str | None
    denial_signal_count: int
    denial_dollars: float
    governed_prebill_edit_aging: float
    governed_recoverable_dollars_still_open: float
    correction_turnaround_days: float


def _load_cdm_reference(repo_root: Path | None = None) -> pd.DataFrame:
    path = Path(repo_root or Path.cwd()) / "data" / "reference" / "cdm_reference.csv"
    return pd.read_csv(path)


def _load_logic_map(repo_root: Path | None = None) -> pd.DataFrame:
    path = Path(repo_root or Path.cwd()) / "data" / "reference" / "department_charge_logic_map.csv"
    return pd.read_csv(path)


def _load_root_cause_map(repo_root: Path | None = None) -> pd.DataFrame:
    path = Path(repo_root or Path.cwd()) / "data" / "reference" / "root_cause_map.csv"
    return pd.read_csv(path)


def _load_governed_kpis(repo_root: Path | None = None) -> pd.DataFrame:
    kpis = load_processed_artifact("kpi_snapshot", repo_root)
    return kpis.loc[kpis["record_type"] == "kpi"].copy()


def _normalize_modifier(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    normalized = str(value).strip()
    return "" if normalized.lower() == "none" else normalized


def _safe_mean(series: pd.Series) -> float:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0.0
    return round(float(numeric.mean()), 2)


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


def _apply_department_service_line_filters(
    df: pd.DataFrame,
    filters: SummaryFilters,
) -> pd.DataFrame:
    scoped = df.copy()
    if filters.departments and "department" in scoped.columns:
        scoped = scoped.loc[scoped["department"].isin(filters.departments)]
    if filters.service_lines and "service_line" in scoped.columns:
        scoped = scoped.loc[scoped["service_line"].isin(filters.service_lines)]
    return scoped.reset_index(drop=True)


def _denial_signal_strength(row_count: int, denial_amount: float) -> str:
    if row_count >= 3 or denial_amount >= 1000:
        return "High"
    if row_count >= 2 or denial_amount >= 300:
        return "Moderate"
    return "Low"


def _cdm_governance_flag(row: pd.Series) -> str:
    cdm_item_id = str(row.get("cdm_item_id", "") or "")
    cdm_modifier = _normalize_modifier(row.get("cdm_expected_modifier"))
    expected_modifier = _normalize_modifier(row.get("expected_modifier_hint"))
    revenue_code = str(row.get("revenue_code", "") or "").strip()
    active_flag = str(row.get("active_flag", "") or "").strip().lower()
    rule_status = str(row.get("rule_status", "") or "").strip().lower()

    if not cdm_item_id:
        return "Missing CDM reference"
    if active_flag != "true" or rule_status in {"stale", "inactive_reference"}:
        return "Stale / inactive reference"
    if expected_modifier and cdm_modifier != expected_modifier:
        return "Modifier mismatch"
    if revenue_code == "":
        return "Revenue-code gap"
    if rule_status == "review_needed":
        return "Rule review needed"
    return "Active aligned reference"


def _interpretation_bucket(row: pd.Series) -> str:
    governance_flag = str(row.get("cdm_governance_flag", ""))
    reason_group = str(row.get("denial_reason_group", ""))
    denial_category = str(row.get("denial_category", ""))
    upstream_root_cause = str(row.get("linked_root_cause_mechanism", ""))

    if governance_flag in {
        "Missing CDM reference",
        "Stale / inactive reference",
        "Modifier mismatch",
        "Revenue-code gap",
        "Rule review needed",
    }:
        return "CDM / rule configuration"
    if reason_group in {"technical_rebill_review", "postbill_rebill_variance"}:
        return "Billing edit management"
    if reason_group == "modifier_validation":
        return "Coding practice"
    if denial_category == "documentation_support_denial":
        return "Documentation behavior"
    return upstream_root_cause or "Payer-policy variance"


def _suggested_action(row: pd.Series) -> str:
    interpretation_bucket = str(row.get("interpretation_bucket", ""))
    governance_flag = str(row.get("cdm_governance_flag", ""))

    if governance_flag in {"Missing CDM reference", "Stale / inactive reference"}:
        return "CDM maintenance review"
    if governance_flag in {"Modifier mismatch", "Rule review needed", "Revenue-code gap"}:
        return "Build review"
    if interpretation_bucket == "Coding practice":
        return "Modifier logic review"
    if interpretation_bucket == "Billing edit management":
        return "Billing edit management review"
    if interpretation_bucket == "Documentation behavior":
        return "Education / documentation follow-up"
    return "Payer-variance watchlist"


def _owner_path(row: pd.Series) -> str:
    owner = str(row.get("linked_owner_team", "") or "")
    owner_hint = str(row.get("operational_owner_hint", "") or "")
    action = _suggested_action(row)
    if owner:
        return f"{owner} -> {action}"
    if owner_hint:
        return f"{owner_hint} -> {action}"
    return action


def _why_this_matters(row: pd.Series) -> str:
    failure_mode = str(row.get("common_failure_mode", "") or "")
    upstream_issue = str(row.get("linked_upstream_issue_domain", "") or "")
    code = str(row.get("expected_code_hint", "") or row.get("expected_code", "") or "")
    if failure_mode:
        return f"Downstream denial signal points back to {upstream_issue.lower()}: {failure_mode.lower()}."
    return f"Downstream denial signal points back to {upstream_issue.lower()} on expected code {code}."


def _build_denial_signal_base(
    repo_root: Path | None,
    filters: SummaryFilters,
) -> pd.DataFrame:
    denials = load_processed_artifact("denials_feedback", repo_root)
    statuses = load_processed_artifact("claims_or_account_status", repo_root)
    expected = load_processed_artifact("expected_charge_opportunities", repo_root)
    cdm_reference = _load_cdm_reference(repo_root).rename(
        columns={"expected_modifier": "cdm_expected_modifier"}
    )
    logic_map = _load_logic_map(repo_root).rename(
        columns={
            "expected_facility_charge_opportunity": "logic_expected_facility_charge_opportunity",
            "common_failure_mode": "logic_common_failure_mode",
            "likely_queue_destination": "logic_likely_queue_destination",
        }
    )
    root_cause_map = _load_root_cause_map(repo_root)

    denial_base = denials.merge(
        statuses[
            [
                "encounter_id",
                "department",
                "service_line",
                "root_cause_mechanism",
                "accountable_owner",
            ]
        ],
        on="encounter_id",
        how="left",
    ).merge(
        expected[
            [
                "expected_opportunity_id",
                "expected_facility_charge_opportunity",
                "expected_code_hint",
                "expected_modifier_hint",
                "expected_units",
                "clinical_event",
                "opportunity_status",
            ]
        ],
        left_on="source_expected_opportunity_id",
        right_on="expected_opportunity_id",
        how="left",
    )
    denial_base = denial_base.merge(
        cdm_reference,
        left_on=["department", "service_line", "expected_code_hint"],
        right_on=["department", "service_line", "expected_code"],
        how="left",
    )
    denial_base = denial_base.merge(
        logic_map[
            [
                "department",
                "clinical_event",
                "logic_expected_facility_charge_opportunity",
                "logic_common_failure_mode",
                "logic_likely_queue_destination",
            ]
        ],
        left_on=["department", "clinical_event", "expected_facility_charge_opportunity"],
        right_on=["department", "clinical_event", "logic_expected_facility_charge_opportunity"],
        how="left",
    )
    denial_base = denial_base.merge(
        root_cause_map[
            [
                "root_cause_mechanism",
                "operational_owner_hint",
            ]
        ],
        left_on="root_cause_mechanism",
        right_on="root_cause_mechanism",
        how="left",
    )
    denial_base = _apply_department_service_line_filters(denial_base, filters)
    denial_base["linked_root_cause_mechanism"] = denial_base["root_cause_mechanism"].fillna("")
    denial_base["linked_owner_team"] = denial_base["accountable_owner"].fillna("")
    denial_base["cdm_governance_flag"] = denial_base.apply(_cdm_governance_flag, axis=1)
    denial_base["interpretation_bucket"] = denial_base.apply(_interpretation_bucket, axis=1)
    denial_base["owner_action_hint"] = denial_base.apply(_suggested_action, axis=1)
    denial_base["likely_owner_path"] = denial_base.apply(_owner_path, axis=1)
    denial_base["upstream_validation_note"] = denial_base.apply(
        lambda row: (
            f"{row['linked_upstream_issue_domain']} signal linked to expected code "
            f"{row['expected_code_hint']} for {row['clinical_event']}."
        ),
        axis=1,
    )
    denial_base["why_this_matters_operationally"] = denial_base.apply(_why_this_matters, axis=1)
    return denial_base


def _build_denial_signal_patterns(denial_base: pd.DataFrame) -> pd.DataFrame:
    if denial_base.empty:
        return pd.DataFrame(
            columns=[
                "pattern_id",
                "denial_category",
                "denial_reason_group",
                "payer_group",
                "denial_amount",
                "linked_upstream_issue_domain",
                "linked_root_cause_mechanism",
                "linked_owner_team",
                "repeat_pattern_signal",
                "denial_signal_strength",
                "owner_action_hint",
                "likely_owner_path",
                "upstream_validation_note",
                "why_this_matters_operationally",
            ]
        )

    grouped = (
        denial_base.groupby(
            [
                "denial_category",
                "denial_reason_group",
                "payer_group",
                "linked_upstream_issue_domain",
                "linked_root_cause_mechanism",
                "linked_owner_team",
                "owner_action_hint",
                "likely_owner_path",
                "upstream_validation_note",
                "why_this_matters_operationally",
            ],
            as_index=False,
        )
        .agg(
            denial_signal_rows=("denial_id", "size"),
            denial_amount=("denial_amount", "sum"),
        )
        .sort_values(
            ["denial_amount", "denial_signal_rows", "denial_reason_group"],
            ascending=[False, False, True],
        )
        .reset_index(drop=True)
    )
    grouped["denial_amount"] = grouped["denial_amount"].round(2)
    grouped["repeat_pattern_signal"] = grouped["denial_signal_rows"].map(
        lambda count: "Repeat pattern" if count > 1 else "Single signal"
    )
    grouped["denial_signal_strength"] = grouped.apply(
        lambda row: _denial_signal_strength(
            int(row["denial_signal_rows"]),
            float(row["denial_amount"]),
        ),
        axis=1,
    )
    grouped.insert(0, "pattern_id", [f"DEN-PAT-{index + 1:02d}" for index in range(len(grouped))])
    return grouped


def _build_cdm_governance_monitor(
    denial_base: pd.DataFrame,
    repo_root: Path | None,
    filters: SummaryFilters,
) -> pd.DataFrame:
    expected = load_processed_artifact("expected_charge_opportunities", repo_root)
    cdm_reference = _load_cdm_reference(repo_root).rename(
        columns={"expected_modifier": "cdm_expected_modifier"}
    )
    logic_map = _load_logic_map(repo_root)

    expected_scope = _apply_department_service_line_filters(expected, filters)
    cdm_base = expected_scope.merge(
        cdm_reference,
        left_on=["department", "service_line", "expected_code_hint"],
        right_on=["department", "service_line", "expected_code"],
        how="left",
    )
    cdm_base = cdm_base.merge(
        logic_map[
            [
                "department",
                "clinical_event",
                "expected_facility_charge_opportunity",
                "common_failure_mode",
            ]
        ],
        on=["department", "clinical_event", "expected_facility_charge_opportunity"],
        how="left",
    )

    denial_by_code = (
        denial_base.groupby(["department", "service_line", "expected_code_hint"], as_index=False)
        .agg(
            denial_signal_rows=("denial_id", "size"),
            denial_amount=("denial_amount", "sum"),
            linked_upstream_issue_domain=("linked_upstream_issue_domain", lambda values: values.mode().iloc[0]),
        )
        .rename(columns={"expected_code_hint": "expected_code"})
    )
    cdm_base = cdm_base.merge(
        denial_by_code,
        on=["department", "service_line", "expected_code"],
        how="left",
    )
    cdm_base["denial_signal_rows"] = cdm_base["denial_signal_rows"].fillna(0).astype(int)
    cdm_base["denial_amount"] = cdm_base["denial_amount"].fillna(0.0).round(2)
    cdm_base["cdm_governance_flag"] = cdm_base.apply(_cdm_governance_flag, axis=1)
    cdm_base["suggested_governance_action"] = cdm_base.apply(_suggested_action, axis=1)
    cdm_base["upstream_validation_note"] = cdm_base.apply(
        lambda row: (
            f"{row['common_failure_mode']}."
            if str(row.get("common_failure_mode", "")).strip()
            else f"Expected code {row['expected_code_hint']} remains tied to {row['clinical_event']}."
        ),
        axis=1,
    )
    relevant = cdm_base.loc[
        (cdm_base["cdm_governance_flag"] != "Active aligned reference")
        | (cdm_base["denial_signal_rows"] > 0)
        | (cdm_base["expected_modifier_hint"].fillna("") != "")
    ].copy()
    if relevant.empty:
        return pd.DataFrame(
            columns=[
                "department",
                "service_line",
                "expected_code",
                "expected_modifier",
                "default_units",
                "revenue_code",
                "active_flag",
                "rule_status",
                "last_update_datetime",
                "cdm_governance_flag",
                "suggested_governance_action",
                "denial_signal_rows",
            ]
        )

    monitor = (
        relevant.groupby(
            [
                "department",
                "service_line",
                "expected_code",
                "cdm_expected_modifier",
                "default_units",
                "revenue_code",
                "active_flag",
                "rule_status",
                "last_update_datetime",
                "cdm_governance_flag",
                "suggested_governance_action",
                "upstream_validation_note",
            ],
            as_index=False,
        )
        .agg(
            denial_signal_rows=("denial_signal_rows", "max"),
            denial_amount=("denial_amount", "max"),
        )
        .sort_values(
            ["denial_signal_rows", "denial_amount", "department", "expected_code"],
            ascending=[False, False, True, True],
        )
        .reset_index(drop=True)
    )
    monitor = monitor.rename(columns={"cdm_expected_modifier": "expected_modifier"})
    monitor["expected_modifier"] = monitor["expected_modifier"].fillna("None")
    monitor["denial_amount"] = monitor["denial_amount"].round(2)
    return monitor


def _selector_options(denial_signal_patterns: pd.DataFrame) -> tuple[str, ...]:
    if denial_signal_patterns.empty:
        return ()
    return tuple(denial_signal_patterns["pattern_id"].tolist())


def _build_linkage_detail(denial_signal_patterns: pd.DataFrame, pattern_id: str | None) -> pd.DataFrame:
    if denial_signal_patterns.empty or pattern_id is None:
        return pd.DataFrame(columns=["field", "value"])
    selected = denial_signal_patterns.loc[denial_signal_patterns["pattern_id"] == pattern_id]
    if selected.empty:
        return pd.DataFrame(columns=["field", "value"])
    row = selected.iloc[0]
    return pd.DataFrame(
        [
            {"field": "Downstream signal", "value": f"{row['denial_category']} / {row['denial_reason_group']}"},
            {"field": "Payer group", "value": str(row["payer_group"])},
            {"field": "Upstream issue domain", "value": str(row["linked_upstream_issue_domain"])},
            {"field": "Likely root cause mechanism", "value": str(row["linked_root_cause_mechanism"])},
            {"field": "Likely owner / action path", "value": str(row["likely_owner_path"])},
            {"field": "Why this matters operationally", "value": str(row["why_this_matters_operationally"])},
            {"field": "Suggested next step", "value": str(row["owner_action_hint"])},
            {"field": "Upstream validation note", "value": str(row["upstream_validation_note"])},
        ]
    )


def build_denial_feedback_cdm_monitor_view(
    repo_root: Path | None = None,
    filters: SummaryFilters | None = None,
) -> DenialFeedbackCdmMonitorView:
    normalized_filters = scope_global_filters(
        filters or SummaryFilters(),
        queues=False,
        recoverability_states=False,
    )
    denial_base = _build_denial_signal_base(repo_root, normalized_filters)
    denial_signal_patterns = _build_denial_signal_patterns(denial_base)
    pattern_selector_options = _selector_options(denial_signal_patterns)
    default_selected_pattern_id = pattern_selector_options[0] if pattern_selector_options else None
    linkage_detail = _build_linkage_detail(denial_signal_patterns, default_selected_pattern_id)
    cdm_governance_monitor = _build_cdm_governance_monitor(
        denial_base,
        repo_root,
        normalized_filters,
    )
    kpi_rows = _load_governed_kpis(repo_root)
    correction_rows = load_processed_artifact("corrections_rebills", repo_root)
    correction_scope = load_processed_artifact("claims_or_account_status", repo_root).merge(
        correction_rows[["claim_id", "encounter_id", "turnaround_days"]],
        on=["claim_id", "encounter_id"],
        how="inner",
    )
    correction_scope = _apply_department_service_line_filters(correction_scope, normalized_filters)
    return DenialFeedbackCdmMonitorView(
        filters=normalized_filters,
        denial_signal_patterns=denial_signal_patterns,
        cdm_governance_monitor=cdm_governance_monitor,
        linkage_detail=linkage_detail,
        pattern_selector_options=pattern_selector_options,
        default_selected_pattern_id=default_selected_pattern_id,
        denial_signal_count=int(len(denial_base)),
        denial_dollars=round(float(denial_base["denial_amount"].sum()), 2),
        governed_prebill_edit_aging=_scoped_governed_kpi_value(
            kpi_rows,
            filters=normalized_filters,
            kpi_name="Prebill edit aging",
        ),
        governed_recoverable_dollars_still_open=_scoped_governed_kpi_value(
            kpi_rows,
            filters=normalized_filters,
            kpi_name="Recoverable dollars still open",
        ),
        correction_turnaround_days=_safe_mean(correction_scope["turnaround_days"]),
    )


def _pattern_label(denial_signal_patterns: pd.DataFrame, pattern_id: str) -> str:
    selected = denial_signal_patterns.loc[denial_signal_patterns["pattern_id"] == pattern_id]
    if selected.empty:
        return pattern_id
    row = selected.iloc[0]
    return (
        f"{row['denial_reason_group']} | {row['payer_group']} | "
        f"{format_currency(float(row['denial_amount']))}"
    )


def render_denial_feedback_cdm_monitor_page(
    page_title: str,
    scope_note: str,
    repo_root: Path | None = None,
) -> None:
    import streamlit as st

    global_filter_options = get_global_filter_options(repo_root)
    render_page_shell(
        page_title,
        (
            "Thin downstream signal layer for denial feedback and CDM governance. "
            "This page links denial patterns back to upstream control failures without becoming a denials workflow."
        ),
        scope_note,
        badges=(
            "Downstream signal layer only",
            "Facility-side only",
            "No appeals workflow",
        ),
    )
    selected_filters = scope_global_filters(
        get_global_filters(global_filter_options),
        queues=False,
        recoverability_states=False,
    )
    view = build_denial_feedback_cdm_monitor_view(repo_root=repo_root, filters=selected_filters)
    render_active_filter_summary(
        view.filters,
        inactive_reasons={
            "queues": "Not applied on the downstream signal monitor.",
            "recoverability_states": "Not applied on the downstream signal monitor.",
        },
    )

    if view.denial_signal_patterns.empty and view.cdm_governance_monitor.empty:
        st.warning("No denial or CDM governance patterns match the current filters.")
        return

    render_section_header(
        "Downstream Signal Snapshot",
        "Keep denials downstream and thin while still linking them back to upstream issue domain, root cause, and owner path.",
    )
    render_kpi_row(
        [
            KpiCard(
                "Downstream denial signals",
                format_count(view.denial_signal_count),
                "Evidence-only denial rows in the current department / service-line slice.",
            ),
            KpiCard(
                "Downstream denial dollars",
                format_currency(view.denial_dollars),
                "Summed denial signal dollars for the current slice.",
            ),
            KpiCard(
                "Governed prebill edit aging",
                f"{view.governed_prebill_edit_aging:.1f} days",
                "Published KPI reference; not a new denial KPI.",
            ),
            KpiCard(
                "Governed recoverable dollars still open",
                format_currency(view.governed_recoverable_dollars_still_open),
                "Published KPI reference for current recoverable exposure.",
            ),
            KpiCard(
                "Correction turnaround days",
                f"{view.correction_turnaround_days:.1f} days",
                "Observed correction turnaround reference for the filtered slice.",
            ),
        ]
    )

    render_table_section(
        "Denial Signal Monitor",
        "Top downstream denial patterns with linked upstream issue domain, likely root cause, repeat signal, and owner / action hint.",
        view.denial_signal_patterns[
            [
                "denial_category",
                "denial_reason_group",
                "payer_group",
                "denial_amount",
                "linked_upstream_issue_domain",
                "linked_root_cause_mechanism",
                "repeat_pattern_signal",
                "denial_signal_strength",
                "owner_action_hint",
            ]
        ],
        column_labels={
            "denial_category": "Denial category",
            "denial_reason_group": "Denial reason group",
            "payer_group": "Payer group",
            "denial_amount": "Denial amount",
            "linked_upstream_issue_domain": "Linked upstream issue domain",
            "linked_root_cause_mechanism": "Linked root cause mechanism",
            "repeat_pattern_signal": "Repeat pattern signal",
            "denial_signal_strength": "Signal strength",
            "owner_action_hint": "Owner / action hint",
        },
        currency_columns=("denial_amount",),
        height=320,
    )

    render_table_section(
        "CDM Governance Monitor",
        "Likely CDM, modifier, or revenue-code issues tied back to the same operating slice. Kept thin and operational, not a full catalog browser.",
        view.cdm_governance_monitor[
            [
                "department",
                "service_line",
                "expected_code",
                "expected_modifier",
                "default_units",
                "revenue_code",
                "active_flag",
                "rule_status",
                "last_update_datetime",
                "cdm_governance_flag",
                "suggested_governance_action",
            ]
        ],
        column_labels={
            "department": "Department",
            "service_line": "Service line",
            "expected_code": "Expected code",
            "expected_modifier": "Expected modifier",
            "default_units": "Default units",
            "revenue_code": "Revenue code",
            "active_flag": "Active flag",
            "rule_status": "Rule status",
            "last_update_datetime": "Last update datetime",
            "cdm_governance_flag": "Governance status",
            "suggested_governance_action": "Suggested governance action",
        },
        decimal_columns=("default_units",),
        height=340,
    )

    if view.pattern_selector_options:
        render_section_header(
            "Linked Interpretation",
            "Pick one downstream denial pattern and inspect how it maps back to upstream control failure and the suggested next step.",
        )
        selected_pattern_id = st.selectbox(
            "Denial pattern",
            options=list(view.pattern_selector_options),
            index=0,
            format_func=lambda pattern_id: _pattern_label(view.denial_signal_patterns, pattern_id),
        )
        linkage_detail = _build_linkage_detail(view.denial_signal_patterns, selected_pattern_id)
        render_table_section(
            "Selected Pattern Linkage",
            "Downstream signal, upstream issue domain, likely root cause, owner path, operational meaning, and suggested next step.",
            linkage_detail,
            column_labels={"field": "Field", "value": "Value"},
            height=320,
        )

    st.info(
        "This monitor keeps denials as downstream evidence only. It does not add appeals tracking, payer adjudication logic, routing changes, or predictive denial modeling."
    )
