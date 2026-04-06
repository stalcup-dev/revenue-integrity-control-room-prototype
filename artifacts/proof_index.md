# Proof Index

## Fastest Public Path

If a recruiter or hiring manager opens only four links after the root README, use this order:

1. [Reviewer walkthrough](./reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md)
2. [Decision Pack export](./decision_pack/revenue_integrity_decision_pack.md)
3. [Current shipped realism state](./realism/post_tuning_realism_report.md)
4. [Test-backed credibility cue](../tests/test_case_detail_payload.py)

## Realism Evidence Chain

- Current shipped realism state: [artifacts/realism/post_tuning_realism_report.md](./realism/post_tuning_realism_report.md)
- Before/after remediation proof: [artifacts/realism/realism_before_after_diff.md](./realism/realism_before_after_diff.md)
- Historical baseline: archived comparison context only. Use the diff first; the baseline report is not the recommended public entry point.

## Core Proof

| Artifact | Why open it first |
| --- | --- |
| [artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md](./reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md) | Strongest first proof. It shows one deterministic operating story from summary to opened proof to export. |
| [artifacts/decision_pack/revenue_integrity_decision_pack.md](./decision_pack/revenue_integrity_decision_pack.md) | Shows the product can package the same current control story into an exported memo. |
| [artifacts/realism/post_tuning_realism_report.md](./realism/post_tuning_realism_report.md) | Authoritative current realism artifact for workflow aging, routing history, recoverability, financial consequence, and correction support. |
| [artifacts/realism/realism_before_after_diff.md](./realism/realism_before_after_diff.md) | Short bridge proving the realism dents were remediated rather than hand-waved away. |
| [tests/test_case_detail_payload.py](../tests/test_case_detail_payload.py) | Best first code-level credibility cue because the assertions read like product behavior, not low-level plumbing. |

## Supporting Proof

| Artifact | What it adds |
| --- | --- |
| [artifacts/queue_governance_browser_audit.md](./queue_governance_browser_audit.md) | Browser-visible queue, blocker, owner, SLA, recoverability, and selected-case governance proof. |
| [artifacts/browser_audit/action_tracker_follow_through.md](./browser_audit/action_tracker_follow_through.md) | Action Tracker follow-through is evidence-backed rather than static text. |
| [artifacts/documentation_trend_realism/filter_state_validation.md](./documentation_trend_realism/filter_state_validation.md) | Documentation Support Exceptions behaves like a believable filtered backlog, not a fixed chart. |
| [artifacts/reconciliation_realism/reconciliation_scope_validation.md](./reconciliation_realism/reconciliation_scope_validation.md) | Charge Reconciliation Monitor behaves believably in broad and filtered slices. |
| [artifacts/scenario_lab_v0_audit.md](./scenario_lab_v0_audit.md) | Scenario Lab stays thin, deterministic, capped, and secondary to the control-room core. |
| [artifacts/success_definition_checklist.md](./success_definition_checklist.md) | Maps public claims to proof artifacts and caveats. |

## Read Order

1. Start with the walkthrough.
2. Check the Decision Pack export.
3. Use the current realism report.
4. Use the realism diff only if someone asks what changed.
5. Use the test file when you want one strong engineering-backed credibility cue without reading the full codebase.
