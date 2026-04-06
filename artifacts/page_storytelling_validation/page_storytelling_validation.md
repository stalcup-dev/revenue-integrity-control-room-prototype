# Secondary Storytelling Pattern Validation

## Scope

Added a lightweight, page-native storytelling cue across the non-summary work pages so each surface answers three reviewer questions near the top:

- what control this page is monitoring
- where current pressure sits in the filtered slice
- who owns the next move

The pattern stays intentionally smaller than the `Control Room Summary` featured story. It uses one framing sentence, three compact callouts, and an optional control note.

## Page-by-page pattern shift

| Page | Old top pattern | New top pattern |
| --- | --- | --- |
| `Charge Reconciliation Monitor` | Header, active filters, KPI row | Header, active filters, compact reconciliation story cue naming the control, current service-line pressure, and owner next move before the KPI row |
| `Modifiers / Edits / Prebill Holds` | Header, active filters, KPI row | Header, active filters, compact prebill-edit story cue naming unresolved edit pressure, repeat handoff concentration, and billing-owner next move |
| `Documentation Support Exceptions` | Header, active filters, KPI row | Header, active filters, compact documentation-support story cue naming unsupported-charge pressure, gap pattern, and routed next move |
| `Opportunity & Action Tracker` | Header, active filters, KPI row | Header, active filters, compact intervention-follow-through story cue naming checkpoint pressure, current recommendation, and intervention-owner next move |
| `Scenario Lab` | Header, active filters, levers | Intentionally thinner what-if framing cue only, clarifying that the page is deterministic, capped, and not a queue-narrative replacement |

## Before / after browser proof

### Charge Reconciliation Monitor

- Before: [charge_reconciliation_before.png](./charge_reconciliation_before.png)
- After: [charge_reconciliation_after.png](./charge_reconciliation_after.png)
- What changed: the page now opens with a mini control story that names reconciliation timeliness pressure, the current driving service line, and the accountable next move.

### Documentation Support Exceptions

- Before: [documentation_before.png](./documentation_before.png)
- After: [documentation_after.png](./documentation_after.png)
- What changed: the page now opens with a mini control story that names the documentation-support control, the current gap pattern, and the routed owner next move.

### Opportunity & Action Tracker

- Before: [action_tracker_before.png](./action_tracker_before.png)
- After: [action_tracker_after.png](./action_tracker_after.png)
- What changed: the page now opens with a mini intervention story that names checkpoint pressure, the current recommendation framing, and the intervention owner who should act next.

### Modifiers / Edits / Prebill Holds

- Before: [modifiers_before.png](./modifiers_before.png)
- After: [modifiers_after.png](./modifiers_after.png)
- What changed: the page now opens with a mini prebill-edit story that names unresolved hold pressure, repeat-pattern concentration, and the billing-side next move.

### Scenario Lab

- After only: [scenario_lab_after.png](./scenario_lab_after.png)
- Why thinner: this page is a secondary what-if support surface, not an operating queue. The framing is intentionally lighter so it reinforces scope without pretending to carry the main narrative burden.

## Capture note

The before screenshots were preserved from the prior filtered browser-audit slice. The after screenshots were captured on the same OR plus Radiology, pre-final-bill-recoverable slice so the storytelling change is the main visible delta rather than a filter change.
