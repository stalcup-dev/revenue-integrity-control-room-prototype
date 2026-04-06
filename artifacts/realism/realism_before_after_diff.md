# Before/After Realism Remediation Proof

> Use this to show the bridge from the earlier realism dents to the current shipped realism state.

Baseline overall status: **fail**
Post-tuning overall status: **pass**

## Recoverability
- status: fail -> pass
- active_counts: {"Post-final-bill recoverable by correction / rebill": 1, "Pre-final-bill recoverable": 12} -> {"Post-final-bill recoverable by correction / rebill": 2, "Post-window financially lost": 9, "Pre-final-bill recoverable": 13}
- active_lost_rate: 0 -> 0.375
- all_status_counts: {"Post-final-bill recoverable by correction / rebill": 1, "Post-window financially lost": 14, "Pre-final-bill recoverable": 15} -> {"Financially closed but still compliance-relevant": 4, "Post-final-bill recoverable by correction / rebill": 2, "Post-window financially lost": 39, "Pre-final-bill recoverable": 17}
- closed_compliance_count: 0 -> 4

## Workflow State
- status: fail -> pass
- active_stage_count: 5 -> 5
- active_stage_counts: {"Charge capture pending": 3, "Coding pending": 2, "Correction / rebill pending": 1, "Documentation pending": 5, "Prebill edit / hold": 2} -> {"Charge capture pending": 4, "Coding pending": 5, "Correction / rebill pending": 2, "Documentation pending": 7, "Prebill edit / hold": 6}
- one_current_blocker_violations: 0 -> 0
- stage_age_median_range_days: 0 -> 4
- stage_age_summary_days: {"Charge capture pending": {"max": 3.0, "median": 3.0, "min": 3.0, "nunique": 1.0}, "Coding pending": {"max": 3.0, "median": 3.0, "min": 3.0, "nunique": 1.0}, "Correction / rebill pending": {"max": 3.0, "median": 3.0, "min": 3.0, "nunique": 1.0}, "Documentation pending": {"max": 3.0, "median": 3.0, "min": 3.0, "nunique": 1.0}, "Prebill edit / hold": {"max": 3.0, "median": 3.0, "min": 3.0, "nunique": 1.0}} -> {"Charge capture pending": {"max": 6.0, "median": 4.0, "min": 2.0, "nunique": 2.0}, "Coding pending": {"max": 4.0, "median": 2.0, "min": 1.0, "nunique": 3.0}, "Correction / rebill pending": {"max": 6.0, "median": 6.0, "min": 6.0, "nunique": 1.0}, "Documentation pending": {"max": 7.0, "median": 4.0, "min": 2.0, "nunique": 4.0}, "Prebill edit / hold": {"max": 7.0, "median": 5.0, "min": 4.0, "nunique": 3.0}}

## Queue History
- status: fail -> pass
- encounter_level_row_count: 0 -> 24
- first_route_only_count: 10 -> 10
- multi_reroute_count: 1 -> 8
- queue_history_row_count: 0 -> 50
- reroute_count_distribution: {"0": 10, "1": 2, "2": 1} -> {"0": 10, "1": 6, "2": 4, "3": 4}
- rerouted_count: 3 -> 14
- routing_reason_populated_count: 0 -> 50
- transition_count: 3 -> 26
- transition_event_density: 0 -> 2.0833

## Financial Consequences
- status: fail -> pass
- late_charge_rate: 0 -> 0.1159
- lost_dollars_after_timing_window: 0 -> 3630
- recoverable_dollars_still_open: 9075 -> 9740

## Correction History
- status: fail -> pass
- correction_history_row_count: 0 -> 4
- postbill_cases_with_correction_history: 0 -> 2
- postbill_recoverable_case_count: 1 -> 2

## Exception Balance
- status: pass -> pass
- recoverable_missed_charge_count: 3 -> 10
- suppressed_packaged_nonbillable_count: 8 -> 15
- unsupported_charge_risk_count: 6 -> 17

## Distribution
- status: pass -> pass
- department_queue_mix: {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Charge Reconciliation Monitor": 1, "Correction / Rebill Pending": 1, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 1}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 1, "Coding Pending Review": 1, "Documentation Support Exceptions": 1, "Modifiers / Edits / Prebill Holds": 1}, "Radiology / Interventional Radiology": {"Charge Reconciliation Monitor": 1, "Coding Pending Review": 1, "Documentation Support Exceptions": 2}} -> {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 2, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 4}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 4, "Coding Pending Review": 3, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 2}, "Radiology / Interventional Radiology": {"Coding Pending Review": 2, "Documentation Support Exceptions": 3}}
- department_repeat_exception_rate: {"OR / Hospital Outpatient Surgery / Procedural Areas": 0.4, "Outpatient Infusion / Oncology Infusion": 0.25, "Radiology / Interventional Radiology": 0.0} -> {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}
- distinct_dominant_queues: 2 -> 3

## Anti-Pattern Resolution
- Resolved: Late charge rate is zero.
- Resolved: Lost dollars after timing window are zero.
- Resolved: Missing recoverability states: Financially closed but still compliance-relevant
- Resolved: No active post-window financially lost items are visible.
- Resolved: Not every post-final-bill recoverable case has correction-history support.
- Resolved: Routing reasons are absent.
- Resolved: Stage-specific aging is effectively flat across the active workflow.
- Remaining: none
