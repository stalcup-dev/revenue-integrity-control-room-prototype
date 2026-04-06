# Mock Reviewer Panel Runbook Template

Internal review-prep template. Simulate a 3-person skeptical review panel.

## A. Panel structure

### Reviewer 1 - Revenue Integrity / Charge Capture leader

- Archetype: Director of Revenue Integrity, Charge Capture Manager, senior RI analyst lead.
- Primary pressure points: taxonomy, chart-to-bill or bill-to-chart logic, modifier or status integrity, recoverability assumptions, charge reconciliation controls, scenario levers tied to real hospital operations.
- What this reviewer should punish: generic leakage language, loose expected-charge logic, weak failed-control mapping, scenario overreach.

### Reviewer 2 - PFS / Billing Operations leader

- Archetype: PFS Manager, Billing Operations Manager, Revenue Cycle Operations Manager, Central Business Office Manager.
- Primary pressure points: prebill queue design, aging logic, routing and ownership logic, correction or rebill workflow, backlog assumptions, operational validation structure.
- What this reviewer should punish: modeled labels without operating meaning, vague queue utility, overclaiming scale, treating the memo layer as proof.

### Reviewer 3 - Coding / CDI / Clinical Ops SME

- Archetype: HIM Coding Supervisor, CDI Specialist, Outpatient Coding Lead, Radiology, OR, or Infusion operations leader.
- Primary pressure points: documentation dependencies, modifier realism, expected-charge logic from clinical activity, service-line workflow realism, separation of coding, documentation, billing, and RI domains.
- What this reviewer should punish: order-based logic, blended issue categories, missing suppression proof, flat service-line stories.

## B. Session timing

Target total: 20 minutes.

### 0:00-2:00 - Opening framing

- State the bounded claim: facility-side, outpatient-first, deterministic-first reviewer-ready prototype.
- State the demo path: control core first, thin extensions last.
- State the guardrails out loud: documented performed activity, not orders alone; one current blocker; stage-specific aging; recoverability; denials downstream-only; predictive secondary.

### 2:00-9:00 - Demo

- 2:00-3:15: `Control Room Summary`
- 3:15-4:45: queue governance, one-current-blocker, recoverability, aging on `Opportunity & Action Tracker`
- 4:45-5:45: `Opportunity & Action Tracker` follow-through
- 5:45-6:45: `Scenario Lab`
- 6:45-7:30: `Denial Feedback + CDM Governance Monitor`
- 7:30-9:00: `Revenue Integrity Decision Pack` trigger and close

### 9:00-19:00 - Hostile or skeptical Q&A

- 9:00-12:00: RI reviewer leads
- 12:00-15:00: PFS reviewer leads
- 15:00-18:00: Coding or Clinical Ops reviewer leads
- 18:00-19:00: moderator chooses the two weakest earlier answers and asks them again in shorter form

### 19:00-20:00 - Close

- Presenter restates the narrow claim.
- Moderator scores clarity, realism, and caveat discipline before any general praise.

## C. Demo order

Use the current product and story order below.

### 1. Control Room Summary

- Show: `Open actionable exceptions`, `Recoverable dollars open`, `Already lost`, `Why The Backlog Exists`, `Where Work Is Stuck Now`, `Who Should Act Next`.
- Presenter sentence to rehearse: `This is the current deterministic control snapshot for the filtered slice: active failed controls, accountable queues, and recoverable-versus-lost exposure.`
- Proof source if challenged: `artifacts/reviewer_proof_pack/demo_script_7min.md`, `artifacts/reviewer_proof_pack/reviewer_proof_pack.md`.

### 2. Queue governance / one-current-blocker / recoverability / aging

- Show on `Opportunity & Action Tracker`: `Queue Priority Ranking`, then one `Selected Case Evidence Trace` with `Case Header`, `Classification`, `Queue Governance`, and `Routing History`.
- Force the presenter to say issue domain, root cause, current blocker, current queue, accountable owner, days in stage, SLA status, and recoverability for one case.
- Proof source if challenged: `artifacts/queue_governance_browser_audit.md`.

### 3. Opportunity & Action Tracker

- Show: `Intervention Snapshot`, `Recurring Issue Patterns`, `Intervention Owners`, `Intervention Plan`, selected intervention follow-through.
- Presenter must keep the claim thin: follow-through support, not full task management.
- Proof source if challenged: `artifacts/browser_audit/action_tracker_follow_through.md`.

### 4. Scenario Lab

- Show: the three levers, `Projected Impact`, `Scenario Output Detail`, and `How this is calculated`.
- Presenter must say `what-if` before `impact`.
- Proof source if challenged: `artifacts/scenario_lab_v0_audit.md`.

### 5. Denial Feedback + CDM Governance Monitor

- Show briefly: denial pattern table, selected-pattern linkage, CDM governance section.
- Keep it late and brief. The only acceptable frame is downstream evidence tied back to upstream control failure.
- Proof source if challenged: `artifacts/denial_feedback_cdm_monitor_audit.md`.

### 6. Decision Pack trigger

- Show: `Revenue Integrity Decision Pack` trigger and rendered memo sections.
- Presenter must frame it as a bounded leave-behind built from the same governed logic already shown live.
- Proof source if challenged: `artifacts/decision_pack/revenue_integrity_decision_pack_audit.md`.

## D. Moderator instructions

- Interrupt when the presenter spends more than 20-30 seconds on portfolio framing without naming a case, control, owner, blocker, or proof surface.
- Interrupt when the presenter says `AI`, `predictive`, `forecast`, `optimization`, `leadership-ready`, or `operations-ready` without an immediate caveat.
- Push for proof whenever the presenter uses words like `realistic`, `hospital-native`, `validated`, `useful`, or `believable`.
- Ask for caveats whenever the presenter cites scale, queue usefulness, scenario impact, recoverability certainty, or workflow acceptance.
- Penalize overclaiming when the presenter implies production deployment, enterprise breadth, denials-platform depth, or predictive dependence.
- Force scope discipline when the presenter drifts into professional billing, inpatient workflows, appeals, adjudication, payer strategy, enterprise worklist management, or broad coding platform claims.
- Force a case-level answer when the presenter tries to answer `documented performed activity` or `failed control mapping` with summary metrics only.
- Ask `what still feels fake?` at least once. Reward direct admission of current limits.

## E. Failure conditions

Count the rehearsal as failed if any of the following happen more than once, or if any single one goes uncorrected after moderator challenge.

- Billing, coding, documentation, and RI domains are blurred into one generic leakage story.
- Scenario Lab is overclaimed as forecast, finance model, optimization engine, or maturity proof.
- Predictive language sounds central instead of secondary.
- Denials sound like the product center instead of downstream-only evidence.
- Facility-side or outpatient-first scope is lost.
- Ownership is not answered clearly for a selected case.
- Recoverability is described vaguely or as accounting certainty instead of governed current-state logic.
- Stage-specific aging is skipped or replaced with generic aging talk.
- The presenter uses orders as the basis for expected-charge logic instead of documented performed activity.
- Packaged, integral, or false-positive suppression is not acknowledged.
- One-current-blocker discipline is not explained clearly.
- The Decision Pack is presented as stronger proof than the live queue.

## Rehearsal rule

Reward short, precise, caveated answers. Penalize polished answers that sound broader than the implemented state.
