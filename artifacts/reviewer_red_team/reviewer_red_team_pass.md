# Archived Skeptical Review Notes

Date: 2026-03-30

Historical review-prep archive only. This document is retained as background skepticism notes, not as part of the primary public proof path. Public readers should start with [`README.md`](../../README.md), [`artifacts/project_summary_and_scope.md`](../project_summary_and_scope.md), and [`artifacts/proof_index.md`](../proof_index.md).

## A. Review method

This red-team pass is grounded in the Source of Truth review-board structure, not in generic product critique.

Reviewer archetypes used:

- Revenue Integrity / Charge Capture leader
- PFS / Billing Operations leader
- Coding / CDI / Clinical Operations SME

Red-team rules used:

- Favor evidence over enthusiasm
- Penalize vague language
- Treat synthetic/public-safe constraints as real credibility limits
- Protect the SoT guardrails: facility-side only, outpatient-first, expected charge from documented performed activity, one-current-blocker, operational recoverability, stage-specific aging, denials downstream-only, predictive optional/secondary

## B. What was reviewed

Pages and artifacts reviewed:

- Control Room Summary
- Queue governance proof
- Opportunity & Action Tracker follow-through proof
- Scenario Lab v0
- Denial Feedback + CDM Governance Monitor
- Revenue Integrity Decision Pack
- Reviewer proof pack
- Demo script
- Reviewer scorecard
- Proof asset index
- Manual audit sample
- Realism scorecards and department-story reports

## C. Shared reviewer-question grading

| Reviewer question | Grade | Evidence used | Strongest objection | Current answer quality | Confidence |
| --- | --- | --- | --- | --- | --- |
| Does this feel like a hospital facility-side control room? | Pass | Control Room Summary, Opportunity & Action Tracker, queue governance browser audit, post-tuning realism report | "This may still be a polished analytics shell rather than a real operating control room." | Strong. Current stage, blocker, owner, SLA, recoverability, and reroute proof are visible enough to clear the generic-BI bar. | Medium-high |
| Does each exception map to a believable failed control? | Pass | Selected case evidence trace, manual audit sample, queue governance proof | "The mapping may still be over-curated because the synthetic rules are too neat." | Strong enough. The case-level trace from performed activity to expected opportunity to blocker is the best current evidence. | Medium |
| Are issue domain and root cause clearly separated? | Borderline | Selected case `Classification`, Denial/CDM monitor linkage, reviewer proof pack | "The distinction exists in the artifacts, but it is easy to blur in the live demo and in summary language." | Mixed. The data model is clear, but the demo narrative still risks collapsing issue domain, root cause, and action path into one story. | Medium |
| Is ownership clear? | Pass | Queue governance proof, current queue fields, Action Tracker selected case, routing history | "Ownership is visible, but real ops reviewers may ask whether the owner fields actually drive work." | Strong. Accountable/supporting/escalation ownership plus queue-governance context answer this better than most prototypes. | Medium-high |
| Are recoverability and aging believable? | Pass | Control Room Summary, queue governance proof, post-tuning realism report, manual audit sample | "Recoverability may look too certain for synthetic data, and some final-billed clean cases can still read oddly." | Strong but not bulletproof. Stage-specific aging and recoverability states are explicit, but semantics still need careful verbal framing. | Medium |
| Would a real RI or billing leader use this queue? | Borderline | Control Room Summary, Opportunity & Action Tracker, queue governance audit, decision pack | "The queue surfaces are credible, but the scale and workflow depth are still too small to prove day-to-day usefulness." | Mixed. The queue logic is believable, but operational usefulness at real backlog volume is still asserted more than proven. | Medium |
| Do the service-line stories feel authentic? | Borderline | Department-story report, post-tuning realism report, manual audit sample | "The three anchor stories are good, but they are still narrow and synthetic, and reviewers may want more messy edge cases." | Adequate. Better than a generic demo, but still vulnerable to department-specific scrutiny. | Medium |
| Do the scenario levers feel operationally real? | Borderline | Scenario Lab v0 audit, live Scenario Lab screenshots, reviewer proof pack | "The levers are reasonable, but the layer is thin, and the SoT phase history makes it easy to question whether this is premature polish." | Mixed. Transparent formulas help, but the evidence is not yet deep enough to make scenario realism a strong selling point. | Medium |
| Is predictive modeling staying in its lane? | Pass | Reviewer proof pack, README scope language, Scenario Lab audit, Denial/CDM audit | "Thin scenario and decision-pack layers could still make the product sound more sophisticated than it is." | Strong. No predictive engine is required, and the artifacts consistently frame deterministic control as the center. | High |
| What still feels fake? | Borderline | Decision Pack sample, reviewer proof pack, department-story report, README/V1-plan phase language, realism artifacts | "Some supporting artifacts sound too clean, phase sequencing is inconsistent, and the sample Decision Pack shows `Validation status: Not yet run`." | Weakest current area. The core logic is credible, but the packaging layer still exposes avoidable trust dents. | High |

## D. Top realism strengths

- One-current-blocker discipline is visible in both summary and case-level proof. That is a real control-room signal, not generic dashboard decoration.
- Ownership is not abstract. Current queue, accountable owner, supporting/escalation roles, and queue-governance definitions are visible together.
- Recoverability is operationally defined instead of hand-wavy. The repo distinguishes pre-final-bill recovery, correction-path recovery, already-lost exposure, and compliance-relevant closed cases.
- Queue history behaves like a transition ledger with reroutes and prior-queue aging instead of a single summary row.
- Service-line stories are differentiated enough to avoid the worst synthetic anti-pattern of one universal hospital workflow.
- Denials are kept downstream-only. That prevents scope sprawl into a denials platform.
- Predictive logic is not required to make the current product coherent.

## E. Top realism weaknesses

- The packaging layer is cleaner than the skeptical reviewer will be. "What still feels fake: none" and similar absolute wording invite distrust.
- An earlier sample Decision Pack had shown `Validation status: Not yet run`, which would have been a visible governance hit if left uncorrected.
- Some phase language is inconsistent across current docs versus current implemented surfaces. A smart reviewer can spot that Scenario Lab, Denial/CDM, and the Decision Pack are presented as current even though older phase docs staged them later.
- Queue usefulness is believable in logic but not fully proven in operational scale. The current backlog is still small enough that a billing leader can say, "This is interesting, but is it really a queue I would run?"
- Issue domain versus root cause is modeled correctly, but the live storytelling can still blur those layers if the demo moves too fast.
- The Decision Pack sample contains a mild narrative mismatch: the top ranked queue is billing/edit driven while the control-story summary sentence leads with documentation support failure. That is not fatal, but it is exactly the kind of stitching a skeptical reviewer notices.
- Scenario realism is transparent, but still thin. It can survive as a caveated extension, not as a main credibility claim.

## F. Overall red-team verdict

**Archive verdict at the time**

- The deterministic control-room core is credible enough for reviewer demo use.
- The strongest proof is in queue governance, one-current-blocker logic, recoverability, ownership, queue history, and case-level traceability.
- The biggest risks are not core-logic failures; they are trust dents in the packaging and supporting artifact language.
- Do not lead with Scenario Lab, Denial/CDM, or the Decision Pack. Lead with the control core and use the thin extensions late.
- Tight demo framing matters. If issue domain, root cause, ownership, and recoverability are not explained explicitly, reviewers will assume the model is blurrier than it is.
- The current sample memo should not be used casually while it still shows `Validation status: Not yet run`.
- Service-line realism is good enough to defend, but not broad enough to overclaim.
