from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


def _bootstrap_src_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    return repo_root


REPO_ROOT = _bootstrap_src_path()


st.set_page_config(
    page_title="RI Control Room",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    from ri_control_room.config import get_app_config, validate_v1_page_layout
    from ri_control_room.constants import FROZEN_V1_DEPARTMENTS, V1_SCOPE_NOTE
    from ri_control_room.ui.shared import get_global_filter_options, render_global_sidebar_filters
    from ri_control_room.ui.theme import apply_theme, render_sidebar_shell

    config = get_app_config(REPO_ROOT)
    apply_theme()

    try:
        validate_v1_page_layout(config.pages_dir)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    render_sidebar_shell(
        st.sidebar,
        app_title=config.app_title,
        scope_note=V1_SCOPE_NOTE,
        departments=FROZEN_V1_DEPARTMENTS,
    )
    render_global_sidebar_filters(get_global_filter_options(REPO_ROOT))

    pages = [
        st.Page(str(spec.path), title=spec.title, icon=spec.icon)
        for spec in config.page_specs
    ]
    navigation = st.navigation(pages=pages, position="sidebar")

    navigation.run()


if __name__ == "__main__":
    main()
