# Reviewer Evidence Pack

Date: 2026-03-26

Historical reviewer-planning archive only. This file captures an earlier evidence-pack snapshot and is not part of the primary public repo path. Public readers should start with [`README.md`](../README.md), [`artifacts/project_summary_and_scope.md`](../artifacts/project_summary_and_scope.md), and [`artifacts/proof_index.md`](../artifacts/proof_index.md).

Evidence basis:

- `data/processed/run_manifest.json` generated at `2026-03-26T15:39:03+00:00`
- validation manifest updated at `2026-03-26T15:39:12+00:00`
- current processed outputs in `data/processed/`
- realism artifacts in `artifacts/realism/`
- browser audit artifact in `artifacts/browser_audit/filter_audit_report.md`

## Purpose

This repo is a deterministic outpatient facility-side revenue integrity control-room prototype. Its job is to answer one operating question:

Which documented performed activities should create expected facility charge opportunities, what is the current blocker when that does not happen cleanly, who owns the work now, and is the opportunity still recoverable?

This is a governed operating prototype, not a denials platform, enterprise revenue cycle suite, payer engine, or predictive triage product.

## Frozen V1 Scope

- Departments:
  - Outpatient Infusion / Oncology Infusion
  - Radiology / Interventional Radiology
  - OR / Hospital Outpatient Surgery / Procedural Areas
- Pages:
  - Control Room Summary
  - Charge Reconciliation Monitor
  - Modifiers / Edits / Prebill Holds
  - Documentation Support Exceptions
  - Opportunity & Action Tracker
- Operating model:
  - deterministic only
  - outpatient facility-side only
  - one current primary blocker per active unit
  - explicit recoverability windows
  - packaged and non-billable suppression treated as required logic

## Current Artifact Footprint

Latest processed run:

- `62` encounters
- `94` orders
- `94` documentation events
- `94` upstream activity signals
- `62` workflow-state header rows
- `83` charge events
- `69` claim lines
- `6` edits / bill holds
- `4` corrections / rebills rows
- `9` denials-feedback rows
- `94` expected charge opportunities
- `24` active queue items
- `50` queue-history transition rows
- `24` intervention-tracking rows
- `64` KPI snapshot rows
- `21` manual-audit sample rows

What that means:

- the repo is not just rendering placeholder UI text
- current outputs cover build, validate, app, reviewer evidence, and realism artifacts
- thin post-bill layers now exist, but they remain intentionally narrow

## Deterministic Control Proof

The core control logic is explicit and reviewable:

1. Expected opportunities are anchored to documented performed activity, not orders alone.
2. Department rules decide whether an activity is separately billable, modifier-dependent, documentation-dependent, packaged, integral, or non-billable.
3. Only one current primary blocker can drive the active work item.
4. Queue routing is stage-driven and owner-visible.
5. Recoverability is rule-based and separates pre-final-bill recovery, post-bill correction / rebill recovery, and already-lost exposure.

That produces a stable pipeline:

`documented activity -> expected opportunity -> current blocker -> owner queue -> transition history -> intervention follow-through -> KPI / priority snapshot`

## Current Queue Reality

Current active queue mix:

- `Documentation Support Exceptions`: `7`
- `Modifiers / Edits / Prebill Holds`: `6`
- `Coding Pending Review`: `5`
- `Charge Reconciliation Monitor`: `4`
- `Correction / Rebill Pending`: `2`

Current accountable owner mix:

- `Department operations`: `11`
- `Billing operations`: `8`
- `Coding team`: `5`

Current recoverability mix:

- `Pre-final-bill recoverable`: `13`
- `Post-window financially lost`: `9`
- `Post-final-bill recoverable by correction / rebill`: `2`

This proves the current queue is not a single clean prebill story. It includes active prebill work, already-lost exposure, and a narrow post-bill recovery path.

## Transition-Ledger Evidence

The current transition-ledger report shows:

- `queue_history` rows: `50`
- `exception_queue` rows: `24`
- transition-event density: `2.0833`
- multi-event cases: `14`
- reroute buckets: `0:10`, `1:6`, `2:4`, `3+:4`

Top transition pairs:

- `Charge Reconciliation Monitor -> Documentation Support Exceptions`
- `Documentation Support Exceptions -> Coding Pending Review`
- `Coding Pending Review -> Modifiers / Edits / Prebill Holds`
- `Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending`

Why this matters:

- queue history now behaves like a believable transition-event ledger
- reroute and handoff patterns are visible instead of collapsed into one summary row
- OR / procedural cases are more handoff-heavy, which matches the intended service-line realism

## Action Tracker Follow-Through Evidence

`intervention_tracking.parquet` currently backs the Action Tracker with visible operational follow-through.

Current checkpoint distribution:

- `Monitor next checkpoint`: `9`
- `Pilot checkpoint complete`: `6`
- `Baseline captured`: `5`
- `Checkpoint overdue`: `2`
- `Turnaround improving`: `2`

Current recommendation distribution:

- `Hold`: `12`
- `Revise`: `6`
- `Expand`: `6`

Current follow-through signals include:

- recurring issue pattern and owner context
- target completion dates
- baseline and current metric values
- correction turnaround baseline/current days where relevant
- before/after validation notes

This keeps the Action Tracker grounded in operating evidence rather than static labels.

## Current KPI And Priority Evidence

`kpi_snapshot.parquet` now contains current KPI rows plus transparent reduced V1 priority-score rows. Current governed KPI outputs include:

- Unreconciled encounter rate
- Charge reconciliation completion within policy window
- Unsupported charge rate
- Late charge rate
- Time to charge entry
- Prebill edit aging
- Department repeat exception rate
- Recoverable dollars still open
- Dollars already lost after timing window
- Edit first-pass clearance rate

Priority rows expose their formula and component values. No predictive scoring is required.

## Validation And Browser Evidence

Manifest snapshot captured in this archived evidence pack:

- schema checks: `pass` at the archived snapshot above
- business-rule checks: `pass` at the archived snapshot above
- overall validation: `pass` at the archived snapshot above

Current realism scorecard status:

- overall result: `pass` at the archived snapshot above
- includes workflow, department, suppression balance, medium-volume ops, downstream payable-signal, transition-ledger, churn, and intervention-follow-through dimensions

Current browser proof:

- `artifacts/browser_audit/filter_audit_report.md` shows sidebar global filters passing across all five V1 pages
- Department, Service line, Queue, and Recoverability filters persist correctly
- queue filtering is intentionally scoped on queue-specific pages and reset behavior is verified

## What Believable V1 Means Now

A reviewer should be able to:

- trace a case from documented performed activity to expected facility charge logic
- explain the current blocker and why only one blocker is active now
- see current owner routing and reroute history
- distinguish packaged or non-billable suppressions from true misses
- review correction / rebill follow-through and thin downstream denial signals without treating the repo as a denials platform or full payable-state model
- inspect Action Tracker progress fields as data-backed operating evidence
- validate UI filter behavior against the proof pack

## What Remains Thin Or Deferred

- Synthetic only; no production source integration
- No denials-management workflow or appeals orchestration
- No predictive prioritization, simulation, or scenario lab
- `corrections_rebills` is a thin support layer, not a full rebill workflow
- `denials_feedback` is a downstream signal layer only
- Intervention tracking is intentionally thinner than a full task-management platform

## Bottom Line

This repo already presents a coherent, action-ready deterministic control-room story with archived build outputs, queue routing, transition-ledger evidence, Action Tracker follow-through support, KPI evidence, realism artifacts, and browser verification. What remains deferred is broader platform scope, stronger real-source grounding, and productionization, not the V1 control-room core.
