# Mock Reviewer Q&A Bank

## A. Shared top-10 reviewer questions

### 1. Does this feel like a hospital facility-side control room?

- Likely skeptic phrasing: `Why is this not just a healthcare BI dashboard with queue labels on top?`
- Strong short answer: `Because the core story is current failed control, current owner queue, current blocker, stage aging, and recoverability, not portfolio reporting alone.`
- Stronger evidence-backed answer: `The live control surfaces and queue-governance audit show current queue, current stage, current primary blocker, accountable owner, SLA status, days in stage, and recoverability on the work surface and again on the selected case.`
- Caveat to add if pressed: `This proves reviewer-ready control structure and routing discipline, not production-scale queue adoption.`
- What page or artifact to point to: `Control Room Summary`, `Opportunity & Action Tracker`, `artifacts/queue_governance_browser_audit.md`, `artifacts/realism/post_tuning_realism_report.md`.

### 2. Does each exception map to a believable failed control?

- Likely skeptic phrasing: `Are these real failed controls, or just synthetic leakage labels?`
- Strong short answer: `The model routes one current actionable blocker, not a blended leakage bucket.`
- Stronger evidence-backed answer: `The selected-case evidence trace ties documented activity and billed state to one current blocker, one current queue, and routing history, while the manual audit rubric requires one primary audit outcome per case.`
- Caveat to add if pressed: `The realism claim is bounded to the frozen outpatient facility-side story set, not every hospital control family.`
- What page or artifact to point to: `Opportunity & Action Tracker` selected case, `docs/MANUAL_AUDIT_RUBRIC.md`, `docs/MANUAL_AUDIT_SAMPLE.md`.

### 3. Are issue domain and root cause clearly separated?

- Likely skeptic phrasing: `This still sounds like coding, documentation, billing, and RI are being mixed together.`
- Strong short answer: `Issue domain answers where the failure sits now; root cause answers why it likely happened.`
- Stronger evidence-backed answer: `The selected case classification and the denial/CDM linkage keep issue domain, likely root cause mechanism, and owner or action path distinct instead of collapsing them into one label.`
- Caveat to add if pressed: `This distinction is strongest at case level; it can blur if the presenter narrates only from summary screens.`
- What page or artifact to point to: `Opportunity & Action Tracker` selected case `Classification`, `Denial Feedback + CDM Governance Monitor`, `artifacts/reviewer_red_team/reviewer_verdict_matrix.md`.

### 4. Is ownership clear?

- Likely skeptic phrasing: `Who actually owns this item right now, and how do you know that is not just decoration?`
- Strong short answer: `Each active item publishes one current queue and one accountable owner, with support and escalation context on the selected case.`
- Stronger evidence-backed answer: `The queue-governance browser audit confirms accountable owner, supporting owner, escalation owner, current queue, aging basis, and SLA status are all visible on the selected-case governance surface.`
- Caveat to add if pressed: `The routing logic is a reviewer-testable operating model, not a claim that every hospital would accept the same owner map unchanged.`
- What page or artifact to point to: `Opportunity & Action Tracker`, `artifacts/queue_governance_browser_audit.md`.

### 5. Are recoverability and aging believable?

- Likely skeptic phrasing: `These recoverability buckets look too clean. Why should I trust them?`
- Strong short answer: `They are governed current-state operating buckets tied to stage and timing, not universal financial truth.`
- Stronger evidence-backed answer: `The realism report shows active cases across pre-final-bill recoverable, post-final-bill recoverable by correction or rebill, and post-window financially lost, and the workflow-state section shows stage-specific aging distributions with zero one-current-blocker violations.`
- Caveat to add if pressed: `Hospitals debate recoverability; the claim here is explicit operating logic, not accounting certainty.`
- What page or artifact to point to: `Control Room Summary`, `artifacts/realism/post_tuning_realism_report.md`, `artifacts/queue_governance_browser_audit.md`.

### 6. Would a real RI or billing leader use this queue?

- Likely skeptic phrasing: `Why would I work this queue instead of my existing billing worklists?`
- Strong short answer: `Because it makes the current blocker, owner, timing pressure, and recoverability visible in one place.`
- Stronger evidence-backed answer: `The summary and action-tracker surfaces show prioritized active exceptions with stage, blocker, queue, owner, SLA, and recoverability, and the follow-through artifact adds monitored intervention movement rather than just counts.`
- Caveat to add if pressed: `The current evidence supports queue coherence and decision usefulness, not day-to-day production scale proof.`
- What page or artifact to point to: `Control Room Summary`, `Opportunity & Action Tracker`, `artifacts/browser_audit/action_tracker_follow_through.md`.

### 7. Do the service-line stories feel authentic?

- Likely skeptic phrasing: `How do I know these departments are not all failing the same way under different labels?`
- Strong short answer: `Each department has its own performed-activity anchor, support rules, and suppression patterns.`
- Stronger evidence-backed answer: `The department-story report shows distinct signatures for infusion timing and waste support, radiology completed-study and distinctness logic, and OR case-state, implant, and handoff timing patterns.`
- Caveat to add if pressed: `This is intentionally a frozen three-story outpatient-first set, not hospital-wide service-line coverage.`
- What page or artifact to point to: `artifacts/realism/department_story_report.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`.

### 8. Do the scenario levers feel operationally real?

- Likely skeptic phrasing: `Is this just fake finance math with prettier labels?`
- Strong short answer: `No. The levers are concrete operating levers with visible formulas and caps.`
- Stronger evidence-backed answer: `Scenario Lab v0 exposes prebill edit clearance rate, correction turnaround days, and routing speed to owner teams, along with baseline inputs, deltas, explicit formulas, and caps on the page.`
- Caveat to add if pressed: `It is a thin deterministic what-if surface, not a planning engine or forecast model.`
- What page or artifact to point to: `Scenario Lab`, `artifacts/scenario_lab_v0_audit.md`.

### 9. Is predictive modeling staying in its lane?

- Likely skeptic phrasing: `What is actually doing the work here, deterministic logic or predictive theater?`
- Strong short answer: `Deterministic logic carries the product; predictive is not required for the current story.`
- Stronger evidence-backed answer: `The core proof is expected activity-to-charge mapping, one-current-blocker routing, queue governance, and stage-specific aging. Scenario is what-if only, and the proof pack explicitly says predictive logic stays secondary.`
- Caveat to add if pressed: `Do not imply hidden models or advanced prioritization beyond the current deterministic shell.`
- What page or artifact to point to: `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`, `artifacts/trust_dent_remediation/demo_script_claim_tightening.md`.

### 10. What still feels fake?

- Likely skeptic phrasing: `Be honest. What would still bother a real hospital reviewer here?`
- Strong short answer: `Scale, breadth, and external validation remain limited even though the control logic is coherent.`
- Stronger evidence-backed answer: `The current pack is strongest on deterministic control structure, department-specific story discipline, and visible suppression. It is weaker on production-scale queue utility, broader modifier breadth, and external reviewer acceptance of the exact owner model.`
- Caveat to add if pressed: `Synthetic realism can survive challenge only when the claim stays narrow and case-grounded.`
- What page or artifact to point to: `artifacts/reviewer_red_team/reviewer_objection_log.md`, `artifacts/reviewer_red_team/reviewer_verdict_matrix.md`, `artifacts/trust_dent_remediation/trust_dent_remediation_plan.md`.

## B. Reviewer-specific question sets

## Reviewer 1 — Revenue Integrity / Charge Capture

### RI-1. Taxonomy feels too clean

- Likely challenge wording: `Real RI leakage work is messier than this. Why is your taxonomy so neat?`
- Best concise answer: `The goal is usable operating separation, not synthetic messiness for its own sake.`
- Proof source to point at: `Opportunity & Action Tracker` selected case `Classification`, `artifacts/reviewer_red_team/reviewer_objection_log.md`.
- Caveat or limit: `The taxonomy is governed and narrower than real enterprise variation.`
- Red-flag answer to avoid: `Hospitals are messy, but we simplified it for the demo.`

### RI-2. Chart-to-bill logic may be overfit

- Likely challenge wording: `How do I know the expected charge was not reverse-engineered from the billed result?`
- Best concise answer: `The expected opportunity is anchored to documented performed activity before charge outcome is evaluated.`
- Proof source to point at: `docs/MANUAL_AUDIT_SAMPLE.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`, `artifacts/realism/department_story_report.md`.
- Caveat or limit: `This is synthetic and public-safe, so the proof is logic traceability, not live source integration.`
- Red-flag answer to avoid: `The model knows what should have been billed because that is how we generated the data.`

### RI-3. Modifier and status logic are too thin

- Likely challenge wording: `Modifier-heavy work is where fake healthcare logic usually falls apart.`
- Best concise answer: `The current claim is narrow: a few governed modifier and status-dependent story families, not modifier completeness.`
- Proof source to point at: `Modifiers / Edits / Prebill Holds`, `artifacts/realism/department_story_report.md`, `docs/MANUAL_AUDIT_SAMPLE.md`.
- Caveat or limit: `Modifier breadth is still limited to the frozen story set.`
- Red-flag answer to avoid: `The modifier engine is broad enough for most hospitals.`

### RI-4. Recoverability sounds too certain

- Likely challenge wording: `Who says these dollars are really recoverable versus lost?`
- Best concise answer: `The buckets describe governed current operating posture, not universal financial certainty.`
- Proof source to point at: `Control Room Summary`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat or limit: `Recoverability definitions are reviewable assumptions and should be challenged.`
- Red-flag answer to avoid: `If it is in the recoverable bucket, the money is definitely recoverable.`

### RI-5. Charge reconciliation still looks summary-heavy

- Likely challenge wording: `I see counts, but where is the real control behavior?`
- Best concise answer: `The control behavior is the case trace from performed activity to missing or mismatched charge to current owner queue.`
- Proof source to point at: `Charge Reconciliation Monitor`, `Opportunity & Action Tracker` selected case, `docs/MANUAL_AUDIT_SAMPLE.md`.
- Caveat or limit: `The demo must show a case trace or this answer weakens immediately.`
- Red-flag answer to avoid: `The totals alone show the control is working.`

### RI-6. Scenario levers are too narrow

- Likely challenge wording: `Three levers do not represent real RI intervention planning.`
- Best concise answer: `Agreed on depth; this is a thin what-if extension, not the center of the product claim.`
- Proof source to point at: `artifacts/scenario_lab_v0_audit.md`, `artifacts/trust_dent_remediation/demo_script_claim_tightening.md`.
- Caveat or limit: `Depth is the current weakness, but the formulas are explicit and bounded.`
- Red-flag answer to avoid: `These three levers are enough to model RI operations.`

### RI-7. One-current-blocker sounds artificial

- Likely challenge wording: `Real accounts have multiple problems. Why force one blocker?`
- Best concise answer: `Because the queue needs one current actionable blocker even when multiple issues exist underneath.`
- Proof source to point at: `artifacts/queue_governance_browser_audit.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat or limit: `Secondary issues still exist; the rule only governs what is current now.`
- Red-flag answer to avoid: `There is only ever one issue on an account.`

### RI-8. Service-line realism is too narrow

- Likely challenge wording: `Three anchor stories are not enough to prove hospital realism.`
- Best concise answer: `Correct. They prove disciplined realism in a bounded outpatient facility-side slice.`
- Proof source to point at: `artifacts/realism/department_story_report.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`.
- Caveat or limit: `Do not stretch this into enterprise coverage.`
- Red-flag answer to avoid: `These three stories generalize across the hospital.`

### RI-9. Packaged or integral suppression is easy to fake

- Likely challenge wording: `How do I know you did not inflate misses by ignoring packaged or non-billable work?`
- Best concise answer: `Because suppression is visible and department-specific, not hidden.`
- Proof source to point at: `artifacts/realism/post_tuning_realism_report.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, selected suppressed case in `docs/MANUAL_AUDIT_SAMPLE.md`.
- Caveat or limit: `Suppression proof has to be shown directly when challenged.`
- Red-flag answer to avoid: `Most documented activity should become a charge anyway.`

### RI-10. Decision Pack may blur the live control story

- Likely challenge wording: `Is the memo layer covering up a thinner queue story?`
- Best concise answer: `No. The memo is a bounded snapshot built from the already-shown governed logic.`
- Proof source to point at: `artifacts/decision_pack/revenue_integrity_decision_pack_audit.md`.
- Caveat or limit: `Use it as a leave-behind, not as stronger proof than the live queue.`
- Red-flag answer to avoid: `Executives only need the memo; they do not need the queue details.`

## Reviewer 2 — PFS / Billing Operations

### PFS-1. Prebill queue design feels modeled

- Likely challenge wording: `Why should I believe this behaves like a real prebill work queue?`
- Best concise answer: `Because the queue carries operating fields that explain work, not just labels: blocker, owner, SLA, aging, recoverability, and routing context.`
- Proof source to point at: `Opportunity & Action Tracker`, `artifacts/queue_governance_browser_audit.md`.
- Caveat or limit: `That proves queue discipline, not real billing-scale adoption.`
- Red-flag answer to avoid: `It looks like a work queue, so it is a work queue.`

### PFS-2. Aging logic is too tidy

- Likely challenge wording: `This aging pattern still looks cleaner than real operations.`
- Best concise answer: `The claim is governed stage-specific aging, not messy-by-default realism theater.`
- Proof source to point at: `artifacts/realism/post_tuning_realism_report.md`, `artifacts/queue_governance_browser_audit.md`.
- Caveat or limit: `Small synthetic populations will still look cleaner than live enterprise queues.`
- Red-flag answer to avoid: `The aging is realistic because we added more overdue items.`

### PFS-3. Routing and ownership are not operationally validated

- Likely challenge wording: `How do I know these owners are the right owners in a real shop?`
- Best concise answer: `You do not have to accept them as universal truth; the point is that the operating model is explicit and reviewable.`
- Proof source to point at: `artifacts/queue_governance_browser_audit.md`, `artifacts/reviewer_proof_pack/reviewer_scorecard.md`.
- Caveat or limit: `Owner mapping is a reviewable operating hypothesis, not a universal standard.`
- Red-flag answer to avoid: `These are the standard hospital owners for this work.`

### PFS-4. Correction or rebill support is thin

- Likely challenge wording: `This is billing-aware, but it is not a rebill workflow.`
- Best concise answer: `Correct. Correction and rebill support is visible, but intentionally thin.`
- Proof source to point at: `artifacts/browser_audit/action_tracker_follow_through.md`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat or limit: `Do not present this as a rebill orchestration platform.`
- Red-flag answer to avoid: `The correction path is basically complete.`

### PFS-5. Backlog is too small to prove usefulness

- Likely challenge wording: `Why should I trust a queue with only a small active sample?`
- Best concise answer: `Because the current proof is logic coherence and prioritization discipline, not scale.`
- Proof source to point at: `artifacts/realism/post_tuning_realism_report.md`, `Control Room Summary`.
- Caveat or limit: `Scale utility remains an open question until broader deployment data exists.`
- Red-flag answer to avoid: `This is enough volume to prove operations value.`

### PFS-6. Validation structure is artifact-heavy

- Likely challenge wording: `I see audits and reports, but where is the day-to-day operating proof?`
- Best concise answer: `The live queue plus selected-case governance is the operating proof; the audits are there to defend it under review.`
- Proof source to point at: `Control Room Summary`, `Opportunity & Action Tracker`, `artifacts/reviewer_proof_pack/proof_asset_index.md`.
- Caveat or limit: `The repo is reviewer-ready, not production-operated.`
- Red-flag answer to avoid: `The artifacts are the product evidence.`

### PFS-7. Recoverable versus lost is not operational enough

- Likely challenge wording: `How does this actually change my work, not just classify dollars?`
- Best concise answer: `It separates current action opportunity from already-lost exposure so the queue and escalation story stay honest.`
- Proof source to point at: `Control Room Summary`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat or limit: `It frames work now versus consequence now; it does not replace financial reporting.`
- Red-flag answer to avoid: `The recoverable dollars metric is mainly for executive storytelling.`

### PFS-8. Queue history may still be synthetic churn

- Likely challenge wording: `How do I know the reroutes were not made up to look operational?`
- Best concise answer: `Because routing reason, reroute counts, and first-route-only versus rerouted mixes are visible and bounded.`
- Proof source to point at: `artifacts/realism/post_tuning_realism_report.md`, `artifacts/queue_governance_browser_audit.md`.
- Caveat or limit: `It is still synthetic queue history, so the right claim is believable handoff structure, not live system replay.`
- Red-flag answer to avoid: `The queue history is realistic because it has multiple reroutes.`

### PFS-9. Decision Pack freshness and governance can dent trust

- Likely challenge wording: `Why should I trust the memo layer if the artifact state looks stale?`
- Best concise answer: `Use the audit and current governed trigger as proof, and keep the memo framed as a snapshot, not a validation substitute.`
- Proof source to point at: `artifacts/decision_pack/revenue_integrity_decision_pack_audit.md`, `artifacts/trust_dent_remediation/decision_pack_freshness_patch.md`.
- Caveat or limit: `If the visible sample looks stale, do not lean on it.`
- Red-flag answer to avoid: `The memo is close enough even if the validation state is stale.`

### PFS-10. Denials page risks pulling the story off course

- Likely challenge wording: `Why are we talking about denials if the queue is supposed to be prebill-first?`
- Best concise answer: `Only because denials act as thin downstream evidence of upstream control failure.`
- Proof source to point at: `artifacts/denial_feedback_cdm_monitor_audit.md`, `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`.
- Caveat or limit: `Keep the page brief and late.`
- Red-flag answer to avoid: `Denials help prove ROI, so they are central.`

## Reviewer 3 — Coding / CDI / Clinical Ops

### CCO-1. Documentation dependencies feel standardized

- Likely challenge wording: `These documentation gaps still read more controlled than clinical reality.`
- Best concise answer: `The claim is department-specific plausibility, not full clinical variation coverage.`
- Proof source to point at: `artifacts/realism/department_story_report.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`.
- Caveat or limit: `Breadth is limited to the frozen stories.`
- Red-flag answer to avoid: `This covers the main documentation variation you would see in practice.`

### CCO-2. Modifier realism is narrow

- Likely challenge wording: `A few modifier examples do not prove coding realism.`
- Best concise answer: `Agreed. The proof is narrow but governed: a few real modifier-dependent cases, not modifier breadth.`
- Proof source to point at: `Modifiers / Edits / Prebill Holds`, `artifacts/realism/department_story_report.md`.
- Caveat or limit: `Do not claim broad coding completeness.`
- Red-flag answer to avoid: `The modifier logic is comprehensive enough.`

### CCO-3. Expected charge from clinical activity is said more than shown

- Likely challenge wording: `Show me the activity driving the expected charge, not just the final label.`
- Best concise answer: `The expected opportunity starts from documented performed activity and then passes support and suppression rules before charge comparison.`
- Proof source to point at: `docs/MANUAL_AUDIT_SAMPLE.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`, `Opportunity & Action Tracker` selected case.
- Caveat or limit: `If the demo skips a case trace, the answer weakens.`
- Red-flag answer to avoid: `Orders usually tell us enough about what should have charged.`

### CCO-4. Coding, documentation, billing, and RI still blur

- Likely challenge wording: `I still hear these domains collapsing into one story.`
- Best concise answer: `That is exactly why the case narration must state issue domain and root cause separately every time.`
- Proof source to point at: `Opportunity & Action Tracker` selected case `Classification`, `Denial Feedback + CDM Governance Monitor`.
- Caveat or limit: `The discipline is visible in the model but can be lost in rushed narration.`
- Red-flag answer to avoid: `They are all revenue cycle issues anyway.`

### CCO-5. Service-line stories may not survive deeper SME challenge

- Likely challenge wording: `Why should I believe three frozen stories are enough to feel hospital-native?`
- Best concise answer: `Because each one maps to a distinct workflow anchor and failure pattern instead of one generic source story.`
- Proof source to point at: `artifacts/realism/department_story_report.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`.
- Caveat or limit: `They are anchor stories, not broad service-line coverage.`
- Red-flag answer to avoid: `The same model pattern works across all service lines.`

### CCO-6. Packaged or integral work may still be overstated

- Likely challenge wording: `If I do not see suppression, I will assume the misses are inflated.`
- Best concise answer: `Suppression is explicit, department-specific, and part of the realism evidence.`
- Proof source to point at: `artifacts/realism/post_tuning_realism_report.md`, `docs/MANUAL_AUDIT_RUBRIC.md`.
- Caveat or limit: `Show a suppressed case directly if challenged.`
- Red-flag answer to avoid: `We filter out obvious false positives in the background.`

### CCO-7. Performed to billable to payable is not the same thing

- Likely challenge wording: `Just because something happened clinically does not mean it becomes billable or payable.`
- Best concise answer: `Correct. Performed activity is only the starting anchor; support, packaging, modifier, and downstream payable realities still matter.`
- Proof source to point at: `docs/MANUAL_AUDIT_RUBRIC.md`, `artifacts/realism/post_tuning_realism_report.md`, `artifacts/denial_feedback_cdm_monitor_audit.md`.
- Caveat or limit: `The product centers on billable control logic first and treats payable state as a later downstream signal.`
- Red-flag answer to avoid: `Performed activity should usually become a charge and payment.`

### CCO-8. Orders are being used implicitly

- Likely challenge wording: `Are you sure this is not still order-based under the hood?`
- Best concise answer: `The governing rule is explicit: start from documented performed activity, not order count.`
- Proof source to point at: `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, `artifacts/reviewer_red_team/reviewer_verdict_matrix.md`.
- Caveat or limit: `Order context may appear, but it is not the charging anchor.`
- Red-flag answer to avoid: `Orders are a good enough proxy for expected charge.`

### CCO-9. Denial linkage could blur downstream billing with clinical truth

- Likely challenge wording: `If you emphasize denials, it starts to sound like denials define the problem.`
- Best concise answer: `They do not. Denials are only a downstream confirmation or signal layer.`
- Proof source to point at: `artifacts/denial_feedback_cdm_monitor_audit.md`, `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`.
- Caveat or limit: `Keep denials late, brief, and explicitly secondary.`
- Red-flag answer to avoid: `Denials prove whether the upstream issue was real.`

### CCO-10. What still feels fake?

- Likely challenge wording: `What would a coding or clinical SME still challenge here?`
- Best concise answer: `Breadth of modifier coverage, wider clinical variation, and exact owner acceptance remain open.`
- Proof source to point at: `artifacts/reviewer_red_team/reviewer_objection_log.md`, `artifacts/trust_dent_remediation/trust_dent_remediation_plan.md`.
- Caveat or limit: `That is why the claim has to stay at bounded reviewer-ready realism.`
- Red-flag answer to avoid: `Nothing material feels fake anymore.`
