# Reviewer Verdict Matrix

| Domain | SoT expectation | Current evidence | Verdict | Risk if challenged | Recommended response |
| --- | --- | --- | --- | --- | --- |
| Facility-side realism | Must feel like a hospital facility-side control room, not generic BI. | Control Room Summary, Opportunity & Action Tracker, queue governance browser audit, realism reports | Pass | Medium | Lead with current blocker, owner queue, SLA, recoverability, and routing history before any portfolio pitch language. |
| Outpatient-first scope discipline | Stay outpatient-first and facility-side only. | Reviewer proof pack, README, department stories, denial guardrails | Pass | Low | Say explicitly that the repo is frozen to three outpatient facility-side anchor stories. |
| Deterministic control credibility | Deterministic logic must carry the product before any advanced layer. | Expected-vs-actual trace, manual audit sample, reviewer proof pack | Pass | Medium | Show one case trace from documented performed activity to blocker before showing Scenario Lab or memo artifacts. |
| One-current-blocker / queue realism | One current blocker, one current queue, governed queue definitions, stage-specific logic. | Queue governance browser audit, selected case evidence trace, realism report | Pass | Medium | Use the selected case to show blocker, queue, aging basis, SLA target, and routing history together. |
| Recoverability realism | Recoverability must be operationally defined, not vaguely inferred. | Control Room Summary, realism report, manual audit sample | Pass | Medium | Frame recoverability as governed current-state logic, not as universal financial truth. |
| Ownership / routing realism | Accountable ownership, supporting/escalation roles, and routing logic must be visible. | Queue governance proof, routing history, Action Tracker | Pass | Medium | Call out accountable/supporting/escalation owners explicitly; do not assume reviewers notice the distinction. |
| Issue-domain vs root-cause separation | Issue domain and root cause must stay separate. | Selected case classification, Denial/CDM linkage, reviewer proof pack | Borderline | Medium-high | Narrate issue domain and root cause separately during the demo; otherwise reviewers may collapse them mentally. |
| Expected-charge from documented performed activity | Expected charge must come from documented performed activity, not orders alone. | Expected-vs-actual trace, manual audit sample, department-story realism | Pass | High | Use one concrete case. This is too important to answer with summary claims. |
| Packaged / false-positive suppression | Performed does not always mean billable; suppressed cases must stay visible. | Manual audit sample, suppression realism sections, selected case suppression note | Borderline | Medium-high | Show one suppressed case directly so the reviewer sees that the model does not inflate leakage. |
| Intervention follow-through | Follow-through must look evidence-driven, not static. | Action Tracker follow-through proof, intervention-tracking artifacts, Decision Pack | Pass | Medium | Use the current monitored metric plus downstream outcome signal, and note that hold/revise/expand all exist. |
| Scenario realism | Scenario levers must be operationally believable, transparent, and auditable. | Scenario Lab v0 audit, live screenshots, reviewer proof pack | Borderline | High | Present Scenario Lab as a thin, caveated extension with explicit formulas and caps. |
| Denials staying downstream-only | Denials may exist only as downstream evidence, not as the product center. | Denial/CDM audit, reviewer proof pack, proof asset index | Pass | Medium | Keep the denial page brief and late in the demo. |
| Predictive staying secondary | Predictive logic must remain optional/secondary. | Reviewer proof pack, README scope, lack of predictive-first workflow | Pass | Low | Say clearly that deterministic control specificity, not predictive sophistication, is the current credibility engine. |

## Read-through

- Strongest current verdicts: facility-side realism, deterministic control credibility, one-current-blocker / queue realism, ownership / routing realism, predictive staying secondary
- Most challenge-prone domains: issue-domain versus root-cause separation in live narration, packaged suppression visibility, scenario realism
- Main non-product risk: supporting artifacts can still sound cleaner and more resolved than a skeptical reviewer will accept
