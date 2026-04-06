# Reviewer Scorecard

## 1. Revenue Integrity / Charge Capture leader

### What they care about

- Whether this feels like a real facility-side control room instead of generic leakage BI
- Whether expected-charge logic is grounded in documented performed activity
- Whether failed controls map cleanly to owner-routed queues and recoverability
- Whether scenario levers reflect real operating actions rather than finance theater

### Strongest pages / artifacts

- `Control Room Summary`
- `Charge Reconciliation Monitor`
- `Opportunity & Action Tracker`
- `artifacts/realism/post_tuning_realism_report.md`
- `artifacts/queue_governance_browser_audit.md`
- `artifacts/scenario_lab_v0_audit.md`

### Top 3 likely objections

1. "This could still be a polished demo rather than a real hospital control environment."
2. "Expected opportunity logic may be too synthetic to trust."
3. "Scenario outputs can drift into unrealistic dollar claims."

### Honest rebuttal / caveat

The strongest answer is the combination of queue-governance proof, department-story realism, manual-audit evidence, and visible scenario formulas. The honest caveat is that this is still synthetic/public-safe evidence, so it proves realism posture and control thinking, not production source fidelity.

## 2. PFS / Billing Operations leader

### What they care about

- Whether prebill queues, aging, and ownership are believable
- Whether rebill/correction paths are handled without pretending to be a full claims platform
- Whether the queue surfaces would actually help an operations leader work backlog
- Whether recoverable versus already-lost framing is operationally useful

### Strongest pages / artifacts

- `Control Room Summary`
- `Modifiers / Edits / Prebill Holds`
- `Opportunity & Action Tracker`
- `artifacts/browser_audit/action_tracker_follow_through.md`
- `artifacts/queue_governance_browser_audit.md`
- `artifacts/decision_pack/revenue_integrity_decision_pack_audit.md`

### Top 3 likely objections

1. "I need to see one current blocker and one current owner, not blended statuses."
2. "Correction/rebill support may be too thin for real billing operations."
3. "The memo layer could hide the actual queue logic."

### Honest rebuttal / caveat

The current product does show one current blocker, stage-specific aging, accountable ownership, and thin correction-path support. The caveat is that `corrections_rebills` remains a narrow support layer, not a full rebill orchestration platform, and the Decision Pack should be presented as a summary artifact built from the queue logic, not as a replacement for the queue.

## 3. Coding / CDI / Clinical Operations SME

### What they care about

- Whether issue domain and root cause stay cleanly separated
- Whether documentation, coding, and workflow failures are distinct instead of blurred
- Whether service-line stories feel authentic across infusion, radiology/IR, and OR/procedural work
- Whether packaged/integral/non-billable suppression is handled honestly

### Strongest pages / artifacts

- `Documentation Support Exceptions`
- `Opportunity & Action Tracker` selected case evidence trace
- `Denial Feedback + CDM Governance Monitor`
- `docs/MANUAL_AUDIT_SAMPLE.md`
- `artifacts/realism/department_story_report.md`
- `artifacts/denial_feedback_cdm_monitor_audit.md`

### Top 3 likely objections

1. "Coding, documentation, and billing problems often get blurred in synthetic demos."
2. "Radiology/IR and OR/procedural stories can feel fake if they all fail the same way."
3. "Suppression logic is often invisible, so misses look overstated."

### Honest rebuttal / caveat

The current best proof is the department-story realism report, manual audit sample, and selected-case classification/governance surfaces. The caveat is that this is still a frozen three-department outpatient-first story set, so it is intentionally narrower than a full hospital coding/CDI platform.

## Overall reviewer posture

- Best-case reaction: "This is a believable deterministic control-room prototype with honest thin extensions."
- Most likely shared concern: "How much of this realism survives beyond synthetic data?"
- Correct answer: "The repo proves control specificity, reviewer traceability, and realism discipline now; production integration and broader workflow depth remain later work."
