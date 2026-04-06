# Synthetic Data Rules

Date: 2026-03-26

## Purpose

This document defines how the current synthetic data should behave so the repo feels like a believable hospital-native control program rather than a random demo dataset.

The rules below reflect the current implemented realism posture, including the completed workflow, department, suppression, medium-volume ops, payable-signal, transition-ledger, and intervention-follow-through slices.

## Core Realism Rules

- Preserve operational logic before visual variety.
- Anchor expected-charge logic to documented performed activity or explicit upstream signals, not orders alone.
- Keep department behavior distinct across infusion, radiology / IR, and OR / procedural areas.
- Do not assume every performed activity becomes separately billable.
- Do not assume every billed line is separately payable.
- Keep one current primary blocker per active encounter or account unit.
- Keep stage-specific aging and recoverability intact.
- Make queue history behave like a believable transition-event ledger, not a one-row summary path.
- Make Action Tracker follow-through fields look evidence-driven, not static.
- Keep denials feedback downstream and thin.

## Current Generation Flow

The synthetic build should follow this order:

1. generate encounter, order, documentation, and upstream activity evidence
2. derive expected charge opportunities from performed activity plus governed department rules
3. generate charge, claim-line, and edit / hold context
4. build the workflow-state header with one current blocker
5. route active work into the exception queue
6. create transition-event queue history for believable handoffs and churn
7. create thin intervention-tracking support for Action Tracker follow-through
8. derive KPI, priority-score, manual-audit, realism, and evidence artifacts

## Global Generation Rules

- Generate data only for the frozen V1 departments.
- Include clean, suppressed, recoverable, correction-path, and already-lost stories.
- Include multiple internal issues on some cases, but publish only one current blocker into the active queue.
- Use non-uniform failure clusters rather than flat random percentages.
- Keep OR / procedural workflows more handoff-heavy than simpler ambulatory patterns where appropriate.
- Preserve believable timing friction between performed activity, documentation, charge posting, edits, reroutes, and intervention checkpoints.

## Department-Specific Rules

### Outpatient Infusion / Oncology Infusion

- Timed administration logic, sequencing, hydration conditionality, waste, and separate-access realism must remain visible.
- Missing stop time, undocumented waste, and hierarchy confusion should create believable support or coding stories.
- Hydration and access work must sometimes suppress to non-billable or integral outcomes rather than always becoming misses.

### Radiology / Interventional Radiology

- Completed versus incomplete study state must remain decisive.
- Laterality, distinctness, contrast, and device linkage must create believable documentation or coding dependencies where relevant.
- Interventional radiology should show longer-tail documentation and linkage friction than straightforward imaging.

### OR / Hospital Outpatient Surgery / Procedural Areas

- Case state, discontinued-procedure logic, implant/supply linkage, and timestamp dependency must remain central.
- OR / procedural stories should show more reroutes and handoffs than infusion or simple imaging where appropriate.
- Some supply or implant stories must suppress because the item is integral or packaged rather than separately billable.

## Suppression And Payable-Signal Rules

- Packaged and non-billable suppressions must exist in every department where apparent misses could otherwise be overstated.
- Suppressed cases should stay visible in source-like and reviewer artifacts so the repo can prove why they were not routed.
- Paid-versus-payable ambiguity may appear only as a thin signal layer. It must not take over the product scope or make the repo read like a denials platform.

## Queue And Churn Rules

### Active queue

- Some cases should resolve on a clean single route.
- Some cases should bounce once.
- Some cases should show multi-hop reroutes with believable ownership changes.
- Routing should remain stage-driven, not random owner switching.

### queue_history

Current queue-history realism must support:

- multiple transition rows per active case where appropriate
- prior_queue -> current_queue visibility
- routing_reason coverage
- days_in_prior_queue variation
- reroute counts of `0`, `1`, `2`, and `3+`
- service-line-aware churn patterns

Believable examples include:

- `Charge Reconciliation Monitor -> Documentation Support Exceptions`
- `Documentation Support Exceptions -> Coding Pending Review`
- `Coding Pending Review -> Modifiers / Edits / Prebill Holds`
- `Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending`

## Intervention Follow-Through Rules

`intervention_tracking` should support believable combinations of:

- recurring issue pattern
- intervention owner
- target completion date
- checkpoint status
- baseline metric
- current metric
- correction turnaround signal
- before/after validation note
- hold / expand / revise recommendation

Generation rules:

- not every intervention should be in progress
- not every intervention should look successful
- `Hold`, `Expand`, and `Revise` must all exist
- checkpoint states must vary
- progress should connect to queue context and recurring issue pattern
- correction-turnaround signals should appear only where a billing-led correction story exists

## Anti-Patterns To Avoid

- order-only expectation with no documented performed activity
- one universal workflow story across all departments
- packaged cases leaking into active missed-charge queues
- queue history collapsing back to one-row summary behavior
- routing reasons missing or too generic
- random churn with no service-line pattern
- all interventions looking equally successful or equally stagnant
- denials feedback turning into the main product story

## Validation Expectations

Synthetic data is acceptable only when the repo can prove:

- deterministic exception logic still passes
- manual audit cases remain explainable from exported evidence
- realism scorecards pass
- transition-ledger evidence shows real event density and churn variety
- intervention follow-through evidence shows checkpoint and recommendation diversity
- browser-visible app behavior remains consistent with the exported data

## Bottom Line

The current synthetic dataset is expected to feel like a realistic outpatient facility-side operating prototype: department-specific, suppression-aware, queue-driven, handoff-aware, and follow-through-aware without drifting into predictive logic, denials operations, or a full workflow-engine design.
