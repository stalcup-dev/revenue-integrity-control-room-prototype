from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import ModuleType

import pandas as pd



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


class _StreamlitExpanderStub:
    def __enter__(self) -> "_StreamlitExpanderStub":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        return None


class _StreamlitStub(ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.titles: list[str] = []
        self.expander_labels: list[str] = []
        self.markdowns: list[str] = []
        self.warnings: list[str] = []
        self.session_state: dict[str, object] = {}

    def title(self, value: str) -> None:
        self.titles.append(value)

    def markdown(self, value: str, *_args, **_kwargs) -> None:
        self.markdowns.append(value)
        return None

    def caption(self, *_args, **_kwargs) -> None:
        return None

    def columns(self, count: int | list[float]) -> list[_StreamlitColumnStub]:
        actual_count = count if isinstance(count, int) else len(count)
        return [_StreamlitColumnStub(self) for _ in range(actual_count)]

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def warning(self, value: str, *_args, **_kwargs) -> None:
        self.warnings.append(value)
        return None

    def info(self, *_args, **_kwargs) -> None:
        return None

    def subheader(self, *_args, **_kwargs) -> None:
        return None

    def dataframe(self, *_args, **_kwargs) -> None:
        return None

    def line_chart(self, *_args, **_kwargs) -> None:
        return None

    def expander(self, label: str, *_args, **_kwargs) -> _StreamlitExpanderStub:
        self.expander_labels.append(label)
        return _StreamlitExpanderStub()


def test_control_room_summary_page_render_and_filters(monkeypatch) -> None:
    from ri_control_room.artifacts import load_processed_artifact
    from ri_control_room.build_pipeline import (
        build_operating_artifacts,
        update_run_manifest_validation_status,
    )
    from ri_control_room.metrics.priority_score import build_priority_scores_df
    from ri_control_room.ui.control_room_summary import (
        SummaryFilters,
        build_control_room_summary_view,
    )

    build_operating_artifacts(ROOT)
    streamlit_stub = _StreamlitStub()
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)

    page_path = ROOT / "app" / "pages" / "01_Control_Room_Summary.py"
    runpy.run_path(str(page_path), run_name="__main__")
    assert streamlit_stub.titles == ["Control Room Summary"]
    assert "Revenue Integrity Decision Pack" in streamlit_stub.expander_labels
    assert any(
        label.startswith("View proof for representative case:")
        for label in streamlit_stub.expander_labels
    )
    assert any("Featured Deterministic Story" in value for value in streamlit_stub.markdowns)
    assert any("Story path:" in value for value in streamlit_stub.markdowns)
    assert any("Recommended next action:" in value for value in streamlit_stub.markdowns)
    assert any("Representative Case Proof" in value for value in streamlit_stub.markdowns)
    assert any("Expected Vs Actual Charge / Control Evidence" in value for value in streamlit_stub.markdowns)

    queue_population = build_priority_scores_df(ROOT)
    kpi_snapshot = load_processed_artifact("kpi_snapshot", ROOT)
    full_view = build_control_room_summary_view(ROOT)

    assert full_view.open_exception_count == len(queue_population)
    assert int(full_view.issue_root_cause_summary["open_exceptions"].sum()) == len(queue_population)
    assert int(full_view.stage_bottleneck_summary["open_exceptions"].sum()) == len(queue_population)
    assert int(full_view.owner_action_summary["open_exceptions"].sum()) == len(queue_population)
    assert int(full_view.backlog_trend.iloc[-1]["open_exceptions"]) == len(queue_population)
    assert list(full_view.suppression_summary["bucket"]) == ["Suppressed by design"]

    recoverable_expected = round(
        float(
            queue_population.loc[
                queue_population["recoverability_status"].isin(
                    {
                        "Pre-final-bill recoverable",
                        "Post-final-bill recoverable by correction / rebill",
                    }
                ),
                "estimated_gross_dollars",
            ].sum()
        ),
        2,
    )
    lost_expected = round(
        float(
            kpi_snapshot.loc[
                (kpi_snapshot["record_type"] == "kpi")
                & (kpi_snapshot["setting_name"] == "All frozen V1 departments")
                & (kpi_snapshot["kpi_name"] == "Dollars already lost after timing window"),
                "kpi_value",
            ].iloc[0]
        ),
        2,
    )
    assert full_view.recoverable_now_dollars == recoverable_expected
    assert full_view.lost_dollars_now == lost_expected
    assert full_view.urgent_exception_count == int(
        (queue_population["sla_status"] != "Within SLA").sum()
    )
    assert full_view.control_story.queue_item_id == "QUEUE-ACC-1025"
    assert full_view.control_story.service_line == "Outpatient Surgery"
    assert (
        full_view.control_story.department
        == "OR / Hospital Outpatient Surgery / Procedural Areas"
    )
    assert full_view.control_story.issue_domain == "Billing / claim-edit failure"
    assert full_view.control_story.root_cause_mechanism == "Workflow / handoff"
    assert full_view.control_story.current_primary_blocker_state == "Prebill edit or hold unresolved"
    assert full_view.control_story.current_queue == "Modifiers / Edits / Prebill Holds"
    assert full_view.control_story.accountable_owner == "Billing operations"
    assert "Overdue against 5-day threshold" in full_view.control_story.aging_sla_status
    assert full_view.control_story.recoverability_status == "Post-window financially lost"
    assert (
        full_view.control_story.recommended_next_action
        == "Work assigned queue, clear hold, and confirm account release path."
    )
    assert "documented performed activity" in full_view.control_story.exception_pattern
    assert "Primary facility procedure charge" in full_view.control_story.exception_pattern
    assert "2 like-for-like accounts total $5,000 gross" in full_view.control_story.why_it_matters
    assert "Prebill edit resolution" in full_view.control_story.story_path
    assert full_view.featured_story_proof.proof_available is True
    assert full_view.featured_story_proof.story_scope_count == 2
    assert full_view.featured_story_proof.representative_queue_item_id == "QUEUE-ACC-1025"
    assert full_view.featured_story_proof.representative_encounter_id
    assert (
        full_view.featured_story_proof.classification["recoverability_status"]
        == "Post-window financially lost"
    )
    assert (
        full_view.featured_story_proof.classification["current_queue"]
        == "Modifiers / Edits / Prebill Holds"
    )
    assert (
        full_view.featured_story_proof.routing_history["current_queue"]
        == "Modifiers / Edits / Prebill Holds"
    )
    assert full_view.featured_story_proof.routing_history["transition_event_count"] >= 1
    assert full_view.featured_story_proof.recommended_next_action == (
        "Work assigned queue, clear hold, and confirm account release path."
    )
    assert "documented performed activity" in (
        full_view.featured_story_proof.control_narrative.lower()
    )
    assert "actual charge state" in full_view.featured_story_proof.control_narrative.lower()
    assert {
        "expected_facility_charge_opportunity",
        "actual_charge_status",
        "suppression_flag",
    }.issubset(full_view.featured_story_proof.expected_vs_actual.columns)
    assert {
        "documentation_event_id",
        "activity_signal_id",
        "signal_basis",
        "supports_charge_flag",
    }.issubset(full_view.featured_story_proof.upstream_evidence.columns)

    assert full_view.recoverable_now_dollars == round(
        float(
            full_view.filtered_population.loc[
                full_view.filtered_population["recoverability_status"].isin(
                    {
                        "Pre-final-bill recoverable",
                        "Post-final-bill recoverable by correction / rebill",
                    }
                ),
                "estimated_gross_dollars",
            ].sum()
        ),
        2,
    )
    scope_buckets = full_view.actionable_vs_suppressed.set_index("bucket")["encounter_count"].to_dict()
    assert scope_buckets["Actionable active work"] == len(queue_population)
    assert scope_buckets["Suppressed by design"] > 0
    assert list(full_view.stage_bottleneck_summary.columns) == [
        "current_prebill_stage",
        "current_primary_blocker_state",
        "current_queue",
        "accountable_owner",
        "open_exceptions",
        "urgent_exceptions",
        "average_age_days",
    ]
    assert list(full_view.actionable_vs_suppressed.columns) == [
        "bucket",
        "encounter_count",
        "share_of_scope",
        "routing_state",
    ]
    assert {
        "current_prebill_stage",
        "current_primary_blocker_state",
        "current_queue",
        "accountable_owner",
        "days_in_stage",
        "sla_status",
        "root_cause_mechanism",
        "recoverability_status",
    }.issubset(full_view.worklist.columns)
    assert full_view.artifact_lineage.build_timestamp_utc != "Not set"
    assert full_view.artifact_lineage.last_validated_at_utc == "Not set"
    assert full_view.artifact_lineage.overall_validation_status == "Not yet run"
    assert set(full_view.artifact_lineage.manifest_summary["field"]) >= {
        "Build timestamp (UTC)",
        "Overall validation status",
        "Seed",
        "Ruleset version",
        "Schema version",
    }
    artifact_counts = full_view.artifact_lineage.artifact_row_counts.set_index("artifact")[
        "row_count"
    ].to_dict()
    assert artifact_counts["encounters.parquet"] >= 60
    assert artifact_counts["kpi_snapshot.parquet"] == len(kpi_snapshot)

    update_run_manifest_validation_status(
        ROOT,
        schema_passed=True,
        business_passed=True,
    )
    validated_view = build_control_room_summary_view(ROOT)
    assert validated_view.artifact_lineage.overall_validation_status == "Passed"
    assert validated_view.artifact_lineage.last_validated_at_utc != "Not set"

    filtered_view = build_control_room_summary_view(
        ROOT,
        SummaryFilters(
            departments=("Radiology / Interventional Radiology",),
            service_lines=(),
            queues=("Documentation Support Exceptions",),
            recoverability_states=("Pre-final-bill recoverable",),
        ),
    )
    assert 0 < filtered_view.open_exception_count < full_view.open_exception_count
    assert set(filtered_view.filtered_population["department"]) == {
        "Radiology / Interventional Radiology"
    }
    assert set(filtered_view.filtered_population["current_queue"]) == {
        "Documentation Support Exceptions"
    }
    assert set(filtered_view.filtered_population["recoverability_status"]) == {
        "Pre-final-bill recoverable"
    }
    assert filtered_view.featured_story_proof.proof_available is True
    assert filtered_view.featured_story_proof.representative_queue_item_id == "QUEUE-ACC-1012"
    assert (
        filtered_view.featured_story_proof.case_header["department"]
        == "Radiology / Interventional Radiology"
    )
    assert (
        filtered_view.featured_story_proof.classification["current_queue"]
        == "Documentation Support Exceptions"
    )
    assert (
        filtered_view.featured_story_proof.classification["recoverability_status"]
        == "Pre-final-bill recoverable"
    )
    filtered_buckets = filtered_view.actionable_vs_suppressed.set_index("bucket")[
        "encounter_count"
    ].to_dict()
    assert filtered_buckets["Actionable active work"] == filtered_view.open_exception_count


def test_representative_case_selection_rule_prefers_priority_then_age_then_queue_item() -> None:
    from ri_control_room.control_story import (
        DeterministicControlStory,
        select_representative_case_row,
    )

    filtered = pd.DataFrame(
        [
            {
                "queue_item_id": "QUEUE-200",
                "department": "Radiology / Interventional Radiology",
                "service_line": "Radiology",
                "issue_domain": "Documentation support failure",
                "root_cause_mechanism": "Documentation behavior",
                "current_prebill_stage": "Documentation pending",
                "current_primary_blocker_state": "Documentation support incomplete",
                "current_queue": "Documentation Support Exceptions",
                "accountable_owner": "Department operations",
                "recoverability_status": "Pre-final-bill recoverable",
                "priority_rank": 2,
                "days_in_stage": 9,
            },
            {
                "queue_item_id": "QUEUE-150",
                "department": "Radiology / Interventional Radiology",
                "service_line": "Radiology",
                "issue_domain": "Documentation support failure",
                "root_cause_mechanism": "Documentation behavior",
                "current_prebill_stage": "Documentation pending",
                "current_primary_blocker_state": "Documentation support incomplete",
                "current_queue": "Documentation Support Exceptions",
                "accountable_owner": "Department operations",
                "recoverability_status": "Pre-final-bill recoverable",
                "priority_rank": 1,
                "days_in_stage": 5,
            },
            {
                "queue_item_id": "QUEUE-120",
                "department": "Radiology / Interventional Radiology",
                "service_line": "Radiology",
                "issue_domain": "Documentation support failure",
                "root_cause_mechanism": "Documentation behavior",
                "current_prebill_stage": "Documentation pending",
                "current_primary_blocker_state": "Documentation support incomplete",
                "current_queue": "Documentation Support Exceptions",
                "accountable_owner": "Department operations",
                "recoverability_status": "Pre-final-bill recoverable",
                "priority_rank": 1,
                "days_in_stage": 7,
            },
            {
                "queue_item_id": "QUEUE-121",
                "department": "Radiology / Interventional Radiology",
                "service_line": "Radiology",
                "issue_domain": "Documentation support failure",
                "root_cause_mechanism": "Documentation behavior",
                "current_prebill_stage": "Documentation pending",
                "current_primary_blocker_state": "Documentation support incomplete",
                "current_queue": "Documentation Support Exceptions",
                "accountable_owner": "Department operations",
                "recoverability_status": "Pre-final-bill recoverable",
                "priority_rank": 1,
                "days_in_stage": 7,
            },
        ]
    )
    story = DeterministicControlStory(
        queue_item_id="QUEUE-150",
        service_line="Radiology",
        department="Radiology / Interventional Radiology",
        control_failure_type="Documentation support",
        issue_domain="Documentation support failure",
        root_cause_mechanism="Documentation behavior",
        exception_pattern="",
        current_prebill_stage="Documentation pending",
        current_primary_blocker_state="Documentation support incomplete",
        current_queue="Documentation Support Exceptions",
        accountable_owner="Department operations",
        aging_sla_status="",
        recoverability_status="Pre-final-bill recoverable",
        why_it_matters="",
        recommended_next_action="Document coaching target and close documentation support gap.",
        story_path="",
    )

    selected = select_representative_case_row(filtered, story)
    assert selected is not None
    assert str(selected["queue_item_id"]) == "QUEUE-120"


def test_featured_story_proof_empty_state_when_filters_remove_all_work() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.control_room_summary import SummaryFilters, build_control_room_summary_view

    build_operating_artifacts(ROOT)
    empty_view = build_control_room_summary_view(
        ROOT,
        SummaryFilters(service_lines=("Not a real service line",)),
    )

    assert empty_view.open_exception_count == 0
    assert empty_view.control_story.queue_item_id == ""
    assert empty_view.featured_story_proof.proof_available is False
    assert "No representative case is available" in empty_view.featured_story_proof.empty_state_message
