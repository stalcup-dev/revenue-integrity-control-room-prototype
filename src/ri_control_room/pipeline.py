from __future__ import annotations

from dataclasses import dataclass

from ri_control_room.constants import FROZEN_V1_DEPARTMENTS, V1_SCOPE_NOTE


@dataclass(frozen=True)
class PageContext:
    page_title: str
    frozen_departments: tuple[str, ...]
    scope_note: str


def build_page_context(page_title: str) -> PageContext:
    return PageContext(
        page_title=page_title,
        frozen_departments=FROZEN_V1_DEPARTMENTS,
        scope_note=V1_SCOPE_NOTE,
    )
