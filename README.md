# Hospital Charge Capture Analytics

Hospital revenue integrity teams do not just need another dashboard. They need a way to see when documented outpatient work should have become a facility charge, where that process broke, who owns the next move, and whether the dollars are still recoverable.

This repo presents that problem as a deterministic control-room case study using public-safe synthetic data. The app traces documented performed activity to expected facility charge opportunity, surfaces the failed control, routes the work to the accountable owner, and keeps blocker, aging, recoverability, and proof visible.

Credibility comes from deterministic traceability, browser-visible operating pages, reviewer walkthrough proof, and explicit realism / validation materials already in the repo.

For the narrative-first walkthrough, start with [case_study.md](./case_study.md).

## Start Here In 4 Clicks

If you open only four repo links, use this order:

1. [Case study](./case_study.md)
2. [Reviewer walkthrough](./artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md)
3. [Decision Pack export](./artifacts/decision_pack/revenue_integrity_decision_pack.md)
4. [Current shipped realism state](./artifacts/realism/post_tuning_realism_report.md)

Use [tests/test_case_detail_payload.py](./tests/test_case_detail_payload.py) as the compact code-level credibility cue, and use the [before/after realism diff](./artifacts/realism/realism_before_after_diff.md) only if you want the remediation bridge. The historical baseline is archived comparison context, not the first realism read.

## What This Is

- A Streamlit flagship app centered on deterministic failed-control detection, not dashboard-only reporting.
- A facility-side outpatient revenue integrity control room with active queues for reconciliation, documentation, prebill edits, and intervention follow-through.
- A reviewer-ready portfolio project with browser-visible walkthroughs, bounded validation materials, and exported proof.
- A public-safe synthetic dataset and build pipeline that show hospital-informed control-room behavior without PHI or private hospital data.
- A focused control-room product boundary: action-ready, scope-disciplined, and explicit about what is thin versus core.

## What This Is Not

- Not a generic BI dashboard.
- Not a denials-management or appeals platform.
- Not a predictive-first product or ML triage demo.
- Not a pro-fee, inpatient-first, or enterprise-wide rev-cycle suite.
- Not a production-integrated hospital deployment.

## Screenshots

Use [case_study.md](./case_study.md) for the full narrative. The screenshots below are the compact visual preview.

<p align="center">
  <a href="artifacts/reviewer_walkthrough_pack/summary_featured_story.png"><img src="artifacts/reviewer_walkthrough_pack/summary_featured_story.png" alt="Control Room Summary with the featured deterministic story" width="48%"></a>
  <a href="artifacts/reviewer_walkthrough_pack/summary_featured_story_proof_open.png"><img src="artifacts/reviewer_walkthrough_pack/summary_featured_story_proof_open.png" alt="Control Room Summary with representative proof opened" width="48%"></a>
</p>

<p align="center"><em>Start on Control Room Summary, then open the representative proof to see why the case surfaced and who owns the next move.</em></p>

<p align="center">
  <a href="artifacts/page_storytelling_validation/charge_reconciliation_after.png"><img src="artifacts/page_storytelling_validation/charge_reconciliation_after.png" alt="Charge Reconciliation Monitor showing backlog pressure and routing" width="32%"></a>
  <a href="artifacts/page_storytelling_validation/action_tracker_after.png"><img src="artifacts/page_storytelling_validation/action_tracker_after.png" alt="Opportunity and Action Tracker with intervention follow-through" width="32%"></a>
  <a href="artifacts/page_storytelling_validation/documentation_after.png"><img src="artifacts/page_storytelling_validation/documentation_after.png" alt="Documentation Support Exceptions showing unsupported charge pressure" width="32%"></a>
</p>

<p align="center"><em>Then move into the operating views that show queue pressure, intervention governance, and documentation support exceptions.</em></p>

## Quick Start

For recruiters and hiring managers on Windows:

1. Double-click [`Launch Hospital Charge Capture Demo.cmd`](./Launch%20Hospital%20Charge%20Capture%20Demo.cmd)
2. Wait for the local setup to finish on first launch
3. Let the browser tab open automatically

If the machine does not have Python installed, build the portable Windows package:

```powershell
python scripts/build_windows_portable.py
```

Then share `dist/windows-portable/` or `dist/hospital-charge-capture-analytics-windows-portable.zip` and have them double-click `Launch Hospital Charge Capture Demo.cmd` inside the packaged folder.

Terminal fallback:

```bash
python scripts/run_demo.py
```

If port `8501` is busy, use `python scripts/run_demo.py --port 8502`.

If you are here to learn how the project is put together rather than just run it, start with [docs/OPERATING_RUNBOOK.md](./docs/OPERATING_RUNBOOK.md).

## What To Click First

1. `Control Room Summary` for the main deterministic story.
2. `Opportunity & Action Tracker` for case evidence and follow-through.
3. `Charge Reconciliation Monitor` for backlog pressure and service-line routing.
4. `Documentation Support Exceptions` for unsupported-charge pressure and accountability.

## Repo Map

- [`Launch Hospital Charge Capture Demo.cmd`](./Launch%20Hospital%20Charge%20Capture%20Demo.cmd): primary Windows double-click launcher for local review.
- [`scripts/build_windows_portable.py`](./scripts/build_windows_portable.py): builder for the no-Python-required Windows package under `dist/`.
- [`scripts/launch_demo_windows.ps1`](./scripts/launch_demo_windows.ps1): PowerShell bootstrap used by the local Windows launcher.
- [`scripts/launch_portable_windows.ps1`](./scripts/launch_portable_windows.ps1): PowerShell bootstrap used inside the packaged portable build.
- [`scripts/run_demo.py`](./scripts/run_demo.py): recruiter-friendly demo bootstrap from a fresh-ish clone.
- [`case_study.md`](./case_study.md): narrative-first case-study walkthrough for portfolio review.
- [`app/streamlit_app.py`](./app/streamlit_app.py): Streamlit app entrypoint.
- [`app/pages/`](./app/pages): Summary plus the non-summary operating pages.
- [`src/ri_control_room/`](./src/ri_control_room): deterministic logic, synthetic generators, metrics, validation, UI helpers, and CLI.
- [`data/reference/`](./data/reference): governed public-safe reference tables that anchor the synthetic build.
- [`data/processed/`](./data/processed): generated synthetic artifacts used by the app.
- [`artifacts/`](./artifacts): walkthrough screenshots, proof packs, realism / validation materials, summary materials, and browser-visible evidence.
- [`docs/recruiter_quickstart.md`](./docs/recruiter_quickstart.md): 5-minute recruiter and hiring-manager guide.

## Proof And Validation Artifacts

If you do not run the app, start here:

- [Project summary and scope](./artifacts/project_summary_and_scope.md)
- [Proof index](./artifacts/proof_index.md)
- [Reviewer walkthrough pack](./artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md)

The [proof index](./artifacts/proof_index.md) links out to the realism materials, memo export, screenshots, and code-level tests if you want the deeper evidence map.

Strongest browser-visible screenshots:

- [Summary featured deterministic story](./artifacts/reviewer_walkthrough_pack/summary_featured_story.png)
- [Action Tracker work view](./artifacts/page_storytelling_validation/action_tracker_after.png)
- [Documentation support view](./artifacts/page_storytelling_validation/documentation_after.png)

## Public-Safe Note

- This repo uses synthetic, public-safe data only.
- No PHI, no private credentials, and no external hospital data are required in the default demo path.
- No `.env` file or secret configuration is needed to run the app locally.

## Known Scope Boundaries

- Facility-side only.
- Outpatient-first only.
- Deterministic-first product center; predictive logic is intentionally out of scope.
- Scenario Lab, denial feedback, and Decision Pack are thin supporting layers, not the main credibility claim.
- The repo proves deterministic control-room logic, traceability, and reviewer-ready packaging, not full payable-state modeling, production deployment maturity, or enterprise-natural source realism.
