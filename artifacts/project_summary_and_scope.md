# Project Summary and Scope

## What this product is

- Hospital-informed
- Facility-side only
- Outpatient-first
- Deterministic-first
- React-first product surface
- Action-ready revenue integrity control room
- Synthetic/public-safe flagship project

In shipped form, this project is a reviewer-ready facility-side outpatient control-room product with React as the primary interaction surface. It maps documented performed activity to expected facility charge opportunity, identifies the current failed control, routes work to the accountable owner, separates recoverable from already-lost exposure, and supports thin follow-through, what-if, downstream signal, and memo layers without changing the deterministic core.

The Streamlit app remains a supporting companion surface for additional proof artifacts, comparison views, and reviewer context.

## What it is not

- Generic BI dashboard
- Denials-management platform
- Payer adjudication engine
- Pro-fee tool
- Predictive-first product
- Enterprise-wide rev-cycle suite
- Production-integrated hospital deployment

## Implemented now

### Primary product surface

- React app: `react-surface`
- One-click Windows launcher: `Launch React Surface Demo.cmd`

### Core operating surfaces

- `Control Room Summary`
- `Charge Reconciliation Monitor`
- `Modifiers / Edits / Prebill Holds`
- `Documentation Support Exceptions`
- `Opportunity & Action Tracker`

### Thin shipped extensions

- `Scenario Lab v0`
- `Denial Feedback + CDM Governance Monitor`
- `Revenue Integrity Decision Pack` trigger and markdown export from `Control Room Summary`

### Supporting companion surface

- Streamlit app entrypoint: `app/streamlit_app.py`
- Role in shipped story: supporting validation/proof context, not the primary product claim

### Implemented capability layer

- Deterministic exception engine grounded in documented performed activity rather than orders alone
- Explicit issue-domain versus root-cause separation
- One current primary blocker per active queue item
- Queue routing with accountable owner, supporting owner, escalation owner, and routing reason
- Queue-history transition ledger with reroutes and prior-queue path
- Governed KPI layer and reduced V1 priority scoring
- Case-detail and evidence-trace support for reviewer drill-down
- Action Tracker follow-through support with baseline/current metric movement and hold / expand / revise recommendation
- Scenario Lab v0 with visible levers, formulas, caps, and bounded what-if outputs
- Decision Pack export built from current governed outputs
- Reviewer proof artifacts, browser audits, realism reports, manual audit support, and supporting validation materials

## Deferred / intentionally not shipped

- Predictive triage as the core operating layer
- Broader denials workflow, appeals operations, or payer recovery platform behavior
- Fuller correction / rebill operations beyond thin support
- Broader department or service-line expansion beyond the frozen V1 set
- Workflow-engine or task-management sprawl beyond current reviewer-facing follow-through support
- Feature growth that weakens the facility-side, outpatient-first, deterministic-first boundary
- Production source integration or enterprise deployment claims

## Why this repo is ready to review

- The current repo shows believable facility-side outpatient control logic rather than generic leakage reporting.
- The React app demonstrates product engineering depth beyond analysis-only output: typed domain modeling, route composition, deterministic computation layers, and reviewer-facing UI communication.
- Performed activity, expected billable opportunity, actual charge state, and a thin downstream denial-signal layer are visible in current surfaces and artifacts.
- Current blocker, owner, aging, recoverability, and next action are explicit on the main operating surfaces.
- Packaged / non-billable / false-positive suppression is visible rather than hidden.
- Operational prioritization exists without requiring predictive logic.
- Reviewer-facing proof is already present across browser-visible artifacts, exports, realism materials, and tests, including walkthrough coherence proof, documentation-support trend realism proof, and charge reconciliation trend/scoping realism proof.

## Launch paths

### React (primary)

- One click on Windows: `Launch React Surface Demo.cmd`
- Terminal fallback: `cd react-surface` then `npm install` and `npm run dev`

### Streamlit (supporting)

- One click on Windows: `Launch Hospital Charge Capture Demo.cmd`
- Terminal fallback: `python scripts/run_demo.py`

## Public scope boundary

The public repo centers on the deterministic facility-side outpatient control-room core plus three intentionally thin extension layers.

### Product center

- Deterministic failed-control detection
- Owner-routed active exception work
- Stage-specific aging and recoverability
- Case-level evidence trace
- Reviewer-facing proof of coherence and realism
- React-first product interaction layer

### Shipped but secondary

- Scenario Lab v0 as deterministic what-if support only
- Denial feedback as downstream evidence only, not a denials-workflow or payable-state center
- Decision Pack as a thin leave-behind artifact, not stronger proof than the live queue

### Not inside the shipped boundary

- Predictive triage engine
- Denials operating platform
- Pro-fee or inpatient-first expansion
- Broad workflow automation platform

## Supporting files

- [proof_index.md](./proof_index.md)
- [success_definition_checklist.md](./success_definition_checklist.md)
- [deferred_scope_boundary.md](./deferred_scope_boundary.md)
- [OR walkthrough talk track](./reviewer_walkthrough_pack/or_prebill_hold_talk_track.md)
- [React screenshot refresh note](./browser_audit/react_surface_lens_screens_2026-05-25.md)

## Bottom line

This project is ready to present as a flagship synthetic/public-safe portfolio repo because the deterministic control-room core, reviewer proof, and scope boundary are explicit. Remaining work is broader future depth outside the current public scope, including stronger real-source grounding and broader downstream maturity, not a missing core product story.
