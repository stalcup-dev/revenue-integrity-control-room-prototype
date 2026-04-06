from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
REQUIREMENTS_FILE = ROOT / "requirements.txt"
MIN_PYTHON = (3, 12)
MAX_PYTHON_EXCLUSIVE = (3, 14)
SUPPORTED_PYTHON_RANGE = "3.12-3.13"
TESTED_PYTHON = "3.13.3"
DEMO_VENV = ROOT / ".venv-demo"
BOOTSTRAPPED_FLAG = "RI_CONTROL_ROOM_DEMO_VENV_READY"
DEMO_STAMP = DEMO_VENV / ".ri_demo_ready"


def _bootstrap_src_path() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


def _ensure_python_version() -> None:
    current_version = sys.version.split()[0]
    if sys.version_info < MIN_PYTHON or sys.version_info >= MAX_PYTHON_EXCLUSIVE:
        raise SystemExit(
            "Supported Python versions for this demo: "
            f"{SUPPORTED_PYTHON_RANGE}. Tested on {TESTED_PYTHON}. "
            f"Current interpreter: {current_version}"
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap and launch the recruiter-ready RI Control Room demo. "
            f"Supported Python: {SUPPORTED_PYTHON_RANGE}. Tested on {TESTED_PYTHON}."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Streamlit port override. Default: 8501.",
    )
    return parser


def _venv_python() -> Path:
    if os.name == "nt":
        return DEMO_VENV / "Scripts" / "python.exe"
    return DEMO_VENV / "bin" / "python"


def _create_venv_if_missing() -> None:
    if DEMO_VENV.exists() and _venv_python().exists():
        return
    print(f"Creating local demo environment: {DEMO_VENV}", flush=True)
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(DEMO_VENV)


def _demo_env_is_fresh() -> bool:
    if not DEMO_STAMP.exists():
        return False
    stamp_mtime = DEMO_STAMP.stat().st_mtime
    watched_files = (
        REQUIREMENTS_FILE,
        ROOT / "pyproject.toml",
        ROOT / "src" / "ri_control_room" / "demo.py",
        Path(__file__).resolve(),
    )
    return all(path.exists() and path.stat().st_mtime <= stamp_mtime for path in watched_files)


def _install_demo_requirements() -> None:
    if _demo_env_is_fresh():
        print("Local demo environment already matches the pinned project setup.", flush=True)
        return
    python_exe = _venv_python()
    print("Installing pinned demo dependencies into the local demo environment...", flush=True)
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        cwd=str(ROOT),
        check=True,
    )
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-e", "."],
        cwd=str(ROOT),
        check=True,
    )
    DEMO_STAMP.write_text("ready\n", encoding="utf-8")


def _reexec_inside_demo_venv(port: int) -> int:
    _create_venv_if_missing()
    _install_demo_requirements()
    env = os.environ.copy()
    env[BOOTSTRAPPED_FLAG] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    python_exe = _venv_python()
    command = [str(python_exe), str(Path(__file__).resolve()), "--port", str(port)]
    completed = subprocess.run(command, cwd=str(ROOT), env=env, check=False)
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    _ensure_python_version()

    if os.environ.get(BOOTSTRAPPED_FLAG) != "1":
        print(
            "Bootstrapping the recruiter demo in an isolated local virtual environment "
            "so your global Python packages are not modified.",
            flush=True,
        )
        return _reexec_inside_demo_venv(args.port)

    _bootstrap_src_path()
    from ri_control_room.demo import run_demo

    return run_demo(ROOT, port=args.port)


if __name__ == "__main__":
    raise SystemExit(main())
