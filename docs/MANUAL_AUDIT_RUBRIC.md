# Manual Audit Rubric

Date: 2026-03-26

Use this rubric with `data/processed/manual_audit_sample.csv` and `docs/MANUAL_AUDIT_SAMPLE.md`.

## Review Purpose

- Prove the deterministic V1 queue reflects hospital-native facility-side charge integrity logic.
- Confirm expected opportunities are grounded in documented performed activity, not order-only assumptions.
- Confirm current queue, queue-history ledger, and Action Tracker follow-through are understandable from exported evidence.
- Catch false positives before presenting the repo as believable V1.

## Required Reviewer Questions For Every Case

1. Did documented performed activity occur, or is this only an order-level expectation?
2. Does the documentation evidence support a separately billable opportunity, a missing-support problem, or a packaged / non-billable outcome?
3. Does the billed state match the expected opportunity and current blocker story?
4. Is the exception classification believable for the department and service-line workflow?
5. Is the current owner queue the right operational destination?
6. Is the recoverability framing believable for the current timing window and stage?
7. If the case rerouted, does the `queue_history` path look like a believable handoff chain rather than random churn?
8. If the case is active in the Action Tracker, do the intervention checkpoint and recommendation fields fit the queue context and repeat-pattern story?

## Allowed Primary Audit Outcomes

- `Clean / no active exception`
- `Recoverable missed charge`
- `Documentation support failure`
- `Coding or modifier dependency`
- `Prebill edit or hold`
- `Correction or rebill follow-through`
- `Packaged / not separately billable`
- `False positive expectation ruled out`

Pick one primary outcome per case. If a case seems to fit two outcomes, document which blocker should be current now and why.

## What The Reviewer Should Inspect

- `upstream_activity`
- `documentation_evidence`
- `expected_opportunity`
- `billed_state`
- `exception_classification`
- `owner_queue`
- `recoverability`
- `queue_history`

For active Action Tracker cases, also inspect:

- recurring issue pattern
- intervention owner
- checkpoint status
- baseline/current metric summary
- correction turnaround note if present
- hold / expand / revise recommendation

## Mandatory Failure Patterns To Flag

- order-only expectation with no documented performed activity
- packaged or integral case treated as leakage
- more than one current blocker visible for the same active unit
- vague or implausible reroute history
- missing or generic routing reason where reroute evidence exists
- missing why-not-billable explanation on non-billable or suppressed cases
- intervention follow-through fields that look disconnected from the queue or issue pattern

## Evidence Standard

- A reviewer should be able to justify the final audit outcome from exported columns and artifacts alone.
- If the exported sample cannot explain the case without hidden logic, V1 is not yet believable.
- If queue-history churn or Action Tracker follow-through cannot be defended from the sample and supporting artifacts, stop and fix the deterministic rules before more polish.
