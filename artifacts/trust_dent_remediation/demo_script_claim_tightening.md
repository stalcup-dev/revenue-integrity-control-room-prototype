# Demo Script Claim Tightening

## Rule

Prefer claim -> proof -> caveat.

Do not let the demo sound like:

- production deployment
- denials are the operating center
- Scenario Lab is a forecast engine
- predictive logic is doing the real work

## 1. Control Room Summary

- Current claim: `This is the operating heartbeat of the product: current failed controls, current owner queues, and recoverable-versus-lost exposure in the same view.`
- Risk in current phrasing: `Operating heartbeat` sounds more mature and scale-proven than the evidence supports.
- Tightened claim: `This is the current deterministic control snapshot for the filtered slice: active failed controls, accountable queues, and recoverable-versus-lost exposure.`
- Proof to point at: `Open actionable exceptions`, `Recoverable dollars open`, `Already lost`, `Why The Backlog Exists`, `Where Work Is Stuck Now`, `Who Should Act Next`
- Caveat to say out loud if challenged: `This proves current control structure and queue governance, not production-scale queue utility.`

## 2. Queue governance / one-current-blocker / aging / ownership

- Current claim: `Every active item is anchored to one current blocker, one current queue, one accountable owner, and stage-specific aging instead of a pile of overlapping issue tags.`
- Risk in current phrasing: Strong claim, but it needs immediate proof or it will sound like governed language rather than visible evidence.
- Tightened claim: `For the selected case, the model publishes one current blocker, one current queue, one accountable owner, and stage-specific aging logic.`
- Proof to point at: `Queue Priority Ranking`, `Case Header`, `Classification`, `Queue Governance`, `Routing History`
- Caveat to say out loud if challenged: `This is current deterministic routing logic for the prototype, not a claim that every hospital would use the same ownership or queue thresholds.`

## 3. Action Tracker follow-through

- Current claim: `This page turns exception ranking into operational follow-through by showing intervention owner, baseline metric, current metric, downstream outcome signal, and hold/expand/revise recommendation.`
- Risk in current phrasing: `Operational follow-through` can sound like a fuller intervention-management platform than the repo actually implements.
- Tightened claim: `This page adds thin follow-through evidence to the ranked exceptions by showing intervention owner, monitored metric movement, downstream signal, and the current hold/expand/revise recommendation.`
- Proof to point at: `Intervention Snapshot`, `Recurring Issue Patterns`, `Intervention Owners`, `Intervention Plan`, action-tracker follow-through proof artifact
- Caveat to say out loud if challenged: `This is believable follow-through support, not a full task-management or intervention platform.`

## 4. Scenario Lab

- Current claim: `Scenario Lab stays in-bounds by using explicit operational levers, visible formulas, and caps rather than black-box forecasting.`
- Risk in current phrasing: Better than most, but still needs a direct caveat so reviewers do not hear `forecasting` and `financial engine`.
- Tightened claim: `Scenario Lab is a thin deterministic what-if surface that uses visible levers, formulas, and caps to test operational assumptions against the current slice.`
- Proof to point at: three levers, `Projected Impact`, `Scenario Output Detail`, `How this is calculated`, Scenario Lab audit note
- Caveat to say out loud if challenged: `This is not a forecast engine and not a finance planning model; it is transparent what-if support only.`

## 5. Denial Feedback + CDM Governance Monitor

- Current claim: `Denials stay downstream and thin here; the point is to validate or surface upstream control failures without turning the product into a denials platform.`
- Risk in current phrasing: Good guardrail, but only if the demo stays brief. Too much time on this page will still make denials feel central.
- Tightened claim: `This page keeps denials as downstream evidence only, linking them back to likely upstream issue domain, root cause, and owner path without turning denials into the operating center.`
- Proof to point at: denial pattern table, selected-pattern linkage, Denial/CDM audit note
- Caveat to say out loud if challenged: `This is not an appeals workflow, adjudication engine, or denials workqueue.`

## 6. Decision Pack trigger

- Current claim: `This packages the current governed app state into a short leadership-ready artifact without inventing a separate reporting logic path.`
- Risk in current phrasing: `Leadership-ready` can sound smoother and more validated than the current sample supports.
- Tightened claim: `This generates a short deterministic snapshot of the current governed app state for reviewer or leadership readout, using the same bounded logic already in the app.`
- Proof to point at: Decision Pack trigger, rendered memo sections, Decision Pack audit note
- Caveat to say out loud if challenged: `Use the memo as a current snapshot and leave-behind, not as stronger proof than the live queue or the current manifest state.`

## Closing guardrail

If challenged on maturity, say:

`The claim here is reviewer-ready deterministic control logic with current evidence, not production deployment.`

If challenged on predictive scope, say:

`Predictive logic is secondary and not required for the current product story to hold.`
