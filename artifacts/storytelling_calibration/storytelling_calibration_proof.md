# Chapter-Page Storytelling Calibration Proof

## Scope

- Goal: tighten chapter-page storytelling cues without adding narrative weight or changing page structure.
- Pages changed: `Opportunity & Action Tracker`, `Documentation Support Exceptions`.
- Shared helper changes: none.

## Files changed

- `src/ri_control_room/ui/opportunity_action_tracker.py`
- `src/ri_control_room/ui/documentation_exceptions.py`
- `tests/test_pages_remaining.py`

## Opportunity & Action Tracker cue

- Before sentence: `This page turns the current routed exception slice into owned interventions with checkpoint and validation signals.`
- After sentence: `Active routed exceptions are translated here into owned interventions with checkpoint and validation signals.`
- Before next move: `Billing operations owns the next move on Modifiers / Edits / Prebill Holds; validate confirm handoff clearance and queue exit on the next validation run. pattern focus: or / hospital outpatient surgery / procedural areas | modifiers / edits / prebill holds | workflow / handoff. recommendation remains hold until the next checkpoint confirms sustained change.`
- After next move: `Billing operations should clear the prebill hold on QUEUE-ACC-1025; validate queue exit on the next run.`

## Documentation Support Exceptions cue

- Before sentence: `This page monitors whether documented activity is still too weak to support expected facility charge opportunity in the current slice.`
- After sentence: `Documentation support is breaking where documented activity still lacks the billable support expected in the current slice.`
- Before current pressure: `missing case timestamp is driving 2 open documentation exception(s) in the current slice.`
- After current pressure: `Missing case time support is driving 2 open documentation exception(s).`
- Before next move: `Department operations owns the next move on IR001; Document coaching target and close documentation support gap.`
- After next move: `Department operations should close the documentation support gap on IR001.`

## Reduced templated phrasing

- No shared cue component rewrite was applied.
- Distinctness was improved by changing the opening lead sentence on the two target chapter pages only.
- Reference screenshot for unchanged chapter phrasing pattern: [reconciliation_phrase_reference.png](./reconciliation_phrase_reference.png)

## Browser proof

- Opportunity & Action Tracker before: [action_tracker_before_calibration.png](./action_tracker_before_calibration.png)
- Opportunity & Action Tracker after: [action_tracker_after_calibration.png](./action_tracker_after_calibration.png)
- Documentation Support Exceptions before: [documentation_before_calibration.png](./documentation_before_calibration.png)
- Documentation Support Exceptions after: [documentation_after_calibration.png](./documentation_after_calibration.png)
- Additional phrasing reference: [reconciliation_phrase_reference.png](./reconciliation_phrase_reference.png)

## Verification

- `pytest tests/test_pages_remaining.py tests/test_opportunity_action_tracker_trace.py tests/test_page_scenario_lab.py -q`

## Scope control

- No summary changes.
- No scenario-lab scope changes.
- No KPI, data-model, routing, or layout changes.
- Change type: copy calibration with light page-local helper support for shorter action text and operator-friendly documentation-gap phrasing.
