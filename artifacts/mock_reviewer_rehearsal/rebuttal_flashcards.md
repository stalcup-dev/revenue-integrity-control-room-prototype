# Rebuttal Flashcards

## Highest-risk realism challenges

### Card 1

- Challenge: `This sounds like generic BI, not a hospital facility-side control room.`
- 10-second answer: `The center of gravity is failed control, current owner queue, current blocker, stage aging, and recoverability, not generic reporting.`
- 30-second answer: `The proof is the live queue surfaces plus the queue-governance audit. They show current stage, current blocker, accountable owner, days in stage, SLA, and recoverability on the work surface and again on the selected case. That is operating control structure, not just BI.`
- Proof: `Control Room Summary`, `Opportunity & Action Tracker`, `artifacts/queue_governance_browser_audit.md`.
- Caveat: `This proves reviewer-ready control structure, not production-scale operating adoption.`
- Do not say: `It is basically a dashboard with some workflow context.`

### Card 2

- Challenge: `You keep saying expected charge comes from clinical reality. Show me.`
- 10-second answer: `Expected opportunity starts from documented performed activity, not orders alone.`
- 30-second answer: `The governing rule is performed activity first, then required support, then packaging or suppression rules, then charge comparison and current blocker routing. That is why the strongest defense is a case trace, not a summary KPI.`
- Proof: `docs/MANUAL_AUDIT_SAMPLE.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, `docs/REAL_WORLD_SOURCE_MAPPING_BY_DEPARTMENT.md`.
- Caveat: `This is logic traceability proof, not live source-system integration.`
- Do not say: `The order usually tells us what should have been charged.`

### Card 3

- Challenge: `Performed does not automatically mean billable or payable.`
- 10-second answer: `Correct. Performed is the anchor, not the conclusion.`
- 30-second answer: `The control path is performed, then supported, then billable after packaging and modifier rules, then only later possibly payable. The product centers on the performed-to-billable control layer, while denials are just a downstream payable-state signal.`
- Proof: `docs/MANUAL_AUDIT_RUBRIC.md`, `artifacts/realism/post_tuning_realism_report.md`, `artifacts/denial_feedback_cdm_monitor_audit.md`.
- Caveat: `The current product is strongest on billable control realism, not full payable-state management.`
- Do not say: `If it happened clinically, it should charge and pay.`

### Card 4

- Challenge: `Real accounts have multiple issues. Why do you force one current blocker?`
- 10-second answer: `Because the queue needs one current actionable blocker even when other issues exist underneath.`
- 30-second answer: `One-current-blocker is an operating rule, not a claim that secondary issues disappear. It keeps the queue usable by publishing the current blocker, queue, owner, and aging state instead of letting one account explode into overlapping active labels.`
- Proof: `artifacts/queue_governance_browser_audit.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat: `Secondary defects can still be present; they are just not the current queue anchor.`
- Do not say: `There is only one issue on each account.`

### Card 5

- Challenge: `Recoverability and aging look too clean to trust.`
- 10-second answer: `They are governed current-state operating buckets tied to stage and timing.`
- 30-second answer: `The point is not accounting certainty. The point is honest operating posture: pre-final-bill recoverable, correction-path recoverable, or already lost, all with stage-specific aging instead of one flat aging number.`
- Proof: `Control Room Summary`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat: `Recoverability definitions are challengeable assumptions, not universal truths.`
- Do not say: `Those recoverable dollars are definitely collectible.`

### Card 6

- Challenge: `Where is the proof that you are not overstating misses and false positives?`
- 10-second answer: `Suppression is visible, not hidden.`
- 30-second answer: `The realism artifacts show packaged, integral, discontinued, and non-billable suppression patterns by department. That is the key defense against inflated leakage logic. If challenged, show a suppressed case directly.`
- Proof: `artifacts/realism/post_tuning_realism_report.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, `docs/MANUAL_AUDIT_SAMPLE.md`.
- Caveat: `Suppression proof has to be shown explicitly; it should not stay implicit.`
- Do not say: `We filter obvious false positives in the background.`

## Scope-discipline challenges

### Card 7

- Challenge: `Is this facility-side only, or are you drifting into professional billing?`
- 10-second answer: `Facility-side only.`
- 30-second answer: `The SoT and proof pack freeze the claim to outpatient-first, facility-side revenue integrity. The current story is documented performed activity to expected facility charge opportunity, owner-routed queue, recoverability, and thin downstream evidence.`
- Proof: `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`, `docs/build_sot.md`.
- Caveat: `Do not borrow professional fee language to make the story sound broader.`
- Do not say: `It should generalize to pro-fee pretty easily.`

### Card 8

- Challenge: `Why is denials on the screen if this is not a denials product?`
- 10-second answer: `Because denials are downstream evidence only.`
- 30-second answer: `The page exists to show whether upstream documentation, billing, or configuration failures surface later. It does not add appeals workflow, adjudication, or denials workqueue logic, and it should stay late and brief in the demo.`
- Proof: `artifacts/denial_feedback_cdm_monitor_audit.md`, `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`.
- Caveat: `If you spend too much time on it, the story drifts.`
- Do not say: `Denials prove the business case, so they are central.`

### Card 9

- Challenge: `Are you claiming a full billing operations platform?`
- 10-second answer: `No. It is reviewer-ready deterministic control logic with thin follow-through support.`
- 30-second answer: `The queue and case surfaces are real proof. Correction and rebill context, intervention follow-through, Scenario Lab, denials, and the memo layer are all intentionally thinner than full operational platforms.`
- Proof: `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`, `artifacts/browser_audit/action_tracker_follow_through.md`.
- Caveat: `Use words like prototype, bounded, and current-state.`
- Do not say: `This is operations-ready.`

### Card 10

- Challenge: `Why should I trust your aging logic?`
- 10-second answer: `Because it is stage-specific, not one flat aging bucket.`
- 30-second answer: `The queue publishes current stage and days in stage, and the realism report shows different age ranges across charge capture pending, coding pending, documentation pending, prebill edit or hold, and correction or rebill pending.`
- Proof: `artifacts/queue_governance_browser_audit.md`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat: `Stage-specific aging is the claim; perfect real-world distribution is not.`
- Do not say: `It is realistic because there are some old items.`

### Card 11

- Challenge: `Who owns this item right now?`
- 10-second answer: `One current queue and one accountable owner are published on the selected case.`
- 30-second answer: `The selected case also shows supporting and escalation owners plus the governance explanation for why the case is routed there now. That is separate from issue domain and root cause.`
- Proof: `Opportunity & Action Tracker`, `artifacts/queue_governance_browser_audit.md`.
- Caveat: `Owner mapping is an explicit operating model, not universal hospital truth.`
- Do not say: `The owner is basically whoever needs to touch it next.`

### Card 12

- Challenge: `Why does the Decision Pack belong here at all?`
- 10-second answer: `As a bounded leave-behind built from the same governed logic already shown live.`
- 30-second answer: `It packages the current queue slice, control story, intervention update, scenario snapshot, and caveats without inventing a separate logic path. It should never be presented as stronger proof than the live queue.`
- Proof: `artifacts/decision_pack/revenue_integrity_decision_pack_audit.md`.
- Caveat: `Use the audit and current trigger; do not lean on stale-looking samples.`
- Do not say: `The memo tells the story so we do not need the queue detail.`

## Methodology, synthetic-data, scenario, and predictive challenges

### Card 13

- Challenge: `This is synthetic. Why should I trust any of it?`
- 10-second answer: `Trust comes from visible control logic, case traceability, and explicit caveats, not from pretending it is live hospital data.`
- 30-second answer: `The repo proves that the assumptions are structured enough to survive reviewer challenge: department-specific mapping, one-current-blocker discipline, stage-specific aging, visible suppression, and manual-audit defensibility. It does not claim live-source fidelity.`
- Proof: `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`, `docs/MANUAL_AUDIT_RUBRIC.md`, `artifacts/realism/post_tuning_realism_report.md`.
- Caveat: `Synthetic realism must stay narrow and challengeable.`
- Do not say: `The synthetic data is realistic enough to stand in for production.`

### Card 14

- Challenge: `Scenario Lab sounds like forecasting.`
- 10-second answer: `It is what-if support, not forecast.`
- 30-second answer: `Scenario Lab uses visible operational levers, explicit formulas, and caps tied to the current governed slice. It tests assumptions like better prebill clearance or faster routing; it does not claim forecast certainty or financial planning maturity.`
- Proof: `Scenario Lab`, `artifacts/scenario_lab_v0_audit.md`, `artifacts/trust_dent_remediation/demo_script_claim_tightening.md`.
- Caveat: `Call it thin and deterministic before you call it useful.`
- Do not say: `This predicts future performance.`

### Card 15

- Challenge: `Is predictive doing the real work here?`
- 10-second answer: `No. Predictive is secondary and not required.`
- 30-second answer: `The credibility engine is deterministic: documented performed activity, support and suppression rules, one current blocker, queue governance, stage aging, and recoverability. Predictive logic is explicitly outside the core proof burden.`
- Proof: `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`, `docs/build_sot.md`.
- Caveat: `Do not imply hidden models, smarter ranking, or future prediction beyond the current deterministic shell.`
- Do not say: `The AI helps find what matters most.`

### Card 16

- Challenge: `What exactly is the scenario doing with dollars?`
- 10-second answer: `It estimates bounded recoverable-dollar lift against the current slice.`
- 30-second answer: `The page shows baseline inputs, scenario deltas, formulas, and caps. The dollar output is explicitly a what-if estimate tied to current recoverability and queue behavior, not a promise of realized financial outcome.`
- Proof: `artifacts/scenario_lab_v0_audit.md`, `artifacts/scenario_lab/scenario_lab_calc.png`.
- Caveat: `Never present the estimate as booked savings or a forecast.`
- Do not say: `This is the financial upside we would expect to realize.`

### Card 17

- Challenge: `How do you keep coding, documentation, billing, and RI boundaries straight?`
- 10-second answer: `By separating issue domain, root cause, owner path, and downstream signal.`
- 30-second answer: `The model does not let one label carry all the meaning. The selected case can show documentation support failure as issue domain, a specific root-cause mechanism, a current owner queue, and a later downstream denial signal without collapsing them into one story.`
- Proof: `Opportunity & Action Tracker` selected case, `Denial Feedback + CDM Governance Monitor`.
- Caveat: `The presenter has to narrate those fields separately or the boundary discipline gets lost.`
- Do not say: `They are all parts of the same problem anyway.`

### Card 18

- Challenge: `What still feels fake here?`
- 10-second answer: `Scale, breadth, and external acceptance are still limited.`
- 30-second answer: `The pack is strongest on bounded deterministic control realism. It is weaker on enterprise breadth, broader modifier coverage, production queue validation, and proving that every real hospital would accept the same owner model or recoverability windows.`
- Proof: `artifacts/reviewer_red_team/reviewer_objection_log.md`, `artifacts/reviewer_red_team/reviewer_verdict_matrix.md`.
- Caveat: `Admitting the remaining gaps usually builds more trust than over-answering them.`
- Do not say: `Nothing major still feels fake.`
