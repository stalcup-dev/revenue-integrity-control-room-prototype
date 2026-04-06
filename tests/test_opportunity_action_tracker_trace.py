from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class _StreamlitColumnStub:
    def multiselect(self, _label: str, options: list[str], default: list[str]) -> list[str]:
        return list(default or options)

    def metric(self, *_args, **_kwargs) -> None:
        return None

    def __enter__(self) -> "_StreamlitColumnStub":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        return None


class _StreamlitStub(ModuleType):
    def __init__(self, selected_queue_item_id: str) -> None:
        super().__init__("streamlit")
        self.selected_queue_item_id = selected_queue_item_id
        self.titles: list[str] = []
        self.captions: list[str] = []
        self.info_messages: list[str] = []
        self.selectbox_labels: list[str] = []

    def title(self, value: str) -> None:
        self.titles.append(value)

    def caption(self, value: str, *_args, **_kwargs) -> None:
        self.captions.append(value)

    def columns(self, count: int) -> list[_StreamlitColumnStub]:
        return [_StreamlitColumnStub() for _ in range(count)]

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

    def info(self, value: str, *_args, **_kwargs) -> None:
        self.info_messages.append(value)

    def selectbox(
        self,
        label: str,
        options: list[str],
        index: int = 0,
        format_func=None,
    ) -> str:
        self.selectbox_labels.append(label)
        assert self.selected_queue_item_id in options
        if callable(format_func):
            format_func(self.selected_queue_item_id)
        return self.selected_queue_item_id


@pytest.mark.parametrize(
    ("queue_item_id", "expect_suppression_info"),
    [
        ("QUEUE-ACC-1003", False),
        ("QUEUE-ACC-1015", False),
        ("QUEUE-ACC-1026", False),
        ("QUEUE-ACC-1021", True),
    ],
)
def test_action_tracker_trace_renders_cleanly_for_manual_qa_matrix(
    monkeypatch,
    queue_item_id: str,
    expect_suppression_info: bool,
) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.opportunity_action_tracker import (
        render_opportunity_action_tracker_page,
    )

    build_operating_artifacts(ROOT)
    streamlit_stub = _StreamlitStub(selected_queue_item_id=queue_item_id)
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)

    render_opportunity_action_tracker_page(
        page_title="Opportunity & Action Tracker",
        scope_note="Deterministic control room.",
        repo_root=ROOT,
    )

    assert streamlit_stub.titles == ["Opportunity & Action Tracker"]
    assert streamlit_stub.selectbox_labels == ["Queue item"]
    assert any("The one current blocker is" in caption for caption in streamlit_stub.captions)
    if expect_suppression_info:
        assert any(
            "should not be treated as active leakage" in message
            for message in streamlit_stub.info_messages
        )
    else:
        assert not streamlit_stub.info_messages
        assert any(
            "No suppressed expected opportunities are attached" in caption
            for caption in streamlit_stub.captions
        )


def test_intervention_recommendation_changes_with_observed_rebill_state() -> None:
    from ri_control_room.synthetic.generate_intervention_tracking import _recommendation

    row = pd.Series({"action_path": "Billing"})
    revise_recommendation, _ = _recommendation(
        row,
        progress_state="turnaround_improving",
        baseline_metric_value=9.2,
        current_metric_value=8.1,
        correction_baseline=9.2,
        correction_current=8.1,
        observed_outcome_status="open_recoverable",
        observed_turnaround_days=2.0,
    )
    expand_recommendation, _ = _recommendation(
        row,
        progress_state="turnaround_improving",
        baseline_metric_value=9.2,
        current_metric_value=8.1,
        correction_baseline=9.2,
        correction_current=8.1,
        observed_outcome_status="closed_successful",
        observed_turnaround_days=2.0,
    )
    hold_recommendation, _ = _recommendation(
        row,
        progress_state="turnaround_improving",
        baseline_metric_value=9.2,
        current_metric_value=8.8,
        correction_baseline=9.2,
        correction_current=8.8,
        observed_outcome_status="open_recoverable",
        observed_turnaround_days=4.0,
    )

    assert revise_recommendation == "Revise"
    assert expand_recommendation == "Expand"
    assert hold_recommendation == "Hold"
