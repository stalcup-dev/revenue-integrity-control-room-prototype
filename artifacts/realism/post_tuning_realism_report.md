# Current Shipped Realism State

> Use this as the authoritative public realism artifact for the current repo state.

Overall status: **pass**

## Summary
- pass: 22 | warn: 0 | fail: 0

## Recoverability Mix
- status: **pass**
- metrics:
  - all_status_counts: {"Financially closed but still compliance-relevant": 4, "Post-final-bill recoverable by correction / rebill": 2, "Post-window financially lost": 39, "Pre-final-bill recoverable": 17}
  - active_counts: {"Post-final-bill recoverable by correction / rebill": 2, "Post-window financially lost": 9, "Pre-final-bill recoverable": 13}
  - active_lost_rate: 0.375
  - closed_compliance_count: 4
- anti-pattern flags: none

## Workflow State Realism
- status: **pass**
- metrics:
  - active_stage_counts: {"Charge capture pending": 4, "Coding pending": 5, "Correction / rebill pending": 2, "Documentation pending": 7, "Prebill edit / hold": 6}
  - active_stage_count: 5
  - stage_age_summary_days: {"Charge capture pending": {"max": 6.0, "median": 4.0, "min": 2.0, "nunique": 2.0}, "Coding pending": {"max": 4.0, "median": 2.0, "min": 1.0, "nunique": 3.0}, "Correction / rebill pending": {"max": 6.0, "median": 6.0, "min": 6.0, "nunique": 1.0}, "Documentation pending": {"max": 7.0, "median": 4.0, "min": 2.0, "nunique": 4.0}, "Prebill edit / hold": {"max": 7.0, "median": 5.0, "min": 4.0, "nunique": 3.0}}
  - one_current_blocker_violations: 0
  - stage_age_median_range_days: 4
- anti-pattern flags: none

## Queue History Realism
- status: **pass**
- metrics:
  - queue_history_row_count: 50
  - encounter_level_row_count: 24
  - transition_event_density: 2.0833
  - reroute_count_distribution: {"0": 10, "1": 6, "2": 4, "3": 4}
  - first_route_only_count: 10
  - rerouted_count: 14
  - multi_reroute_count: 8
  - transition_count: 26
  - routing_reason_populated_count: 50
- anti-pattern flags: none

## Financial Consequence Realism
- status: **pass**
- metrics:
  - late_charge_rate: 0.1159
  - lost_dollars_after_timing_window: 3630
  - recoverable_dollars_still_open: 9740
- anti-pattern flags: none

## Exception Class Balance
- status: **pass**
- metrics:
  - recoverable_missed_charge_count: 10
  - unsupported_charge_risk_count: 17
  - suppressed_packaged_nonbillable_count: 15
- anti-pattern flags: none

## Distribution Realism
- status: **pass**
- metrics:
  - department_queue_mix: {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 2, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 4}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 4, "Coding Pending Review": 3, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 2}, "Radiology / Interventional Radiology": {"Coding Pending Review": 2, "Documentation Support Exceptions": 3}}
  - department_repeat_exception_rate: {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}
  - distinct_dominant_queues: 3
- anti-pattern flags: none

## Correction History Realism
- status: **pass**
- metrics:
  - postbill_recoverable_case_count: 2
  - correction_history_row_count: 4
  - postbill_cases_with_correction_history: 2
- anti-pattern flags: none

## Transition Ledger Realism
- status: **pass**
- metrics:
  - queue_history_row_count: 50
  - exception_queue_row_count: 24
  - transition_event_density: 2.0833
  - multi_event_case_count: 14
  - distinct_transition_pair_count: 5
  - routing_reason_coverage: 1
  - days_in_prior_queue_summary: {"max": 3.0, "median": 1.0, "min": 0.0, "nunique": 4}
- anti-pattern flags: none

## Handoff Churn Realism
- status: **pass**
- metrics:
  - reroute_bucket_distribution: {"0": 10, "1": 6, "2": 4, "3+": 4}
  - department_reroute_mean: {"OR / Hospital Outpatient Surgery / Procedural Areas": 2.0, "Outpatient Infusion / Oncology Infusion": 0.7273, "Radiology / Interventional Radiology": 0.4}
  - service_line_reroute_mean: {"Infusion": 0.7273, "Interventional Radiology": 0.0, "Outpatient Surgery": 2.0, "Radiology": 0.5}
  - top_transition_pairs: {"Charge Reconciliation Monitor -> Coding Pending Review": 4, "Charge Reconciliation Monitor -> Documentation Support Exceptions": 4, "Coding Pending Review -> Modifiers / Edits / Prebill Holds": 8, "Documentation Support Exceptions -> Coding Pending Review": 8, "Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending": 2}
- anti-pattern flags: none

## Intervention Followthrough Realism
- status: **pass**
- metrics:
  - checkpoint_distribution: {"Baseline captured": 5, "Checkpoint overdue": 2, "Monitor next checkpoint": 9, "Pilot checkpoint complete": 6, "Turnaround improving": 2}
  - recommendation_distribution: {"Expand": 6, "Hold": 12, "Revise": 6}
  - metric_delta_summary: {"max_delta": 2.2, "median_delta": 0.65, "nonzero_count": 20, "positive_count": 18}
  - correction_turnaround_row_count: 8
  - owner_context_match_rate: 1
  - recurring_pattern_coverage: 1
- anti-pattern flags: none

## Transition Intervention Antipatterns
- status: **pass**
- metrics:
  - transition_event_density: 2.0833
  - generic_routing_reason_rate: 0.02
  - owner_context_match_rate: 1
  - recommendation_distribution: {"Expand": 6, "Hold": 12, "Revise": 6}
  - department_reroute_mean: {"OR / Hospital Outpatient Surgery / Procedural Areas": 2.0, "Outpatient Infusion / Oncology Infusion": 0.7273, "Radiology / Interventional Radiology": 0.4}
- anti-pattern flags: none

## Infusion Story Realism
- status: **pass**
- metrics:
  - encounter_count: 21
  - start_stop_dependency_case_count: 20
  - start_stop_dependency_rate: 0.9524
  - sequence_non_primary_case_count: 4
  - hydration_conditional_case_count: 2
  - waste_support_case_count: 4
  - access_site_case_count: 2
  - documentation_gap_counts: {"<blank>": 15, "missing_stop_time": 4, "undocumented_waste": 2}
  - clinical_event_counts: {"Drug waste scenario": 6, "Hydration infusion distinct from therapy": 2, "Initial therapeutic infusion": 3, "Separate access-site administration": 2, "Timed infusion unit-conversion review": 20}
- anti-pattern flags: none

## Radiology Story Realism
- status: **pass**
- metrics:
  - encounter_count: 20
  - completed_study_case_count: 16
  - incomplete_study_case_count: 4
  - laterality_site_case_count: 4
  - distinctness_case_count: 2
  - contrast_device_case_count: 6
  - unsupported_case_count: 6
  - documentation_gap_counts: {"<blank>": 12, "incomplete_study": 4, "missing_device_linkage": 2, "missing_laterality": 2}
  - clinical_event_counts: {"Completed diagnostic imaging study": 12, "Distinct same-day imaging study": 2, "Incomplete or discontinued imaging study": 4, "Interventional device or contrast linkage": 6, "Laterality/site-dependent imaging study": 4}
- anti-pattern flags: none

## Or Procedural Story Realism
- status: **pass**
- metrics:
  - encounter_count: 21
  - discontinued_case_count: 4
  - implant_supply_case_count: 12
  - timestamp_gap_case_count: 2
  - late_post_risk_case_count: 5
  - postbill_recoverable_case_count: 2
  - correction_history_case_count: 2
  - mean_reroute_count_by_department: {"infusion": 0.7368, "or_procedural": 1.0833, "radiology_ir": 0.2857}
  - clinical_event_counts: {"Completed outpatient procedure": 15, "Discontinued procedure": 4, "Implant or supply capture": 12, "Timestamp-dependent procedural support": 2}
- anti-pattern flags: none

## Department Story Antipatterns
- status: **pass**
- metrics:
  - documented_performed_support_rate: 1
  - department_documentation_gap_signatures: {"infusion": ["missing_stop_time", "undocumented_waste"], "or_procedural": ["missing_case_timestamp", "missing_implant_linkage"], "radiology_ir": ["incomplete_study", "missing_device_linkage", "missing_laterality"]}
  - modifier_case_event_map: {"infusion": {"Drug waste scenario": 2, "Initial therapeutic infusion": 2, "Timed infusion unit-conversion review": 4}, "radiology_ir": {"Distinct same-day imaging study": 2}}
  - invalid_modifier_case_count: 0
  - failure_category_dominance: {"modifier_dependency_case": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.8}, "packaged_or_nonbillable_suppressed": {"department": "OR / Hospital Outpatient Surgery / Procedural Areas", "share": 0.4}, "recoverable_missed_charge": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.6}, "unsupported_charge_risk": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.3529}}
  - top_failure_status_by_department: {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}
  - top_clinical_event_by_department: {"infusion": "Timed infusion unit-conversion review", "or_procedural": "Completed outpatient procedure", "radiology_ir": "Completed diagnostic imaging study"}
- anti-pattern flags: none

## Undercapture Balance Realism
- status: **pass**
- metrics:
  - overall_count: 10
  - overall_rate: 0.1064
  - department_counts: {"OR / Hospital Outpatient Surgery / Procedural Areas": 2, "Outpatient Infusion / Oncology Infusion": 6, "Radiology / Interventional Radiology": 2}
  - department_rates: {"OR / Hospital Outpatient Surgery / Procedural Areas": 0.0606, "Outpatient Infusion / Oncology Infusion": 0.1818, "Radiology / Interventional Radiology": 0.0714}
  - departments_with_undercapture_count: 3
  - top_failure_class_by_department: {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}
- anti-pattern flags: none

## Unsupported Balance Realism
- status: **pass**
- metrics:
  - overall_count: 17
  - overall_rate: 0.1809
  - department_counts: {"OR / Hospital Outpatient Surgery / Procedural Areas": 5, "Outpatient Infusion / Oncology Infusion": 6, "Radiology / Interventional Radiology": 6}
  - unsupported_with_charge_count: 17
  - unsupported_with_charge_rate: 1
  - closed_compliance_unsupported_count: 4
  - charge_status_distribution: {"posted": 8, "posted_held_prebill": 2, "posted_pending_support": 7}
- anti-pattern flags: none

## Suppression Balance Realism
- status: **pass**
- metrics:
  - overall_count: 15
  - overall_rate: 0.1596
  - department_counts: {"OR / Hospital Outpatient Surgery / Procedural Areas": 6, "Outpatient Infusion / Oncology Infusion": 5, "Radiology / Interventional Radiology": 4}
  - meaningful_explanation_rate: 1
  - generic_explanation_rate: 0
  - department_reason_counts: {"infusion": {"access_site_integral_to_primary_infusion": 2, "iv_push_documented_without_infusion_duration": 1, "same_day_hydration_integral_to_primary_infusion": 2}, "or_procedural": {"discontinued_before_billable_procedure_threshold": 4, "supply_integral_to_procedural_package": 2}, "radiology_ir": {"contrast_packaged_into_primary_technical_service": 2, "incomplete_study": 2}}
  - suppressed_charge_capture_queue_count: 0
- anti-pattern flags: none

## Suppression Balance Antipatterns
- status: **pass**
- metrics:
  - overall_status_counts: {"modifier_dependency_case": 10, "packaged_or_nonbillable_suppressed": 15, "recoverable_missed_charge": 10, "unsupported_charge_risk": 17}
  - overall_status_rates: {"modifier_dependency_case": 0.1064, "packaged_or_nonbillable_suppressed": 0.1596, "recoverable_missed_charge": 0.1064, "unsupported_charge_risk": 0.1809}
  - top_failure_class_by_department: {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}
  - separately_billable_rate: 0.7979
  - dominant_department_by_class: {"modifier_dependency_case": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.8}, "packaged_or_nonbillable_suppressed": {"department": "OR / Hospital Outpatient Surgery / Procedural Areas", "share": 0.4}, "recoverable_missed_charge": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.6}, "unsupported_charge_risk": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.3529}}
  - suppression_reason_signatures: {"infusion": ["access_site_integral_to_primary_infusion", "iv_push_documented_without_infusion_duration", "same_day_hydration_integral_to_primary_infusion"], "or_procedural": ["discontinued_before_billable_procedure_threshold", "supply_integral_to_procedural_package"], "radiology_ir": ["contrast_packaged_into_primary_technical_service", "incomplete_study"]}
  - unsupported_reason_signatures: {"infusion": ["missing_stop_time", "undocumented_waste"], "or_procedural": ["missing_case_timestamp", "missing_implant_linkage"], "radiology_ir": ["incomplete_study", "missing_device_linkage", "missing_laterality"]}
- anti-pattern flags: none

## Medium Volume Ops Realism
- status: **pass**
- metrics:
  - encounter_count: 62
  - active_exception_count: 24
  - department_queue_mix: {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 2, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 4}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 4, "Coding Pending Review": 3, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 2}, "Radiology / Interventional Radiology": {"Coding Pending Review": 2, "Documentation Support Exceptions": 3}}
  - distinct_dominant_queues: 3
  - reroute_distribution: {"0": 10, "1": 6, "2": 4, "3": 4}
  - rerouted_case_count: 14
  - multi_reroute_count: 8
  - repeat_exception_rate_by_department: {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}
  - repeat_root_cause_cluster_count_ge_2: 8
- anti-pattern flags: none

## Payable State Signal Realism
- status: **pass**
- metrics:
  - denials_feedback_row_count: 9
  - linked_upstream_rate: 1
  - payer_group_count: 4
  - denial_category_counts: {"documentation_support_denial": 6, "technical_denial": 3}
  - issue_domain_counts: {"Billing / claim-edit failure": 1, "Documentation support failure": 8}
  - closed_compliance_count: 4
  - closed_compliance_signal_rows: 4
- anti-pattern flags: none

## Ops Mix Payable Antipatterns
- status: **pass**
- metrics:
  - denial_feedback_share_of_encounters: 0.1452
  - blank_upstream_issue_domain_count: 0
  - top_failure_class_by_department: {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}
  - repeat_exception_rate_by_department: {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}
  - distinct_dominant_queues: 3
- anti-pattern flags: none

## What Still Feels Fake
- No realism anti-pattern flags remain.
