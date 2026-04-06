# Suppression Balance Report

Overall status: **pass**

## Summary
- pass: 4 | warn: 0 | fail: 0
- overall counts/rates: {"status_counts": {"modifier_dependency_case": 10, "packaged_or_nonbillable_suppressed": 15, "recoverable_missed_charge": 10, "unsupported_charge_risk": 17}, "status_rates": {"modifier_dependency_case": 0.1064, "packaged_or_nonbillable_suppressed": 0.1596, "recoverable_missed_charge": 0.1064, "unsupported_charge_risk": 0.1809}}

## Undercapture Balance Realism
- status: **pass**
- metrics: {"department_counts": {"OR / Hospital Outpatient Surgery / Procedural Areas": 2, "Outpatient Infusion / Oncology Infusion": 6, "Radiology / Interventional Radiology": 2}, "department_rates": {"OR / Hospital Outpatient Surgery / Procedural Areas": 0.0606, "Outpatient Infusion / Oncology Infusion": 0.1818, "Radiology / Interventional Radiology": 0.0714}, "departments_with_undercapture_count": 3, "overall_count": 10, "overall_rate": 0.1064, "top_failure_class_by_department": {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}}
- anti-pattern flags: none

## Unsupported Balance Realism
- status: **pass**
- metrics: {"charge_status_distribution": {"posted": 8, "posted_held_prebill": 2, "posted_pending_support": 7}, "closed_compliance_unsupported_count": 4, "department_counts": {"OR / Hospital Outpatient Surgery / Procedural Areas": 5, "Outpatient Infusion / Oncology Infusion": 6, "Radiology / Interventional Radiology": 6}, "overall_count": 17, "overall_rate": 0.1809, "unsupported_with_charge_count": 17, "unsupported_with_charge_rate": 1.0}
- anti-pattern flags: none

## Suppression Balance Realism
- status: **pass**
- metrics: {"department_counts": {"OR / Hospital Outpatient Surgery / Procedural Areas": 6, "Outpatient Infusion / Oncology Infusion": 5, "Radiology / Interventional Radiology": 4}, "department_reason_counts": {"infusion": {"access_site_integral_to_primary_infusion": 2, "iv_push_documented_without_infusion_duration": 1, "same_day_hydration_integral_to_primary_infusion": 2}, "or_procedural": {"discontinued_before_billable_procedure_threshold": 4, "supply_integral_to_procedural_package": 2}, "radiology_ir": {"contrast_packaged_into_primary_technical_service": 2, "incomplete_study": 2}}, "generic_explanation_rate": 0.0, "meaningful_explanation_rate": 1.0, "overall_count": 15, "overall_rate": 0.1596, "suppressed_charge_capture_queue_count": 0}
- anti-pattern flags: none

## Suppression Balance Antipatterns
- status: **pass**
- metrics: {"dominant_department_by_class": {"modifier_dependency_case": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.8}, "packaged_or_nonbillable_suppressed": {"department": "OR / Hospital Outpatient Surgery / Procedural Areas", "share": 0.4}, "recoverable_missed_charge": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.6}, "unsupported_charge_risk": {"department": "Outpatient Infusion / Oncology Infusion", "share": 0.3529}}, "overall_status_counts": {"modifier_dependency_case": 10, "packaged_or_nonbillable_suppressed": 15, "recoverable_missed_charge": 10, "unsupported_charge_risk": 17}, "overall_status_rates": {"modifier_dependency_case": 0.1064, "packaged_or_nonbillable_suppressed": 0.1596, "recoverable_missed_charge": 0.1064, "unsupported_charge_risk": 0.1809}, "separately_billable_rate": 0.7979, "suppression_reason_signatures": {"infusion": ["access_site_integral_to_primary_infusion", "iv_push_documented_without_infusion_duration", "same_day_hydration_integral_to_primary_infusion"], "or_procedural": ["discontinued_before_billable_procedure_threshold", "supply_integral_to_procedural_package"], "radiology_ir": ["contrast_packaged_into_primary_technical_service", "incomplete_study"]}, "top_failure_class_by_department": {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}, "unsupported_reason_signatures": {"infusion": ["missing_stop_time", "undocumented_waste"], "or_procedural": ["missing_case_timestamp", "missing_implant_linkage"], "radiology_ir": ["incomplete_study", "missing_device_linkage", "missing_laterality"]}}
- anti-pattern flags: none
