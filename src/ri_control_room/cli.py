from __future__ import annotations

import argparse
from pathlib import Path

from ri_control_room.artifacts import load_existing_priority_scores, resolve_repo_root
from ri_control_room.build_pipeline import (
    build_operating_artifacts,
    update_run_manifest_validation_status,
)
from ri_control_room.demo import DEFAULT_DEMO_PORT, launch_demo_app, run_demo
from ri_control_room.validation.business_rule_checks import run_business_rule_checks
from ri_control_room.validation.schema_checks import run_schema_checks


def _build_command(repo_root: Path) -> int:
    manifest_path = build_operating_artifacts(repo_root)
    print(f"Built artifacts and wrote manifest: {manifest_path}")
    return 0


def _validate_command(repo_root: Path) -> int:
    schema_results = run_schema_checks(repo_root)
    business_results = run_business_rule_checks(repo_root)
    schema_passed = bool(schema_results["passed"].all())
    business_passed = bool(business_results["passed"].all())
    manifest_path = update_run_manifest_validation_status(
        repo_root,
        schema_passed=schema_passed,
        business_passed=business_passed,
    )
    print(schema_results.to_string(index=False))
    print(business_results.to_string(index=False))
    print(f"Updated manifest: {manifest_path}")
    return 0 if schema_passed and business_passed else 1


def _app_command(repo_root: Path, *, port: int) -> int:
    load_existing_priority_scores(repo_root)
    return launch_demo_app(repo_root, port=port)


def _demo_command(repo_root: Path, *, port: int) -> int:
    return run_demo(repo_root, port=port)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ri_control_room")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Optional repo root override.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("build", help="Explicitly build synthetic artifacts and manifest.")
    subparsers.add_parser("validate", help="Validate existing artifacts and update manifest.")
    app_parser = subparsers.add_parser(
        "app",
        help="Run the Streamlit app against existing artifacts.",
    )
    app_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_DEMO_PORT,
        help=f"Streamlit port override. Default: {DEFAULT_DEMO_PORT}.",
    )
    demo_parser = subparsers.add_parser(
        "demo",
        help="Ensure synthetic artifacts exist, then launch the recruiter-ready Streamlit demo.",
    )
    demo_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_DEMO_PORT,
        help=f"Streamlit port override. Default: {DEFAULT_DEMO_PORT}.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.repo_root)
    if args.command == "build":
        return _build_command(repo_root)
    if args.command == "validate":
        return _validate_command(repo_root)
    if args.command == "app":
        return _app_command(repo_root, port=args.port)
    if args.command == "demo":
        return _demo_command(repo_root, port=args.port)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
