from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build_windows_portable.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_windows_portable", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_enable_embedded_site_packages_updates_pth_file(tmp_path: Path) -> None:
    module = _load_module()
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    pth_path = runtime_dir / "python313._pth"
    pth_path.write_text("python313.zip\n.\n#import site\n", encoding="utf-8")

    module._enable_embedded_site_packages(runtime_dir)

    updated = pth_path.read_text(encoding="utf-8")
    assert r"Lib\site-packages" in updated
    assert "import site" in updated
    assert "#import site" not in updated
    assert (runtime_dir / "Lib" / "site-packages").exists()


def test_portable_launcher_cmd_uses_portable_powershell_script() -> None:
    module = _load_module()

    launcher = module._portable_launcher_cmd()

    assert "launch_portable_windows.ps1" in launcher
    assert "pause" in launcher
