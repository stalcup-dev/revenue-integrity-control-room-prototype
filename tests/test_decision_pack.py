from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_decision_pack_payload_and_markdown_cover_required_sections(tmp_path) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.decision_pack import (
        DECISION_PACK_TITLE,
        build_revenue_integrity_decision_pack,
        export_revenue_integrity_decision_pack,
        render_revenue_integrity_decision_pack_markdown,
    )
    from ri_control_room.ui.shared import SummaryFilters

    build_operating_artifacts(ROOT)
    payload = build_revenue_integrity_decision_pack(
        ROOT,
        filters=SummaryFilters(
            departments=("Radiology / Interventional Radiology",),
            service_lines=(),
            queues=(),
            recoverability_states=("Pre-final-bill recoverable",),
        ),
    )

    assert payload.title == DECISION_PACK_TITLE
    assert payload.executive_summary["total_open_exceptions"] > 0
    assert payload.executive_summary["recoverable_now_dollars"] >= 0
    assert payload.executive_summary["already_lost_dollars"] >= 0
    assert payload.executive_summary["exceptions_breaching_sla"] >= 0
    assert payload.top_priority_work_queues.shape[0] >= 1
    assert {
        "issue_domain",
        "owner_team",
        "queue_name",
        "sla_status",
        "recoverability",
        "dollars_at_risk",
        "recoverable_dollars",
        "recommended_next_step",
    }.issubset(payload.top_priority_work_queues.columns)
    assert payload.control_story.queue_item_id
    assert payload.control_story.service_line == "Radiology"
    assert (
        payload.control_story.department
        == "Radiology / Interventional Radiology"
    )
    assert payload.control_story.issue_domain == "Coding failure"
    assert payload.control_story.root_cause_mechanism == "Coding practice"
    assert payload.control_story.current_primary_blocker_state == "Coding or modifier review pending"
    assert payload.control_story.current_queue == "Coding Pending Review"
    assert payload.control_story.accountable_owner == "Coding team"
    assert "Overdue against 3-day threshold" in payload.control_story.aging_sla_status
    assert payload.control_story.recoverability_status == "Pre-final-bill recoverable"
    assert (
        payload.control_story.recommended_next_action
        == "Route coding review and validate modifier or code alignment."
    )
    assert {
        "intervention_type",
        "owner",
        "baseline_metric",
        "current_metric",
        "downstream_outcome_signal",
        "recommendation",
    }.issubset(payload.intervention_update.keys())
    assert {
        "lever_settings_used",
        "projected_backlog_reduction",
        "projected_sla_improvement_points",
        "projected_recoverable_dollar_lift",
        "ninety_day_impact_estimate",
        "note",
    }.issubset(payload.scenario_snapshot.keys())
    assert len(payload.guardrails) == 6

    markdown = render_revenue_integrity_decision_pack_markdown(payload)
    expected_sections = [
        "## Executive summary",
        "## Top priority work queues",
        "## Current control story",
        "## Intervention update",
        "## Scenario snapshot",
        "## Guardrails / caveats",
    ]
    last_position = -1
    for section in expected_sections:
        position = markdown.find(section)
        assert position > last_position
        last_position = position
    assert "Recoverable now vs already lost" in markdown
    assert "Top owner queue" in markdown
    assert "Story path:" in markdown
    assert "Service line / department:" in markdown
    assert "Issue domain:" in markdown
    assert "Root cause mechanism:" in markdown
    assert "Where work is stuck now:" in markdown
    assert "Who owns it now:" in markdown
    assert "Aging / SLA:" in markdown
    assert "Recoverability:" in markdown
    assert "Recommended next action:" in markdown
    assert "Hold / expand / revise recommendation" in markdown
    assert "Projected backlog reduction" in markdown
    assert "Scenario snapshot uses the current Scenario Lab v0 default lever targets" in markdown
    assert "Facility-side only." in markdown
    assert "Outpatient-first." in markdown
    assert "Deterministic-first." in markdown
    assert "Synthetic/public-safe data." in markdown
    assert "Scenario results are what-if estimates, not forecasts." in markdown
    assert "Denials are evidence-only, not the product center." in markdown

    output_path = tmp_path / "decision_pack.md"
    written_path = export_revenue_integrity_decision_pack(
        ROOT,
        filters=payload.filters,
        output_path=output_path,
    )
    assert written_path == output_path
    assert written_path.read_text(encoding="utf-8") == markdown
