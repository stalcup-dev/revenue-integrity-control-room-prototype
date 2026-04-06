from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_package_imports_and_page_registry() -> None:
    from ri_control_room.config import get_app_config, validate_v1_page_layout
    from ri_control_room.constants import FROZEN_V1_DEPARTMENTS, V1_PAGE_FILES
    from ri_control_room.pipeline import build_page_context

    assert len(FROZEN_V1_DEPARTMENTS) == 3
    assert "ED / Observation" not in " ".join(FROZEN_V1_DEPARTMENTS)
    assert len(V1_PAGE_FILES) == 7

    config = get_app_config(ROOT)
    validate_v1_page_layout(config.pages_dir)

    context = build_page_context("Smoke")
    assert context.page_title == "Smoke"
    assert context.frozen_departments == FROZEN_V1_DEPARTMENTS
