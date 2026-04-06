from __future__ import annotations

import sys
from types import ModuleType


class _StreamlitStub(ModuleType):
    def __init__(self) -> None:
        super().__init__("streamlit")
        self.markdown_calls: list[str] = []
        self.titles: list[str] = []

    def markdown(self, body: str, **_kwargs) -> None:
        self.markdown_calls.append(body)

    def title(self, value: str) -> None:
        self.titles.append(value)

    def subheader(self, *_args, **_kwargs) -> None:
        return None

    def caption(self, *_args, **_kwargs) -> None:
        return None


def test_apply_theme_injects_css_on_every_call(monkeypatch) -> None:
    from ri_control_room.ui.theme import apply_theme

    streamlit_stub = _StreamlitStub()
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)

    apply_theme()
    apply_theme()

    assert len(streamlit_stub.markdown_calls) == 2


def test_render_page_shell_uses_shared_wrapper(monkeypatch) -> None:
    from ri_control_room.ui.theme import render_page_shell

    streamlit_stub = _StreamlitStub()
    monkeypatch.setitem(sys.modules, "streamlit", streamlit_stub)

    render_page_shell(
        "Control Room Summary",
        "Fast operational scan.",
        "Deterministic control room.",
        badges=("Facility-side only",),
    )

    assert streamlit_stub.titles == ["Control Room Summary"]
    assert any("Hospital Revenue Integrity Control Room" in call for call in streamlit_stub.markdown_calls)
    assert any("Fast operational scan." in call for call in streamlit_stub.markdown_calls)
