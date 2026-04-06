# Manual Audit Sample

Deterministic 21-case audit pack exported from the current V1 synthetic control-room outputs.

## INF001

- Case rank: 1
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: infusion_primary_clean
- Current prebill stage: Final billed
- Upstream activity: activities=Primary therapeutic infusion administration; support=complete; basis=documentation_event
- Documentation evidence: types=infusion_administration; status=complete; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Timed infusion units derived from documented duration; status=expected_charge_supported; why_not_billable=none
- Billed state: charge_status=posted; charge_codes=INF-01; current_stage=Final billed; final_bill=2026-02-04 08:15
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the clean control case does not create an active exception.

## INF002

- Case rank: 2
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: hydration_conditional
- Current prebill stage: Final billed
- Upstream activity: activities=Primary therapeutic infusion administration; Same-day hydration administration; support=complete; basis=documentation_event
- Documentation evidence: types=infusion_administration; hydration_administration; status=complete; gaps=none; supports_charge_true=1/2
- Expected opportunity: targets=Timed infusion units derived from documented duration; Hydration administration charge; status=expected_charge_supported; packaged_or_nonbillable_suppressed; why_not_billable=same_day_hydration_integral_to_primary_infusion
- Billed state: charge_status=posted; charge_codes=INF-01; INF-02; current_stage=Final billed; final_bill=2026-02-04 11:15
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the case suppresses to packaged or non-billable and should not become leakage.

## INF004

- Case rank: 3
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: missing_stop_time
- Current prebill stage: Documentation pending
- Upstream activity: activities=Primary therapeutic infusion administration; support=incomplete; basis=documentation_event
- Documentation evidence: types=infusion_administration; status=incomplete; gaps=missing_stop_time; supports_charge_true=0/1
- Expected opportunity: targets=Timed infusion units derived from documented duration; status=unsupported_charge_risk; why_not_billable=missing_stop_time
- Billed state: charge_status=posted_pending_support; charge_codes=INF-01; current_stage=Documentation pending; final_bill=not final billed
- Exception classification: issue_domain=Documentation support failure; blocker=Documentation support incomplete
- Owner queue: Documentation Support Exceptions
- Accountable owner: Department operations
- Recoverability: Pre-final-bill recoverable
- Queue history: transition_events=1; reroute_count=0; prior_queue=none; path=Documentation Support Exceptions
- Audit focus: Confirm the documented activity exists but the support gap blocks clean billing.

## INF005

- Case rank: 4
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: waste_documented
- Current prebill stage: Charge capture pending
- Upstream activity: activities=Primary therapeutic infusion administration; Drug waste review support; support=complete; basis=documentation_event
- Documentation evidence: types=infusion_administration; waste_support_record; status=complete; gaps=none; supports_charge_true=2/2
- Expected opportunity: targets=Timed infusion units derived from documented duration; Waste-related charge opportunity; status=recoverable_missed_charge; why_not_billable=none
- Billed state: charge_status=no charge rows; charge_codes=none; current_stage=Charge capture pending; final_bill=not final billed
- Exception classification: issue_domain=Charge capture failure; blocker=Missing or late charge capture
- Owner queue: Charge Reconciliation Monitor
- Accountable owner: Department operations
- Recoverability: Pre-final-bill recoverable
- Queue history: transition_events=1; reroute_count=0; prior_queue=none; path=Charge Reconciliation Monitor
- Audit focus: Confirm a true missed-charge or late-post story, not a packaged false positive.

## INF006

- Case rank: 5
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: waste_missing
- Current prebill stage: Prebill edit / hold
- Upstream activity: activities=Primary therapeutic infusion administration; Drug waste review support; support=complete; incomplete; basis=documentation_event
- Documentation evidence: types=infusion_administration; waste_support_record; status=complete; incomplete; gaps=undocumented_waste; supports_charge_true=1/2
- Expected opportunity: targets=Waste-related charge opportunity; status=modifier_dependency_case; unsupported_charge_risk; why_not_billable=undocumented_waste
- Billed state: charge_status=posted_held_prebill; charge_codes=INF-01; INF-02; current_stage=Prebill edit / hold; final_bill=not final billed
- Exception classification: issue_domain=Billing / claim-edit failure; blocker=Prebill edit or hold unresolved
- Owner queue: Modifiers / Edits / Prebill Holds
- Accountable owner: Billing operations
- Recoverability: Post-window financially lost
- Queue history: transition_events=4; reroute_count=3; prior_queue=Coding Pending Review; path=Charge Reconciliation Monitor -> Documentation Support Exceptions -> Coding Pending Review -> Modifiers / Edits / Prebill Holds
- Audit focus: Confirm the issue is a governed edit or hold path with real billing ownership.

## INF009

- Case rank: 6
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: concurrent_infusion
- Current prebill stage: Coding pending
- Upstream activity: activities=Primary therapeutic infusion administration; Concurrent infusion add-on; support=complete; basis=documentation_event
- Documentation evidence: types=infusion_administration; status=complete; gaps=none; supports_charge_true=2/2
- Expected opportunity: targets=Timed infusion units derived from documented duration; Primary therapeutic infusion administration charge; status=modifier_dependency_case; why_not_billable=none
- Billed state: charge_status=posted_pending_coding; charge_codes=INF-01; INF-02; current_stage=Coding pending; final_bill=not final billed
- Exception classification: issue_domain=Coding failure; blocker=Coding or modifier review pending
- Owner queue: Coding Pending Review
- Accountable owner: Coding team
- Recoverability: Pre-final-bill recoverable
- Queue history: transition_events=2; reroute_count=1; prior_queue=Documentation Support Exceptions; path=Documentation Support Exceptions -> Coding Pending Review
- Audit focus: Confirm modifier or coding review is the true current blocker.

## INF010

- Case rank: 7
- Department: Outpatient Infusion / Oncology Infusion
- Service line: Infusion
- Scenario code: late_charge_risk
- Current prebill stage: Charge capture pending
- Upstream activity: activities=Primary therapeutic infusion administration; support=complete; basis=documentation_event
- Documentation evidence: types=infusion_administration; status=complete; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Timed infusion units derived from documented duration; status=recoverable_missed_charge; why_not_billable=none
- Billed state: charge_status=no charge rows; charge_codes=none; current_stage=Charge capture pending; final_bill=not final billed
- Exception classification: issue_domain=Charge capture failure; blocker=Missing or late charge capture
- Owner queue: Charge Reconciliation Monitor
- Accountable owner: Department operations
- Recoverability: Post-window financially lost
- Queue history: transition_events=1; reroute_count=0; prior_queue=none; path=Charge Reconciliation Monitor
- Audit focus: Confirm a true missed-charge or late-post story, not a packaged false positive.

## IR001

- Case rank: 8
- Department: Radiology / Interventional Radiology
- Service line: Interventional Radiology
- Scenario code: device_link_gap
- Current prebill stage: Documentation pending
- Upstream activity: activities=Primary completed imaging study; IR device linkage support; support=complete; incomplete; basis=documentation_event
- Documentation evidence: types=study_completion; device_linkage_record; status=complete; incomplete; gaps=missing_device_linkage; supports_charge_true=1/2
- Expected opportunity: targets=Facility technical imaging charge; Device or contrast-related technical charge when local rules allow; status=expected_charge_supported; unsupported_charge_risk; why_not_billable=missing_device_linkage
- Billed state: charge_status=posted_pending_support; charge_codes=IR0-01; IR0-02; current_stage=Documentation pending; final_bill=not final billed
- Exception classification: issue_domain=Documentation support failure; blocker=Documentation support incomplete
- Owner queue: Documentation Support Exceptions
- Accountable owner: Department operations
- Recoverability: Post-window financially lost
- Queue history: transition_events=1; reroute_count=0; prior_queue=none; path=Documentation Support Exceptions
- Audit focus: Confirm the documented activity exists but the support gap blocks clean billing.

## IR002

- Case rank: 9
- Department: Radiology / Interventional Radiology
- Service line: Interventional Radiology
- Scenario code: incomplete_ir_case
- Current prebill stage: Closed / monitored through denial feedback only
- Upstream activity: activities=Primary completed imaging study; support=partial; basis=documentation_event
- Documentation evidence: types=study_completion; status=partial; gaps=incomplete_study; supports_charge_true=0/1
- Expected opportunity: targets=No routine separate charge opportunity or reduced local charge; status=unsupported_charge_risk; why_not_billable=incomplete_study
- Billed state: charge_status=posted; charge_codes=IR0-01; current_stage=Closed / monitored through denial feedback only; final_bill=2026-02-06 11:45
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Financially closed but still compliance-relevant
- Queue history: No reroute history.
- Audit focus: Confirm the clean control case does not create an active exception.

## OR001

- Case rank: 10
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: completed_case_clean
- Current prebill stage: Final billed
- Upstream activity: activities=Primary outpatient procedure; support=complete; basis=documentation_event
- Documentation evidence: types=operative_case_record; status=complete; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Primary facility procedure charge; status=expected_charge_supported; why_not_billable=none
- Billed state: charge_status=posted; charge_codes=OR0-01; current_stage=Final billed; final_bill=2026-02-06 21:05
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the clean control case does not create an active exception.

## OR002

- Case rank: 11
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: discontinued_partial
- Current prebill stage: Prebill edit / hold
- Upstream activity: activities=Primary outpatient procedure; support=partial; basis=documentation_event
- Documentation evidence: types=operative_case_record; status=partial; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Reduced partial charge or no charge depending on local rule; status=packaged_or_nonbillable_suppressed; why_not_billable=discontinued_before_billable_procedure_threshold
- Billed state: charge_status=posted_held_prebill; charge_codes=OR0-01; current_stage=Prebill edit / hold; final_bill=not final billed
- Exception classification: issue_domain=Billing / claim-edit failure; blocker=Prebill edit or hold unresolved
- Owner queue: Modifiers / Edits / Prebill Holds
- Accountable owner: Billing operations
- Recoverability: Pre-final-bill recoverable
- Queue history: transition_events=3; reroute_count=2; prior_queue=Coding Pending Review; path=Documentation Support Exceptions -> Coding Pending Review -> Modifiers / Edits / Prebill Holds
- Audit focus: Confirm the issue is a governed edit or hold path with real billing ownership.

## OR004

- Case rank: 12
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: implant_link_gap
- Current prebill stage: Final billed
- Upstream activity: activities=Primary outpatient procedure; Implant or supply usage; support=complete; incomplete; basis=documentation_event
- Documentation evidence: types=operative_case_record; implant_supply_log; status=complete; incomplete; gaps=missing_implant_linkage; supports_charge_true=1/2
- Expected opportunity: targets=Primary facility procedure charge; Implant or supply-related charge when separately captured; status=expected_charge_supported; unsupported_charge_risk; why_not_billable=missing_implant_linkage
- Billed state: charge_status=posted; charge_codes=OR0-01; OR0-02; current_stage=Final billed; final_bill=2026-02-07 06:05
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the clean control case does not create an active exception.

## OR005

- Case rank: 13
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: supply_integral
- Current prebill stage: Final billed
- Upstream activity: activities=Primary outpatient procedure; Implant or supply usage; support=complete; basis=documentation_event
- Documentation evidence: types=operative_case_record; implant_supply_log; status=complete; gaps=none; supports_charge_true=1/2
- Expected opportunity: targets=Primary facility procedure charge; Implant or supply-related charge when separately captured; status=expected_charge_supported; packaged_or_nonbillable_suppressed; why_not_billable=supply_integral_to_procedural_package
- Billed state: charge_status=suppressed_nonbillable; charge_codes=OR0-01; OR0-02; current_stage=Final billed; final_bill=2026-02-07 09:05
- Exception classification: issue_domain=Packaged / non-billable / false-positive classification; blocker=Suppressed as nonbillable
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the case suppresses to packaged or non-billable and should not become leakage.

## OR006

- Case rank: 14
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: late_post_risk
- Current prebill stage: Prebill edit / hold
- Upstream activity: activities=Primary outpatient procedure; Implant or supply usage; support=complete; basis=documentation_event
- Documentation evidence: types=operative_case_record; implant_supply_log; status=complete; gaps=none; supports_charge_true=2/2
- Expected opportunity: targets=Primary facility procedure charge; Implant or supply-related charge when separately captured; status=expected_charge_supported; why_not_billable=none
- Billed state: charge_status=posted_held_prebill; charge_codes=OR0-01; OR0-02; current_stage=Prebill edit / hold; final_bill=not final billed
- Exception classification: issue_domain=Billing / claim-edit failure; blocker=Prebill edit or hold unresolved
- Owner queue: Modifiers / Edits / Prebill Holds
- Accountable owner: Billing operations
- Recoverability: Post-window financially lost
- Queue history: transition_events=3; reroute_count=2; prior_queue=Coding Pending Review; path=Charge Reconciliation Monitor -> Coding Pending Review -> Modifiers / Edits / Prebill Holds
- Audit focus: Confirm the issue is a governed edit or hold path with real billing ownership.

## OR007

- Case rank: 15
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: timestamp_missing
- Current prebill stage: Documentation pending
- Upstream activity: activities=Primary outpatient procedure; support=incomplete; basis=documentation_event
- Documentation evidence: types=operative_case_record; status=incomplete; gaps=missing_case_timestamp; supports_charge_true=0/1
- Expected opportunity: targets=Timestamp-dependent procedural facility charge; status=unsupported_charge_risk; why_not_billable=missing_case_timestamp
- Billed state: charge_status=posted_pending_support; charge_codes=OR0-01; current_stage=Documentation pending; final_bill=not final billed
- Exception classification: issue_domain=Documentation support failure; blocker=Documentation support incomplete
- Owner queue: Documentation Support Exceptions
- Accountable owner: Department operations
- Recoverability: Post-window financially lost
- Queue history: transition_events=2; reroute_count=1; prior_queue=Charge Reconciliation Monitor; path=Charge Reconciliation Monitor -> Documentation Support Exceptions
- Audit focus: Confirm the documented activity exists but the support gap blocks clean billing.

## OR010

- Case rank: 16
- Department: OR / Hospital Outpatient Surgery / Procedural Areas
- Service line: Outpatient Surgery
- Scenario code: correction_rebill_pending
- Current prebill stage: Correction / rebill pending
- Upstream activity: activities=Primary outpatient procedure; support=complete; basis=documentation_event
- Documentation evidence: types=operative_case_record; status=complete; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Primary facility procedure charge; status=expected_charge_supported; why_not_billable=none
- Billed state: charge_status=posted_needs_correction; charge_codes=OR0-01; current_stage=Correction / rebill pending; final_bill=2026-02-08 00:05
- Exception classification: issue_domain=Billing / claim-edit failure; blocker=Correction or rebill pending
- Owner queue: Correction / Rebill Pending
- Accountable owner: Billing operations
- Recoverability: Post-final-bill recoverable by correction / rebill
- Queue history: transition_events=4; reroute_count=3; prior_queue=Modifiers / Edits / Prebill Holds; path=Charge Reconciliation Monitor -> Coding Pending Review -> Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending
- Audit focus: Confirm the account left prebill, entered correction, and remains financially recoverable.

## RAD001

- Case rank: 17
- Department: Radiology / Interventional Radiology
- Service line: Radiology
- Scenario code: completed_study_clean
- Current prebill stage: Final billed
- Upstream activity: activities=Primary completed imaging study; support=complete; basis=documentation_event
- Documentation evidence: types=study_completion; status=complete; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Facility technical imaging charge; status=expected_charge_supported; why_not_billable=none
- Billed state: charge_status=posted; charge_codes=RAD-01; current_stage=Final billed; final_bill=2026-02-05 14:45
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the clean control case does not create an active exception.

## RAD002

- Case rank: 18
- Department: Radiology / Interventional Radiology
- Service line: Radiology
- Scenario code: incomplete_study_nonbillable
- Current prebill stage: Final billed
- Upstream activity: activities=Primary completed imaging study; support=partial; basis=documentation_event
- Documentation evidence: types=study_completion; status=partial; gaps=incomplete_study; supports_charge_true=0/1
- Expected opportunity: targets=No routine separate charge opportunity or reduced local charge; status=packaged_or_nonbillable_suppressed; why_not_billable=incomplete_study
- Billed state: charge_status=suppressed_nonbillable; charge_codes=RAD-01; current_stage=Final billed; final_bill=2026-02-05 17:45
- Exception classification: issue_domain=Packaged / non-billable / false-positive classification; blocker=Suppressed as nonbillable
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the case suppresses to packaged or non-billable and should not become leakage.

## RAD003

- Case rank: 19
- Department: Radiology / Interventional Radiology
- Service line: Radiology
- Scenario code: laterality_missing
- Current prebill stage: Documentation pending
- Upstream activity: activities=Primary completed imaging study; support=incomplete; basis=documentation_event
- Documentation evidence: types=study_completion; status=incomplete; gaps=missing_laterality; supports_charge_true=0/1
- Expected opportunity: targets=Laterality/site-dependent technical imaging charge; status=unsupported_charge_risk; why_not_billable=missing_laterality
- Billed state: charge_status=posted_pending_support; charge_codes=RAD-01; current_stage=Documentation pending; final_bill=not final billed
- Exception classification: issue_domain=Documentation support failure; blocker=Documentation support incomplete
- Owner queue: Documentation Support Exceptions
- Accountable owner: Department operations
- Recoverability: Pre-final-bill recoverable
- Queue history: transition_events=1; reroute_count=0; prior_queue=none; path=Documentation Support Exceptions
- Audit focus: Confirm the documented activity exists but the support gap blocks clean billing.

## RAD006

- Case rank: 20
- Department: Radiology / Interventional Radiology
- Service line: Radiology
- Scenario code: distinctness_required
- Current prebill stage: Coding pending
- Upstream activity: activities=Primary completed imaging study; Same-day repeat imaging study; support=complete; basis=documentation_event
- Documentation evidence: types=study_completion; status=complete; gaps=none; supports_charge_true=2/2
- Expected opportunity: targets=Facility technical imaging charge; Distinct same-day technical imaging charge; status=expected_charge_supported; modifier_dependency_case; why_not_billable=none
- Billed state: charge_status=posted_pending_coding; charge_codes=RAD-01; RAD-02; current_stage=Coding pending; final_bill=not final billed
- Exception classification: issue_domain=Coding failure; blocker=Coding or modifier review pending
- Owner queue: Coding Pending Review
- Accountable owner: Coding team
- Recoverability: Pre-final-bill recoverable
- Queue history: transition_events=2; reroute_count=1; prior_queue=Documentation Support Exceptions; path=Documentation Support Exceptions -> Coding Pending Review
- Audit focus: Confirm modifier or coding review is the true current blocker.

## RAD007

- Case rank: 21
- Department: Radiology / Interventional Radiology
- Service line: Radiology
- Scenario code: late_post_risk
- Current prebill stage: Final billed
- Upstream activity: activities=Primary completed imaging study; support=complete; basis=documentation_event
- Documentation evidence: types=study_completion; status=complete; gaps=none; supports_charge_true=1/1
- Expected opportunity: targets=Facility technical imaging charge; status=expected_charge_supported; why_not_billable=none
- Billed state: charge_status=posted; charge_codes=RAD-01; current_stage=Final billed; final_bill=2026-02-06 14:45
- Exception classification: issue_domain=No active exception; blocker=No active blocker
- Owner queue: No active queue
- Accountable owner: No active owner
- Recoverability: Post-window financially lost
- Queue history: No reroute history.
- Audit focus: Confirm the clean control case does not create an active exception.
