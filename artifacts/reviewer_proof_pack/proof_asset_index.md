# Proof Asset Index

| Asset | What it proves | Where to use it in the demo | Proof type |
| --- | --- | --- | --- |
| [artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md](../reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md) | One deterministic operating story holds together from summary surface to opened proof to exported memo. | Use first in the demo or as the first public proof artifact. | Narrative proof |
| [artifacts/decision_pack/revenue_integrity_decision_pack.md](../decision_pack/revenue_integrity_decision_pack.md) | The same current control story survives into a clean exported memo. | Use immediately after the walkthrough. | Export proof |
| [artifacts/realism/post_tuning_realism_report.md](../realism/post_tuning_realism_report.md) | Current shipped realism state. The dataset passes workflow, recoverability, queue-history, department-story, suppression, ops-mix, payable-signal, and intervention-follow-through realism checks. | Use first when a reviewer asks, "Why should I trust the synthetic realism?" | Test proof |
| [artifacts/realism/realism_before_after_diff.md](../realism/realism_before_after_diff.md) | Before/after remediation proof. It shows exactly how the historical realism dents were removed. | Use after the current report if a reviewer asks what changed. | Test proof |
| [tests/test_case_detail_payload.py](../../tests/test_case_detail_payload.py) | Business-facing assertions prove case detail, blocker logic, routing history, suppression context, and correction follow-through are enforced in code. | Use as the first code-backed credibility cue. | Test proof |
| [artifacts/queue_governance_browser_audit.md](../queue_governance_browser_audit.md) | Current queue, blocker, ownership, SLA, recoverability, and queue-governance context are visibly present on working app surfaces. | Use when showing one-current-blocker, aging, and ownership. | Browser proof |
| [artifacts/browser_audit/action_tracker_follow_through.md](../browser_audit/action_tracker_follow_through.md) | Action Tracker follow-through is not static text; it shows baseline/current metric movement, downstream outcome signal, and recommendation. | Use during the intervention follow-through step. | Browser proof |
| [artifacts/scenario_lab_v0_audit.md](../scenario_lab_v0_audit.md) | Scenario Lab v0 uses operational levers, visible formulas, and caps tied to current governed data sources. | Use only after the core control-room proof path is established. | Narrative proof |
| [artifacts/denial_feedback_cdm_monitor_audit.md](../denial_feedback_cdm_monitor_audit.md) | Denials remain downstream-only evidence while still linking back to upstream issue domain, root cause, and owner/action path. | Use only after the core control-room proof path is established. | Narrative proof |
| [docs/MANUAL_AUDIT_SAMPLE.md](../../docs/MANUAL_AUDIT_SAMPLE.md) | Individual cases remain traceable from performed activity through expected opportunity, billed state, queue owner, recoverability, and audit focus. | Use if a reviewer wants a paper-trail example after the walkthrough. | Narrative proof |

## Recommended proof order

1. Start with the walkthrough.
2. Open the exported Decision Pack.
3. Use the current shipped realism report, then the before/after diff if needed.
4. Use `test_case_detail_payload.py` as the first code-backed credibility cue.
5. Use queue-governance, Action Tracker, Scenario Lab, and Denial/CDM artifacts only as supporting proof after the core path is clear.
