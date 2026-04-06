from __future__ import annotations

APP_TITLE = "Hospital Facility-Side Revenue Integrity Control Room"

FROZEN_V1_DEPARTMENTS = (
    "Outpatient Infusion / Oncology Infusion",
    "Radiology / Interventional Radiology",
    "OR / Hospital Outpatient Surgery / Procedural Areas",
)

WORKFLOW_STAGE_LADDER = (
    "Open encounter",
    "Charge capture pending",
    "Documentation pending",
    "Coding pending",
    "Prebill edit / hold",
    "Ready to final bill",
    "Final billed",
    "Correction / rebill pending",
    "Closed / monitored through denial feedback only",
)

RECOVERABILITY_STATES = (
    "Pre-final-bill recoverable",
    "Post-final-bill recoverable by correction / rebill",
    "Post-window financially lost",
    "Financially closed but still compliance-relevant",
)

V1_SCOPE_NOTE = (
    "Deterministic, outpatient-first, facility-side control room. "
    "Scenario Lab is transparent, secondary, and non-predictive."
)

V1_PAGE_REGISTRY = (
    ("01_Control_Room_Summary.py", "Control Room Summary", ":material/dashboard:"),
    (
        "02_Charge_Reconciliation_Monitor.py",
        "Charge Reconciliation Monitor",
        ":material/fact_check:",
    ),
    (
        "03_Modifiers_Edits_Prebill_Holds.py",
        "Modifiers / Edits / Prebill Holds",
        ":material/rule:",
    ),
    (
        "04_Documentation_Support_Exceptions.py",
        "Documentation Support Exceptions",
        ":material/description:",
    ),
    (
        "05_Opportunity_Action_Tracker.py",
        "Opportunity & Action Tracker",
        ":material/task_alt:",
    ),
    (
        "06_Scenario_Lab.py",
        "Scenario Lab",
        ":material/tune:",
    ),
    (
        "07_Denial_Feedback_CDM_Governance.py",
        "Denial Feedback + CDM Governance Monitor",
        ":material/radar:",
    ),
)

V1_PAGE_FILES = tuple(filename for filename, _, _ in V1_PAGE_REGISTRY)
