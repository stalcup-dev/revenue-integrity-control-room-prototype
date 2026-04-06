# Transition Ledger Report

Overall status: **pass**

## Queue History Shape
- queue_history rows: 50 vs exception_queue rows: 24
- transition-event density: 2.0833
- multi-event cases: 14
- reroute buckets: {"0": 10, "1": 6, "2": 4, "3+": 4}

## Transition Evidence
- top queue transitions: {"Charge Reconciliation Monitor -> Coding Pending Review": 4, "Charge Reconciliation Monitor -> Documentation Support Exceptions": 4, "Coding Pending Review -> Modifiers / Edits / Prebill Holds": 8, "Documentation Support Exceptions -> Coding Pending Review": 8, "Modifiers / Edits / Prebill Holds -> Correction / Rebill Pending": 2}
- routing-reason coverage: 1.0
- top routing reasons: {"Charge reconciliation flagged missing waste support before bill drop.": 2, "Department follow-through could not validate waste support after revenue-integrity handoff.": 2, "Documented waste is waiting on charge-entry follow-through before bill drop.": 2, "Residual waste-support risk remained after coding review and moved into prebill hold.": 2, "Resolved waste support rerouted into coding review for modifier alignment.": 2, "Timed infusion cannot clear until stop time support is completed.": 2}
- days in prior queue summary: {"max": 3.0, "median": 1.0, "min": 0.0, "nunique": 4}

## Intervention Follow-Through
- checkpoint distribution: {"Baseline captured": 5, "Checkpoint overdue": 2, "Monitor next checkpoint": 9, "Pilot checkpoint complete": 6, "Turnaround improving": 2}
- recommendation distribution: {"Expand": 6, "Hold": 12, "Revise": 6}
- metric delta summary: {"max_delta": 2.2, "median_delta": 0.65, "nonzero_count": 20, "positive_count": 18}
- correction turnaround rows: 8

## What Still Feels Fake
- No transition-ledger or intervention follow-through flags remain.
