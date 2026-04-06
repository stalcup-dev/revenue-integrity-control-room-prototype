# Prebuild Board - Source of Truth

Historical planning archive only. This document is retained as background build-governance material, not as the shipped product entrypoint for recruiters or reviewers. Start with [`README.md`](../README.md), [`artifacts/project_summary_and_scope.md`](../artifacts/project_summary_and_scope.md), and [`artifacts/proof_index.md`](../artifacts/proof_index.md) for the current public-facing product story.

## Hospital Facility-Side Revenue Integrity Control Room

**Status:** Pre-build review, revised after Expert Report 1
**Purpose:** Align all pre-build reviewers on the same business problem, scope, controls, assumptions, and design direction before implementation begins.
**Project type:** Public-safe synthetic-data healthcare analytics flagship project
**Primary interface:** Streamlit
**Primary goal:** Build a hospital-native, facility-side revenue integrity control room that identifies charge capture and billing-integrity exceptions, routes them to the right owners, prioritizes recoverable opportunities, and supports forward-looking operational improvement.

## Related Docs

* [V1_IMPLEMENTATION_PLAN.md](V1_IMPLEMENTATION_PLAN.md)
* [KPI_DICTIONARY.md](KPI_DICTIONARY.md)
* [DATA_MODEL.md](DATA_MODEL.md)
* [SYNTHETIC_DATA_RULES.md](SYNTHETIC_DATA_RULES.md)
* [DEPARTMENT_LOGIC_MAP.md](DEPARTMENT_LOGIC_MAP.md)

## Doc Roles

* `BUILD_SOT.md` = governance / strategy / scope control
* `V1_IMPLEMENTATION_PLAN.md` = execution contract
* `KPI_DICTIONARY.md` = governed metrics
* `DATA_MODEL.md` = implementation-ready schema reference
* `SYNTHETIC_DATA_RULES.md` = synthetic generation rulebook
* `DEPARTMENT_LOGIC_MAP.md` = department-specific performed-activity mapping

---

# 1) North Star

## Decision

Which facility-side departments, service lines, and exception queues should leadership prioritize first to reduce legitimate revenue leakage and compliance risk?

## Metric / threshold

Prioritize queues with the highest combination of:

* recoverable dollars
* repeat exception volume
* aging severity
* preventable share
* operational fixability
* control failure urgency

## Action

Route the highest-value exceptions into owner-based work queues, distinguish what is still recoverable from what is already lost, and validate targeted interventions over 30-60-90 days.

---

# 2) Revised Business Question

Where is the hospital’s **facility-side outpatient-first revenue integrity process** failing due to charge capture gaps, modifier/status issues, documentation support failures, prebill edit failures, or unreconciled encounters — and which exception queues should be worked first?

This project must answer:

1. **What control failed?**
2. **What exception did that create?**
3. **Who owns the exception now?**
4. **How old is it?**
5. **Is it still recoverable?**
6. **What intervention would reduce recurrence?**

---

# 3) Project Positioning

This project is intentionally designed as a **hospital facility-side revenue integrity control room**, not:

* a generic healthcare BI dashboard
* an enterprise-wide denials platform
* a professional fee billing analytics app
* an AI-heavy “revenue leakage” platform

It should signal:

* hospital workflow understanding
* revenue integrity control thinking
* charge capture knowledge
* chart-to-bill / bill-to-chart reconciliation discipline
* prebill exception management
* operational accountability
* leader-facing actionability

This project should feel:

* hospital-native
* outpatient-first
* operationally believable
* financially coherent
* clinically plausible
* control-oriented
* action-ready

---

# 4) Non-Negotiable Design Principles

## Public-safe

* Synthetic data only
* No PHI
* No real patient data
* No real hospital data

## Scope discipline

* Facility-side billing only
* Outpatient-first
* No professional fee scope in V1
* Inpatient logic only where needed for status / timing contrast, not as a major workflow focus

## Control-first

The project must center on:

* charge reconciliation
* prebill exception management
* ownership routing
* correction turnaround
* recurring control failures
* preventable recurrence

The dashboard sits on top of these controls. It does not replace them.

## Deterministic first

* A believable deterministic exception engine is mandatory
* Predictive modeling is secondary
* Scenario simulation must use operationally believable levers

## Action-first

Every page must support an operational decision such as:

* what queue to work first
* which department is overdue
* which issue is still recoverable
* which intervention to test

---

# 5) Review Board Purpose

This Source of Truth is intended for use by three separate domain-review chats before implementation begins.

The review board exists to validate:

* revenue integrity realism
* workflow realism
* coding / documentation realism
* KPI usefulness
* exception taxonomy
* queue ownership
* control design
* synthetic data credibility

No assumption should be treated as hospital-realistic until it can survive review from the appropriate domain expert.

---

# 6) Review Board Roles

## Reviewer 1 — Revenue Integrity / Charge Capture Leader

**Archetype:** Director of Revenue Integrity, Charge Capture Manager, senior Revenue Integrity Analyst lead

### Owns review of:

* exception taxonomy
* chart-to-bill / bill-to-chart logic
* modifier / status integrity
* recoverability assumptions
* charge reconciliation controls
* scenario levers tied to real hospital operations

---

## Reviewer 2 — Patient Financial Services / Billing Operations Leader

**Archetype:** PFS Manager, Billing Operations Manager, Revenue Cycle Operations Manager, Central Business Office Manager

### Owns review of:

* prebill queue design
* aging logic
* routing / ownership logic
* correction / rebill workflow
* backlog assumptions
* operational validation structure

---

## Reviewer 3 — Coding / CDI / Clinical Operations SME

**Archetype:** HIM Coding Supervisor, CDI Specialist, Outpatient Coding Lead, Radiology / OR / Infusion operations leader

### Owns review of:

* documentation dependencies
* modifier realism
* expected-charge logic from clinical activity
* service-line workflow realism
* distinctions among coding, documentation, charge entry, and downstream billing issues

---

# 7) Locked Scope for V1

## Facility-side only

This project focuses on **hospital facility billing**, not professional billing.

## Outpatient-first

The primary environment is outpatient / facility-side charge capture and prebill exception management.

## Service lines / departments to emphasize

V1 should be designed around three anchor stories:

1. **Outpatient Infusion / Oncology Infusion**
2. **Radiology / Interventional Radiology**
3. **OR / Hospital Outpatient Surgery / Procedural Areas**

Optional later expansion:

* ED / Observation
* Cath lab / endoscopy / other interventional areas

## Areas to de-emphasize in V1

* ED facility E/M as a primary V1 story
* broad inpatient DRG optimization
* enterprise denials platform
* professional fee workflows
* payer contracting strategy
* forecasting-heavy finance planning

## Department-freeze rule

The three V1 departments must be explicitly chosen and frozen before build begins.

This project should not attempt a universal expected-charge engine across the whole hospital in V1.

---

# 8) Revised Leakage Story We Want the Data to Tell

The synthetic data should tell a realistic hospital story:

A hospital can lose legitimate revenue — and create compliance risk — through repeated control failures across charge capture, documentation support, modifier/status correctness, reconciliation, and prebill edit management.

The project should reveal that exceptions can be:

* **found**
* **classified**
* **owned**
* **aged**
* **sized**
* **split into recoverable vs already lost**
* **routed for correction**
* **tracked for prevention**

The data should support the narrative that:

* some exceptions are recoverable before final bill
* some are already lost due to timing or missed correction windows
* some represent undercapture risk
* some represent unsupported / compliance risk
* some documented performed activity may not be separately billable or separately payable
* different departments fail in different ways
* recurring issues often come from workflow, build, documentation, or training failures

## Performed → Billable → Payable rule

The control room must visibly respect this chain:

* **performed** does not automatically mean billable
* **billable** does not automatically mean separately payable

Expected-charge logic must be built from **documented performed activity**, not from orders alone and not from the assumption that every documented activity should generate a separately payable facility line.

---

# 8A) Workflow State Model (Mandatory)

The control room must reflect **where the account is stuck now**, not only what issue tags are attached to it.

## Current-state ladder

Each account or claim should move through a stage-based operating model such as:

* Open encounter
* Charge capture pending
* Documentation pending
* Coding pending
* Prebill edit / hold
* Ready to final bill
* Final billed
* Correction / rebill pending
* Closed / monitored through denial feedback only

## One-current-blocker rule

One account may have multiple issue tags, but only **one current primary blocker state**.

This rule is mandatory to prevent double counting, queue duplication, and conflicting aging logic.

## Stage-state operating purpose

The deterministic control room should always be able to answer:

* what stage the account is currently in
* what issue is the primary blocker
* who currently owns the blocker
* how long the account has been in the current stage
* what event exits the stage

# 8B) Recoverability Windows (Mandatory)

Recoverability must be operationally defined rather than inferred loosely.

## Required recoverability states

* Pre-final-bill recoverable
* Post-final-bill recoverable by correction / rebill
* Post-window financially lost
* Financially closed but still compliance-relevant

## Rule

Every open exception should carry a recoverability state based on current workflow stage, timing window, and correction pathway.

Recoverability logic must not be treated as a vague estimate.

# 8C) Queue Operating Definitions (Mandatory)

For each queue in the control room, define:

* business purpose
* entry rule
* exit rule
* aging clock start
* SLA target
* overdue threshold
* accountable owner
* supporting owner
* escalation owner
* escalation trigger

Without these definitions, aging and ownership logic will drift.

# 8D) Stage-Specific Aging Logic

Do not use one generic aging pattern across all workflows.

Separate aging logic should exist for at least:

* open encounter / charge capture pending
* reconciliation pending
* prebill edit / hold
* correction / rebill
* denial feedback signal backlog

Aging buckets and SLA expectations should be stage-specific.

# 9) Exception Taxonomy (Revised)

Do **not** use one flat list of leakage categories.

Use a **two-layer taxonomy**.

## Layer 1 — Issue domain

### 1. Charge capture failure

* Service performed but no charge
* Drug or supply used but no charge
* Wrong encounter linkage / wrong DOS
* Missed timed units
* Missed ancillary or add-on service

### 2. Charge integrity / configuration failure

* Wrong CDM mapping
* Wrong revenue code / CPT / HCPCS
* Wrong default units
* Missing or wrong modifier logic
* Payer-specific configuration gap

### 3. Documentation support failure

* Charged service lacks supporting documentation
* Missing start / stop time
* Missing nursing or procedure documentation
* Order / result / administration mismatch
* Missing medical-necessity support or physician intent where required

### 4. Patient status / case classification failure

* Observation status mismatch
* Observation hours undercaptured
* Wrong outpatient vs inpatient pathway
* Status logic inconsistent with billing path

### 5. Coding failure

* Facility E/M level issue
* Missed procedure coding
* Diagnosis / procedure mismatch
* Coding not aligned to supported documentation

### 6. Billing / claim-edit failure

* Claim stuck in prebill edit queue
* NCCI / MUE / modifier edit unresolved
* Correction / rebill missed
* Late charge after bill finalization window
* Packaged / integral service treated as separately billable

### 7. Packaged / non-billable / false-positive classification

* Activity documented but not separately billable
* Activity billable only if documentation dependencies are met
* Packaged / integral service suppressed correctly
* Expected-charge false positive ruled out by manual audit logic

### 8. Denial feedback signal

* Modifier denial trend
* Medical necessity denial trend
* Upstream workflow issue surfacing as denial pattern
* Repeat payer-specific failure pattern

## Layer 2 — Root cause mechanism

Every issue should also be tagged to one of these:

* People / training
* Workflow / handoff
* System build / interface
* CDM / rule configuration
* Documentation behavior
* Coding practice
* Billing edit management
* Payer-policy variance

## Mandatory distinction

The project must clearly distinguish:

* revenue integrity issues
* coding issues
* billing issues
* documentation issues

If those blur together, the project will not feel hospital-native.

---

# 10) Analytical Layers (Revised)

## Layer 1 — Deterministic exception engine

This is the foundation of the project.

### Purpose

Answer:

* What should have been captured or reviewed?
* What actually happened?
* What exception exists?
* Who owns it?
* Is it still recoverable?
* What control failed?

### Required outputs

* issue domain
* root cause mechanism
* owner team
* aging bucket
* recoverability status
* recommended action
* dollars at risk
* dollars recoverable now
* dollars already lost

## Layer 2 — Operational scenario simulation

The scenario layer should model what happens if specific controls improve.

### Purpose

Support practical operational decision-making, not vague financial fantasy.

### Example levers

* % of departments reconciling within policy window
* modifier automation adoption rate
* prebill edit clearance rate
* staff training completion rate
* charge correction turnaround days
* CDM correction turnaround time
* exception routing speed to owners

## Layer 3 — Predictive prioritization (optional / secondary)

A predictive layer may be added later to help triage open encounters or accounts.

### Purpose

Prioritize review workload after deterministic rules are trusted.

### Important note

Predictive scoring is **not** the credibility engine of this project.
The deterministic control layer is.

---

# 11) Revised Core Data Model

This project should not rely on one giant flat table.
It should be built around realistic facility-side control data.

## encounters

**Grain:** one row per encounter

### Candidate fields

* encounter_id
* facility_account_id
* patient_type
* admit_datetime
* discharge_datetime
* service_line
* department
* encounter_setting
* payer_group
* status_pathway
* final_bill_status
* final_bill_datetime

---

## claims_or_account_status

**Grain:** one row per account / claim workflow header

### Candidate fields

* claim_id
* encounter_id
* account_status
* current_prebill_stage
* current_primary_blocker_state
* current_queue
* claim_create_datetime
* bill_hold_start_datetime
* scrubber_release_datetime
* final_bill_datetime
* first_submit_datetime
* rebill_flag
* corrected_claim_flag

### Purpose

This is the central workflow-state header for billing operations.

Use it to model where the account is currently stuck, what queue currently owns it, and which billing-stage milestones have already occurred.

---

## orders

**Grain:** one row per order / ordered clinical event

### Candidate fields

* order_id
* encounter_id
* order_type
* order_datetime
* procedure_or_med_code
* ordering_provider
* order_status

---

## documentation_events

**Grain:** one row per relevant documentation event

### Candidate fields

* doc_event_id
* encounter_id
* documentation_type
* event_datetime
* support_complete_flag
* start_time
* stop_time
* documentation_gap_type

---

## upstream_activity_signals (optional but recommended)

**Grain:** one row per upstream charge-relevant clinical or operational signal

### Candidate fields

* signal_id
* encounter_id
* department
* signal_type
* source_system
* source_reference_id
* signal_datetime
* expected_code_hint
* expected_modifier_hint
* expected_units_hint
* documentation_dependency_flag
* support_status
* separately_billable_flag
* packaged_or_integral_flag
* billability_basis_note

### Purpose

Use this table if expected-charge derivation requires more explicit source behavior than can be cleanly represented through orders, documentation events, or charge-event references alone.

This table may represent:

* procedure logs
* medication administration
* supply / implant usage
* OR time
* other upstream activity that drives expected-charge logic

Expected-charge derivation should prefer **documented performed activity** from this table or equivalent source structures, not orders alone.

## charge_events

**Grain:** one row per charge event posted or expected

### Candidate fields

* charge_event_id
* encounter_id
* source_type
* source_reference_id
* CPT_HCPCS_code
* revenue_code
* modifier_code
* units
* amount
* charge_datetime
* charge_status
* expected_flag

---

## claim_lines

**Grain:** one row per claim line / billed line

### Candidate fields

* claim_line_id
* encounter_id
* claim_id
* bill_type
* line_code
* modifier_code
* billed_units
* billed_amount
* final_billed_flag
* bill_drop_datetime

---

## edits_bill_holds

**Grain:** one row per prebill edit or hold

### Candidate fields

* edit_id
* encounter_id
* claim_id
* issue_domain
* edit_type
* opened_datetime
* resolved_datetime
* age_days
* current_owner_team
* resolution_status

---

## corrections_rebills

**Grain:** one row per correction / rebill activity

### Candidate fields

* correction_id
* encounter_id
* claim_id
* correction_type
* correction_open_datetime
* correction_close_datetime
* turnaround_days
* outcome_status

---

## denials_feedback

**Grain:** one row per denial signal

### Candidate fields

* denial_id
* encounter_id
* claim_id
* denial_category
* denial_reason_group
* payer_group
* denial_amount
* linked_upstream_issue_domain

### Denial Feedback Guardrail

Denial feedback is included only as a signal layer to validate or surface upstream control failures.

It is not intended to make this project:

* a denials-management platform
* a payer adjudication engine
* a full denial-appeal workflow tool

Denials should remain downstream evidence of control failure, not the central operating scope.

---

## department_charge_logic_map (mandatory)

**Grain:** one row per department-specific activity-to-charge logic rule

### Candidate fields

* logic_rule_id
* department
* clinical_event_type
* required_documentation_elements
* expected_facility_charge_opportunity
* common_modifier_logic
* separately_billable_flag
* packaged_or_integral_flag
* typical_failure_mode
* evidence_completeness_rule

### Purpose

This table is the department-specific source of truth that maps performed activity to expected facility charge opportunity and explains when an activity is not separately billable.

---

## cdm_reference

**Grain:** one row per CDM / rule reference item

### Candidate fields

* cdm_item_id
* department
* service_line
* expected_code
* expected_modifier
* default_units
* revenue_code
* active_flag
* last_update_datetime

---

## exception_queue

**Grain:** one row per routed exception item

### Candidate fields

* queue_item_id
* encounter_id
* claim_id
* current_primary_blocker_state
* issue_domain
* root_cause_mechanism
* exception_type
* accountable_owner
* supporting_owner
* escalation_owner
* department
* service_line
* aging_bucket
* sla_status
* recoverability_status
* dollars_recoverable_now
* dollars_already_lost
* evidence_completeness_status
* why_not_billable_explanation
* recommended_action
* opened_date
* resolved_date

### Rule

An account may carry multiple issue tags, but queue routing must always anchor to one current primary blocker state.

---

## queue_history

**Grain:** one row per queue transition or routing event

### Candidate fields

* queue_history_id
* encounter_id
* claim_id
* prior_queue
* current_queue
* prior_owner
* current_owner
* first_routed_datetime
* last_routed_datetime
* reroute_count
* days_in_prior_queue
* routing_reason

### Purpose

Use this table to make bottlenecks, handoff failures, and repeat rerouting visible.

---

# 12) KPI Layer (Revised)

The KPI layer must reflect real control management.

## Primary KPIs

* Unreconciled encounter rate
* Late charge rate
* Charge reconciliation completion within policy window
* Time to charge entry
* Prebill edit aging
* Recoverable dollars still open
* Dollars already lost after timing window
* Department repeat exception rate
* Modifier-related preventable edit rate
* Correction turnaround days
* Unsupported charge rate
* Edit first-pass clearance rate

## Secondary KPIs

* Charge-to-final-bill days
* Discharge-to-final-bill days for inpatient-specific contrast only
* Leakage dollars per 100 encounters
* Leakage dollars per case

## KPI caution flags

The following should not be used lazily:

* generic missing modifier rate
* one-size-fits-all discharge-to-bill lag
* black-box expected-vs-billed gap score
* overall leakage variance % without denominator discipline

Every KPI must have:

* numerator
* denominator
* exclusions
* grain
* claim-setting applicability

## KPI Definition Rule

Before implementation, each primary KPI must have a documented definition including:

* business purpose
* numerator
* denominator
* exclusions
* grain
* applicable settings
* owner
* interpretation caveats

No KPI should appear in the app unless its definition is documented and approved.

## Deferred KPI note

The following metrics are removed from early scope unless explicit supporting structures are later added:

* audit yield rate
* department attestation completion rate
* observation-hours exception rate

If these are ever retained later, they require explicit source tables and workflow logic such as:

* audit_reviews
* department_attestations

They should not re-enter the KPI list without corresponding modeled data structures.

---

# 13) Queue Prioritization Logic (Revised)

A key feature of the control room is routing the right work first.

## Proposed priority score

`0.35 * normalized_recoverable_dollars + 0.20 * repeat_exception_rate + 0.15 * aging_severity + 0.10 * preventable_share + 0.10 * sla_breach_risk + 0.10 * fixability_score`

## Interpretation

The project should prioritize work not just by size, but by:

* current recoverability
* repeat failure pattern
* urgency
* likelihood of prevention
* actionability

## Priority component definition rule

The following components must be explicitly defined before they appear in a score:

* preventable_share
* fixability_score
* sla_breach_risk

If these components are not defined transparently, they should not be used in the priority formula.

## Mandatory queue fields

Every exception should display:

* issue domain
* root cause mechanism
* owner team
* department
* aging
* SLA status
* recoverability
* dollars at risk
* recommended next step

---

# 14) Streamlit App Structure (Revised)

The app should feel like a **control environment**, not just an executive dashboard.

## Phase-to-Page Delivery Map

The page architecture below reflects the full product roadmap, not the V1 build requirement.

### V1 pages

* Control Room Summary
* Charge Reconciliation Monitor
* Modifiers / Edits / Prebill Holds
* Documentation Support Exceptions
* Opportunity & Action Tracker

### V2 pages

* Scenario Lab

### V3 pages

* Predictive Triage
* Exports / memo layer / alerts as applicable

Only the pages required for deterministic control-room operation should be considered mandatory in V1.

## Page 1 — Control Room Summary

### Purpose

Fast operational scan of open exceptions and control health

### Should show

* open exceptions by issue domain
* recoverable dollars now vs already lost
* exceptions breaching SLA
* departments overdue on reconciliation
* top owner queues
* trend in open exception backlog

---

## Page 2 — Charge Reconciliation Monitor

### Purpose

Track completion and timeliness of reconciliation controls

### Should show

* reconciliation completion within policy window
* unreconciled encounters
* overdue departments
* exception aging by service line
* control completion trend

---

## Page 3 - Modifiers / Edits / Prebill Holds

### Purpose

Surface unresolved edits and modifier-related failures

### Should show

* prebill edit aging
* unresolved modifier-related edits
* edit first-pass clearance
* repeat payer / department patterns

---

## Page 4 - Documentation Support Exceptions

### Purpose

Separate unsupported or under-supported charges from pure routing failures

### Should show

* unsupported charge trends
* missing time documentation
* order / documentation / admin mismatches
* owner routing between operations, coding, and documentation review

---

## Page 5 - Opportunity & Action Tracker

### Purpose

Prioritize intervention and track corrections

### Should show

* recoverable now vs lost
* queue priority ranking
* owner assignments
* correction turnaround
* recurring issue pattern
* education vs build vs coding vs billing action path
* intervention owner
* target completion date
* checkpoint status
* baseline metric
* current metric
* before / after validation note
* hold / expand / revise recommendation

### Rule

The action tracker must support visible intervention follow-through, not just exception ranking.

---

## Page 7 — Scenario Lab

### Purpose

Model operational improvement using believable control levers

### Should show

* operational sliders
* projected recoverable dollar lift
* projected backlog reduction
* projected SLA improvement
* 90-day impact estimate

---

## Page 8 — Predictive Triage (Optional Later)

### Purpose

Support review prioritization after deterministic controls are stable

### Should show

* at-risk encounter buckets
* suggested review candidates
* model transparency summary
* performance at operational thresholds

---

# 15) Synthetic Data Requirements (Revised)

The synthetic data must tell a believable control-failure story.

## Required characteristics

* Departments behave differently
* Facility and professional billing are clearly separated
* Outpatient vs inpatient logic is not blurred
* Expected signals come from believable upstream sources
* Expected signals are grounded in documented performed activity, not orders alone
* Exceptions cluster by service line and workflow type
* Not all failures are underbilling; some are unsupported / compliance risk
* Some cases should resolve to packaged / integral / not separately billable / false positive
* Exceptions can move through review, correction, and prevention states

## Expected signals should be grounded in things like

* orders
* documentation events
* procedure logs
* medication administration
* OR time
* supply or implant usage
* CDM / modifier logic
* prebill edit conditions

These signals may be represented through:

* orders
* documentation_events
* source_reference_id in charge_events
* upstream_activity_signals when more explicit traceability is needed

## Example story rules

* Outpatient infusion depends on start / stop times, sequencing, hydration rules, separate-access logic, unit conversion, and waste scenarios
* Radiology / IR depends on completed-study status, site / laterality / distinctness support, contrast / device linkage where relevant, and facility-side workflow realities
* OR / procedural areas depend on case status, discontinued-procedure states, implant / device / supply linkage, and documentation timestamp dependency
* Modifier failures are patterned and clinically justified, not random
* Late charges are more likely in certain departments and handoff-heavy workflows
* Repeat exceptions should point back to workflow, build, or education problems
* Some expected activities should intentionally suppress to packaged / integral / not separately billable outcomes

## Anti-patterns to avoid

* one universal workflow for every department
* no separation between facility and professional billing
* no distinction between outpatient and inpatient logic
* expected charges generated from the same rule table as billed charges
* building expected charges from orders instead of documented performed activity
* assuming every documented activity creates a separately payable line
* uniform leakage rates everywhere
* random modifier omissions with no workflow pattern
* only underbilling and never unsupported / overbilled / packaged / false-positive outcomes
* no correction history
* no recoverability logic
* predictive features that use post-resolution or post-denial information

---

# 16) Predictive Modeling Expectations (Demoted)

The predictive layer is optional in the early build.

## Candidate targets

* open exception escalation risk
* late-charge risk
* unreconciled encounter risk
* high-priority review candidate flag
* false-positive suppression support candidate

## Candidate features

* department
* service_line
* encounter_setting
* discharge timing
* weekend / after-hours timing
* documentation completeness signals
* activity complexity
* charge count complexity
* historical department lag patterns
* open edit burden

## Recommended modeling path

Start with:

* logistic regression baseline

Then compare with:

* gradient boosting model

## Recommended evaluation

* AUC
* precision / recall
* threshold-based usefulness
* feature importance
* workload lift by risk bucket

## Framing

The model is a **workqueue prioritization aid** after deterministic exception rules are trusted.
It is not the core product story.

---

# 17) Scenario Simulation Expectations (Reframed)

The scenario layer is still required, but it must use operationally believable levers.

## Required levers

At minimum, the simulation layer should support:

* departments reconciling within policy window
* modifier automation adoption
* prebill edit clearance rate
* training completion rate
* correction turnaround speed
* CDM correction turnaround
* routing speed to owner teams

## Required outputs

* projected recoverable dollar lift
* projected open-exception reduction
* projected SLA improvement
* projected lost-dollar prevention
* 90-day impact estimate
* simple implementation effort framing

## Important rule

All scenario logic must be transparent and auditable.
No fake “AI magic” simulator.

---

# 18) 30-60-90 Validation Framing (Revised)

## 30 days

* validate deterministic exception rules
* validate service-line stories
* identify top owner queues
* establish baseline recoverable vs lost opportunity
* confirm queue routing and ownership
* run manual sampled audit review against early exception classes

## 60 days

* pilot interventions in 1–2 high-risk areas
* monitor backlog, aging, and SLA improvement
* measure correction turnaround improvement
* assess repeat exception reduction
* compare exception precision by leakage class and false-positive class

## 90 days

* quantify recoverable dollars improved
* validate reduction in repeat exceptions
* compare hold / expand / revise recommendation
* identify build, education, or workflow fixes to scale

---

# 19) Out of Scope for Early Build (Revised)

To keep this flagship project disciplined, the following stay out of scope initially:

* professional fee billing analytics
* enterprise denials platform
* full claims adjudication engine
* full payer contract modeling
* broad inpatient DRG optimization
* NLP on clinical notes
* enterprise auth / permissions
* feature sprawl unrelated to facility-side controls

---

# 20) Revised Build Order

## V1

* lock facility-side outpatient-first scope
* freeze three anchor service-line stories: Outpatient Infusion / Oncology Infusion, Radiology / Interventional Radiology, OR / Hospital Outpatient Surgery / Procedural Areas
* define workflow state model and one-current-blocker rule
* define queue operating definitions and stage-specific aging rules
* build upstream signal tables (orders, documentation, charge events)
* build minimum claims_or_account_status structure
* build deterministic exception engine
* build exception queue with owner / SLA / aging / recoverability
* build queue-history minimum fields needed for routing visibility
* build V1 pages: Control Room Summary, Charge Reconciliation Monitor, Modifiers / Edits / Prebill Holds, Documentation Support Exceptions, Opportunity & Action Tracker

## V2

* add operational scenario lab
* add correction / rebill tracking
* add denial feedback and CDM governance monitor
* expand action tracker

## V3

* add predictive triage
* add exports / memo layer
* add threshold alerts and polish

## Build Dependency Clarification

Some tables or concepts may appear in the core model before their full operational views are implemented.

### V1 requirement

Model only the minimum fields needed to support deterministic exception routing.

### V2 requirement

Expand correction / rebill tracking, denial feedback usage, and CDM governance views into fuller operational workflows.

Presence in the data model does not automatically mean full V1 UI or workflow scope.

---

# 21) Reviewer Questions to Keep in Mind

All reviewers should pressure-test the same core questions:

1. Does this feel like a hospital facility-side control room?
2. Does each exception map to a believable failed control?
3. Are issue domain and root cause clearly separated?
4. Is ownership clear?
5. Are recoverability and aging believable?
6. Would a real RI or billing leader use this queue?
7. Do the service-line stories feel authentic?
8. Do the scenario levers feel operationally real?
9. Is predictive modeling staying in its lane?
10. What would make this feel fake?

---

# 22) Sign-Off Criteria Before Build Begins (Revised)

The pre-build board should not approve implementation until these conditions are met:

## Scope clarity

* facility-side only
* outpatient-first scope approved
* no professional fee creep
* three anchor service-line stories approved and frozen
* V1 explicitly limited to outpatient / procedural revenue integrity

## Control realism

* deterministic exception engine approved
* issue-domain taxonomy approved
* root-cause mechanism taxonomy approved
* queue ownership approved
* recoverability logic approved

## Workflow realism

* prebill edit / hold logic approved
* correction / rebill pathway approved
* SLA / aging structure approved
* 30-60-90 validation structure approved

## Data model clarity

At minimum, approved structure for:

* encounters
* orders
* documentation_events
* charge_events
* claim_lines
* edits_bill_holds
* corrections_rebills
* denials_feedback
* cdm_reference
* exception_queue

## KPI clarity

* KPI list approved
* data dictionary approved for each KPI
* claim-setting applicability approved
* prioritization score approved

## Synthetic data realism

* service-line behavior rules approved
* anti-pattern list approved
* undercapture and compliance-risk balance approved
* packaged / integral / false-positive logic approved
* correction history and audit trail logic approved
* modifiers are rule-based, not randomized
* department-specific performed-activity → expected-charge maps approved
* manual audit rubric exists before modeling starts

## Forward-looking layer

* operational scenario levers approved
* predictive layer purpose constrained and approved

---

# 23) Success Definition (Revised)

This project succeeds if it demonstrates:

* facility-side hospital realism
* believable charge reconciliation controls
* department-specific performed-activity → expected-charge logic
* prebill exception management logic
* clear ownership routing
* recoverable vs lost opportunity framing
* visible packaged / integral / false-positive suppression logic
* operational prioritization
* realistic scenario planning
* optional predictive triage that supports, not replaces, deterministic control logic
  The project fails if it feels like:
* generic healthcare BI
* one giant revenue leakage blob
* fake synthetic claims logic
* AI theater without workflow specificity
* a dashboard with healthcare labels but no control environment

---

# 24) One-Sentence Portfolio Pitch (Revised)

Built a hospital facility-side outpatient revenue integrity control room in Streamlit that maps documented performed activity to expected facility charge opportunities, identifies documentation, modifier, charge-entry, and prebill exception failures, routes them to the right owners, suppresses non-billable false positives, and simulates the impact of targeted workflow improvements.

---

# 25) Final Rule

If an assumption cannot survive challenge from the relevant domain reviewer, it should not yet be treated as hospital-realistic.

This project must earn realism before it earns polish.

And it must earn control specificity before it earns sophistication.
