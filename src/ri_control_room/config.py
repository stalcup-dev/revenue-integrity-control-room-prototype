from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ri_control_room.constants import APP_TITLE, V1_PAGE_REGISTRY


@dataclass(frozen=True)
class PageSpec:
    filename: str
    title: str
    icon: str
    path: Path


@dataclass(frozen=True)
class AppConfig:
    app_title: str
    repo_root: Path
    pages_dir: Path
    page_specs: tuple[PageSpec, ...]


def get_app_config(repo_root: Path) -> AppConfig:
    pages_dir = repo_root / "app" / "pages"
    page_specs = tuple(
        PageSpec(
            filename=filename,
            title=title,
            icon=icon,
            path=pages_dir / filename,
        )
        for filename, title, icon in V1_PAGE_REGISTRY
    )
    return AppConfig(
        app_title=APP_TITLE,
        repo_root=repo_root,
        pages_dir=pages_dir,
        page_specs=page_specs,
    )


def validate_v1_page_layout(pages_dir: Path) -> None:
    expected = {filename for filename, _, _ in V1_PAGE_REGISTRY}
    discovered = {path.name for path in pages_dir.glob("*.py")}

    missing = sorted(expected - discovered)
    unexpected = sorted(discovered - expected)
    if not missing and not unexpected:
        return

    details: list[str] = []
    if missing:
        details.append(f"missing V1 pages: {', '.join(missing)}")
    if unexpected:
        details.append(
            "unexpected unregistered pages detected: "
            f"{', '.join(unexpected)}. Only pages in the governed shell registry are allowed."
        )
    raise RuntimeError("V1 page registry validation failed: " + " | ".join(details))
