# Department Story Before/After Diff

## Infusion / Oncology Infusion
- top realism improvements: start_stop_dependency_count, waste_case_count
- start_stop_dependency_count: 11 -> 32
- sequence_non_primary_count: 2 -> 4
- hydration_conditional_count: 1 -> 2
- waste_case_count: 2 -> 4
- access_site_case_count: 1 -> 2
- documentation_gap_counts: {"<blank>": 10, "missing_stop_time": 1, "undocumented_waste": 1} -> {"<blank>": 27, "missing_stop_time": 4, "undocumented_waste": 2}
- current failure-mode mix: {"clinical_event_counts": {"Drug waste scenario": 6, "Hydration infusion distinct from therapy": 2, "Initial therapeutic infusion": 3, "Separate access-site administration": 2, "Timed infusion unit-conversion review": 20}, "department_label": "Infusion / Oncology Infusion", "documentation_gap_counts": {"<blank>": 15, "missing_stop_time": 4, "undocumented_waste": 2}, "opportunity_status_counts": {"expected_charge_supported": 8, "modifier_dependency_case": 8, "packaged_or_nonbillable_suppressed": 5, "recoverable_missed_charge": 6, "unsupported_charge_risk": 6}}
- remaining realism gaps: none

## Radiology / Interventional Radiology
- top realism improvements: completed_study_count, contrast_device_count
- completed_study_count: 9 -> 24
- incomplete_study_count: 2 -> 4
- laterality_site_count: 2 -> 4
- distinctness_case_count: 1 -> 2
- contrast_device_count: 1 -> 6
- unsupported_count: 3 -> 6
- current failure-mode mix: {"clinical_event_counts": {"Completed diagnostic imaging study": 12, "Distinct same-day imaging study": 2, "Incomplete or discontinued imaging study": 4, "Interventional device or contrast linkage": 6, "Laterality/site-dependent imaging study": 4}, "department_label": "Radiology / Interventional Radiology", "documentation_gap_counts": {"<blank>": 12, "incomplete_study": 4, "missing_device_linkage": 2, "missing_laterality": 2}, "opportunity_status_counts": {"expected_charge_supported": 14, "modifier_dependency_case": 2, "packaged_or_nonbillable_suppressed": 4, "recoverable_missed_charge": 2, "unsupported_charge_risk": 6}}
- remaining realism gaps: none

## OR / Procedural
- top realism improvements: implant_supply_count, late_post_risk_count
- discontinued_case_count: 2 -> 4
- implant_supply_count: 2 -> 12
- timestamp_gap_count: 1 -> 2
- late_post_risk_count: 2 -> 5
- postbill_recoverable_queue_count: 1 -> 2
- correction_history_count: 1 -> 2
- current failure-mode mix: {"clinical_event_counts": {"Completed outpatient procedure": 15, "Discontinued procedure": 4, "Implant or supply capture": 12, "Timestamp-dependent procedural support": 2}, "department_label": "OR / Procedural", "documentation_gap_counts": {"<blank>": 16, "missing_case_timestamp": 2, "missing_implant_linkage": 3}, "opportunity_status_counts": {"expected_charge_supported": 20, "packaged_or_nonbillable_suppressed": 6, "recoverable_missed_charge": 2, "unsupported_charge_risk": 5}}
- remaining realism gaps: none

## Cross-Department Notes
- No cross-department anti-pattern flags remain.
