# Hospital Charge Capture Analytics Case Study

This repo is easiest to evaluate as a story, not as a feature list.

The core question is simple: when documented outpatient hospital work should have produced a facility charge but did not cleanly make it to billable state, can you tell what failed, who owns the next move, and whether the dollars are still recoverable?

This project answers that question with a deterministic, facility-side, outpatient-first revenue integrity control room built as a React-first product surface on public-safe synthetic data.

## The Business Problem

Hospital revenue leakage often appears first as ambiguity.

A procedure happened. Documentation exists. Something should likely have been charged. But the work can break across documentation, coding, CDM, billing edits, or operational handoffs. Generic dashboards can show lag, aging, and dollars. They usually do not tell a reviewer which control failed, why the case surfaced, who owns it now, or whether intervention still matters.

That is the gap this app is designed to close.

## Business Question to Decision

- Business question: Which outpatient exception queues should be worked first to reduce preventable revenue loss and compliance risk?
- Decision produced: Prioritize queues by current blocker, accountable owner, aging, and recoverability so teams can focus first on salvageable work with the highest operational urgency.

## The Story In One Case

The clearest reviewer-safe example in the repo is encounter `OR006`, surfaced as queue item `QUEUE-ACC-1025`.

An outpatient OR procedure is completed. Documented performed activity supports a primary facility procedure charge. But the account does not progress cleanly because it is stuck in `Modifiers / Edits / Prebill Holds`.

The app does not stop at "charge leakage detected." It narrows the story down deterministically:

- Failed control: `Prebill edit resolution`
- Issue domain: `Billing / claim-edit failure`
- Root cause: `Workflow / handoff`
- Current owner: `Billing operations`
- Aging: `7` days in stage, overdue against a `5`-day threshold
- Recoverability: `Post-window financially lost`
- Next move: clear the hold and confirm the account release path

That is the product claim: the repo makes the operating story legible, actionable, and provable.

## Business Impact (Current Shipped Slice)

This project does more than surface exceptions. It translates analysis into operating decisions with measurable impact signals.

### Financial and queue impact

- Open exceptions currently governed in one operating view: `24`
- Recoverable dollars still open: `$9,740`
- Dollars already lost after timing window: `$3,630`
- Exceptions currently breaching SLA: `17`
- Top pressure queue: `Billing operations | Modifiers / Edits / Prebill Holds`

### Why this matters operationally

- The worklist is not just descriptive. It distinguishes what can still be recovered from what is financially closed, so teams can prioritize salvageable work first.
- The queue and owner framing reduces ambiguity by making the current blocker and accountable team explicit at case level.
- The deterministic trace from performed activity to expected charge opportunity shortens root-cause time compared with generic KPI-only reporting.

### Scenario-informed upside (explicitly caveated)

On the same filtered slice, the current Scenario Lab v0 snapshot shows:

- Projected backlog reduction: `4`
- Projected SLA improvement: `+16.6 points`
- Projected recoverable dollar lift: `$2,464`
- 90-day impact estimate: `$7,392`

These scenario figures are what-if estimates, not forecasts. They are included to support intervention prioritization, not to replace the deterministic operating proof.

### Scope caveat

All impact figures in this public repo are synthetic and public-safe by design. They demonstrate decision quality and operating realism, not live hospital financial performance.

## Visual Walkthrough

The current visual proof path is React-first and product-first: these screenshots highlight not just analysis outcomes, but software product decisions in routing, caveat framing, and evidence packaging.

<p align="center">
  <a href="artifacts/browser_audit/react_control_room_summary_2026-05-25.png"><img src="artifacts/browser_audit/react_control_room_summary_2026-05-25.png" alt="React Control Room Summary" width="48%"></a>
  <a href="artifacts/browser_audit/react_reviewer_proof_pack_lens_2026-05-25.png"><img src="artifacts/browser_audit/react_reviewer_proof_pack_lens_2026-05-25.png" alt="React Reviewer Proof Pack Lens" width="48%"></a>
</p>

<p align="center"><em>Top row: React shell and proof-pack lens show deterministic operations framing and core-proof-first packaging in the same product surface.</em></p>

<p align="center">
  <a href="artifacts/browser_audit/react_scenario_claim_tightening_lens_2026-05-25.png"><img src="artifacts/browser_audit/react_scenario_claim_tightening_lens_2026-05-25.png" alt="React Scenario Claim-Tightening Lens" width="48%"></a>
  <a href="artifacts/browser_audit/react_decision_pack_freshness_lens_2026-05-25.png"><img src="artifacts/browser_audit/react_decision_pack_freshness_lens_2026-05-25.png" alt="React Decision Pack Freshness Lens" width="48%"></a>
</p>

<p align="center"><em>Bottom row: React caveat governance and freshness framing keep scenario language bounded and reviewer-safe.</em></p>

Screenshot captions:

1. React Control Room Summary: persistent global filters, deterministic queue posture, and product-level app shell quality.
2. React Reviewer Proof Pack Lens: explicit core-vs-supporting proof hierarchy and reviewer read-order guidance.
3. React Scenario Claim-Tightening Lens: claim wording is tightened to proof anchors with caveats visible at read time.
4. React Decision Pack Freshness Lens: snapshot date and confidence framing reduce stale-proof and overclaim risk.

## What The Reviewer Should Notice

1. The story begins with performed activity, not with a loose financial estimate.
2. The current failed control is explicit instead of buried in a generic exception bucket.
3. Ownership is visible at the case level.
4. Aging and recoverability make the work operational, not just descriptive.
5. The same story survives across summary, proof, and exported memo surfaces.

## Why This Matters

A believable analytics case study should show more than charts. It should show decision logic.

This repo demonstrates that a reviewer can move from surfaced issue, to case-level evidence, to routed intervention, to exported decision-pack language without the narrative changing. That is stronger than a dashboard that only says performance is off and leaves the reviewer guessing about cause and ownership.

## How To Review This Repo

After this page, use this order:

1. [Reviewer walkthrough](./artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md)
2. [Decision Pack export](./artifacts/decision_pack/revenue_integrity_decision_pack.md)
3. [Current shipped realism state](./artifacts/realism/post_tuning_realism_report.md)
4. [Project summary and scope](./artifacts/project_summary_and_scope.md)

If you want the boundary/spec path first instead, open [Project summary and scope](./artifacts/project_summary_and_scope.md).

## Scope Boundary

This case study is intentionally bounded.

- Facility-side only
- Outpatient-first only
- Deterministic-first
- Public-safe synthetic data only
- Not a denials platform
- Not a predictive triage demo
- Not a production-integrated hospital deployment

That boundary is part of the credibility. The repo is making a focused claim about deterministic control-room logic, traceability, and operating workflow clarity, not pretending to be a full enterprise rev-cycle platform.
