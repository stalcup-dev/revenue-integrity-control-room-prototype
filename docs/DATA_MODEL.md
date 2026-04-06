# Data Model

Date: 2026-03-26

## Purpose

This document describes the current implemented V1 data model for the deterministic outpatient facility-side control room. It is intentionally implementation-grounded: it focuses on the processed artifacts, their role in the pipeline, and how they relate to one another now.

This is not a future-state enterprise schema. It is the current V1 artifact model for the synthetic flagship prototype.

## Modeling Rules

- Scope is limited to the frozen V1 departments:
  - Outpatient Infusion / Oncology Infusion
  - Radiology / Interventional Radiology
  - OR / Hospital Outpatient Surgery / Procedural Areas
- Expected-charge logic must trace to documented performed activity or explicit upstream activity signals, not orders alone.
- `claims_or_account_status` is the current workflow-state header.
- `exception_queue` is active current work only.
- `queue_history` is a transition-event ledger for active exception churn, not a one-row summary path.
- One current primary blocker remains mandatory.
- `corrections_rebills` and `denials_feedback` are implemented as thin support layers, not standalone workflow products.

## Current Processed Artifacts

### Source-like synthetic inputs

These tables are generated to resemble the facts the deterministic engine needs:

- `encounters.parquet`
  - Grain: one encounter or procedural case instance
  - Role: scope, department, service timing, encounter status
- `orders.parquet`
  - Grain: one order or scheduled service instance
  - Role: supporting context only; not sufficient on its own for expected-charge logic
- `documentation_events.parquet`
  - Grain: one documentation milestone or evidence event
  - Role: support completeness, missing support, timing lag, signature/state logic
- `upstream_activity_signals.parquet`
  - Grain: one performed-activity or expectation-supporting signal
  - Role: performed-activity anchor for expected-charge logic
- `charge_events.parquet`
  - Grain: one posted, adjusted, or voided facility charge event
  - Role: charge presence, charge timing, unsupported-charge checks
- `claim_lines.parquet`
  - Grain: one prebill or billed claim-line representation
  - Role: modifier, edit, and financial-line context
- `edits_bill_holds.parquet`
  - Grain: one edit or bill-hold instance
  - Role: prebill edit / hold realism and line-level blocker support

### Current workflow-state header

- `claims_or_account_status.parquet`
  - Grain: one current header row per encounter or account unit
  - Primary role: authoritative current stage, current primary blocker, current queue, aging, and recoverability status
  - Important fields:
    - `current_prebill_stage`
    - `current_primary_blocker_state`
    - `current_primary_blocker_code`
    - `current_queue`
    - `stage_age_days`
    - `recoverability_status`

This table is the single-current-state header that keeps the queue deterministic.

### Deterministic opportunity layer

- `expected_charge_opportunities.parquet`
  - Grain: one expected opportunity candidate tied to documented activity
  - Role: expected-charge support, missed-charge, unsupported-charge, modifier dependency, documentation dependency, and packaged / non-billable suppression logic
  - Important fields include expected opportunity target text, opportunity status, and why-not-billable explanation where relevant

### Active operational work

- `exception_queue.parquet`
  - Grain: one active routed work item per current blocker
  - Role: owner-routed active queue surface
  - Important fields:
    - `queue_item_id`
    - `encounter_id`
    - `department`
    - `service_line`
    - `current_prebill_stage`
    - `issue_domain`
    - `root_cause_mechanism`
    - `current_queue`
    - `accountable_owner`
    - `stage_age_days`
    - `sla_status`
    - `recoverability_status`
    - `why_not_billable_explanation`

`exception_queue` must carry at most one active item per encounter or account unit.

### Transition-event ledger

- `queue_history.parquet`
  - Grain: one routing or transition event
  - Role: handoff, reroute, and churn evidence for active work
  - Important fields:
    - `queue_history_id`
    - `encounter_id`
    - `transition_event_index`
    - `transition_event_type`
    - `prior_queue`
    - `current_queue`
    - `routing_reason`
    - `days_in_prior_queue`
    - `reroute_count`
    - `owner_handoff_flag`
    - `current_record_flag`

This is now a true transition ledger for active work. Some cases have one clean route; others show multi-hop routing.

### Follow-through support

- `intervention_tracking.parquet`
  - Grain: one current intervention-support row per active queue item
  - Role: Action Tracker follow-through evidence
  - Important fields:
    - `action_path`
    - `recurring_issue_pattern`
    - `intervention_owner`
    - `target_completion_date`
    - `checkpoint_status`
    - `baseline_metric_name`
    - `baseline_metric_value`
    - `current_metric_value`
    - `metric_delta`
    - `correction_turnaround_signal`
    - `before_after_validation_note`
    - `hold_expand_revise_recommendation`

This is intentionally thin operational support. It is not a task timeline or ticketing engine.

### KPI and ranking layer

- `priority_scores.parquet`
  - Grain: one active queue item
  - Role: transparent reduced V1 priority rank output
- `kpi_snapshot.parquet`
  - Grain: one KPI record or one priority-score record
  - Role: published KPI evidence for all-scope and department-specific views

Current published KPI rows include:

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
- Transparent reduced V1 priority score

### Reviewer-support artifacts in processed data

- `manual_audit_sample.csv`
  - Grain: one curated review case
  - Role: reviewer-facing audit sample with upstream evidence, expected opportunity, blocker, queue, recoverability, and queue-history summary

## Thin Current Support Layers

### corrections_rebills.parquet

- Current status: implemented, intentionally thin
- Grain: one correction or rebill support row
- Role: post-bill recoverable follow-through, correction type, outcome status, reason, turnaround support
- Important rule: this supports the control-room story for post-bill recovery but does not make the repo a full rebill workflow platform

### denials_feedback.parquet

- Current status: implemented, intentionally thin
- Grain: one downstream denial-feedback signal row
- Role: correlation signal back to upstream issue domains and closed/compliance-relevant monitoring
- Important rule: this is evidence-only downstream signal support, not a denials-management product center

## Reference Tables

The current deterministic engine is governed by reference tables under `data/reference/`, especially:

- `department_charge_logic_map.csv`
- `queue_definitions.csv`
- `stage_aging_rules.csv`
- `recoverability_rules.csv`
- `issue_domain_map.csv`
- `root_cause_map.csv`

These references drive department-specific charging logic, queue routing, aging, and recoverability interpretation.

## Current Join Spine

The practical join model is:

1. `encounter_id` is the main cross-table spine.
2. `claims_or_account_status` expresses the one current workflow header for that encounter or account unit.
3. `expected_charge_opportunities` joins documented activity, support state, and charge reality to derive expected outcomes.
4. `exception_queue` publishes the single active routed work item driven by the current blocker.
5. `queue_history` records the transition events behind that active work.
6. `intervention_tracking` joins back to `queue_item_id` to add follow-through evidence.
7. `priority_scores` and `kpi_snapshot` summarize queue exposure, performance, and ranking.
8. `corrections_rebills` and `denials_feedback` add narrow downstream context where applicable.

## One-Current-Blocker Rule

The data model preserves this operating rule:

- many issue tags can exist below the surface
- one current primary blocker must drive active work
- `claims_or_account_status` holds the current blocker header
- `exception_queue` holds at most one active queue item for that current blocker
- `queue_history` explains how the current state was reached

## What The Model Does Not Claim

- It is not a production warehouse schema.
- It is not a full closed-item enterprise workflow ledger.
- It is not a denials, appeals, or payer adjudication model.
- It is not a predictive data model.

## Bottom Line

The implemented V1 data model is already sufficient to support deterministic expected-charge logic, active owner-routed queueing, transition-event churn visibility, Action Tracker follow-through, thin correction and denial signals, KPI publication, and reviewer audit artifacts for the frozen outpatient facility-side scope.
