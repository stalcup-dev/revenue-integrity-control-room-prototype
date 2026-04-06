# Reviewer Walkthrough: OR Prebill Hold Story

This walkthrough freezes one reviewer-safe story from the default `Control Room Summary` slice: `QUEUE-ACC-1025` on encounter `OR006` in `OR / Hospital Outpatient Surgery / Procedural Areas`. The failed control is prebill edit resolution. Documented performed activity supports a primary facility procedure charge for a completed outpatient procedure, but a workflow/handoff failure left the account in `Modifiers / Edits / Prebill Holds`, owned by `Billing operations`, aged `7` days and already `Post-window financially lost`. This pack is synthetic/public-safe and is intended to prove story coherence across summary, proof, and memo surfaces for one frozen V1 example only.

## Screenshot Pack

- [Featured story on Control Room Summary](./summary_featured_story.png)
- [Featured story with representative proof opened](./summary_featured_story_proof_open.png)
- [Decision Pack current control story section](./decision_pack_current_control_story.png)
- Matching exported memo: [revenue_integrity_decision_pack.md](../decision_pack/revenue_integrity_decision_pack.md)

## 3-Step Reviewer Flow

1. Start on `Control Room Summary` and read the `Featured Deterministic Story`.
   Confirm the failed control, issue domain, root cause, blocker, owner, aging, recoverability, and next action all appear in one short narrative.
2. Open `View proof for representative case: QUEUE-ACC-1025`.
   Confirm why the case surfaced: documented performed activity supports the expected facility procedure charge, actual charge state is `posted held prebill`, the current blocker is `Prebill edit or hold unresolved`, and the case is still routed to `Billing operations`.
3. Open `Revenue Integrity Decision Pack` and compare `Current control story`.
   Confirm the memo keeps the same narrative as the summary and proof surfaces instead of inventing a new explanation.

## Parity Note

| Narrative element | Summary story | Proof case | Memo / export |
| --- | --- | --- | --- |
| Control failed | `Prebill edit resolution` | Current queue and routing history show prebill hold escalation into `Modifiers / Edits / Prebill Holds` | `Control failure type: Prebill edit resolution` |
| Why the case surfaced | Documented activity supports a primary facility procedure charge; actual charge state is `posted held prebill` | Control narrative repeats documented activity support plus actual charge state `posted_held_prebill` | `Exception pattern surfaced` keeps the same reason |
| Issue domain | `Billing / claim-edit failure` | Classification: `Billing / claim-edit failure` | `Issue domain: Billing / claim-edit failure` |
| Root cause | `Workflow / handoff` | Classification: `Workflow / handoff` | `Root cause mechanism: Workflow / handoff` |
| Blocker | `Prebill edit or hold unresolved` | Classification: `Prebill edit or hold unresolved` | `Where work is stuck now: Prebill edit / hold -> Prebill edit or hold unresolved -> Modifiers / Edits / Prebill Holds` |
| Owner | `Billing operations` | Case header and classification: `Billing operations` | `Who owns it now: Billing operations` |
| Aging / SLA | `7 days` and `Overdue against 5-day threshold` | `days_in_stage = 7`, `sla_status = Overdue` | `Aging / SLA: 7 days in stage ... Overdue against 5-day threshold` |
| Recoverability | `Post-window financially lost` | Classification: `Post-window financially lost` | `Recoverability: Post-window financially lost` |
| Next action | `Work assigned queue, clear hold, and confirm account release path.` | Representative proof KPI repeats the same recommended next action | `Recommended next action: Work assigned queue, clear hold, and confirm account release path.` |

## What This Proves

- One deterministic control story can be read at summary level, opened to case-level proof, and restated in the Decision Pack without changing the core narrative.
- A reviewer can see what control failed, why the case surfaced, who owns it now, whether it is still recoverable, and what should happen next without reading code.
- The proof is operationally structured rather than marketing-heavy: blocker, queue, owner, aging, recoverability, and next step remain explicit.

## What This Does Not Claim Yet

- This does not claim live source-system integration or production-scale operational proof.
- This does not claim broad department coverage beyond one frozen V1 story.
- This does not claim predictive capability; the current proof is deterministic and evidence-trace based.
- This does not claim financial recovery is still possible on this case; the story explicitly says it is already post-window lost.
