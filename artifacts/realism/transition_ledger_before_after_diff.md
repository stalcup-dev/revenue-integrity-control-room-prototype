# Transition Ledger Before/After Diff

## Queue History Shape
- queue_history_row_count: 24 -> 50
- exception_queue_row_count: 24 -> 24
- transition_event_density: 1 -> 2.0833
- multi_event_case_count: 10 -> 14
- reroute buckets: {"0": 14, "1": 4, "2": 4, "3+": 2} -> {"0": 10, "1": 6, "2": 4, "3+": 4}

## Transition Evidence
- top transitions: {"Charge Reconciliation Monitor -> Modifiers / Edits / Prebill Holds": 2, "Coding Pending Review -> Modifiers / Edits / Prebill Holds": 4, "Documentation Support Exceptions -> Coding Pending Review": 2, "Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending": 2} -> {"Charge Reconciliation Monitor -> Coding Pending Review": 4, "Charge Reconciliation Monitor -> Documentation Support Exceptions": 4, "Coding Pending Review -> Modifiers / Edits / Prebill Holds": 8, "Documentation Support Exceptions -> Coding Pending Review": 8, "Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending": 2}
- routing-reason coverage: 1 -> 1
- days in prior queue summary: {"max": 3.0, "median": 0.0, "min": 0.0, "nunique": 4} -> {"max": 3.0, "median": 1.0, "min": 0.0, "nunique": 4}

## Intervention Follow-Through
- checkpoint distribution: {} -> {"Baseline captured": 5, "Checkpoint overdue": 2, "Monitor next checkpoint": 9, "Pilot checkpoint complete": 6, "Turnaround improving": 2}
- recommendation distribution: {} -> {"Expand": 6, "Hold": 12, "Revise": 6}
- metric delta summary: {} -> {"max_delta": 2.2, "median_delta": 0.65, "nonzero_count": 20, "positive_count": 18}

## Remaining Notes
- No transition-ledger or intervention follow-through flags remain.
