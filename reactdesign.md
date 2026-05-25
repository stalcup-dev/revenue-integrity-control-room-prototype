# design.md — React Revenue Integrity Control Room

## Recommended coding-agent model

Use a higher-tier reasoning/code model for the first implementation slice because this is a domain-heavy healthcare analytics UI with multiple interacting concepts. Use a smaller/mini model only for narrow follow-up tasks such as copy polish, component extraction, CSS cleanup, or fixture expansion.

---

## 1. North Star

### Decision

Which facility-side outpatient departments, service lines, and owner-routed exception queues should leadership prioritize first to reduce legitimate revenue leakage and compliance risk?

### Metric / threshold

Surface queue pressure by dollars at risk, recoverable dollars, blocker aging, active case count, owner queue, recoverability state, and failed-control pattern.

### Action

Help a reviewer or leader answer, in under 10 seconds:

1. What control failed?
2. Who owns the exception now?
3. How old is it?
4. Is it still recoverable?
5. What should happen next?

This React build is a portfolio-grade product interface for the existing hospital facility-side outpatient revenue integrity control-room project. It should look polished, modern, and executive-ready while preserving the deterministic operating logic of the original project.

---

## 2. Product positioning

Build this as a **hospital-native revenue integrity control room**, not a generic BI dashboard.

The interface should feel like:

- a control environment
- an owner-routed operational work system
- a case investigation surface
- an executive decision page
- a reviewer-ready portfolio product

It should not feel like:

- a generic KPI dashboard
- a random chart gallery
- a denials-management platform
- an AI/ML demo
- a claims adjudication engine
- a reimbursement prediction toy

The strongest portfolio message is:

> I converted a deterministic hospital revenue integrity analytics project into a polished React product interface that shows healthcare analytics judgment, frontend execution, and decision-focused design.

---

## 3. Locked domain scope

### Facility-side only

This app is about hospital facility billing controls. Do not drift into professional-fee billing.

### Outpatient-first

The control room is focused on outpatient / facility-side charge capture, reconciliation, documentation support, prebill exception management, correction / rebill review, and downstream signal monitoring.

### Frozen V1 departments

Use these as the primary department anchors:

1. Outpatient Infusion / Oncology Infusion
2. Radiology / Interventional Radiology
3. OR / Hospital Outpatient Surgery / Procedural Areas

### Deferred areas

Do not add these as primary V1 sections:

- ED / Observation
- Cath lab / endoscopy expansion
- Enterprise denials operations
- Broad inpatient DRG optimization
- Professional fee workflows
- Payer contract modeling
- Predictive triage
- Full Scenario Lab

---

## 4. Non-negotiable business rules

### Rule 1 — Performed → Billable → Payable

The UI must visibly respect this chain:

- performed does not automatically mean billable
- billable does not automatically mean separately payable
- expected-charge logic must come from documented performed activity, not orders alone
- not every documented activity should create a separately payable facility line

### Rule 2 — Deterministic first

The credibility engine is deterministic exception logic. Do not center the UI around AI scoring, prediction, or vague leakage estimation.

### Rule 3 — One-current-blocker rule

A case can have multiple issue tags, but only one current primary blocker should drive:

- routing
- owner attribution
- aging
- current queue placement
- next action

### Rule 4 — Action-first

Every visible page should help answer one or more of these:

- What queue should be worked first?
- Which department is overdue?
- Which dollars are still recoverable?
- Which cases are suppressed by design?
- Which intervention should be held, expanded, or revised?

---

## 5. Design principles

### Visual style

Target: professional, elegant, sleek, hospital-control-room polish.

Use:

- clean white / slate surfaces
- subtle blue, emerald, amber, and rose accents
- generous spacing
- rounded cards
- soft shadows
- strong typographic hierarchy
- restrained animation
- dark hero/header or dark side navigation for contrast
- badges for recoverability, priority, queue, and status

Avoid:

- neon cyberpunk styling
- cluttered chart walls
- excessive gradients
- tiny dense tables as the default experience
- generic SaaS templates with no healthcare specificity

### Interaction style

The app should support fast decision scanning:

1. Read executive header.
2. Scan KPI cards.
3. Filter by department / queue / recoverability.
4. Select a case from the queue.
5. See evidence trace, failed control, owner, current blocker, aging, and next action.
6. Review intervention cards to decide hold / expand / revise.

---

## 6. Target tech stack

Use this stack unless the existing repo already dictates otherwise:

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui-style primitives if available
- lucide-react icons
- Recharts for charts if charting is needed
- React Router if multiple pages are implemented
- Local typed fixture data for the first slice

Do not require a backend for the first slice. Start with typed local mock data shaped like the future app data contract.

---

## 7. Information architecture

### Primary navigation

V1 pages:

1. Control Room Summary
2. Charge Reconciliation Monitor
3. Modifiers / Edits / Prebill Holds
4. Documentation Support Exceptions
5. Opportunity & Action Tracker

V2 / later:

- Scenario Lab
- Predictive Triage
- Exports / memo layer
- Alerts

### First slice to build

Build only the flagship page first:

`Control Room Summary`

It must include:

- app shell
- sidebar navigation
- global filters
- executive hero / North Star header
- KPI cards
- prioritized exception worklist
- selected case detail panel
- evidence trace section
- recoverability / owner / aging block
- intervention cards

Do not build all pages in the first pass.

---

## 8. Required global filters

Add global filter controls for:

- Department
- Service line
- Queue
- Recoverability

Filters should:

- persist while navigating pages once routes exist
- be visibly summarized near the page header
- not silently disappear on queue-fixed pages
- show a clear empty state when no records match

---

## 9. Core UI components

Create reusable components with clear names.

### App shell

`AppShell`

Responsibilities:

- left sidebar navigation
- main content container
- responsive layout
- global visual frame

### Sidebar

`SidebarNav`

Include navigation items:

- Control Room Summary
- Charge Reconciliation
- Prebill Holds
- Documentation Exceptions
- Action Tracker

Only the Summary page must be functional in the first slice. Other nav items can be disabled or stubbed.

### Filter controls

`GlobalFilters`

Controls:

- department select
- service line select
- queue select
- recoverability select

### KPI cards

`MetricCard`

Required KPI cards on first page:

- Dollars at risk
- Recoverable now
- Average blocker aging
- Active cases

Optional later cards:

- Unreconciled encounter rate
- Late charge rate
- Prebill edit aging
- Unsupported charge rate
- Edit first-pass clearance rate

### Queue worklist

`ExceptionWorklist`

Each case card should show:

- case id
- department
- queue
- priority
- current blocker
- dollars at risk
- aging days
- recoverability badge

### Case detail panel

`CaseDetailPanel`

Required fields:

- case id
- department
- service line
- issue domain
- root cause mechanism
- current queue
- current primary blocker
- current owner
- aging
- recoverability status
- dollars at risk
- dollars recoverable now
- control failure narrative
- recommended next action
- expected vs actual summary
- evidence list

### Evidence trace

`EvidenceTrace`

Show a compact deterministic trace:

1. Documented performed activity
2. Expected facility charge or review event
3. Actual posted / missing / held state
4. Classification
5. Routing decision
6. Suppression or why-not-billable note if applicable

### Intervention cards

`InterventionCard`

Each card should show:

- intervention title
- owner
- checkpoint status
- baseline metric
- current metric
- recommendation: hold / expand / revise
- validation note

---

## 10. TypeScript data contracts

Create a `src/data/types.ts` file or equivalent.

Use these interfaces as the initial contract:

```ts
export type Priority = "Critical" | "High" | "Medium" | "Low";

export type RecoverabilityStatus =
  | "Pre-final-bill recoverable"
  | "Post-final-bill recoverable by correction / rebill"
  | "Post-window financially lost"
  | "Financially closed but still compliance-relevant";

export type QueueName =
  | "Open encounter"
  | "Charge capture pending"
  | "Documentation pending"
  | "Coding pending"
  | "Prebill edit / hold"
  | "Ready to final bill"
  | "Final billed"
  | "Correction / rebill pending"
  | "Closed / monitored through denial feedback only";

export type IssueDomain =
  | "Charge capture failure"
  | "Charge integrity / configuration failure"
  | "Documentation support failure"
  | "Patient status / case classification failure"
  | "Coding failure"
  | "Billing / claim-edit failure"
  | "Packaged / non-billable / false-positive classification"
  | "Denial feedback signal";

export type RootCauseMechanism =
  | "People / training"
  | "Workflow / handoff"
  | "System build / interface"
  | "CDM / rule configuration"
  | "Documentation behavior"
  | "Coding practice"
  | "Billing edit management"
  | "Payer-policy variance";

export interface RevenueIntegrityCase {
  id: string;
  department: string;
  serviceLine: string;
  queue: QueueName;
  owner: string;
  priority: Priority;
  issueDomain: IssueDomain;
  rootCauseMechanism: RootCauseMechanism;
  currentPrimaryBlocker: string;
  agingDays: number;
  recoverabilityStatus: RecoverabilityStatus;
  dollarsAtRisk: number;
  dollarsRecoverableNow: number;
  dollarsAlreadyLost: number;
  expectedSummary: string;
  actualSummary: string;
  controlFailureNarrative: string;
  recommendedAction: string;
  suppressionNote?: string;
  evidenceTrace: EvidenceTraceItem[];
}

export interface EvidenceTraceItem {
  step: string;
  status: "complete" | "warning" | "blocked" | "suppressed";
  detail: string;
}

export interface InterventionTrackingItem {
  id: string;
  title: string;
  owner: string;
  targetCompletionDate: string;
  checkpointStatus: "Not started" | "In progress" | "Validated" | "Needs revision";
  baselineMetric: string;
  currentMetric: string;
  recommendation: "Hold" | "Expand" | "Revise";
  validationNote: string;
}
```

---

## 11. Fixture data requirements

Create local fixture data under:

`src/data/revenueIntegrityCases.ts`

The fixture data should include at least 8 cases covering:

- one OR prebill hold case
- one IR charge capture pending case
- one oncology infusion documentation support case
- one correction / rebill pending case
- one packaged / non-billable suppressed case
- one post-window financially lost case
- one coding pending case
- one denial feedback signal case

The synthetic data must show a believable mix of:

- recoverable opportunity
- already-lost timing-window failures
- correction / rebill recovery
- compliance-relevant but financially closed issues
- suppressed false positives / packaged / integral cases

---

## 12. First-slice layout requirements

### Desktop layout

Use this layout:

- fixed left sidebar, approximately 260–300 px
- main content area with max width around 1280–1440 px
- hero panel at top
- four KPI cards beneath hero
- two-column operational area:
  - left: queue worklist and filters/search
  - right: selected case detail panel
- intervention cards below case detail

### Mobile / responsive layout

For smaller screens:

- sidebar can collapse or stack above content
- KPI cards become one or two columns
- worklist and case detail stack vertically
- no horizontal overflow

---

## 13. Visual acceptance criteria

The first slice is acceptable when:

- the page looks like a serious healthcare analytics product
- the North Star decision is visible without scrolling
- KPI cards are readable and not crowded
- case cards clearly show priority, owner queue, dollars, and aging
- selected case detail clearly explains the failed control
- recoverability status is visually obvious
- the evidence trace makes the deterministic logic credible
- intervention cards show hold / expand / revise decisions
- the interface does not feel like a generic dashboard template

---

## 14. Functional acceptance criteria

The first slice is acceptable when:

- filters update the visible case list
- search filters by case id, owner, blocker, department, or service line
- selecting a case updates the detail panel
- KPI cards recalculate based on filtered cases
- empty results show a clear empty state
- all mock data is typed
- no console errors occur
- build succeeds

---

## 15. Quality gates

Run these commands before claiming done:

```bash
npm install
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

If the repo does not already have one of these scripts, add the missing script or document why it is unavailable in the final implementation note.

Minimum expected scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest"
  }
}
```

---

## 16. Accessibility requirements

- Use semantic buttons for clickable cards.
- Ensure visible focus states.
- Do not rely only on color to indicate priority or status.
- Use readable contrast.
- Provide accessible labels for select controls and search input.
- Preserve keyboard navigation for filters and case selection.

---

## 17. Copy guidelines

Use healthcare-native, operational language.

Prefer:

- current blocker
- owner queue
- recoverability
- failed control
- expected vs actual
- evidence trace
- correction / rebill path
- documentation support
- prebill edit hold
- packaged / non-billable suppression

Avoid:

- generic leakage score
- AI detected
- magic recommendation
- claim optimization engine
- payer prediction
- black-box risk score

---

## 18. Do-not-build list for first slice

Do not build these yet:

- authentication
- database connection
- backend API
- full Streamlit parity
- all pages
- predictive model
- scenario lab
- export engine
- alerting system
- complex role-based permissions
- real hospital data integration
- payer contract modeling

Protect the slice. Make the flagship page excellent first.

---

## 19. Implementation plan

### Slice 0 — Prove toolchain

Goal: confirm the React app can install, run, lint, typecheck, and build.

Acceptance criteria:

- `npm install` succeeds
- `npm run dev` starts locally
- `npm run build` succeeds
- no unrelated architecture changes

### Slice 1 — App shell and visual foundation

Goal: create the main visual frame.

Tasks:

- create `AppShell`
- create `SidebarNav`
- create top hero panel
- add route or page placeholder for Control Room Summary
- establish Tailwind theme conventions

Acceptance criteria:

- polished app frame visible
- sidebar nav visible
- hero displays North Star decision
- responsive behavior is acceptable

### Slice 2 — Typed fixture data

Goal: create realistic local data contracts and seed cases.

Tasks:

- add TypeScript interfaces
- create fixture file with at least 8 cases
- include intervention tracking fixture data
- ensure all fixture data compiles

Acceptance criteria:

- cases cover all required recoverability and exception patterns
- no `any` types needed for core data
- data can drive KPI cards and case details

### Slice 3 — Summary metrics and filters

Goal: make the page interactive.

Tasks:

- create `GlobalFilters`
- create `MetricCard`
- compute KPI values from filtered cases
- add search input
- add empty state

Acceptance criteria:

- filters and search affect case list
- KPI cards recalculate based on filtered cases
- empty state appears when no cases match

### Slice 4 — Worklist and case detail

Goal: create the operational core.

Tasks:

- create `ExceptionWorklist`
- create `CaseDetailPanel`
- create `EvidenceTrace`
- selecting a case updates detail panel

Acceptance criteria:

- each case card shows priority, queue, department, dollars, aging, and recoverability
- selected detail shows failed control, expected vs actual, owner, next action, and evidence trace
- deterministic story is understandable without developer explanation

### Slice 5 — Intervention tracker preview

Goal: show follow-through governance.

Tasks:

- create `InterventionCard`
- add intervention data
- show hold / expand / revise decisions

Acceptance criteria:

- cards display owner, baseline, current metric, recommendation, and validation note
- section reinforces operational follow-through, not just reporting

### Slice 6 — Polish and QA

Goal: make it portfolio-ready.

Tasks:

- refine spacing, typography, and responsive behavior
- add loading-safe and empty states
- remove dead code
- run quality gates
- update README or implementation note if appropriate

Acceptance criteria:

- lint passes
- typecheck passes
- tests pass if present
- build passes
- UI is screenshot-ready for portfolio use

---

## 20. Eisenhower Matrix for the coding agent

| Priority | Work | Instruction |
|---|---|---|
| Urgent + Important | First-slice app shell, filters, KPI cards, worklist, case detail, evidence trace | Build now |
| Important, Not Urgent | Additional pages, route polish, charts, export-ready screenshots | Defer until flagship page is strong |
| Urgent, Not Important | Pixel-perfect color tuning before logic is clear | Timebox tightly |
| Not Important | Auth, backend, predictive model, payer modeling, full Streamlit clone | Do not build |

---

## 21. Definition of done

The React design slice is done when a reviewer can open the app and immediately understand:

- this is facility-side outpatient revenue integrity
- the app is deterministic-first
- cases are owner-routed
- recoverability is operationally defined
- the selected case has a clear evidence trace
- the UI shows both analytics judgment and frontend skill

Final implementation note must include:

- files created / modified
- commands run
- screenshots captured if available
- known limitations
- next recommended slice

---

## 22. Saved Game Protocol

At the end of each coding session, leave the repo in one of two states:

### State A — Shippable slice

- quality gates run
- implementation note updated
- no obvious broken UI

### State B — Saved checkpoint

Create or update a `NOTES.md` entry with:

- what was completed
- what is blocked
- next exact command to run
- next exact file to edit
- known failing command, if any

Do not leave a vague half-state.

---

## 23. Final guardrail

Polish must serve the control-room story. Do not let the React interface become pretty but generic.

The app wins when it proves this:

> Documented performed activity flows into expected facility charge review, deterministic controls identify where the process broke, the case is routed to the right owner, recoverability is visible, and leadership can decide what to work next.

---

## 24. React Surface Screenshot Refresh (2026-05-25)

The React route expansion now includes reviewer-proof and claim-caveat support lenses that are captured as browser-visible screenshots.

### New screenshot pack

- `artifacts/browser_audit/react_surface_lens_screens_2026-05-25.md`
- `artifacts/browser_audit/react_control_room_summary_2026-05-25.png`
- `artifacts/browser_audit/react_reviewer_proof_pack_lens_2026-05-25.png`
- `artifacts/browser_audit/react_scenario_claim_tightening_lens_2026-05-25.png`
- `artifacts/browser_audit/react_decision_pack_freshness_lens_2026-05-25.png`

### Documentation updates completed

- Root README screenshot gallery expanded with the new React lens row.
- Case study visual walkthrough expanded with the same new React lens row.
- Proof index supporting-proof table now links the screenshot refresh note.

### Why this matters

This keeps the portfolio-visible proof layer current with the shipped React slices, so reviewers can verify claim-tightening and proof-packaging behavior directly in browser screenshots instead of relying only on code or planning notes.

