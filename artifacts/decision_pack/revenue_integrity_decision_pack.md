# Revenue Integrity Decision Pack

- Build timestamp (UTC): 2026-03-31T16:08:02+00:00
- Validation status: Passed

## Executive summary

- Total open exceptions: 24
- Recoverable now vs already lost: $9,740 vs $3,630
- Exceptions breaching SLA: 17
- Top owner queue: Billing operations | Modifiers / Edits / Prebill Holds
- Top service line / department of concern: Outpatient Surgery | OR / Hospital Outpatient Surgery / Procedural Areas

## Top priority work queues

- #1 Modifiers / Edits / Prebill Holds | Billing / claim-edit failure | Billing operations
  SLA status: Overdue.
  Recoverability: Post-window financially lost.
  Dollars at risk / recoverable: $8,400 / $2,500.
  Recommended next step: Work assigned queue, clear hold, and confirm account release path.
- #2 Documentation Support Exceptions | Documentation support failure | Department operations
  SLA status: Overdue.
  Recoverability: Pre-final-bill recoverable.
  Dollars at risk / recoverable: $4,310 / $1,130.
  Recommended next step: Document coaching target and close documentation support gap.
- #3 Coding Pending Review | Coding failure | Coding team
  SLA status: Overdue.
  Recoverability: Pre-final-bill recoverable.
  Dollars at risk / recoverable: $2,710 / $2,710.
  Recommended next step: Route coding review and validate modifier or code alignment.

## Current control story

- Story path: Prebill edit resolution -> Billing / claim-edit failure from Workflow / handoff -> Prebill edit / hold | Prebill edit or hold unresolved | Modifiers / Edits / Prebill Holds -> Billing operations -> Post-window financially lost -> Work assigned queue, clear hold, and confirm account release path.
- Service line / department: Outpatient Surgery | OR / Hospital Outpatient Surgery / Procedural Areas
- Control failure type: Prebill edit resolution
- Issue domain: Billing / claim-edit failure
- Root cause mechanism: Workflow / handoff
- Exception pattern surfaced: 2 routed exceptions in Outpatient Surgery show Billing / claim-edit failure from Workflow / handoff. documented performed activity from documentation event supports Primary facility procedure charge for Completed outpatient procedure; actual charge state is posted held prebill.
- Where work is stuck now: Prebill edit / hold -> Prebill edit or hold unresolved -> Modifiers / Edits / Prebill Holds
- Who owns it now: Billing operations
- Aging / SLA: 7 days in stage (Days since edit or prebill hold opened); Overdue against 5-day threshold.
- Recoverability: Post-window financially lost
- Why it matters: 2 like-for-like accounts total $5,000 gross and sit in Post-window financially lost after 7 days in the current stage.
- Recommended next action: Work assigned queue, clear hold, and confirm account release path.

## Intervention update

- Intervention type: Billing / correction action
- Owner: Billing operations
- Baseline metric: Median handoff turnaround days: 8.8 days
- Current metric: Median handoff turnaround days: 9.3 days
- Downstream outcome signal: Modifiers / Edits / Prebill Holds: Overdue at 7 days aged.
- Hold / expand / revise recommendation: Hold

## Scenario snapshot

- Lever settings used:
  - Prebill edit clearance rate: 25.0% to 35.0%.
  - Correction turnaround days: 2.0 to 1.5.
  - Routing speed to owner teams: 1.7 to 1.2 days.
- Projected backlog reduction: 4
- Projected SLA improvement: +16.6 points
- Projected recoverable dollar lift: $2,464
- 90-day impact estimate: $7,392
- Note: Scenario snapshot uses the current Scenario Lab v0 default lever targets for the same filtered slice.

## Guardrails / caveats

- Facility-side only.
- Outpatient-first.
- Deterministic-first.
- Synthetic/public-safe data.
- Scenario results are what-if estimates, not forecasts.
- Denials are evidence-only, not the product center.
