# KPI Dictionary

## Title and purpose

This document is the governed KPI dictionary for V1 only. It defines the exact meaning, scope, numerator, denominator, exclusions, and usage warnings for every metric allowed in the V1 outpatient facility-side control room.

This file exists to prevent KPI drift, denominator sloppiness, and vague dashboard math. It follows the governed V1 direction established in `docs/build_sot.md` and the execution contract in `docs/V1_IMPLEMENTATION_PLAN.md`.

## KPI governance rule

No KPI may appear in a V1 dashboard, data model, requirements doc, or demo unless it is defined in this file using the required template. If a metric name, denominator, exclusion rule, or grain changes, the dictionary must be updated before the metric is treated as governed.

Governance rules for V1:

- V1 metrics apply only to the frozen V1 departments.
- V1 metrics must be deterministic and reproducible from declared source fields and rules.
- A KPI may not reuse another KPI's name with different logic.
- A KPI may not be implemented with a hidden fallback denominator or analyst-side adjustment.
- Deferred metrics are explicitly out of V1 even if the raw data exists.

## Current implementation status

`kpi_snapshot.parquet` currently publishes these governed KPI rows:

- Unreconciled encounter rate
- Charge reconciliation completion within policy window
- Unsupported charge rate
- Late charge rate
- Time to charge entry
- Prebill edit aging
- Department repeat exception rate
- Recoverable dollars still open
- Dollars already lost after timing window
- Edit first-pass clearance rate

`kpi_snapshot.parquet` also publishes `Transparent reduced V1 priority score` rows for active queue items.

The repo now also includes thin current support for correction follow-through in `intervention_tracking.parquet` and `corrections_rebills.parquet`. That support improves operating realism, but it does not by itself mean `Correction turnaround days` is already a published KPI row.

## Global metric conventions

The following conventions apply to every V1 KPI unless the KPI definition says otherwise:

- Scope is limited to Outpatient Infusion / Oncology Infusion, Radiology / Interventional Radiology, and OR / Hospital Outpatient Surgery / Procedural Areas.
- Scope is outpatient facility-side only. Inpatient, ED-first, and Observation-first workflows are excluded from V1 KPI logic.
- The operational unit is either the encounter, the procedure unit, the charge line, or the blocker item, as specified in each KPI's grain.
- Policy windows are department- and blocker-specific values from governed rules. V1 does not use a single enterprise-wide lag standard.
- Unless noted otherwise, reporting should use service-date eligibility for operational rates and resolution-date eligibility for turnaround metrics.
- Cancelled cases, no-shows, test patients, training records, and encounters without expected chargeable activity are excluded.
- Dollar metrics refer to estimated gross charge dollars at risk or lost. They are not cash, net revenue, contractual allowance, or margin metrics.
- Snapshot metrics and flow metrics must not be trended as if they are the same thing. A snapshot shows what is open at a point in time; a flow metric shows what happened during a period.
- The one-current-blocker rule from V1 applies to primary operational queue metrics. Supporting detail may exist underneath, but the top-line metric logic must respect the governed blocker state.

## Required KPI template

Every V1 KPI definition must include:

- KPI name
- business purpose
- numerator
- denominator
- exclusions
- grain
- applicable settings
- owner
- interpretation caveats
- why leadership cares
- likely misuse / warning

## Primary V1 KPI definitions

### Unreconciled encounter rate

- KPI name: Unreconciled encounter rate
- business purpose: Shows how much eligible outpatient work has not yet completed charge reconciliation after it should reasonably be complete.
- numerator: Count of eligible encounters or procedure units in frozen V1 departments that remain unreconciled at the reporting cutoff and have reached the point where reconciliation should be complete under policy.
- denominator: Count of eligible encounters or procedure units in frozen V1 departments that have reached the point where reconciliation should be complete under policy at the same reporting cutoff.
- exclusions: Cancelled cases, no-shows, test or training records, encounters without expected chargeable activity, and items still too early to evaluate under department policy.
- grain: Encounter or procedure unit snapshot at report cutoff, using the governed operational unit for the department.
- applicable settings: Outpatient Infusion / Oncology Infusion, Radiology / Interventional Radiology, OR / Hospital Outpatient Surgery / Procedural Areas.
- owner: Revenue Integrity operations.
- interpretation caveats: This is a snapshot rate, not a throughput rate. High-acuity procedural areas may legitimately have later completion timing than straightforward infusion visits, so policy windows must be department-specific.
- why leadership cares: It shows current operational exposure and whether the control room is keeping the queue from aging into avoidable loss.
- likely misuse / warning: Do not divide by all encounters seen in the period. Only eligible encounters that should already be reconciled belong in the denominator.

### Late charge rate

- KPI name: Late charge rate
- business purpose: Measures how often charges are entered after the governed department policy window, indicating delayed capture and elevated loss risk.
- numerator: Count of posted charge lines entered after the applicable department policy window measured from service completion or procedure completion.
- denominator: Count of posted charge lines tied to eligible V1 encounters or procedure units in the same reporting period.
- exclusions: Void-only correction lines, test patients, cancelled/no-show cases, retroactive system conversions, and charges with approved backdated exceptions documented in the action tracker.
- grain: Charge line.
- applicable settings: All frozen V1 departments.
- owner: Department operations with Revenue Integrity support.
- interpretation caveats: Departments with documentation dependency or staged procedure closeout may have different normal timing. Comparisons are only valid when the policy window is configured correctly for each department.
- why leadership cares: Late charge behavior is an early operational signal for missed revenue and unstable close processes.
- likely misuse / warning: Do not use one universal late threshold across infusion, radiology, and procedural areas.

### Charge reconciliation completion within policy window

- KPI name: Charge reconciliation completion within policy window
- business purpose: Measures whether eligible outpatient work is fully reconciled before the governed deadline.
- numerator: Count of eligible encounters or procedure units completed as reconciled within the applicable policy window, meaning expected charges are posted or explicitly cleared as not required and no active primary blocker remains.
- denominator: Count of eligible encounters or procedure units whose reconciliation outcome can be evaluated in the reporting period.
- exclusions: Cancelled/no-show cases, encounters without expected chargeable activity, test records, and cases still inside the policy window at period end.
- grain: Encounter or procedure unit.
- applicable settings: All frozen V1 departments.
- owner: Revenue Integrity operations.
- interpretation caveats: This is the preferred completion KPI for V1 because it respects department-specific policy windows. It should not be replaced with a generic discharge-to-bill lag.
- why leadership cares: It shows whether the operating model is meeting the organization's own standard for timely reconciliation.
- likely misuse / warning: Do not count an item as complete just because a bill exists; it must also have no active current blocker under V1 rules.

### Time to charge entry

- KPI name: Time to charge entry
- business purpose: Quantifies how long it takes for chargeable work to appear as posted charges after service completion.
- numerator: Sum of elapsed hours from service completion or procedure completion to first posted charge entry across eligible units.
- denominator: Count of eligible encounters or procedure units with at least one posted charge.
- exclusions: Cancelled/no-show cases, non-chargeable visits, test patients, and units with missing service completion timestamps that prevent valid timing calculation.
- grain: Encounter or procedure unit.
- applicable settings: All frozen V1 departments.
- owner: Department operations.
- interpretation caveats: This is an average elapsed-time measure. It is sensitive to timestamp quality and can be skewed by a small number of very late entries; median may be reviewed later, but average is the governed V1 definition.
- why leadership cares: It exposes operational delay before issues become unrecoverable or hit prebill queues.
- likely misuse / warning: Do not compare this metric to billing lag or claim-drop timing. It measures charge entry only.

### Prebill edit aging

- KPI name: Prebill edit aging
- business purpose: Shows how long open prebill edit items are sitting unresolved in the current queue.
- numerator: Sum of open age in calendar days for all active prebill edit blocker items at the report cutoff.
- denominator: Count of active prebill edit blocker items at the same cutoff.
- exclusions: Closed edits, items with documented approved hold status outside normal workflow, test records, and edits outside the frozen V1 departments.
- grain: Blocker item snapshot.
- applicable settings: All frozen V1 departments where prebill edit logic exists.
- owner: Revenue Integrity operations.
- interpretation caveats: This is a snapshot aging measure, not a completion measure. One old edit can materially move the average in a small queue.
- why leadership cares: Aging prebill edits directly threaten timely billing and reveal whether queue cleanup is keeping pace with inbound work.
- likely misuse / warning: Do not blend open-item aging with turnaround for items already resolved. Those are different metrics with different operational meaning.

### Recoverable dollars still open

- KPI name: Recoverable dollars still open
- business purpose: Quantifies the estimated gross charge value that is still recoverable but remains unresolved in the active queue.
- numerator: Sum of estimated gross charge dollars tied to open or at-risk recoverable blocker items at the report cutoff.
- denominator: Total estimated gross charge dollars tied to all blocker items identified in scope at the same cutoff.
- exclusions: Expired items already classified as lost, items lacking governed dollar estimation logic, test records, and out-of-scope departments.
- grain: Blocker item snapshot with dollar rollup.
- applicable settings: All frozen V1 departments.
- owner: Revenue Integrity leadership.
- implementation note: The current V1 synthetic build estimates blocker dollars from encounter-level non-suppressed gross charge totals. If a recoverable missed-charge item has no posted charge yet, the fallback estimate is the department median eligible encounter gross amount. This fallback is explicit and deterministic; no modeled cash conversion is used.
- interpretation caveats: The headline value is the numerator dollar amount. The denominator exists to support optional share-of-total context, but the primary KPI is the dollar exposure itself. This is gross charge exposure, not expected cash.
- why leadership cares: It quantifies how much recoverable value is still sitting in the queue waiting for action.
- likely misuse / warning: Do not present this as collectible revenue or as a finance forecast.

### Dollars already lost after timing window

- KPI name: Dollars already lost after timing window
- business purpose: Quantifies the estimated gross charge dollars tied to blocker items that have moved beyond their recoverability window.
- numerator: Sum of estimated gross charge dollars tied to blocker items classified as expired or lost under governed recoverability rules.
- denominator: Total estimated gross charge dollars tied to all blocker items identified in scope during the reporting period.
- exclusions: Items later reopened through approved exception handling, items lacking governed dollar estimation logic, test records, and out-of-scope departments.
- grain: Blocker item period total.
- applicable settings: All frozen V1 departments.
- owner: Revenue Integrity leadership.
- implementation note: The same explicit encounter-level gross-dollar estimation rule used for `Recoverable dollars still open` is used here. Suppressed packaged or non-billable encounters are not counted as lost dollars.
- interpretation caveats: This is a consequence metric driven by the configured recoverability window. It is valid only if the lost classification logic is consistent and auditable.
- why leadership cares: It translates unresolved operational defects into visible financial loss exposure.
- likely misuse / warning: Do not mix this with write-offs, denials, or cash loss. It is a governed gross charge loss estimate for V1 control-room use.

### Department repeat exception rate

- KPI name: Department repeat exception rate
- business purpose: Identifies departments where the same types of exceptions recur after prior correction, signaling process instability rather than isolated misses.
- numerator: Count of blocker items in a department whose current exception type matches a previously resolved exception type for the same department-defined operational pattern within the repeat lookback window.
- denominator: Count of blocker items created in that department during the reporting period.
- exclusions: One-off nonrepeat exception types flagged as external, test records, and blocker items without enough history to evaluate repeat logic.
- grain: Blocker item by department.
- applicable settings: All frozen V1 departments, with repeat lookback window governed in rules.
- owner: Department operations leader.
- interpretation caveats: Repeat logic depends on a governed repeat key and lookback window. Comparisons are only valid when the same repeat logic is applied consistently across departments.
- why leadership cares: It distinguishes queue volume caused by persistent workflow defects from queue volume caused by ordinary operational variation.
- likely misuse / warning: Do not use raw counts alone. High-volume departments naturally generate more exceptions; the rate is what makes departments comparable.

### Modifier-related preventable edit rate

- KPI name: Modifier-related preventable edit rate
- business purpose: Measures the share of modifier-related edit volume that should have been prevented through correct charge capture or coding workflow.
- numerator: Count of modifier-related blocker items classified by governed rules as preventable because the modifier was missing, incomplete, or inconsistent with available documentation and could have been captured correctly upstream.
- denominator: Count of eligible encounters, procedure units, or charge lines subject to modifier-related rules in the reporting period.
- exclusions: Payer-unique edits not governed in V1 rules, edits caused solely by downstream system defects, cases with insufficient documentation to determine preventability, and test records.
- grain: Modifier-related blocker item against the department's governed operational unit.
- applicable settings: Departments and services where modifiers are a governed V1 rule domain.
- owner: Revenue Integrity with coding support.
- interpretation caveats: This is intentionally narrower than a generic missing modifier rate. It counts only governed modifier-related edits that are classified as preventable.
- why leadership cares: It points to avoidable rework and training opportunities with direct operational impact.
- likely misuse / warning: Do not relabel every modifier edit as preventable. Preventability must be rule-based and auditable.

### Correction turnaround days

- KPI name: Correction turnaround days
- business purpose: Measures how quickly the organization resolves blocker items once they enter the governed workflow.
- numerator: Sum of calendar days from blocker item creation timestamp to blocker item resolution timestamp for items resolved in the reporting period.
- denominator: Count of blocker items resolved in the reporting period.
- exclusions: Still-open items, reopened items not yet re-resolved, test records, and items lacking valid start or resolution timestamps.
- grain: Resolved blocker item.
- applicable settings: All frozen V1 departments.
- owner: Revenue Integrity operations.
- interpretation caveats: This is a flow metric based on resolved items only. It does not describe the age of open inventory.
- why leadership cares: It shows whether teams are clearing issues fast enough once work is identified.
- likely misuse / warning: Do not compare this directly to prebill edit aging. One measures resolved flow; the other measures open backlog age.

### Unsupported charge rate

- KPI name: Unsupported charge rate
- business purpose: Measures how often posted charges lack the required order, documentation, or procedural support defined by governed V1 rules.
- numerator: Count of posted charge lines flagged as unsupported because required supporting documentation, order evidence, or procedural linkage is missing or inconsistent under V1 rules.
- denominator: Count of posted charge lines in eligible frozen-scope departments during the reporting period.
- exclusions: Charges on cancelled/no-show cases, charges exempted by governed department rule, test records, and charges where support exists but source-system linkage is temporarily delayed under an approved exception.
- grain: Charge line.
- applicable settings: All frozen V1 departments where support rules are governed.
- owner: Revenue Integrity with department leadership.
- interpretation caveats: This metric is only comparable when support requirements are defined consistently by department and charge type. Procedural areas may require more nuanced support logic than infusion visits.
- why leadership cares: It indicates compliance and revenue risk tied to insufficient charge support before issues become write-offs or audit findings.
- likely misuse / warning: Do not use this KPI as a proxy for fraud or intent. It is an operational support-quality measure.

### Edit first-pass clearance rate

- KPI name: Edit first-pass clearance rate
- business purpose: Measures how often prebill edits or bill holds are cleared without repeat routing, reopen, or secondary escalation.
- numerator: Count of prebill edit or bill-hold items resolved on their first routed pass without reopen, reroute back into active work, or repeat escalation.
- denominator: Count of prebill edit or bill-hold items closed in the reporting period.
- exclusions: Items still open at period end, test records, edits closed only because of account cancellation, and items lacking enough routing history to determine whether first-pass clearance occurred.
- grain: Resolved edit or bill-hold item using queue-history-backed workflow outcome.
- applicable settings: All frozen V1 departments where prebill edit or bill-hold workflow exists.
- owner: Revenue Integrity operations with billing operations support.
- interpretation caveats: This is a flow quality metric, not a backlog metric. It depends on reliable queue history and consistent reopen or reroute event capture.
- why leadership cares: It shows whether edits are being cleared cleanly the first time or bouncing through avoidable rework.
- likely misuse / warning: Do not treat this as a productivity score for individuals. It is a workflow quality measure and should be interpreted alongside edit complexity and volume.

## Current implementation boundary

The governed V1 KPI dictionary is broader than the current published KPI snapshot. The implemented snapshot is intentionally limited to the KPIs that can be built from existing deterministic V1 tables without inventing hidden rules:

- Unreconciled encounter rate
- Late charge rate
- Charge reconciliation completion within policy window
- Time to charge entry
- Prebill edit aging
- Recoverable dollars still open
- Dollars already lost after timing window
- Department repeat exception rate
- Unsupported charge rate
- Edit first-pass clearance rate

The following governed KPIs remain documented but are not published in the current synthetic KPI snapshot:

- Modifier-related preventable edit rate
- Correction turnaround days

Status notes:

- `Modifier-related preventable edit rate` remains deferred as a published KPI because the current edit realism is narrower than a fully governed preventability numerator/denominator pair.
- `Correction turnaround days` now has thin supporting evidence in `intervention_tracking` and `corrections_rebills`, but it remains deferred as a published KPI row until the repo models a fuller resolved-item flow denominator without hidden shortcuts.

## Transparent V1 priority score

The full source-of-truth score concept includes `preventable_share`, `fixability_score`, and `sla_breach_risk`. Those components are not yet governed as explicit V1 fields, so they are intentionally excluded from the implemented score.

The current implemented score is the reduced V1 priority score:

`100 * (0.50 * normalized_recoverable_dollars + 0.30 * department_repeat_exception_rate + 0.20 * aging_severity)`

Component definitions:

- `normalized_recoverable_dollars`: Active queue-item estimated gross dollars divided by the largest active queue-item estimated gross dollars in the same snapshot.
- `department_repeat_exception_rate`: Current department share of active queue items with reroute evidence in `queue_history` under the reduced V1 repeat rule.
- `aging_severity`: `stage_age_days / overdue_threshold_days`, capped to the 0-1 range so stage-specific SLA rules remain the anchor.

Guardrails:

- No black-box expected-vs-billed gap score is allowed in V1.
- No undefined `preventable_share`, `fixability_score`, or `sla_breach_risk` term may appear in the implemented score.
- Score rows must expose their component values and the exact formula text.

## Deferred KPI list

The following metrics are explicitly deferred or excluded from V1:

- Audit yield rate: deferred because V1 is a deterministic control room, not an audit program optimization layer.
- Department attestation completion rate: deferred because attestation workflow governance is not a frozen V1 page or operating requirement.
- Observation-hours exception rate: deferred because ED/Observation is not a frozen primary V1 department story.
- Generic missing modifier rate: excluded because V1 uses the narrower and governed `Modifier-related preventable edit rate` instead.
- One-size-fits-all discharge-to-bill lag: excluded because V1 is outpatient facility-side and uses department-specific reconciliation windows rather than one enterprise lag.
- Black-box expected-vs-billed gap score: excluded because V1 does not permit opaque scoring or probabilistic expected-charge logic as required KPI math.

## Metric caveats and comparability rules

Use these rules whenever V1 KPIs are compared across departments, periods, or dashboards:

- Do not compare a snapshot KPI to a flow KPI without stating the difference.
- Do not compare departments unless the same eligibility, policy window, and support rules were applied.
- Do not roll inpatient, ED, or Observation populations into V1 outpatient KPI denominators.
- Do not convert gross charge exposure metrics into revenue claims without separate approved finance logic.
- Do not substitute charge-line grain for encounter grain or vice versa.
- Do not count items still inside their policy window as late, lost, or unreconciled.
- Do not treat reopened items as cleanly resolved history without honoring the reopen logic in the action tracker.
- If a policy window, repeat lookback, or preventability rule changes, trend breaks must be disclosed.
