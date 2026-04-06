# Docs Reconciliation Report

## Files reviewed

- `docs/BUILD_SOT.md`
- `docs/V1_IMPLEMENTATION_PLAN.md`
- `docs/KPI_DICTIONARY.md`
- `docs/DATA_MODEL.md`
- `docs/SYNTHETIC_DATA_RULES.md`
- `docs/DEPARTMENT_LOGIC_MAP.md`

## Files changed

- `docs/BUILD_SOT.md`
- `docs/V1_IMPLEMENTATION_PLAN.md`
- `docs/KPI_DICTIONARY.md`
- `docs/DATA_MODEL.md`
- `docs/SYNTHETIC_DATA_RULES.md`
- `docs/DEPARTMENT_LOGIC_MAP.md`

## Contradictions fixed

- Restored `BUILD_SOT.md` as the clear governing source by adding related-doc navigation and explicit doc-role definitions.
- Removed stale V1 page drift in `BUILD_SOT.md` by dropping the dedicated `Status / Observation Integrity` page from the frozen V1 page set.
- Removed stale observation-first V1 drift from `BUILD_SOT.md` page, KPI, scenario-lever, expected-signal, and build-order sections where later frozen V1 scope had clearly superseded it.
- Reconciled the V1 build order in `BUILD_SOT.md` so the named anchor departments and V1 page list match the frozen V1 scope.
- Reconciled `V1_IMPLEMENTATION_PLAN.md` to the saved governing scope, including exact V1 departments, exact V1 pages, V2 Scenario Lab, V3-or-later Predictive Triage, and the saved core V1 table set.
- Reconciled `KPI_DICTIONARY.md` to the authoritative KPI layer by renaming `Dollars already lost` to `Dollars already lost after timing window`, adding `Edit first-pass clearance rate`, and deferring `Observation-hours exception rate`.
- Reconciled `DATA_MODEL.md` to the authoritative workflow-state model by tightening `claims_or_account_status`, `exception_queue`, stage-specific aging notes, and making `corrections_rebills` a partial V1 structure instead of a pure placeholder.
- Replaced stale “BUILD_SOT was empty” assumptions across the dependent docs so each document now points back to `BUILD_SOT.md` as the sole governing source.

## Any unresolved ambiguity requiring human decision

- No blocking V1 scope contradictions remain after reconciliation.
- Future-phase treatment of ED / Observation remains optional-later in `BUILD_SOT.md`, but it is no longer presented as a primary V1 department story, V1 page, or active V1 KPI.

## Final alignment statement

The reviewed doc set is now aligned to `docs/BUILD_SOT.md` as the governing source for V1 scope, page set, KPI set, workflow-state logic, recoverability framing, synthetic-data rules, and department-specific performed-activity logic.
