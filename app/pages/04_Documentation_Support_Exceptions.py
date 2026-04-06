from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_src_path() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


_bootstrap_src_path()
from ri_control_room.pipeline import build_page_context  # noqa: E402
from ri_control_room.ui.documentation_exceptions import render_documentation_exceptions_page  # noqa: E402


context = build_page_context("Documentation Support Exceptions")
REPO_ROOT = Path(__file__).resolve().parents[2]

render_documentation_exceptions_page(
    page_title=context.page_title,
    scope_note=context.scope_note,
    repo_root=REPO_ROOT,
)
