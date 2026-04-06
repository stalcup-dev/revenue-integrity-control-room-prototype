# Architecture Overview

Date: 2026-03-26

## Purpose

This repo implements a deterministic outpatient facility-side revenue integrity control room. The architecture answers one operating question:

Which documented performed activities should create expected facility charge opportunities, what is the current blocker when that does not happen cleanly, who owns the work now, and is the opportunity still recoverable?

## Architecture Principles

- Deterministic first
- Facility-side only
- Outpatient-first
- One current blocker per active queue item
- Expected-charge logic grounded in documented performed activity, not orders alone
- Packaged and non-billable suppression treated as required logic
- Queue routing and follow-through designed for operational decisions, not descriptive reporting

## Current End-To-End Flow

### 1. Synthetic source-like generation

The build starts from synthetic but source-shaped operational tables:

- `encounters`
- `orders`
- `documentation_events`
- `upstream_activity_signals`
- `charge_events`
- `claim_lines`
- `edits_bill_holds`
- `claims_or_account_status`
- thin `corrections_rebills`
- thin `denials_feedback`

These are generated with department-specific workflow rules for the three frozen V1 departments.

### 2. Expected opportunity derivation

`src/ri_control_room/logic/derive_expected_charge_opportunities.py` produces `expected_charge_opportunities.parquet` by combining:

- documented performed activity
- documentation support state
- department charge logic rules
- charge-event presence
- workflow-state context

The key rule is unchanged: expected-charge logic is grounded in documented performed activity or explicit upstream signals, not orders alone.

### 3. Workflow-state header

`src/ri_control_room/synthetic/generate_claims_account_status.py` builds `claims_or_account_status.parquet`, the current workflow-state header for each encounter or account unit. It carries:

- current prebill stage
- current primary blocker state and code
- issue domain and root cause
- current queue
- stage-specific aging
- recoverability status

This table is the control header that keeps the rest of the pipeline deterministic and one-blocker-driven.

### 4. Active exception queue

`src/ri_control_room/logic/build_exception_queue.py` converts the workflow-state header into `exception_queue.parquet`, the active routed work surface. It exposes:

- current queue and accountable owner
- queue entry timing
- aging and SLA fields
- recoverability framing
- why-not-billable context where relevant

The queue remains stage-driven:

- Charge Reconciliation Monitor
- Documentation Support Exceptions
- Coding Pending Review
- Modifiers / Edits / Prebill Holds
- Correction / Rebill Pending

### 5. Transition-event queue history

`src/ri_control_room/logic/build_queue_history.py` now produces `queue_history.parquet` as a transition-event ledger rather than a compressed summary path.

Current ledger behavior includes:

- multiple transition rows per active case when warranted
- prior_queue -> current_queue combinations
- routing reasons
- days in prior queue
- reroute count and cumulative path
- owner-handoff visibility
- current-record flag for the latest state

This is the evidence layer for churn, bottlenecks, and repeat rerouting.

### 6. Follow-through support

`src/ri_control_room/synthetic/generate_intervention_tracking.py` produces `intervention_tracking.parquet`, which backs the Opportunity & Action Tracker with:

- recurring issue pattern
- intervention owner
- target completion date
- checkpoint status
- baseline and current metrics
- correction turnaround signals
- before/after validation note
- hold / expand / revise recommendation

This is intentionally thin operational follow-through support, not a full intervention workflow engine.

### 7. KPI and priority layer

`src/ri_control_room/metrics/kpis.py` writes `kpi_snapshot.parquet`, which contains:

- current governed KPI rows
- all-scope and department-specific views
- transparent reduced V1 priority-score rows for active work

Priority scoring is explicit and component-based. No predictive or black-box ranking is required for the app to function.

### 8. Case detail and app layer

The Streamlit app loads shared processed outputs into five current pages:

- Control Room Summary
- Charge Reconciliation Monitor
- Modifiers / Edits / Prebill Holds
- Documentation Support Exceptions
- Opportunity & Action Tracker

Case-detail payloads combine expected opportunity, workflow header, queue state, queue-history ledger, KPI context, and intervention follow-through so reviewers can inspect why a case is actionable now.

### 9. Validation and artifact layer

`src/ri_control_room/build_pipeline.py` and `src/ri_control_room/artifacts.py` write:

- `data/processed/run_manifest.json`
- manual audit sample export
- realism reports under `artifacts/realism/`
- transition-ledger before/after evidence

`python -m ri_control_room validate` then updates the manifest validation block after schema and business-rule checks pass.

The repo also includes browser-audit proof under `artifacts/browser_audit/` for sidebar global filter behavior across the V1 pages.

## Current Relationship Summary

At a practical level, the current architecture behaves like this:

1. Synthetic encounter, activity, documentation, charge, claim, and edit tables establish the operational facts.
2. Department logic rules convert documented performed activity into expected facility charge opportunities.
3. `claims_or_account_status` expresses the one current blocker and current stage.
4. `exception_queue` turns the current blocker into active owner-routed work.
5. `queue_history` records the believable transition ledger behind that work.
6. `intervention_tracking` adds thin but data-backed follow-through context for the Action Tracker.
7. `corrections_rebills` and `denials_feedback` provide narrow support layers for post-bill recovery and downstream signal monitoring.
8. `kpi_snapshot` and `priority_scores` summarize exposure, performance, and active-work ranking.
9. The Streamlit app surfaces the same deterministic story page by page.

## What This Architecture Is Not

- Not a production data platform
- Not a full denials or appeals workflow
- Not a warehouse-ingestion implementation
- Not a predictive prioritization stack
- Not a generic task-management platform

## Current Constraints

- Synthetic inputs and outputs only
- Prototype-scale data rather than real operational volume
- `corrections_rebills` and `denials_feedback` are intentionally thin sidecar layers
- Queue history is strong for active exception churn but not a full closed-item enterprise ledger
- Intervention tracking is believable support, not a full project-management timeline

## Bottom Line

The implemented architecture is now:

documented performed activity -> expected opportunity derivation -> workflow-state header -> active queue -> transition-event ledger -> intervention follow-through -> KPI / priority layer -> Streamlit control-room pages -> realism and browser evidence

That is the current implemented system, not a future roadmap sketch.
