# Operating Runbook

Date: 2026-03-26

## Purpose

This repo operates as a deterministic, outpatient-first, facility-side revenue integrity control room. Its job is to:

- map documented performed activity to expected facility charge opportunities
- classify one current primary blocker for each active encounter or account unit
- route active work into the correct operational queue
- separate pre-final-bill recovery, post-bill correction / rebill recovery, and already-lost exposure
- support case review, action tracking, and reviewer validation from exported evidence

This is an operating prototype. It is not a denials platform, payer engine, pro-fee tool, or predictive triage product.

## Current Commands

This runbook assumes the contributor / operating path, not the one-command recruiter demo bootstrap in `python scripts/run_demo.py`.

Install intent:

- `python -m pip install -e .` is sufficient for contributor and operating use because `pyproject.toml` declares the package dependency ranges.
- Add `python -m pip install -r requirements.txt` before `python -m pip install -e .` only when you want the same pinned runtime versions used by the reproducible demo bootstrap.
- Treat `requirements.txt` as the pinned demo environment and `pyproject.toml` as the editable package contract.

Install once in editable mode:

```powershell
python -m pip install -e .
```

Build or refresh processed outputs:

```powershell
python -m ri_control_room build
```

Validate the current build:

```powershell
python -m ri_control_room validate
ruff check app src tests
pytest -q tests
```

Run the app:

```powershell
python -m ri_control_room app
```

The repo no longer requires `PYTHONPATH=src` as the normal operating path.

## Frozen V1 Scope

- Outpatient Infusion / Oncology Infusion
- Radiology / Interventional Radiology
- OR / Hospital Outpatient Surgery / Procedural Areas

Current pages:

- Control Room Summary
- Charge Reconciliation Monitor
- Modifiers / Edits / Prebill Holds
- Documentation Support Exceptions
- Opportunity & Action Tracker

ED and Observation are not primary V1 departments.

## Inputs

### Synthetic operating inputs

- `encounters`
- `orders`
- `documentation_events`
- `upstream_activity_signals`
- `claims_or_account_status`
- `charge_events`
- `claim_lines`
- `edits_bill_holds`
- `corrections_rebills`
- `denials_feedback`

### Governing reference inputs

- `data/reference/department_charge_logic_map.csv`
- `data/reference/queue_definitions.csv`
- `data/reference/stage_aging_rules.csv`
- `data/reference/recoverability_rules.csv`
- `data/reference/issue_domain_map.csv`
- `data/reference/root_cause_map.csv`

The current build is synthetic only. No production EHR, charging, billing, or warehouse feeds are connected.

## Outputs

The build currently writes these control-room outputs to `data/processed/`:

- `expected_charge_opportunities.parquet`
- `exception_queue.parquet`
- `queue_history.parquet`
- `priority_scores.parquet`
- `intervention_tracking.parquet`
- `kpi_snapshot.parquet`
- `manual_audit_sample.csv`

Supporting synthetic tables are also generated for encounter, workflow-state, documentation, activity-signal, charge, claim-line, edit, corrections / rebills, and denials-feedback layers.

The latest in-repo processed run at the time of this refresh contains:

- `62` encounters
- `94` expected charge opportunities
- `24` active queue items
- `50` queue-history transition rows
- `24` intervention-tracking rows
- `64` KPI snapshot rows
- `4` corrections / rebills rows
- `9` denials-feedback rows
- `21` manual-audit sample rows

## Deterministic Workflow Model

### Current stage-to-queue mapping

- `Charge capture pending` -> `Charge Reconciliation Monitor`
- `Documentation pending` -> `Documentation Support Exceptions`
- `Coding pending` -> `Coding Pending Review`
- `Prebill edit / hold` -> `Modifiers / Edits / Prebill Holds`
- `Correction / rebill pending` -> `Correction / Rebill Pending`

### Current blocker rule

- Multiple internal issue tags may exist beneath one encounter.
- Only one current primary blocker can drive the active routed work item.
- Active routing comes from the workflow-state header, not from a flat pile of issue tags.
- Deterministic control logic remains the credibility engine.

### Current recoverability framing

- `Pre-final-bill recoverable`
- `Post-final-bill recoverable by correction / rebill`
- `Post-window financially lost`
- `Financially closed but still compliance-relevant`

Recoverability remains stage-specific and operationally visible in both queue and KPI outputs.

## Queue And Follow-Through Reality

### Exception queue

`exception_queue.parquet` is the active work surface. It exposes the current queue, current stage, accountable owner, stage-specific aging, recoverability, and one-current-blocker context for each active item.

### Queue history

`queue_history.parquet` is now a transition-event ledger rather than a one-row summary path. It records:

- first routing into active work
- reroutes between queues
- ownership-heavy handoffs
- stage-specific prior-queue aging
- routing reasons
- cumulative path and reroute count

This is the main evidence layer for bottlenecks, handoff failures, and repeat churn.

### Opportunity & Action Tracker

The Action Tracker is backed by `intervention_tracking.parquet`. Current fields support:

- recurring issue pattern
- intervention owner
- target completion date
- checkpoint status
- baseline metric
- current metric
- correction turnaround signal
- before/after validation note
- hold / expand / revise recommendation

This is intentionally thin follow-through support, not a full intervention management system.

## Current Validation And Evidence Flow

### Build

`python -m ri_control_room build` regenerates processed outputs, updates the run manifest, and writes realism artifacts including transition-ledger evidence.

### Validate

`python -m ri_control_room validate` updates the run manifest validation block and runs schema plus business-rule checks against existing outputs.

Current business-rule coverage includes:

- expected-charge logic anchored to documented performed activity rather than orders alone
- one-current-blocker enforcement
- packaged / non-billable suppression handling
- stage-based queue routing
- recoverability coverage
- queue-history and reroute realism checks

### Browser verification

Browser evidence lives under `artifacts/browser_audit/`. The current repo includes a passing filter audit proving that sidebar Department, Service line, Queue, and Recoverability filters persist across the V1 pages, with queue scoping intentionally fixed on queue-specific pages.

### Realism evidence

Current realism evidence lives under `artifacts/realism/` and includes:

- overall realism scorecard report
- department story realism report
- suppression balance report
- medium-volume ops and payable-state report
- transition-ledger report
- transition-ledger before/after diff

## What Believable V1 Means Now

Believable V1 does not mean production-ready. It means a reviewer can:

- trace expected opportunities back to documented performed activity
- explain the current blocker and current queue from exported evidence
- see reroute and handoff history in `queue_history`
- distinguish recoverable work from correction-path recovery and already-lost exposure
- review Action Tracker follow-through fields as data-backed operating signals rather than static labels
- confirm packaged or non-billable suppressions do not leak into active recovery queues
- validate browser-visible filter behavior against the proof pack

Reference docs:

- `docs/V1_VALIDATION_CHECKLIST.md`
- `docs/REVIEWER_EVIDENCE_PACK.md`
- `docs/MANUAL_AUDIT_SAMPLE.md`
- `docs/MANUAL_AUDIT_RUBRIC.md`

## Known Limitations

- Synthetic data only
- No production source-system integration
- Prototype-scale volume, not enterprise scale
- `corrections_rebills` and `denials_feedback` remain thin support layers
- Queue history is realistic for active exception churn, not a full enterprise workflow engine
- Intervention tracking is operationally believable but intentionally lighter than a task platform

## Bottom Line

Treat this repo as a governed facility-side outpatient control-room prototype with implemented build, validate, app, realism, and reviewer-evidence workflows. Do not treat it as a production operating system or as a denials platform.
