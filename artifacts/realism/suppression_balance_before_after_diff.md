# Suppression Balance Before/After Diff

## Overall Mix
- status counts: {"modifier_dependency_case": 5, "packaged_or_nonbillable_suppressed": 7, "recoverable_missed_charge": 3, "unsupported_charge_risk": 7} -> {"modifier_dependency_case": 10, "packaged_or_nonbillable_suppressed": 15, "recoverable_missed_charge": 10, "unsupported_charge_risk": 17}
- status rates: {"modifier_dependency_case": 0.1111, "packaged_or_nonbillable_suppressed": 0.1556, "recoverable_missed_charge": 0.0667, "unsupported_charge_risk": 0.1556} -> {"modifier_dependency_case": 0.1064, "packaged_or_nonbillable_suppressed": 0.1596, "recoverable_missed_charge": 0.1064, "unsupported_charge_risk": 0.1809}

## Infusion / Oncology Infusion
- status counts: {"modifier_dependency_case": 3, "packaged_or_nonbillable_suppressed": 2, "recoverable_missed_charge": 3, "unsupported_charge_risk": 2} -> {"modifier_dependency_case": 8, "packaged_or_nonbillable_suppressed": 5, "recoverable_missed_charge": 6, "unsupported_charge_risk": 6}
- top failure class: modifier_dependency_case -> modifier_dependency_case
- suppression reasons: {"packaged_or_integral": 2} -> {"access_site_integral_to_primary_infusion": 2, "iv_push_documented_without_infusion_duration": 1, "same_day_hydration_integral_to_primary_infusion": 2}
- unsupported reasons: {"missing_stop_time": 1, "undocumented_waste": 1} -> {"missing_stop_time": 4, "undocumented_waste": 2}

## Radiology / Interventional Radiology
- status counts: {"modifier_dependency_case": 2, "packaged_or_nonbillable_suppressed": 2, "recoverable_missed_charge": 0, "unsupported_charge_risk": 3} -> {"modifier_dependency_case": 2, "packaged_or_nonbillable_suppressed": 4, "recoverable_missed_charge": 2, "unsupported_charge_risk": 6}
- top failure class: unsupported_charge_risk -> unsupported_charge_risk
- suppression reasons: {"incomplete_study": 1, "packaged_or_integral": 1} -> {"contrast_packaged_into_primary_technical_service": 2, "incomplete_study": 2}
- unsupported reasons: {"incomplete_study": 1, "missing_device_linkage": 1, "missing_laterality": 1} -> {"incomplete_study": 2, "missing_device_linkage": 2, "missing_laterality": 2}

## OR / Procedural
- status counts: {"modifier_dependency_case": 0, "packaged_or_nonbillable_suppressed": 3, "recoverable_missed_charge": 0, "unsupported_charge_risk": 2} -> {"modifier_dependency_case": 0, "packaged_or_nonbillable_suppressed": 6, "recoverable_missed_charge": 2, "unsupported_charge_risk": 5}
- top failure class: packaged_or_nonbillable_suppressed -> packaged_or_nonbillable_suppressed
- suppression reasons: {"packaged_or_integral": 3} -> {"discontinued_before_billable_procedure_threshold": 4, "supply_integral_to_procedural_package": 2}
- unsupported reasons: {"missing_case_timestamp": 1, "missing_implant_linkage": 1} -> {"missing_case_timestamp": 2, "missing_implant_linkage": 3}

## Balance Notes
- No balance anti-pattern flags remain.
