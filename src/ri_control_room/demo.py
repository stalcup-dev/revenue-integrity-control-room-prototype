from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from ri_control_room.artifacts import load_existing_priority_scores, resolve_repo_root
from ri_control_room.build_pipeline import build_operating_artifacts


DEFAULT_DEMO_PORT = 8501
SERVER_READY_TIMEOUT_SECONDS = 30.0
START_HERE_PAGES = (
    "Control Room Summary",
    "Opportunity & Action Tracker",
    "Charge Reconciliation Monitor",
)
ARTIFACTS_REUSED_NOTE = "Existing processed artifacts reused"
ARTIFACTS_REBUILT_NOTE = "Processed artifacts rebuilt"
DEMO_VALIDATION_NOTE = "Not run during demo boot"


def demo_url(port: int = DEFAULT_DEMO_PORT) -> str:
    return f"http://127.0.0.1:{port}"


def demo_pages_note() -> str:
    return "Open these pages first: " + " -> ".join(START_HERE_PAGES)


def demo_runtime_note(port: int = DEFAULT_DEMO_PORT) -> str:
    return (
        f"Local demo URL: {demo_url(port)}\n"
        f"{demo_pages_note()}\n"
        "Dataset: public-safe synthetic data only, no PHI."
    )


def demo_boot_summary(
    *,
    port: int = DEFAULT_DEMO_PORT,
    artifact_note: str,
    validation_note: str = DEMO_VALIDATION_NOTE,
) -> str:
    divider = "=" * 60
    return (
        f"\n{divider}\n"
        "Demo Ready\n"
        f"URL: {demo_url(port)}\n"
        f"Open first: {' -> '.join(START_HERE_PAGES)}\n"
        f"Artifacts: {artifact_note}\n"
        f"Validation: {validation_note}\n"
        "Stop: Ctrl+C\n"
        f"{divider}"
    )


def demo_artifacts_ready(repo_root: Path | None = None) -> bool:
    root = resolve_repo_root(repo_root)
    try:
        priority_scores = load_existing_priority_scores(root)
    except Exception:
        return False
    return not priority_scores.empty


def ensure_demo_artifacts(repo_root: Path | None = None) -> str:
    root = resolve_repo_root(repo_root)
    if demo_artifacts_ready(root):
        print(f"{ARTIFACTS_REUSED_NOTE}.", flush=True)
        return ARTIFACTS_REUSED_NOTE
    print(
        "Processed demo artifacts missing or unreadable. Rebuilding fresh public-safe artifacts...",
        flush=True,
    )
    manifest_path = build_operating_artifacts(root)
    print(f"{ARTIFACTS_REBUILT_NOTE}: {manifest_path}", flush=True)
    return ARTIFACTS_REBUILT_NOTE


def _streamlit_command(root: Path, *, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(root / "app" / "streamlit_app.py"),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]


def _wait_for_demo_server(
    process: subprocess.Popen[object],
    *,
    port: int,
    timeout_seconds: float = SERVER_READY_TIMEOUT_SECONDS,
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(demo_url(port), timeout=1.0) as response:
                if 200 <= response.status < 500:
                    return True
        except urllib.error.URLError:
            pass
        time.sleep(0.5)
    return False


def _stop_streamlit_process(process: subprocess.Popen[object]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def launch_demo_app(
    repo_root: Path | None = None,
    *,
    port: int = DEFAULT_DEMO_PORT,
) -> int:
    root = resolve_repo_root(repo_root)
    print(demo_runtime_note(port), flush=True)
    subprocess.run(
        _streamlit_command(root, port=port),
        cwd=str(root),
        check=False,
    )
    return 0


def run_demo(
    repo_root: Path | None = None,
    *,
    port: int = DEFAULT_DEMO_PORT,
) -> int:
    root = resolve_repo_root(repo_root)
    artifact_note = ensure_demo_artifacts(root)
    process = subprocess.Popen(
        _streamlit_command(root, port=port),
        cwd=str(root),
    )
    try:
        if _wait_for_demo_server(process, port=port):
            print(
                demo_boot_summary(
                    port=port,
                    artifact_note=artifact_note,
                ),
                flush=True,
            )
        return int(process.wait())
    except KeyboardInterrupt:
        print("\nStopping demo...", flush=True)
        _stop_streamlit_process(process)
        return 130
