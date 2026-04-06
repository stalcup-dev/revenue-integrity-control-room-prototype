# Reviewer Proof Pack

Date: 2026-03-30

## Purpose

This pack translates the current implemented product into a compact public proof map: what the product is, what it is not, which claims are backed by artifacts, and where the caveats are.

## What the product is

The current product is a hospital-informed, facility-side, outpatient-first revenue integrity control-room prototype built around deterministic failed-control detection. It maps documented performed activity to expected facility charge opportunities, separates issue domain from root cause, enforces one current blocker, routes work to accountable owners, frames recoverable versus already-lost exposure, and includes thin follow-through, what-if, and downstream signal layers that stay secondary to the control core.

Current implemented surfaces:

- Control Room Summary
- Charge Reconciliation Monitor
- Modifiers / Edits / Prebill Holds
- Documentation Support Exceptions
- Opportunity & Action Tracker
- Scenario Lab v0
- Denial Feedback + CDM Governance Monitor
- Revenue Integrity Decision Pack trigger on Control Room Summary

## What the product is not

- Not a denials-management platform
- Not professional fee analytics
- Not a payer adjudication engine
- Not a predictive-first triage product
- Not a generic healthcare BI dashboard
- Not a production-integrated hospital deployment
- Not a full task-management or workflow-engine platform

Denials remain downstream evidence only. Predictive logic stays secondary and is not required for the current product to function.

## One-sentence portfolio pitch

Built a deterministic facility-side outpatient revenue integrity control-room prototype that ties documented performed activity to expected facility charge opportunity, routes the current failed control to the right owner, separates recoverable from lost exposure, and packages operating proof into reviewer-ready artifacts.

## Current implemented capability map

### Deterministic control layer

- Expected-charge derivation from documented performed activity and governed department rules
- One-current-blocker enforcement
- Stage-specific aging and recoverability
- Issue-domain versus root-cause separation
- Owner-routed active exception queue
- Queue-history transition ledger with reroutes and prior-queue aging

### Operational review layer

- Control Room Summary for backlog, recoverability, and owner pressure
- Queue-specific monitors for reconciliation, documentation, coding/edit, and prebill hold work
- Opportunity & Action Tracker with intervention owner, checkpoint status, baseline/current metric, and hold/expand/revise recommendation

### Thin extension layers

- Scenario Lab v0 as a secondary thin what-if surface with explicit operational levers, caps, and what-if outputs
- Denial Feedback + CDM Governance Monitor as a secondary downstream signal monitor with downstream-to-upstream linkage
- Revenue Integrity Decision Pack as a short memo artifact generated from current governed outputs

### Reviewer evidence layer

- Manual audit sample and rubric
- Browser audit screenshots and notes
- Queue governance browser audit
- Action Tracker follow-through proof
- Scenario Lab audit
- Denial/CDM monitor audit
- Decision Pack audit
- Realism scorecards and department-story reports

## Reviewer question -> proof map

| Reviewer question | Current proof |
| --- | --- |
| Does this feel like a hospital facility-side control room? | Start with [artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md](../reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md), then use [artifacts/realism/post_tuning_realism_report.md](../realism/post_tuning_realism_report.md) and [artifacts/queue_governance_browser_audit.md](../queue_governance_browser_audit.md) to show stage, blocker, owner, SLA, recoverability, and queue realism in the current synthetic/public-safe prototype. |
| Does each exception map to a believable failed control? | Case-detail surfaces and the queue-governance audit show expected opportunity, current blocker, routing context, and one-current-blocker logic instead of a generic leakage blob. |
| Are issue domain and root cause clearly separated? | Action Tracker selected case and Denial/CDM monitor explicitly show issue domain separately from root cause mechanism and owner/action hint. |
| Is ownership clear? | Current queue, accountable owner, supporting/escalation ownership, and queue-governance definitions are visible in the selected-case evidence trace and summary work surfaces. |
| Are recoverability and aging believable? | Control Room Summary, KPI snapshot, queue-governance audit, and realism report all show stage-specific aging plus recoverability states of pre-final-bill recoverable, correction-path recoverable, already lost, and compliance-relevant closed. |
| Would a real RI or billing leader use this queue? | Owner-routed queue mix, current blocker logic, SLA pressure, and recommended next action are visible in Control Room Summary and Opportunity & Action Tracker. |
| Do the service-line stories feel authentic? | [artifacts/realism/post_tuning_realism_report.md](../realism/post_tuning_realism_report.md), [artifacts/realism/department_story_report.md](../realism/department_story_report.md), and [docs/MANUAL_AUDIT_SAMPLE.md](../../docs/MANUAL_AUDIT_SAMPLE.md) show distinct infusion, radiology/IR, and OR/procedural patterns. |
| Do the scenario levers feel operationally real enough to review? | [artifacts/scenario_lab_v0_audit.md](../scenario_lab_v0_audit.md) shows prebill edit clearance, correction turnaround, and routing speed to owner teams, plus visible formulas and caps on a thin secondary what-if page. |
| Is predictive modeling staying in its lane? | The current product center is deterministic. Scenario output is transparent what-if only, and denials remain downstream-only signal visibility. No predictive triage is required logic. |
| What would make this feel fake? | Order-only expected logic, blurred issue versus root cause, flat service-line behavior, generic leakage totals, denials taking over scope, and hidden scenario math. Current realism and audit artifacts exist specifically to show those anti-patterns are being avoided. |

## Success-definition alignment

| Success definition | Current implemented alignment |
| --- | --- |
| Facility-side hospital-informed realism | The app and realism artifacts stay facility-side, outpatient-first, and queue-driven rather than generic rev-cycle BI. |
| Believable charge reconciliation controls | Charge Reconciliation Monitor plus current workflow-state header and queue-routing logic show reconciliation as an operating control, not a passive KPI. |
| Department-specific performed-activity -> expected-charge logic | Department-story realism artifacts and manual-audit sample show distinct infusion, radiology/IR, and OR/procedural rules. |
| Prebill exception management logic | Current queue structure, one-current-blocker enforcement, aging, SLA, and owner routing support a believable prebill control room. |
| Clear ownership routing | Accountable owner plus supporting/escalation ownership are visible in Action Tracker case detail and queue-governance proof. |
| Recoverable vs lost framing | Control Room Summary and Decision Pack explicitly show recoverable-now versus already-lost exposure. |
| Visible packaged / integral / false-positive suppression logic | Suppression logic appears in realism evidence, manual audit, and case-detail views rather than being hidden. |
| Operational prioritization | Priority ranking and owner-routed work surfaces exist without requiring predictive scoring. |
| Realistic scenario planning | Scenario Lab v0 is intentionally thin, operationally grounded enough for reviewer credibility, formula-visible, and capped. |
| Predictive triage secondary, not central | Predictive logic is not required for current value; deterministic control specificity remains the credibility engine. |

## Honest limitations / caveats

- Synthetic/public-safe only; no PHI and no real hospital source integration
- Outpatient-first and facility-side only; not a broad enterprise rev-cycle platform
- Denials remain downstream-only evidence, not a workqueue or appeals product center
- Scenario Lab is v0 what-if logic, not forecasting or optimization
- Current intervention follow-through is believable but intentionally thinner than a full task-management platform
- Current scale proves coherence, realism discipline, and reviewer trust, not production readiness or enterprise-natural source fidelity
- Some archived planning docs reflect earlier sequencing; the implemented product now includes thin scenario, denial, and decision-pack surfaces that should still be presented as narrow extensions, not as full new product centers

## Bottom line

This product holds up best when it is presented honestly: deterministic control-room core first, reviewer evidence second, thin extensions last, and limitations stated directly.
