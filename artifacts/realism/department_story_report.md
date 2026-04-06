# Department Story Report

Overall status: **pass**

## Summary
- pass: 4 | warn: 0 | fail: 0

## Infusion / Oncology Infusion
- status: **pass**
- scenario counts: {"access_site_case_count": 2, "documentation_gap_counts": {"<blank>": 27, "missing_stop_time": 4, "undocumented_waste": 2}, "hydration_conditional_count": 2, "sequence_non_primary_count": 4, "start_stop_dependency_count": 32, "waste_case_count": 4}
- failure-mode mix: {"clinical_event_counts": {"Drug waste scenario": 6, "Hydration infusion distinct from therapy": 2, "Initial therapeutic infusion": 3, "Separate access-site administration": 2, "Timed infusion unit-conversion review": 20}, "department_label": "Infusion / Oncology Infusion", "documentation_gap_counts": {"<blank>": 15, "missing_stop_time": 4, "undocumented_waste": 2}, "opportunity_status_counts": {"expected_charge_supported": 8, "modifier_dependency_case": 8, "packaged_or_nonbillable_suppressed": 5, "recoverable_missed_charge": 6, "unsupported_charge_risk": 6}}
- what still feels fake: none

## Radiology / Interventional Radiology
- status: **pass**
- scenario counts: {"completed_study_count": 24, "contrast_device_count": 6, "distinctness_case_count": 2, "incomplete_study_count": 4, "laterality_site_count": 4, "unsupported_count": 6}
- failure-mode mix: {"clinical_event_counts": {"Completed diagnostic imaging study": 12, "Distinct same-day imaging study": 2, "Incomplete or discontinued imaging study": 4, "Interventional device or contrast linkage": 6, "Laterality/site-dependent imaging study": 4}, "department_label": "Radiology / Interventional Radiology", "documentation_gap_counts": {"<blank>": 12, "incomplete_study": 4, "missing_device_linkage": 2, "missing_laterality": 2}, "opportunity_status_counts": {"expected_charge_supported": 14, "modifier_dependency_case": 2, "packaged_or_nonbillable_suppressed": 4, "recoverable_missed_charge": 2, "unsupported_charge_risk": 6}}
- what still feels fake: none

## OR / Procedural
- status: **pass**
- scenario counts: {"correction_history_count": 2, "discontinued_case_count": 4, "implant_supply_count": 12, "late_post_risk_count": 5, "postbill_recoverable_queue_count": 2, "timestamp_gap_count": 2}
- failure-mode mix: {"clinical_event_counts": {"Completed outpatient procedure": 15, "Discontinued procedure": 4, "Implant or supply capture": 12, "Timestamp-dependent procedural support": 2}, "department_label": "OR / Procedural", "documentation_gap_counts": {"<blank>": 16, "missing_case_timestamp": 2, "missing_implant_linkage": 3}, "opportunity_status_counts": {"expected_charge_supported": 20, "packaged_or_nonbillable_suppressed": 6, "recoverable_missed_charge": 2, "unsupported_charge_risk": 5}}
- what still feels fake: none

## Cross-Department Anti-Patterns
- status: **pass**
- metrics: {"department_documentation_gap_signatures": {"infusion": ["missing_stop_time", "undocumented_waste"], "or_procedural": ["missing_case_timestamp", "missing_implant_linkage"], "radiology_ir": ["incomplete_study", "missing_device_linkage", "missing_laterality"]}, "documented_performed_support_rate": 1.0, "failure_category_dominance": {"modifier_dependency_case": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.8}, "packaged_or_nonbillable_suppressed": {"department": "OR / Hospital Outpatient Surgery / Procedural Areas", "share": 0.4}, "recoverable_missed_charge": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.6}, "unsupported_charge_risk": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.3529}}, "invalid_modifier_case_count": 0, "modifier_case_event_map": {"infusion": {"Drug waste scenario": 2, "Initial therapeutic infusion": 2, "Timed infusion unit-conversion review": 4}, "radiology_ir": {"Distinct same-day imaging study": 2}}, "top_clinical_event_by_department": {"infusion": "Timed infusion unit-conversion review", "or_procedural": "Completed outpatient procedure", "radiology_ir": "Completed diagnostic imaging study"}, "top_failure_status_by_department": {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}}
- anti-pattern flags: none
