# Source System Mapping Contract

Date: 2026-03-26

## Purpose

This document explains how the current synthetic V1 artifacts would map to likely real hospital source domains later. It is a bridge document for realism and warehouse planning. It is not a production ingestion spec.

## Scope And Guardrails

- Facility-side only
- Outpatient-first
- Deterministic-first
- Expected-charge logic anchored to documented performed activity, not orders alone
- `exception_queue`, `queue_history`, `intervention_tracking`, `priority_scores`, and `kpi_snapshot` remain derived operating tables rather than raw source extracts
- `denials_feedback` remains a thin downstream signal layer, not a denials platform commitment

## Core Mapping Principles

- Use `encounter_id` and `account_id` as the main cross-system spine wherever possible.
- Preserve encounter-level context even when downstream billing sources are claim- or line-based.
- Keep one current workflow-state header in `claims_or_account_status`.
- Keep one current active blocker in `exception_queue`.
- Preserve timestamps needed to explain operational control, not just financial posting.
- Prefer retaining raw evidence and resolving conflicts in warehouse logic rather than overwriting source ambiguity.

## Current Artifact To Likely Source Mapping

### encounters

- Likely source domains:
  - ADT or encounter header extract
  - outpatient scheduling / registration feed
  - facility account header
- Current role in repo:
  - department scope, encounter timing, status, and encounter spine

### orders

- Likely source domains:
  - EHR orders
  - radiology accessioning
  - infusion treatment-plan or schedule feeds
  - procedural order systems
- Current role in repo:
  - supporting context only; not authoritative expected-charge evidence by itself

### documentation_events

- Likely source domains:
  - nursing documentation milestones
  - procedure note status
  - imaging completion documentation
  - infusion administration documentation
- Current role in repo:
  - support completeness, missing-support, and timing evidence

### upstream_activity_signals

- Likely source domains:
  - MAR administration records
  - imaging completion feeds
  - OR / procedure logs
  - implant, device, or supply usage feeds
- Current role in repo:
  - primary performed-activity basis for expected-charge logic

### charge_events

- Likely source domains:
  - hospital charge transaction detail
  - charge router or charge review worklists
  - patient accounting transaction feeds
- Current role in repo:
  - posted, adjusted, and voided facility charge evidence

### claim_lines

- Likely source domains:
  - claim staging tables
  - scrubber output
  - patient accounting billed-line extracts
- Current role in repo:
  - modifier, edit, and financial-line context

### edits_bill_holds

- Likely source domains:
  - scrubber edit tables
  - DNB / bill-hold worklists
  - billing workqueue extracts
- Current role in repo:
  - prebill hold and modifier / edit realism

### claims_or_account_status

- Likely source domains:
  - patient accounting account header
  - claim-status extracts
  - bill-hold status
  - warehouse-derived current-state logic
- Current role in repo:
  - current stage, current blocker, aging, recoverability, and current queue header

### expected_charge_opportunities

- Likely source domains:
  - warehouse-derived deterministic table built from performed activity, documentation support, and charge reality
- Current role in repo:
  - expected opportunity, support, suppression, and leakage logic

### exception_queue

- Likely source domains:
  - warehouse-derived active operating table
- Current role in repo:
  - one active routed work item per current blocker

### queue_history

- Likely source domains:
  - warehouse-derived transition ledger built from current-state snapshots, queue logic, and any available workqueue history
- Current role in repo:
  - transition-event evidence for reroutes, handoffs, routing reasons, and prior-queue aging

### intervention_tracking

- Likely source domains:
  - warehouse-derived intervention support table
  - optional future joins to improvement logs, owner worklists, or QA follow-up notes
- Current role in repo:
  - thin Action Tracker follow-through support, not a task-management system

### corrections_rebills

- Likely source domains:
  - correction worklists
  - rebill status extracts
  - replacement-claim or account-adjustment support tables
- Current role in repo:
  - thin post-bill recoverable follow-through support

### denials_feedback

- Likely source domains:
  - denial reason extracts
  - remit / follow-up analytics
  - warehouse correlation tables
- Current role in repo:
  - downstream signal layer only

### kpi_snapshot and priority_scores

- Likely source domains:
  - warehouse-derived publication tables built from the operational layers above
- Current role in repo:
  - governed KPI publication and transparent active-work ranking

## Warehouse Readiness Expectations

- Preserve source identifiers alongside standardized encounter/account keys.
- Keep enough raw evidence to explain why a case became actionable, suppressed, rerouted, corrected, or closed.
- Version any rules that change expected-charge derivation, suppression logic, blocker priority, queue routing, or recoverability windows.
- Preserve transition-event evidence if the real environment has queue snapshots or workqueue history.
- Keep downstream denial correlation separate from the main pre-loss control workflow.

## What This Contract Does Not Do

- It does not implement production ingestion.
- It does not guarantee source availability at any specific hospital.
- It does not define a full warehouse model.
- It does not turn V1 into a denials, appeals, or payer platform.

## Bottom Line

The current synthetic V1 artifacts map conceptually to likely hospital source domains, but they should still be read as a warehouse-planning bridge rather than source-realistic operating proof. The main next step later is source-backed lineage and warehouse implementation, not inventing a different product story.
