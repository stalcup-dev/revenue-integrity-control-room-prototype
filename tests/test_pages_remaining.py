from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class _StreamlitColumnStub:
    def __init__(self, streamlit_stub: "_StreamlitStub") -> None:
        self._streamlit_stub = streamlit_stub

    def multiselect(self, _label: str, options: list[str], default: list[str]) -> list[str]:
        return list(default or options)

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def __enter__(self) -> "_StreamlitColumnStub":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        return None


class _StreamlitStub(ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.titles: list[str] = []
        self.selectbox_labels: list[str] = []
        self.session_state: dict[str, object] = {}
        self.sidebar = self
        self.multiselect_overrides: dict[str, list[str]] = {}
        self.button_presses: set[str] = set()

    def title(self, value: str) -> None:
        self.titles.append(value)

    def markdown(self, *_args, **_kwargs) -> None:
        return None

    def caption(self, *_args, **_kwargs) -> None:
        return None

    def columns(self, count: int | list[float]) -> list[_StreamlitColumnStub]:
        actual_count = count if isinstance(count, int) else len(count)
        return [_StreamlitColumnStub(self) for _ in range(actual_count)]

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def warning(self, *_args, **_kwargs) -> None:
        return None

    def subheader(self, *_args, **_kwargs) -> None:
        return None

    def dataframe(self, *_args, **_kwargs) -> None:
        return None

    def line_chart(self, *_args, **_kwargs) -> None:
        return None

    def info(self, *_args, **_kwargs) -> None:
        return None

    def multiselect(self, label: str, options: list[str], default: list[str]) -> list[str]:
        return list(self.multiselect_overrides.get(label, default or options))

    def button(self, label: str, *_args, **_kwargs) -> bool:
        return label in self.button_presses

    def number_input(
        self,
        _label: str,
        *,
        min_value: float,
        max_value: float,
        value: float,
        step: float,
    ) -> float:
        _ = (min_value, max_value, step)
        return value

    def selectbox(
        self,
        label: str,
        options: list[str],
        index: int = 0,
        format_func=None,
    ) -> str:
        self.selectbox_labels.append(label)
        selected = options[index]
        if callable(format_func):
            format_func(selected)
        return selected


def test_remaining_pages_render_and_reconcile(monkeypatch) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.config import get_app_config
    from ri_control_room.metrics.priority_score import build_priority_scores_df
    from ri_control_room.ui.documentation_exceptions import build_documentation_exceptions_view
    from ri_control_room.ui.modifiers_edits import build_modifiers_edits_view
    from ri_control_room.ui.opportunity_action_tracker import (
        build_opportunity_action_tracker_view,
    )
    from ri_control_room.ui.reconciliation_monitor import build_reconciliation_monitor_view
    from ri_control_room.ui.shared import SummaryFilters

    build_operating_artifacts(ROOT)
    expected_titles = {
        "02_Charge_Reconciliation_Monitor.py": "Charge Reconciliation Monitor",
        "03_Modifiers_Edits_Prebill_Holds.py": "Modifiers / Edits / Prebill Holds",
        "04_Documentation_Support_Exceptions.py": "Documentation Support Exceptions",
        "05_Opportunity_Action_Tracker.py": "Opportunity & Action Tracker",
        "06_Scenario_Lab.py": "Scenario Lab",
        "07_Denial_Feedback_CDM_Governance.py": "Denial Feedback + CDM Governance Monitor",
    }
    for filename, title in expected_titles.items():
        streamlit_stub = _StreamlitStub()
        monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)
        runpy.run_path(str(ROOT / "app" / "pages" / filename), run_name="__main__")
        assert streamlit_stub.titles == [title]
        if filename == "05_Opportunity_Action_Tracker.py":
            assert streamlit_stub.selectbox_labels == ["Queue item"]

    population = build_priority_scores_df(ROOT)
    recon_view = build_reconciliation_monitor_view(ROOT)
    modifiers_view = build_modifiers_edits_view(ROOT)
    documentation_view = build_documentation_exceptions_view(ROOT)
    tracker_view = build_opportunity_action_tracker_view(ROOT)

    assert recon_view.unreconciled_encounters_count == int(
        (population["current_queue"] == "Charge Reconciliation Monitor").sum()
    )
    assert "reconciliation timeliness" in recon_view.story_cue.sentence.lower()
    assert len(recon_view.story_cue.callouts) == 3
    assert any(
        "next move" == callout.label.lower()
        and "owns the next move" in callout.value.lower()
        for callout in recon_view.story_cue.callouts
    )
    assert modifiers_view.unresolved_edit_count == int(
        (population["current_queue"] == "Modifiers / Edits / Prebill Holds").sum()
    )
    assert "prebill edit pressure" in modifiers_view.story_cue.sentence.lower()
    assert any(
        "current pressure" == callout.label.lower()
        and "open edit" in callout.value.lower()
        for callout in modifiers_view.story_cue.callouts
    )
    assert documentation_view.unsupported_exception_count == int(
        (population["current_queue"] == "Documentation Support Exceptions").sum()
    )
    assert "documented activity" in documentation_view.story_cue.sentence.lower()
    assert any(
        "current pressure" == callout.label.lower()
        and "missing case time support" in callout.value.lower()
        for callout in documentation_view.story_cue.callouts
    )
    assert any(
        "next move" == callout.label.lower()
        and "should" in callout.value.lower()
        for callout in documentation_view.story_cue.callouts
    )
    assert len(documentation_view.unsupported_charge_trend) == 10
    assert int(documentation_view.unsupported_charge_trend.iloc[-1]["unsupported_exceptions"]) == (
        documentation_view.unsupported_exception_count
    )
    assert (
        documentation_view.unsupported_charge_trend["unsupported_exceptions"].nunique() > 1
    )
    assert (
        documentation_view.unsupported_charge_trend["recoverable_dollars"].nunique() > 1
    )
    assert (
        documentation_view.unsupported_charge_trend["unsupported_exceptions"].diff().fillna(0) < 0
    ).any()
    assert (
        documentation_view.unsupported_charge_trend["unsupported_exceptions"].diff().fillna(0) > 0
    ).any()
    assert tracker_view.open_actions_count == len(population)
    assert "owned interventions" in tracker_view.story_cue.sentence.lower()
    assert "hold / expand / revise" in tracker_view.story_cue.note.lower()
    assert any(
        "next move" == callout.label.lower()
        and "pattern focus" not in callout.value.lower()
        and "should" in callout.value.lower()
        and "validate" in callout.value.lower()
        for callout in tracker_view.story_cue.callouts
    )
    assert not tracker_view.recurring_issue_patterns.empty
    assert not tracker_view.intervention_owner_summary.empty
    assert tracker_view.queue_item_selector_options
    assert tracker_view.default_selected_queue_item_id == tracker_view.queue_item_selector_options[0]
    assert {
        "current_queue",
        "current_prebill_stage",
        "current_primary_blocker_state",
        "accountable_owner",
        "days_in_stage",
        "sla_status",
        "recoverability_status",
    }.issubset(tracker_view.queue_priority_ranking.columns)
    assert {
        "intervention_type",
        "intervention_owner",
        "target_completion_date",
        "checkpoint_status",
        "baseline_metric",
        "current_metric",
        "correction_turnaround_signal",
        "downstream_outcome_signal",
        "before_after_validation_note",
        "hold_expand_revise_recommendation",
        "next_action",
    }.issubset(tracker_view.action_tracker.columns)
    correction_follow_through = tracker_view.action_tracker.loc[
        tracker_view.action_tracker["queue_item_id"] == "QUEUE-ACC-1029"
    ].iloc[0]
    assert correction_follow_through["intervention_type"] == "Billing / correction action"
    assert "correction turnaround 2.0 days" in correction_follow_through["downstream_outcome_signal"]
    assert correction_follow_through["hold_expand_revise_recommendation"] == "Revise"

    assert recon_view.filter_options["queues"] == ("Charge Reconciliation Monitor",)
    assert modifiers_view.filter_options["queues"] == ("Modifiers / Edits / Prebill Holds",)
    assert documentation_view.filter_options["queues"] == ("Documentation Support Exceptions",)
    assert "Coding Pending Review" in tracker_view.filter_options["queues"]

    shared_filters = SummaryFilters(
        departments=("Radiology / Interventional Radiology",),
        service_lines=(),
        queues=(),
        recoverability_states=("Pre-final-bill recoverable",),
    )
    recon_filtered = build_reconciliation_monitor_view(ROOT, shared_filters)
    modifiers_filtered = build_modifiers_edits_view(ROOT, shared_filters)
    documentation_filtered = build_documentation_exceptions_view(ROOT, shared_filters)
    tracker_filtered = build_opportunity_action_tracker_view(ROOT, shared_filters)

    expected_recon = population.loc[
        (population["department"] == "Radiology / Interventional Radiology")
        & (population["recoverability_status"] == "Pre-final-bill recoverable")
        & (population["current_queue"] == "Charge Reconciliation Monitor")
    ]
    expected_modifiers = population.loc[
        (population["department"] == "Radiology / Interventional Radiology")
        & (population["recoverability_status"] == "Pre-final-bill recoverable")
        & (population["current_queue"] == "Modifiers / Edits / Prebill Holds")
    ]
    expected_docs = population.loc[
        (population["department"] == "Radiology / Interventional Radiology")
        & (population["recoverability_status"] == "Pre-final-bill recoverable")
        & (population["current_queue"] == "Documentation Support Exceptions")
    ]
    expected_tracker = population.loc[
        (population["department"] == "Radiology / Interventional Radiology")
        & (population["recoverability_status"] == "Pre-final-bill recoverable")
    ]

    assert len(recon_filtered.filtered_population) == len(expected_recon)
    assert len(modifiers_filtered.filtered_population) == len(expected_modifiers)
    assert len(documentation_filtered.filtered_population) == len(expected_docs)
    assert int(documentation_filtered.unsupported_charge_trend.iloc[-1]["unsupported_exceptions"]) == (
        len(expected_docs)
    )
    assert len(tracker_filtered.filtered_population) == len(expected_tracker)
    assert set(tracker_filtered.action_tracker["hold_expand_revise_recommendation"]).issubset(
        {"Hold", "Expand", "Revise"}
    )

    config = get_app_config(ROOT)
    page_titles = {spec.title for spec in config.page_specs}
    assert all("Status" not in title and "Observation" not in title for title in page_titles)


def test_global_sidebar_filters_persist_and_scope_by_page(monkeypatch) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.documentation_exceptions import build_documentation_exceptions_view
    from ri_control_room.ui.opportunity_action_tracker import (
        build_opportunity_action_tracker_view,
    )
    from ri_control_room.ui.reconciliation_monitor import build_reconciliation_monitor_view
    from ri_control_room.ui.shared import (
        get_global_filter_options,
        get_global_filters,
        render_global_sidebar_filters,
        scope_global_filters,
    )

    build_operating_artifacts(ROOT)
    streamlit_stub = _StreamlitStub()
    streamlit_stub.multiselect_overrides = {
        "Department": ["Outpatient Infusion / Oncology Infusion"],
        "Service line": ["Infusion"],
        "Queue": ["Charge Reconciliation Monitor"],
        "Recoverability": ["Pre-final-bill recoverable"],
    }
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)

    global_options = get_global_filter_options(ROOT)
    render_global_sidebar_filters(global_options)
    global_filters = get_global_filters(global_options)
    assert global_filters.departments == ("Outpatient Infusion / Oncology Infusion",)
    assert global_filters.service_lines == ("Infusion",)
    assert global_filters.queues == ("Charge Reconciliation Monitor",)
    assert global_filters.recoverability_states == ("Pre-final-bill recoverable",)

    tracker_view = build_opportunity_action_tracker_view(ROOT, global_filters)
    assert set(tracker_view.filtered_population["current_queue"]) == {"Charge Reconciliation Monitor"}
    assert set(tracker_view.filtered_population["department"]) == {
        "Outpatient Infusion / Oncology Infusion"
    }
    assert set(tracker_view.filtered_population["service_line"]) == {"Infusion"}
    assert set(tracker_view.filtered_population["recoverability_status"]) == {
        "Pre-final-bill recoverable"
    }

    queue_fixed_filters = scope_global_filters(global_filters, queues=False)
    recon_view = build_reconciliation_monitor_view(ROOT, queue_fixed_filters)
    documentation_view = build_documentation_exceptions_view(ROOT, queue_fixed_filters)
    assert set(recon_view.filtered_population["current_queue"]) == {
        "Charge Reconciliation Monitor"
    }
    assert set(documentation_view.filtered_population["current_queue"]) == {
        "Documentation Support Exceptions"
    }
    assert set(recon_view.filtered_population["department"]) == {
        "Outpatient Infusion / Oncology Infusion"
    }
    assert set(documentation_view.filtered_population["service_line"]) == {"Infusion"}


def test_documentation_trend_matches_current_backlog_across_representative_filter_states() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.documentation_exceptions import build_documentation_exceptions_view
    from ri_control_room.ui.shared import SummaryFilters

    build_operating_artifacts(ROOT)
    scenarios = {
        "all_departments": SummaryFilters(),
        "or_procedural": SummaryFilters(
            departments=("OR / Hospital Outpatient Surgery / Procedural Areas",)
        ),
        "radiology_ir": SummaryFilters(
            departments=("Radiology / Interventional Radiology",)
        ),
        "infusion": SummaryFilters(
            departments=("Outpatient Infusion / Oncology Infusion",)
        ),
    }

    moving_slices = 0
    for filters in scenarios.values():
        view = build_documentation_exceptions_view(ROOT, filters)
        trend = view.unsupported_charge_trend

        assert not trend.empty
        assert int(trend.iloc[-1]["unsupported_exceptions"]) == view.unsupported_exception_count
        assert float(trend.iloc[-1]["recoverable_dollars"]) == round(
            float(view.filtered_population["estimated_gross_dollars"].sum()),
            2,
        )

        if (
            trend["unsupported_exceptions"].nunique() > 1
            or trend["recoverable_dollars"].nunique() > 1
        ):
            moving_slices += 1

    assert moving_slices >= 2


def test_reconciliation_monitor_trend_and_service_line_scope_match_representative_slices() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.reconciliation_monitor import build_reconciliation_monitor_view
    from ri_control_room.ui.shared import SummaryFilters

    build_operating_artifacts(ROOT)
    scenarios = {
        "all_departments": (
            SummaryFilters(),
            {"Infusion", "Outpatient Surgery"},
        ),
        "or_procedural": (
            SummaryFilters(
                departments=("OR / Hospital Outpatient Surgery / Procedural Areas",)
            ),
            {"Outpatient Surgery"},
        ),
        "infusion": (
            SummaryFilters(
                departments=("Outpatient Infusion / Oncology Infusion",)
            ),
            {"Infusion"},
        ),
    }

    moving_slices = 0
    for name, (filters, expected_service_lines) in scenarios.items():
        view = build_reconciliation_monitor_view(ROOT, filters)
        trend = view.control_completion_trend

        assert list(trend.columns) == [
            "snapshot_date",
            "open_unreconciled",
            "overdue_unreconciled",
        ]
        assert not trend.empty
        assert int(trend.iloc[-1]["open_unreconciled"]) == view.unreconciled_encounters_count
        assert int(trend.iloc[-1]["overdue_unreconciled"]) == int(
            (view.filtered_population["sla_status"] != "Within SLA").sum()
        )

        service_lines = set(view.aging_by_service_line["service_line"])
        assert service_lines == expected_service_lines

        if name == "all_departments":
            assert len(view.aging_by_service_line) > 1
            assert set(view.filtered_population["service_line"]) == {"Infusion"}
            assert (
                view.aging_by_service_line.loc[
                    view.aging_by_service_line["service_line"] == "Outpatient Surgery",
                    "open_exceptions",
                ].iloc[0]
                == 0
            )

        if (
            trend["open_unreconciled"].nunique() > 1
            or trend["overdue_unreconciled"].nunique() > 1
        ):
            moving_slices += 1

    assert moving_slices >= 2
