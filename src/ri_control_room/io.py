from __future__ import annotations

import sys
from pathlib import Path


def get_repo_root(anchor: Path | None = None) -> Path:
    base = (anchor or Path(__file__)).resolve()
    return base.parents[2]


def ensure_src_on_path(anchor: Path | None = None) -> Path:
    repo_root = get_repo_root(anchor)
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    return src_path
