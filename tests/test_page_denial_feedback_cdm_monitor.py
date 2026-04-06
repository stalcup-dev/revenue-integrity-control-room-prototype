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

    def info(self, *_args, **_kwargs) -> None:
        return None

    def line_chart(self, *_args, **_kwargs) -> None:
        return None

    def multiselect(self, _label: str, options: list[str], default: list[str]) -> list[str]:
        return list(default or options)

    def button(self, *_args, **_kwargs) -> bool:
        return False

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


def test_denial_feedback_cdm_monitor_view_includes_linked_signal_and_governance_fields() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.denial_feedback_cdm_monitor import (
        build_denial_feedback_cdm_monitor_view,
    )

    build_operating_artifacts(ROOT)
    view = build_denial_feedback_cdm_monitor_view(ROOT)

    assert not view.denial_signal_patterns.empty
    assert not view.cdm_governance_monitor.empty
    assert {
        "denial_category",
        "denial_reason_group",
        "payer_group",
        "denial_amount",
        "linked_upstream_issue_domain",
        "linked_root_cause_mechanism",
        "linked_owner_team",
        "owner_action_hint",
    }.issubset(view.denial_signal_patterns.columns)
    assert {
        "department",
        "service_line",
        "expected_code",
        "expected_modifier",
        "default_units",
        "revenue_code",
        "active_flag",
        "rule_status",
        "cdm_governance_flag",
        "suggested_governance_action",
    }.issubset(view.cdm_governance_monitor.columns)
    assert {
        "Downstream signal",
        "Upstream issue domain",
        "Likely root cause mechanism",
        "Likely owner / action path",
        "Suggested next step",
    }.issubset(set(view.linkage_detail["field"]))


def test_denial_feedback_cdm_monitor_page_renders(monkeypatch) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts

    build_operating_artifacts(ROOT)
    streamlit_stub = _StreamlitStub()
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)
    runpy.run_path(
        str(ROOT / "app" / "pages" / "07_Denial_Feedback_CDM_Governance.py"),
        run_name="__main__",
    )
    assert streamlit_stub.titles == ["Denial Feedback + CDM Governance Monitor"]
    assert streamlit_stub.selectbox_labels == ["Denial pattern"]
