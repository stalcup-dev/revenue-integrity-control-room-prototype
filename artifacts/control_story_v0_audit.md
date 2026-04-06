# Deterministic Control Story v0 Audit Note

## Story structure

- The shared story stays in a fixed deterministic sequence: control failure type -> exception pattern surfaced -> where work is stuck now -> who owns it now -> recoverability -> recommended next action.
- The block separately shows `issue domain` and `root cause mechanism` so the failure class and causal mechanism are not blurred together.
- The block keeps stage-specific aging visible through `days in stage`, `aging basis label`, `SLA status`, and the current stage/blocker/queue path.

## Data sources used

- `data/processed/priority_scores.parquet` supplies the selected routed work item, service line, department, issue domain, root cause, one current blocker, current queue, accountable owner, stage aging, SLA status, recoverability, and dollars.
- `data/processed/expected_charge_opportunities.parquet`, `data/processed/charge_events.parquet`, and `data/processed/claim_lines.parquet` feed the selected case trace used to keep the story grounded in documented performed activity, expected facility charge opportunity, and actual charge state.
- `src/ri_control_room/ui/opportunity_action_tracker.py` and the shared control-story helper use the same deterministic next-action mapping, so the summary block and the memo cannot drift on recommended action wording.

## Why this stays deterministic

- The story selects one current routed work item from the already priority-ranked filtered queue and then tightens the view to a like-for-like cohort; it does not score, predict, or simulate anything new.
- Every visible sentence is assembled from governed fields already present in the queue and case-detail layer. No queue routing logic, scenario math, or predictive triage was changed.
- Suppression is only mentioned when the selected case already proves suppressed expected opportunities in the deterministic expected-vs-actual trace.

## Proof artifacts

- Control Room Summary screenshot: [control_story_summary.png](./browser_audit/control_story_summary.png)
- Sample exported Decision Pack: [revenue_integrity_decision_pack.md](./decision_pack/revenue_integrity_decision_pack.md)
