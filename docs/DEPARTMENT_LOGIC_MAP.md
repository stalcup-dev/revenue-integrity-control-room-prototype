# Department Logic Map

## Title and purpose

This document is the department-specific performed-activity-to-charge-opportunity map for the three frozen V1 departments. It shows, in hospital-native terms, how documented activity becomes a potential facility charge opportunity, where billing dependencies differ by department, and why many apparent gaps are not true misses.

This file is limited to the current implemented V1 and should be read alongside `docs/build_sot.md`, `docs/DATA_MODEL.md`, and `docs/SYNTHETIC_DATA_RULES.md`.

## Current implemented coverage

These department maps are not aspirational only. The current synthetic build already uses them to drive:

- expected-charge opportunity generation
- support-gap and suppression realism
- current blocker classification
- owner queue routing
- queue-history transition patterns
- manual-audit sample case selection

Current realism emphasis by department:

- Outpatient Infusion / Oncology Infusion: timed hierarchy, hydration conditionality, waste, and support completeness
- Radiology / Interventional Radiology: completed versus incomplete study state, laterality, distinctness, contrast, and device linkage
- OR / Hospital Outpatient Surgery / Procedural Areas: case state, discontinued-procedure logic, implant / supply linkage, timestamp dependency, and heavier handoff realism

## How to read the map

- Each row is a review pattern, not a billing regulation.
- The tables start with performed activity and documentation evidence, then describe the expected facility-side charge opportunity and the most likely reason the opportunity does or does not become billable.
- `Separately billable?` means whether the activity commonly results in its own facility charge line when documented correctly.
- `Packaged / integral possibility?` highlights where the activity may be real but should not create a separate missed-charge exception.
- `Likely queue destination` is the V1 operational destination if the row turns into an active current blocker.
- `Why it may not be billable` must be read before classifying any row as a true missed charge.

## Common column definitions

| column | meaning |
|---|---|
| clinical event | the department-native event or service that actually happened |
| performed-activity evidence | the documented or system evidence that the event occurred |
| required documentation elements | minimum support expected before the event can be treated as a clean facility charge opportunity |
| expected facility charge opportunity | the likely facility technical charge or charge family expected from the activity |
| common modifier logic | modifier conditions commonly associated with the opportunity when applicable |
| separately billable? | whether the activity typically produces its own facility line when supported |
| packaged / integral possibility? | whether the event may be bundled, packaged, or integral and therefore not separately chargeable |
| common failure mode | the most typical way the opportunity fails or becomes questionable |
| likely queue destination | the most likely V1 queue if action is still required |
| why it may not be billable | the main reason a valid-looking activity should still be suppressed from missed-charge routing |

## Department map: Outpatient Infusion / Oncology Infusion

| clinical event | performed-activity evidence | required documentation elements | expected facility charge opportunity | common modifier logic | separately billable? | packaged / integral possibility? | common failure mode | likely queue destination | why it may not be billable |
|---|---|---|---|---|---|---|---|---|---|
| Initial therapeutic infusion | MAR administration record, infusion start event, nursing administration note | drug name, dose, route, start time, stop time, patient-specific administration confirmation | primary therapeutic infusion administration charge plus associated drug charge where applicable | typically none at facility level unless department-specific drug or wastage rule applies | usually yes | low for the primary infusion administration itself | missing stop time or absent start/stop duration support causes unit uncertainty | Charge Reconciliation Monitor or Documentation Support Exceptions | duration may not meet the threshold for the infusion hierarchy and may fall back to another administration type |
| IV push medication administration | MAR push administration, nurse note, medication administration timestamp | drug, push time, route, administered amount | IV push administration charge plus drug charge where applicable | usually none; some drug-specific modifier rules may still apply | usually yes | low | documented as generic administration without clear push timing or count of pushes | Charge Reconciliation Monitor | documentation may support only one push when multiple pushes were assumed, or the service may already be represented within the documented regimen logic |
| Hydration infusion before or after therapy | start/stop timestamps, hydration documentation, fluid administration record | reason for hydration, start/stop times, distinct hydration period, supporting nursing note where required | hydration administration charge | usually none unless the department has a local distinction rule | sometimes | high; hydration may be conditional, incidental, or integral to primary therapy | hydration documented but not clearly distinct from therapeutic infusion time | Documentation Support Exceptions | hydration may be nonseparately billable because it is supportive, overlapping, too short, or not distinct from the primary infusion hierarchy |
| Concurrent infusion | multiple simultaneous medication administration records, overlapping time evidence | distinct drugs, overlapping start/stop support, primary versus concurrent relationship | concurrent infusion administration charge | none in many cases, but hierarchy must still be correct | sometimes | medium | sequential and concurrent logic confused in documentation or charge selection | Modifiers / Edits / Prebill Holds or Documentation Support Exceptions | the second infusion may not qualify as concurrent if timing does not overlap or hierarchy places it under another administration code |
| Sequential infusion after initial infusion | separate timed administration after initial infusion, sequential nursing documentation | sequential timing, distinct drug or bag, documented changeover, stop/start support | sequential infusion administration charge | generally none; hierarchy logic is the key dependency | sometimes | medium | missing timing distinction between initial and subsequent infusion phases | Charge Reconciliation Monitor | if the event is not clearly sequential, it may collapse into the initial administration logic rather than a separately billable additional line |
| Separate access-site service | vascular access event, line insertion or access documentation distinct from infusion administration | access site documentation, distinct procedure/support note, timing or event evidence showing separate work | separate access-related facility charge when department rules allow it | sometimes local modifier or distinctness logic if same-day overlap exists | sometimes | high; may be integral to the infusion visit | access work assumed billable without support that it was distinct and separately chargeable | Documentation Support Exceptions | access services are often integral to the infusion encounter and may not qualify as separate charge lines |
| Drug charge with unit conversion | pharmacy dispense/admin evidence, MAR administered amount, governed conversion rule | administered quantity, concentration, units, waste if relevant, final administered total | HCPCS or local drug charge converted to billable units | wastage-related modifier may apply when governed and supported | usually yes | low to medium depending on drug packaging logic | administered dose documented, but billed units do not align with governed unit conversion | Charge Reconciliation Monitor or Modifiers / Edits / Prebill Holds | rounded or assumed units may be wrong, and some vial/package situations do not support the anticipated separate units |
| Drug waste scenario | pharmacy prep record, administered amount, discarded amount, nursing waste documentation | drug identity, administered amount, discarded amount, timing, waste documentation, any required witness or support field | waste-related charge opportunity or wastage-related billing treatment | waste modifier logic applies only when the department rule and support requirements are met | sometimes | medium | waste suspected from dose mismatch but discarded amount not explicitly documented | Modifiers / Edits / Prebill Holds or Documentation Support Exceptions | waste may be unsupported, below threshold, included in package assumptions, or governed not to produce a separate valid opportunity |
| Infusion encounter with missing stop time | start time present, medication administration documented, no reliable stop time | complete timed administration support including stop time or sufficient alternative duration evidence | possible infusion administration charge, but only if duration can be supported | no special modifier logic; the dependency is documentation completeness | uncertain | medium | system infers infusion duration from workflow timestamps that are not valid charge support | Documentation Support Exceptions | without valid duration support, the event may not support an infusion-level charge and may only support a lesser administration type or no separate timed charge |

## Department map: Radiology / Interventional Radiology

| clinical event | performed-activity evidence | required documentation elements | expected facility charge opportunity | common modifier logic | separately billable? | packaged / integral possibility? | common failure mode | likely queue destination | why it may not be billable |
|---|---|---|---|---|---|---|---|---|---|
| Completed diagnostic imaging study | study completion status, modality completion event, performed exam record | completed study status, performed exam code, service timestamp, department, accession or exam linkage | facility technical charge for the completed imaging study | usually limited; distinctness or repeat-study logic may apply in select cases | usually yes | low | order exists and room workflow occurred, but performed study status never reached completed | Charge Reconciliation Monitor | a scheduled or initiated study is not enough; incomplete or aborted exams may not support a full technical charge |
| Incomplete or discontinued imaging study | started exam workflow, technologist notes, incomplete study status | explicit incomplete/discontinued status, reason, any partial-performed evidence | sometimes none; sometimes reduced or no charge opportunity depending on department rule | modifier logic varies and may be absent in V1 | often no | high | incomplete study treated as if it were a normal completed exam | False-positive suppression before queueing, or Documentation Support Exceptions if status is unclear | the study may not be billable because it was not completed to technical charge criteria |
| Laterality-dependent imaging or procedure | completed study record plus left/right/bilateral site evidence | laterality or site specificity in the performed record, final study linkage, consistent code-to-site mapping | technical charge for the site-specific study or service | laterality-related coding logic may affect clean billing outcome | usually yes when supported | low | performed event exists but laterality/site specificity is missing or inconsistent | Documentation Support Exceptions or Modifiers / Edits / Prebill Holds | without laterality or site specificity, the charge may be unsupported or unbillable as coded |
| Contrast administration tied to imaging | contrast administration record, completed imaging study, medication/event linkage | contrast amount, timing, study linkage, completed exam support where required | contrast-related facility charge where separately captured under department rules | usually none, but some claim-line logic may still arise | sometimes | medium; may be bundled into the study or not separately charged by local rule | contrast documented in nursing/pharmacy records but not linked to the completed study | Charge Reconciliation Monitor or Documentation Support Exceptions | contrast may be packaged or not separately chargeable for that study type even when administered |
| Interventional device use | procedure log, implant/device entry, procedure completion record | device identity, procedure linkage, quantity, timing, completed intervention support | device or supply-related technical charge where governed | occasionally distinctness or device-related billing logic downstream | sometimes | medium to high depending on procedure family | device documented in the case log but no valid link to the performed intervention or supply record | Charge Reconciliation Monitor | the device may be integral to the primary procedural package or unsupported for separate capture |
| Same-day distinct imaging or interventional services | multiple completed study/procedure records, separate timestamps, separate accession or case segments | evidence that services were distinct, not duplicative, plus separate completion support | separate technical charge opportunities for multiple same-day services | distinctness-related modifier logic may apply where governed | sometimes | medium | same-day repeat or related service lacks support that it was distinct from the primary event | Modifiers / Edits / Prebill Holds or Documentation Support Exceptions | one of the services may not be separately billable if it is duplicative, repeat-without-support, or bundled by rule |
| IR procedure with supply/contrast linkage gap | procedure completion event plus partial supply or contrast evidence | completed case, supply/device/contrast linkage, performed timestamps, case documentation | interventional facility technical charge plus supply or contrast opportunities where applicable | modifier logic less central than documentation linkage | usually yes for the case, variable for add-on supply/contrast lines | medium | procedure posts, but supporting supply or contrast records are late or missing links | Documentation Support Exceptions or Charge Reconciliation Monitor | supporting items may be real but not separately billable, or the missing linkage may prevent them from becoming valid opportunities |

## Department map: OR / Hospital Outpatient Surgery / Procedural Areas

| clinical event | performed-activity evidence | required documentation elements | expected facility charge opportunity | common modifier logic | separately billable? | packaged / integral possibility? | common failure mode | likely queue destination | why it may not be billable |
|---|---|---|---|---|---|---|---|---|---|
| Completed outpatient procedure | case completion status, procedure log, room timestamps, performed procedure record | completed case status, primary procedure documentation, start/stop or room timestamps, department linkage | primary facility procedure charge and related technical case charges under local rule | some procedures may require modifier support for distinctness or reduced/discontinued status | usually yes | low for primary procedure, higher for secondary add-ons | performed case completed, but charge posting delayed while manual reconciliation waits on final case documentation | Charge Reconciliation Monitor | a final clean facility opportunity may still depend on completed documentation and correct case state, not just schedule presence |
| Discontinued procedure | case state marked discontinued or aborted, partial procedure documentation | discontinued status, reason, extent of procedure performed, timing, operative or procedural note support | reduced, partial, or no facility charge opportunity depending on local rule | reduced/discontinued modifier logic may apply where governed | sometimes | high | discontinued case routed as full missed primary procedure | Documentation Support Exceptions or Modifiers / Edits / Prebill Holds | the case may not support the full expected charge and may support only reduced or no separate billing outcome |
| Implant or device use during case | implant log, device documentation, completed case support | device identifier, quantity, timing, case linkage, completed or sufficiently performed procedure support | implant or device charge where separately captured | usually no frequent modifier, but claim-line edits may follow | sometimes | medium to high depending on procedure package logic | implant logged clinically but not reconciled to charge capture workflow | Charge Reconciliation Monitor | implant/device use may be included in the procedure package, unsupported, or not separately billable for that case type |
| Supply capture during ambulatory procedure | supply usage documentation, pick list, case log, procedural support | supply identity, quantity, timing, case linkage, department rule allowing separate capture | supply-related charge opportunity when the supply is separately captured | rarely modifier-driven; more often a support or edit issue | sometimes | high | supplies assumed separately chargeable because they were used in the room | Charge Reconciliation Monitor or Documentation Support Exceptions | many supplies are integral to the case and should not create separate missed-charge exceptions |
| Anesthesia or prep-stage activity relevant to facility capture | pre-op or anesthesia workflow timestamps, prep documentation, room-in events | documented relationship to the facility case, local rule supporting separate facility capture if any | sometimes no separate charge; sometimes a governed facility prep/recovery opportunity depending on local rule | modifier logic uncommon in V1 | often no | high | prep or anesthesia workflow interpreted as a standalone missed facility charge without department support | False-positive suppression before queueing | prep-stage or anesthesia-related workflow may be clinically real but not a separate facility charge opportunity in this V1 scope |
| Late manual supply reconciliation after completed case | completed case, delayed supply reconciliation event, late posting timestamp | completed case support, supply linkage, reconciled quantities, final case close timing | late-posted supply or device charge where local rules allow separate capture | modifier logic not typically primary | sometimes | medium to high | case closes operationally, but supply capture posts days later and creates apparent missing-charge exposure | Charge Reconciliation Monitor or Opportunity & Action Tracker | the item may be late but still valid, or it may ultimately prove packaged/integral and not a true miss |
| Timestamp-dependent room or procedure service | room-in/room-out, procedure start/stop, case timeline events | complete time sequence, performed procedure linkage, final case state | time-sensitive facility procedural opportunity where local rules depend on case timing | occasional reduced/discontinued logic may apply | sometimes | medium | one or more core timestamps are missing, inconsistent, or entered after the fact | Documentation Support Exceptions | without defensible timing, the service may not support the expected facility charge even if the case itself occurred |

## Common false-positive patterns

- Orders exist, but no completed performed activity exists.
- Clinical workflow shows an event started, but final completed or billable status was never reached.
- Documentation exists in one source, but expected-charge logic initially misses the late or cross-source linkage.
- A second same-day service appears duplicative until distinctness support is reviewed.
- Supply, hydration, or access work looks chargeable until packaging or integral logic is applied.
- A late-posted but still within-policy charge appears missing in a point-in-time snapshot and then self-resolves.

## Common packaged / integral patterns

- Hydration that is supportive or not distinct from the primary infusion hierarchy.
- Access-site work that is integral to the overall infusion visit.
- Contrast, devices, or supplies that are included in the primary technical service under local rules.
- OR supplies that are part of the procedural package rather than separate charge opportunities.
- Prep-stage or ancillary workflow that supports the case operationally but does not create its own facility charge line.

## Reviewer notes / realism guardrails

- Start with performed activity, not with charge code expectations.
- Do not classify a row as a true missed charge until `why it may not be billable` has been ruled out.
- Department logic must stay department-specific. Infusion hierarchy, radiology completion state, and procedural packaging cannot be forced into one generic rule set.
- Modifier issues are secondary to activity and documentation support. A modifier cannot rescue an event that was never validly documented as separately billable.
- Queue routing and queue-history churn should still feel department-native. OR / procedural stories can be more handoff-heavy than simpler infusion or imaging work.
- Synthetic records should include both real misses and believable suppressions for every department map above.
- If a synthetic encounter cannot be traced from performed evidence to expected facility opportunity through a department-native row in this document, it should not be treated as a governed V1 example.
