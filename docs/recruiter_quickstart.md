# Recruiter Quickstart

## What This App Demonstrates

This app demonstrates a deterministic, facility-side, outpatient-first revenue integrity control-room prototype built around documented performed activity. It maps documented performed activity to expected facility charge opportunity, surfaces the current failed control, routes the exception to the accountable owner, and keeps blocker, aging, recoverability, and next move visible. It is intentionally public-safe and synthetic, so the proof is product thinking, traceability, and hospital-informed workflow realism rather than private data access.

## Run It In Under 5 Minutes

Primary path from the repo root:

```bash
python scripts/run_demo.py
```

Supported Python: `3.12`-`3.13`. Tested on `3.13.3`.

Install path intent:

- `python scripts/run_demo.py` is the pinned recruiter/demo path.
- `requirements.txt` provides the exact runtime versions that bootstrap uses for reproducible demo behavior.
- `pyproject.toml` provides the package dependency ranges used by `python -m pip install -e .` for editable install and contributor workflows.
- `python -m ri_control_room ...` is the contributor / operating command family after the editable install is present.

That command will:

1. create or reuse a local `.venv-demo` environment
2. install pinned runtime packages there
3. reuse existing processed demo artifacts or rebuild them if they are missing or unreadable
4. launch Streamlit at `http://127.0.0.1:8501`
5. print a short end-of-boot summary with the URL, first pages, artifact state, validation status, and `Ctrl+C` stop instruction

Validation is not run as part of demo boot.

Backup manual path if you want to mirror the pinned demo install steps yourself:

Create the virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m ri_control_room demo
```

Windows no-activation fallback:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m ri_control_room demo
```

macOS / Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
python -m ri_control_room demo
```

`python -m pip install -e .` alone is enough for editable contributor use, because it installs the dependency ranges declared in `pyproject.toml`. Use `python -m pip install -r requirements.txt` before it when you want the same pinned runtime versions as the recruiter demo bootstrap.

If port `8501` is already in use, run `python scripts/run_demo.py --port 8502` or `python -m ri_control_room demo --port 8502`.

## Open These 3 Pages First

1. `Control Room Summary`
   What to look for: the featured deterministic story, current failed control, blocker, owner, aging, recoverability, and next action on one reviewer-safe slice.
2. `Opportunity & Action Tracker`
   What to look for: priority-ranked intervention work, selected case evidence trace, queue governance, checkpoint status, and hold / expand / revise follow-through.
3. `Charge Reconciliation Monitor`
   What to look for: backlog and overdue pressure by service line, plus the lightweight storytelling cue that explains what control is under pressure and who owns the next move.

Good fourth page if time allows:

4. `Documentation Support Exceptions`
   What to look for: unsupported-charge pressure, documentation-gap patterns, and routed accountability between documentation, coding, and operations.

## If You Do Not Run The App

Start with these artifacts instead:

- [Project summary and scope](../artifacts/project_summary_and_scope.md)
- [Proof index](../artifacts/proof_index.md)
- [Reviewer walkthrough pack](../artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md)
- [Decision Pack export](../artifacts/decision_pack/revenue_integrity_decision_pack.md)
- [Documentation trend realism validation](../artifacts/documentation_trend_realism/filter_state_validation.md)
- [Charge reconciliation realism validation](../artifacts/reconciliation_realism/reconciliation_scope_validation.md)
- [Secondary storytelling validation screenshots](../artifacts/page_storytelling_validation/page_storytelling_validation.md)

Read the first three items as the main proof path. The Decision Pack is a thin leave-behind artifact, and Scenario Lab / Denial Feedback are secondary support surfaces rather than the main credibility burden.

## Public-Safe Notes

- Synthetic data only
- No PHI
- No private credentials
- No external systems required for the default local demo
