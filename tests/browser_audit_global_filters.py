from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PORT = 8510
APP_URL = f"http://127.0.0.1:{PORT}"
ARTIFACT_DIR = ROOT / "artifacts" / "browser_audit"

FILTER_SELECTION = {
    "Department": (
        "OR / Hospital Outpatient Surgery / Procedural Areas",
        "Radiology / Interventional Radiology",
    ),
    "Service line": (
        "Outpatient Surgery",
        "Radiology",
    ),
    "Queue": ("Documentation Support Exceptions",),
    "Recoverability": ("Pre-final-bill recoverable",),
}

FILTER_REMOVALS = {
    "Department": ("Outpatient Infusion / Oncology Infusion",),
    "Service line": ("Infusion", "Interventional Radiology"),
    "Queue": (
        "Charge Reconciliation Monitor",
        "Coding Pending Review",
        "Correction / Rebill Pending",
        "Modifiers / Edits / Prebill Holds",
    ),
    "Recoverability": ("Post-final-bill recoverable by correction / rebill",),
}

DEFAULT_FILTER_SUMMARY = (
    "Department: 3 selected",
    "Service line: 4 selected",
    "Queue: 5 selected",
    "Recoverability: 2 selected",
)


@dataclass(frozen=True)
class AuditRow:
    page: str
    department: str
    service_line: str
    queue: str
    recoverability: str
    active_filter_summary: str
    result: str
    notes: str


def _wait_for_server(url: str, process: subprocess.Popen[str], timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("Streamlit app exited before the browser audit could connect.")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(1)
    raise TimeoutError(f"Timed out waiting for Streamlit app at {url}.")


def _start_streamlit() -> subprocess.Popen[str]:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/streamlit_app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(PORT),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _sidebar(page: Page):
    return page.locator("[data-testid='stSidebar']")


def _body_text(page: Page) -> str:
    page.wait_for_timeout(1200)
    return page.locator("body").inner_text()


def _wait_for_page(page: Page, title: str) -> None:
    page.get_by_role("heading", name=title).wait_for(timeout=30000)
    page.locator("body").get_by_text("ACTIVE FILTERS", exact=False).wait_for(timeout=30000)
    page.wait_for_timeout(1000)


def _go_to_page(page: Page, title: str) -> None:
    _sidebar(page).get_by_role("link").filter(has_text=title).first.click()
    _wait_for_page(page, title)


def _multiselect_widget(page: Page, label: str):
    return _sidebar(page).locator("[data-testid='stMultiSelect']", has_text=label).first


def _remove_selected_value(page: Page, label: str, value: str) -> None:
    for _ in range(5):
        widget = _multiselect_widget(page, label)
        tag = widget.locator("[data-baseweb='tag']", has_text=value)
        if tag.count() == 0:
            return
        tag.first.locator("[title='Delete']").click()
        page.wait_for_timeout(1400)
    raise AssertionError(f"Failed to remove sidebar selection '{value}' from '{label}'.")


def _apply_filter_slice(page: Page) -> None:
    for label, removals in FILTER_REMOVALS.items():
        for value in removals:
            _remove_selected_value(page, label, value)


def _assert_active_filter_summary(page: Page, expected_lines: tuple[str, ...]) -> None:
    body_text = _body_text(page)
    for line in expected_lines:
        if line not in body_text:
            raise AssertionError(f"Expected active-filter text not found: {line}")


def _assert_no_inline_filter_multiselects(page: Page) -> None:
    if page.locator("main [data-testid='stMultiSelect']").count() != 0:
        raise AssertionError("Found duplicate inline multiselect filters in the main canvas.")


def _metric_text(page: Page, label: str) -> str:
    return page.locator("div[data-testid='stMetric']").filter(has_text=label).first.inner_text()


def _write_audit_report(rows: list[AuditRow]) -> Path:
    report_path = ARTIFACT_DIR / "filter_audit_report.md"
    lines = [
        "# Global Filter Browser Audit",
        "",
        "| Page | Dept | Service line | Queue | Recoverability | Active filter summary | Pass/Fail | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.page} | {row.department} | {row.service_line} | {row.queue} | "
            f"{row.recoverability} | {row.active_filter_summary} | {row.result} | {row.notes} |"
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def run_browser_audit() -> tuple[list[AuditRow], list[Path], Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_paths = [
        ARTIFACT_DIR / "summary_filtered.png",
        ARTIFACT_DIR / "charge_reconciliation_filtered.png",
        ARTIFACT_DIR / "modifiers_filtered.png",
        ARTIFACT_DIR / "documentation_filtered.png",
        ARTIFACT_DIR / "action_tracker_filtered.png",
        ARTIFACT_DIR / "summary_reset.png",
    ]
    for path in screenshot_paths:
        if path.exists():
            path.unlink()

    process = _start_streamlit()
    rows: list[AuditRow] = []
    try:
        _wait_for_server(APP_URL, process)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1400})
            page.goto(APP_URL)
            _wait_for_page(page, "Control Room Summary")

            for label in FILTER_SELECTION:
                if label not in _body_text(page):
                    raise AssertionError(f"Sidebar filter label missing: {label}")

            _apply_filter_slice(page)
            filtered_summary = (
                "Department: 2 selected",
                "Service line: 2 selected",
                "Queue: Documentation Support Exceptions",
                "Recoverability: Pre-final-bill recoverable",
            )
            _assert_active_filter_summary(page, filtered_summary)
            _assert_no_inline_filter_multiselects(page)
            if "3" not in _metric_text(page, "Open actionable exceptions"):
                raise AssertionError("Summary page did not narrow to the expected filtered count.")
            page.screenshot(path=str(screenshot_paths[0]), full_page=True)
            rows.append(
                AuditRow(
                    page="Control Room Summary",
                    department="Pass",
                    service_line="Pass",
                    queue="Pass",
                    recoverability="Pass",
                    active_filter_summary="Visible",
                    result="Pass",
                    notes="Queue filter applied; no duplicate inline filter widgets found.",
                )
            )

            _go_to_page(page, "Charge Reconciliation Monitor")
            _assert_active_filter_summary(
                page,
                (
                    "Department: 2 selected",
                    "Service line: 2 selected",
                    "Queue: Fixed to Charge Reconciliation Monitor on this page.",
                    "Recoverability: Pre-final-bill recoverable",
                ),
            )
            _assert_no_inline_filter_multiselects(page)
            if "2" not in _metric_text(page, "Unreconciled encounters"):
                raise AssertionError("Reconciliation page did not respect the non-queue filters.")
            page.screenshot(path=str(screenshot_paths[1]), full_page=True)
            rows.append(
                AuditRow(
                    page="Charge Reconciliation Monitor",
                    department="Pass",
                    service_line="Pass",
                    queue="Scoped out",
                    recoverability="Pass",
                    active_filter_summary="Visible",
                    result="Pass",
                    notes="Queue intentionally scoped out and clearly explained.",
                )
            )

            _go_to_page(page, "Modifiers / Edits / Prebill Holds")
            _assert_active_filter_summary(
                page,
                (
                    "Department: 2 selected",
                    "Service line: 2 selected",
                    "Queue: Fixed to Modifiers / Edits / Prebill Holds on this page.",
                    "Recoverability: Pre-final-bill recoverable",
                ),
            )
            _assert_no_inline_filter_multiselects(page)
            if "1" not in _metric_text(page, "Unresolved modifier edits"):
                raise AssertionError("Modifiers page did not respect the non-queue filters.")
            page.screenshot(path=str(screenshot_paths[2]), full_page=True)
            rows.append(
                AuditRow(
                    page="Modifiers / Edits / Prebill Holds",
                    department="Pass",
                    service_line="Pass",
                    queue="Scoped out",
                    recoverability="Pass",
                    active_filter_summary="Visible",
                    result="Pass",
                    notes="Queue intentionally scoped out and clearly explained.",
                )
            )

            _go_to_page(page, "Documentation Support Exceptions")
            _assert_active_filter_summary(
                page,
                (
                    "Department: 2 selected",
                    "Service line: 2 selected",
                    "Queue: Fixed to Documentation Support Exceptions on this page.",
                    "Recoverability: Pre-final-bill recoverable",
                ),
            )
            _assert_no_inline_filter_multiselects(page)
            if "3" not in _metric_text(page, "Unsupported charge exceptions"):
                raise AssertionError("Documentation page did not respect the non-queue filters.")
            page.screenshot(path=str(screenshot_paths[3]), full_page=True)
            rows.append(
                AuditRow(
                    page="Documentation Support Exceptions",
                    department="Pass",
                    service_line="Pass",
                    queue="Scoped out",
                    recoverability="Pass",
                    active_filter_summary="Visible",
                    result="Pass",
                    notes="Queue intentionally scoped out and clearly explained.",
                )
            )

            _go_to_page(page, "Opportunity & Action Tracker")
            _assert_active_filter_summary(page, filtered_summary)
            _assert_no_inline_filter_multiselects(page)
            if "3" not in _metric_text(page, "Open interventions"):
                raise AssertionError("Action Tracker page did not respect the global filter slice.")
            page.screenshot(path=str(screenshot_paths[4]), full_page=True)
            rows.append(
                AuditRow(
                    page="Opportunity & Action Tracker",
                    department="Pass",
                    service_line="Pass",
                    queue="Pass",
                    recoverability="Pass",
                    active_filter_summary="Visible",
                    result="Pass",
                    notes="All four global filters persisted and remained active.",
                )
            )

            _go_to_page(page, "Control Room Summary")
            _sidebar(page).get_by_text("Reset filters", exact=True).click()
            _wait_for_page(page, "Control Room Summary")
            _assert_active_filter_summary(page, DEFAULT_FILTER_SUMMARY)
            if "13" not in _metric_text(page, "Open actionable exceptions"):
                raise AssertionError("Reset filters did not restore the default summary slice.")
            page.screenshot(path=str(screenshot_paths[5]), full_page=True)
            rows.append(
                AuditRow(
                    page="Summary Reset",
                    department="Pass",
                    service_line="Pass",
                    queue="Pass",
                    recoverability="Pass",
                    active_filter_summary="Visible",
                    result="Pass",
                    notes="Reset behavior confirmed and default all-state restored.",
                )
            )
            browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except Exception:
            process.kill()
            process.wait(timeout=10)

    report_path = _write_audit_report(rows)
    return rows, screenshot_paths, report_path


def main() -> None:
    rows, screenshot_paths, report_path = run_browser_audit()
    print(f"Audit report: {report_path}")
    for screenshot_path in screenshot_paths:
        print(f"Screenshot: {screenshot_path}")
    for row in rows:
        print(f"{row.page}: {row.result} - {row.notes}")


if __name__ == "__main__":
    main()
