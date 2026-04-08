from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST_ROOT = ROOT / "dist" / "windows-portable"
RUNTIME_DIRNAME = "runtime"
PORTABLE_LAUNCHER_PS1 = ROOT / "scripts" / "launch_portable_windows.ps1"
ZIP_NAME = "hospital-charge-capture-analytics-windows-portable.zip"
TESTED_PYTHON = "3.13.3"
PYTHON_EMBED_URL = (
    f"https://www.python.org/ftp/python/{TESTED_PYTHON}/python-{TESTED_PYTHON}-embed-amd64.zip"
)
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
ROOT_FILES_TO_COPY = (
    "README.md",
    "case_study.md",
    "requirements.txt",
    "pyproject.toml",
    "LICENSE",
)
ROOT_DIRS_TO_COPY = (
    "app",
    "artifacts",
    "data",
    "docs",
    "scripts",
    "src",
)
IGNORED_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv-demo",
    "__pycache__",
    "dist",
}
IGNORED_FILE_PATTERNS = (
    "*.pyc",
    "*.pyo",
    "*.log",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a Windows-portable recruiter package with an embedded Python runtime "
            "so the demo can launch on machines without Python preinstalled."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DIST_ROOT,
        help=f"Portable distribution directory. Default: {DIST_ROOT}",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Skip creating the final ZIP archive.",
    )
    return parser


def _ignore_directory(_path: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name in IGNORED_DIR_NAMES}
    for pattern in IGNORED_FILE_PATTERNS:
        ignored.update({name for name in names if Path(name).match(pattern)})
    return ignored


def _copy_project_payload(destination_root: Path) -> None:
    for filename in ROOT_FILES_TO_COPY:
        source = ROOT / filename
        shutil.copy2(source, destination_root / filename)

    for dirname in ROOT_DIRS_TO_COPY:
        source = ROOT / dirname
        destination = destination_root / dirname
        shutil.copytree(source, destination, ignore=_ignore_directory)


def _download_file(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def _runtime_python_executable(runtime_dir: Path) -> Path:
    return runtime_dir / "python.exe"


def _runtime_pth_file(runtime_dir: Path) -> Path:
    matches = sorted(runtime_dir.glob("python*._pth"))
    if not matches:
        raise FileNotFoundError(f"Could not locate embedded runtime ._pth file in {runtime_dir}")
    return matches[0]


def _enable_embedded_site_packages(runtime_dir: Path) -> None:
    pth_path = _runtime_pth_file(runtime_dir)
    original_lines = pth_path.read_text(encoding="utf-8").splitlines()

    updated_lines: list[str] = []
    site_packages_line = r"Lib\site-packages"
    saw_site_packages = False
    saw_import_site = False

    for line in original_lines:
        stripped = line.strip()
        if stripped == site_packages_line:
            saw_site_packages = True
            updated_lines.append(line)
            continue
        if stripped == "#import site":
            saw_import_site = True
            if not saw_site_packages:
                updated_lines.append(site_packages_line)
                saw_site_packages = True
            updated_lines.append("import site")
            continue
        if stripped == "import site":
            saw_import_site = True
            if not saw_site_packages:
                updated_lines.append(site_packages_line)
                saw_site_packages = True
            updated_lines.append(line)
            continue
        updated_lines.append(line)

    if not saw_site_packages:
        updated_lines.append(site_packages_line)
    if not saw_import_site:
        updated_lines.append("import site")

    pth_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    (runtime_dir / "Lib" / "site-packages").mkdir(parents=True, exist_ok=True)


def _extract_embedded_runtime(runtime_archive: Path, runtime_dir: Path) -> None:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(runtime_archive) as archive:
        archive.extractall(runtime_dir)
    _enable_embedded_site_packages(runtime_dir)


def _run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=str(cwd), check=True)


def _install_runtime_packages(distribution_root: Path) -> None:
    runtime_dir = distribution_root / RUNTIME_DIRNAME
    python_exe = _runtime_python_executable(runtime_dir)
    get_pip_path = runtime_dir / "get-pip.py"

    print("Downloading pip bootstrap for the embedded runtime...", flush=True)
    _download_file(GET_PIP_URL, get_pip_path)

    print("Installing pip into the embedded runtime...", flush=True)
    _run([str(python_exe), str(get_pip_path)], cwd=distribution_root)

    print("Installing the local packaging toolchain into the embedded runtime...", flush=True)
    _run(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-warn-script-location",
            "setuptools>=69",
            "wheel",
        ],
        cwd=distribution_root,
    )

    print("Installing pinned runtime dependencies into the portable package...", flush=True)
    _run(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-warn-script-location",
            "--no-build-isolation",
            "-r",
            "requirements.txt",
            ".",
        ],
        cwd=distribution_root,
    )

    get_pip_path.unlink(missing_ok=True)


def _portable_launcher_cmd() -> str:
    return (
        "@echo off\n"
        "setlocal\n"
        "cd /d \"%~dp0\"\n"
        "powershell -NoLogo -NoProfile -ExecutionPolicy Bypass "
        "-File \"%~dp0scripts\\launch_portable_windows.ps1\"\n"
        "set \"EXIT_CODE=%ERRORLEVEL%\"\n"
        "if not \"%EXIT_CODE%\"==\"0\" if not \"%EXIT_CODE%\"==\"130\" (\n"
        "    echo.\n"
        "    pause\n"
        ")\n"
        "exit /b %EXIT_CODE%\n"
    )


def _portable_readme() -> str:
    return (
        "Hospital Charge Capture Analytics Portable Demo\r\n"
        "==============================================\r\n\r\n"
        "1. Double-click 'Launch Hospital Charge Capture Demo.cmd'.\r\n"
        "2. Wait for the browser tab to open automatically.\r\n"
        "3. If Windows prompts about PowerShell execution, choose to allow the local launcher.\r\n"
    )


def _write_portable_launchers(distribution_root: Path) -> None:
    launcher_target = distribution_root / "Launch Hospital Charge Capture Demo.cmd"
    launcher_target.write_text(_portable_launcher_cmd(), encoding="utf-8")
    shutil.copy2(
        PORTABLE_LAUNCHER_PS1,
        distribution_root / "scripts" / PORTABLE_LAUNCHER_PS1.name,
    )
    (distribution_root / "PORTABLE_README.txt").write_text(_portable_readme(), encoding="utf-8")


def _create_zip_archive(distribution_root: Path) -> Path:
    archive_base = distribution_root.parent / ZIP_NAME.removesuffix(".zip")
    archive_path = Path(shutil.make_archive(str(archive_base), "zip", distribution_root.parent, distribution_root.name))
    return archive_path


def build_portable_distribution(output_dir: Path, *, zip_output: bool = True) -> tuple[Path, Path | None]:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Copying project payload into {output_dir}...", flush=True)
    _copy_project_payload(output_dir)

    runtime_dir = output_dir / RUNTIME_DIRNAME
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        runtime_archive = temp_dir / "python-embed.zip"
        print(f"Downloading embedded Python {TESTED_PYTHON} from python.org...", flush=True)
        _download_file(PYTHON_EMBED_URL, runtime_archive)
        print("Extracting embedded Python runtime...", flush=True)
        _extract_embedded_runtime(runtime_archive, runtime_dir)

    _install_runtime_packages(output_dir)
    _write_portable_launchers(output_dir)

    archive_path: Path | None = None
    if zip_output:
        print("Creating the portable ZIP archive...", flush=True)
        archive_path = _create_zip_archive(output_dir)

    return output_dir, archive_path


def main(argv: list[str] | None = None) -> int:
    if sys.platform != "win32":
        raise SystemExit("This builder currently supports Windows only.")

    args = build_parser().parse_args(argv)
    output_dir, archive_path = build_portable_distribution(
        args.output_dir,
        zip_output=not args.no_zip,
    )

    print("\nPortable Windows demo package ready.", flush=True)
    print(f"Folder: {output_dir}", flush=True)
    if archive_path is not None:
        print(f"ZIP: {archive_path}", flush=True)
    print(
        "Share the folder or ZIP, then have the reviewer double-click "
        "'Launch Hospital Charge Capture Demo.cmd'.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
