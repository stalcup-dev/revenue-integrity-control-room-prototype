from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_cli_build_and_validate_commands() -> None:
    from ri_control_room.cli import main

    build_exit = main(["--repo-root", str(ROOT), "build"])
    validate_exit = main(["--repo-root", str(ROOT), "validate"])

    assert build_exit == 0
    assert validate_exit == 0
    assert (ROOT / "data" / "processed" / "run_manifest.json").exists()


def test_cli_app_command_uses_existing_artifacts(monkeypatch) -> None:
    from ri_control_room.build_pipeline import build_operating_artifacts
    from ri_control_room.cli import main

    calls: list[list[str]] = []

    class _CompletedProcess:
        returncode = 0

    def _fake_run(command: list[str], cwd: str, check: bool) -> _CompletedProcess:
        calls.append(command)
        assert cwd == str(ROOT)
        assert check is False
        return _CompletedProcess()

    build_operating_artifacts(ROOT)
    monkeypatch.setattr("ri_control_room.demo.subprocess.run", _fake_run)

    exit_code = main(["--repo-root", str(ROOT), "app"])
    assert exit_code == 0
    assert calls
    assert calls[0][:3] == [sys.executable, "-m", "streamlit"]


def test_cli_demo_command_builds_if_artifacts_missing_and_prints_summary_block(
    monkeypatch,
    capsys,
) -> None:
    from ri_control_room.cli import main

    calls: list[list[str]] = []

    class _FakePopen:
        def __init__(self, command: list[str], cwd: str) -> None:
            calls.append(command)
            assert cwd == str(ROOT)
            self.returncode = 0

        def poll(self) -> None:
            return None

        def wait(self) -> int:
            return self.returncode

    build_calls: list[Path] = []

    def _fake_build(repo_root: Path) -> Path:
        build_calls.append(repo_root)
        return repo_root / "data" / "processed" / "run_manifest.json"

    monkeypatch.setattr("ri_control_room.demo.demo_artifacts_ready", lambda _repo_root: False)
    monkeypatch.setattr("ri_control_room.demo.build_operating_artifacts", _fake_build)
    monkeypatch.setattr("ri_control_room.demo._wait_for_demo_server", lambda *args, **kwargs: True)
    monkeypatch.setattr("ri_control_room.demo.subprocess.Popen", _FakePopen)

    exit_code = main(["--repo-root", str(ROOT), "demo", "--port", "8512"])

    assert exit_code == 0
    assert build_calls == [ROOT]
    assert calls
    assert calls[0][:3] == [sys.executable, "-m", "streamlit"]
    output = capsys.readouterr().out
    assert "Processed artifacts rebuilt:" in output
    assert "Demo Ready" in output
    assert "URL: http://127.0.0.1:8512" in output
    assert "Open first: Control Room Summary -> Opportunity & Action Tracker -> Charge Reconciliation Monitor" in output
    assert "Validation: Not run during demo boot" in output
    assert "Stop: Ctrl+C" in output
