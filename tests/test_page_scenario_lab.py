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
        self.session_state: dict[str, object] = {}
        self.sidebar = self
        self.number_input_values: dict[str, float] = {}

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

    def number_input(
        self,
        label: str,
        *,
        min_value: float,
        max_value: float,
        value: float,
        step: float,
    ) -> float:
        _ = step
        configured = self.number_input_values.get(label, value)
        return min(max(float(configured), float(min_value)), float(max_value))


def test_scenario_lab_view_and_projection_use_only_v0_levers() -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.ui.scenario_lab import build_scenario_lab_view, project_scenario_lab

    build_operating_artifacts(ROOT)
    view = build_scenario_lab_view(ROOT)

    assert [lever.label for lever in view.lever_configs] == [
        "Prebill edit clearance rate",
        "Correction turnaround days",
        "Routing speed to owner teams",
    ]
    assert "deterministic what-if" in view.story_cue.sentence.lower()
    assert len(view.story_cue.callouts) == 3
    assert any(
        "lever test" == callout.label.lower()
        and "projected backlog" in callout.value.lower()
        for callout in view.story_cue.callouts
    )
    assert len(view.lever_configs) == 3
    assert {
        "Open exceptions in current slice",
        "Governed prebill edit aging",
        "Governed recoverable dollars still open",
        "Correction turnaround baseline",
        "Routing speed to owner teams baseline",
        "Prebill edit clearance rate baseline proxy",
    }.issubset(set(view.baseline_inputs["baseline_metric"]))

    levers = {lever.key: lever for lever in view.lever_configs}
    projection = project_scenario_lab(
        view,
        target_prebill_clearance_rate=levers["prebill_clearance_rate"].default_target_value,
        target_correction_turnaround_days=levers["correction_turnaround_days"].default_target_value,
        target_routing_speed_days=levers["routing_speed_to_owner_teams"].default_target_value,
    )

    assert projection.projected_recoverable_dollar_lift >= 0
    assert projection.projected_backlog_reduction >= 0
    assert projection.projected_sla_improvement_points >= 0
    assert projection.ninety_day_impact_estimate == round(
        projection.projected_recoverable_dollar_lift * 3.0,
        2,
    )
    assert projection.implementation_effort in {"Low", "Moderate", "Moderate-high"}
    assert {
        "Projected recoverable dollar lift",
        "Projected open-exception / backlog reduction",
        "Projected SLA improvement",
        "90-day impact estimate",
    }.issubset(set(projection.output_summary["output"]))
    assert projection.formula_summary["guardrail"].str.contains("cap", case=False).any()


def test_scenario_lab_page_renders(monkeypatch) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts

    build_operating_artifacts(ROOT)
    streamlit_stub = _StreamlitStub()
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)
    runpy.run_path(str(ROOT / "app" / "pages" / "06_Scenario_Lab.py"), run_name="__main__")
    assert streamlit_stub.titles == ["Scenario Lab"]
