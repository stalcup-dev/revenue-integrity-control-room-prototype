# Ops Mix Before/After Diff

## Row Counts
- encounters: 30 -> 62
- claims_or_account_status: 30 -> 62
- expected_charge_opportunities: 45 -> 94
- exception_queue: 12 -> 24
- queue_history: 12 -> 50
- priority_scores: 12 -> 24
- denials_feedback: 0 -> 9

## Queue Concentration
- department queue mix: {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 1, "Documentation Support Exceptions": 1, "Modifiers / Edits / Prebill Holds": 2}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 2, "Coding Pending Review": 1, "Documentation Support Exceptions": 1, "Modifiers / Edits / Prebill Holds": 1}, "Radiology / Interventional Radiology": {"Coding Pending Review": 1, "Documentation Support Exceptions": 2}} -> {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Correction / Rebill Pending": 2, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 4}, "Outpatient Infusion / Oncology Infusion": {"Charge Reconciliation Monitor": 4, "Coding Pending Review": 3, "Documentation Support Exceptions": 2, "Modifiers / Edits / Prebill Holds": 2}, "Radiology / Interventional Radiology": {"Coding Pending Review": 2, "Documentation Support Exceptions": 3}}

## Reroute Distribution
- reroute distribution: {"0": 7, "1": 2, "2": 2, "3": 1} -> {"0": 10, "1": 6, "2": 4, "3": 4}

## Repeat Patterns
- repeat exception rate by department: {"OR / Hospital Outpatient Surgery / Procedural Areas": 0.75, "Outpatient Infusion / Oncology Infusion": 0.2, "Radiology / Interventional Radiology": 0.3333} -> {"OR / Hospital Outpatient Surgery / Procedural Areas": 1.0, "Outpatient Infusion / Oncology Infusion": 0.3636, "Radiology / Interventional Radiology": 0.4}
- repeat root-cause clusters: {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Billing edit management": 1, "Documentation behavior": 1, "Workflow / handoff": 2}, "Outpatient Infusion / Oncology Infusion": {"Coding practice": 2, "Documentation behavior": 2, "Workflow / handoff": 1}, "Radiology / Interventional Radiology": {"Coding practice": 1, "Documentation behavior": 2}} -> {"OR / Hospital Outpatient Surgery / Procedural Areas": {"Billing edit management": 2, "Documentation behavior": 2, "Workflow / handoff": 4}, "Outpatient Infusion / Oncology Infusion": {"Coding practice": 5, "Documentation behavior": 4, "Workflow / handoff": 2}, "Radiology / Interventional Radiology": {"Coding practice": 2, "Documentation behavior": 3}}

## Payable-State Signals
- closed compliance count: 1 -> 4
- payable signal counts: {"denials_feedback_rows": 0, "issue_domain_counts": {}, "payer_groups": {}, "upstream_linked_rows": 0} -> {"closed_compliance_signal_rows": 4, "denial_category_counts": {"documentation_support_denial": 6, "technical_denial": 3}, "denials_feedback_rows": 9, "issue_domain_counts": {"Billing / claim-edit failure": 1, "Documentation support failure": 8}, "payer_group_counts": {"Blue Cross": 1, "Commercial": 3, "Managed Medicaid": 4, "Medicare": 1}, "upstream_linked_rows": 9}

## Remaining Notes
- No ops-mix or payable-state anti-pattern flags remain.
