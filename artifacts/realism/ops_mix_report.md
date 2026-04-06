# Ops Mix Report

Overall status: **pass**

## Summary
- pass: 3 | warn: 0 | fail: 0
- ops-mix snapshot: {"artifact_row_counts": {"claims_or_account_status": 62, "denials_feedback": 9, "encounters": 62, "exception_queue": 24, "expected_charge_opportunities": 94, "priority_scores": 24, "queue_history": 50}, "closed_compliance_count": 4, "department_queue_mix": {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 2, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 4}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 4, "Coding Pending Review": 3, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 2}, "Radiology / Interventional Radiology": {"Coding Pending Review": 2, "Documentation Support Exceptions": 3}}, "payable_signal_counts": {"closed_compliance_signal_rows": 4, "denial_category_counts": {"documentation_support_denial": 6, "technical_denial": 3}, "denials_feedback_rows": 9, "issue_domain_counts": {"Billing / claim-edit failure": 1, "Documentation support failure": 8}, "payer_group_counts": {"Blue Cross": 1, "Commercial": 3, "Managed Medicaid": 4, "Medicare": 1}, "upstream_linked_rows": 9}, "repeat_exception_rate_by_department": {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}, "repeat_root_cause_clusters_by_department": {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Billing edit management": 2, "Documentation behavior": 2, "Workflow / handoff": 4}, "Outpatient Infusion / Oncology Infusion": {"Coding practice": 5, "Documentation behavior": 4, "Workflow / handoff": 2}, "Radiology / Interventional Radiology": {"Coding practice": 2, "Documentation behavior": 3}}, "reroute_distribution": {"0": 10, "1": 6, "2": 4, "3": 4}, "status_stage_counts": {"Charge capture pending": 4, "Closed / monitored through denial feedback only": 4, "Coding pending": 5, "Correction / rebill pending": 2, "Documentation pending": 7, "Final billed": 30, "Prebill edit / hold": 6, "Ready to final bill": 4}}

## Medium Volume Ops Realism
- status: **pass**
- metrics: {"active_exception_count": 24, "department_queue_mix": {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 2, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 4}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 4, "Coding Pending Review": 3, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 2}, "Radiology / Interventional Radiology": {"Coding Pending Review": 2, "Documentation Support Exceptions": 3}}, "distinct_dominant_queues": 3, "encounter_count": 62, "multi_reroute_count": 8, "repeat_exception_rate_by_department": {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}, "repeat_root_cause_cluster_count_ge_2": 8, "reroute_distribution": {"0": 10, "1": 6, "2": 4, "3": 4}, "rerouted_case_count": 14}
- anti-pattern flags: none

## Payable State Signal Realism
- status: **pass**
- metrics: {"closed_compliance_count": 4, "closed_compliance_signal_rows": 4, "denial_category_counts": {"documentation_support_denial": 6, "technical_denial": 3}, "denials_feedback_row_count": 9, "issue_domain_counts": {"Billing / claim-edit failure": 1, "Documentation support failure": 8}, "linked_upstream_rate": 1.0, "payer_group_count": 4}
- anti-pattern flags: none

## Ops Mix Payable Antipatterns
- status: **pass**
- metrics: {"blank_upstream_issue_domain_count": 0, "denial_feedback_share_of_encounters": 0.1452, "distinct_dominant_queues": 3, "repeat_exception_rate_by_department": {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}, "top_failure_class_by_department": {"infusion": "modifier_dependency_case", "or_procedural": "packaged_or_nonbillable_suppressed", "radiology_ir": "unsupported_charge_risk"}}
- anti-pattern flags: none
