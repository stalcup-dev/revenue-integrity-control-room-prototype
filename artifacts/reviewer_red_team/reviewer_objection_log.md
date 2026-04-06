# Reviewer Objection Log

## Reviewer 1 - Revenue Integrity / Charge Capture leader

### 1. Taxonomy still feels cleaner than real hospital leakage work

- Objection statement: "The issue-domain and root-cause taxonomy may be governed, but real RI work is messier than this and often does not stay this neatly separated."
- Severity: major
- What current artifact/page partially answers it: Reviewer proof pack, selected case `Classification`, Denial/CDM monitor linkage
- Why the current answer is or is not strong enough: The separation exists in the current model, but the proof is mostly artifact-driven. A skeptical reviewer can still say the categories were reverse-engineered to look clean in demo form.
- Recommended response in demo: "The point is not to reproduce hospital messiness as noise. The point is to keep issue domain, root cause, and owner/action path separated so the operating decision stays usable."
- Future build fix or only better framing: better framing

### 2. Chart-to-bill / bill-to-chart logic may be overfit to synthetic rules

- Objection statement: "You say expected charge comes from documented performed activity, but in a synthetic build that can still be too convenient and too deterministic."
- Severity: critical
- What current artifact/page partially answers it: Manual audit sample, selected case expected-vs-actual trace, department-story realism report
- Why the current answer is or is not strong enough: This is one of the strongest current areas, but it still depends on reviewers trusting synthetic source-like evidence. That trust is earned, not assumed.
- Recommended response in demo: "Walk one case from documented activity to expected opportunity to current blocker. Do not answer this objection with summary claims."
- Future build fix or only better framing: better framing

### 3. Modifier/status integrity may still be too thin

- Objection statement: "Modifier-heavy work, status logic, and packaging edge cases are where synthetic healthcare demos usually fall apart."
- Severity: major
- What current artifact/page partially answers it: Modifiers / Edits / Prebill Holds page, manual audit sample, department-story report
- Why the current answer is or is not strong enough: The repo shows rule-based modifier cases and suppression logic, but the visible proof is still narrow and concentrated in a few story families.
- Recommended response in demo: "Use one infusion modifier case and one radiology distinctness case, then show that suppression exists alongside misses."
- Future build fix or only better framing: future build fix

### 4. Recoverability assumptions may look too certain

- Objection statement: "Hospitals often debate what is really recoverable, so these recoverability states may read as overconfident."
- Severity: major
- What current artifact/page partially answers it: Control Room Summary, queue governance proof, post-tuning realism report
- Why the current answer is or is not strong enough: The logic is explicit, which is good. The risk is semantic overconfidence, especially when synthetic cases make the buckets look cleaner than real life.
- Recommended response in demo: "Frame recoverability as governed current-state operating logic, not as an accounting certainty or universal hospital rule."
- Future build fix or only better framing: better framing

### 5. Charge reconciliation controls may be too summary-heavy

- Objection statement: "I can see reconciliation counts, but I still need to know this behaves like a real charge-control process and not just a missed-charge report."
- Severity: major
- What current artifact/page partially answers it: Charge Reconciliation Monitor, queue governance proof, manual audit sample
- Why the current answer is or is not strong enough: The current proof is coherent, but the reconciliation story is not the deepest surface in the pack and can be overshadowed by summary metrics.
- Recommended response in demo: "Show one true missed-charge case from documented activity to no charge posted to owner queue."
- Future build fix or only better framing: better framing

### 6. Scenario levers may be too thin to feel like real RI operations

- Objection statement: "Three levers are better than fake AI math, but they may still be too narrow to represent real RI intervention planning."
- Severity: major
- What current artifact/page partially answers it: Scenario Lab v0 audit, Scenario Lab screenshots
- Why the current answer is or is not strong enough: The formulas are transparent, which is a plus. The weakness is depth, not honesty.
- Recommended response in demo: "Present Scenario Lab as a thin v0 extension, not as the main claim of product maturity."
- Future build fix or only better framing: future build fix

### 7. Decision Pack may compress too much and blur the control story

- Objection statement: "The Decision Pack is useful, but its short narrative can look stitched together rather than organically consistent with the live queue."
- Severity: major
- What current artifact/page partially answers it: Decision Pack sample, Decision Pack audit note
- Why the current answer is or is not strong enough: The pack proves provenance, but the sample can still read as assembled from multiple summaries instead of one coherent operating story.
- Recommended response in demo: "Treat the Decision Pack as a leave-behind, not as the primary proof of control realism."
- Future build fix or only better framing: future build fix

### 8. Absolute wording weakens trust

- Objection statement: "Phrases like `what still feels fake: none` sound promotional, not skeptical."
- Severity: minor
- What current artifact/page partially answers it: Department-story report, post-tuning realism report
- Why the current answer is or is not strong enough: The underlying realism evidence is solid. The wording is the problem.
- Recommended response in demo: "Acknowledge directly that synthetic work always has realism limits, then point to the specific anti-patterns the repo is trying to avoid."
- Future build fix or only better framing: small artifact update

## Reviewer 2 - PFS / Billing Operations leader

### 1. Prebill queue design may still be too model-driven

- Objection statement: "The queue names and blockers are believable, but I still want to know whether this behaves like a real prebill work queue rather than a modeled classification layer."
- Severity: critical
- What current artifact/page partially answers it: Control Room Summary, Opportunity & Action Tracker, queue governance browser audit
- Why the current answer is or is not strong enough: Queue governance helps a lot, but volume and day-to-day operational realism are not proven at real billing scale.
- Recommended response in demo: "Show current queue, aging basis, SLA thresholds, and routing history for one selected case before discussing any summary metric."
- Future build fix or only better framing: better framing

### 2. Aging logic may feel too clean

- Objection statement: "Stage-specific aging is present, but the aging distribution can still feel too tidy for real operations."
- Severity: major
- What current artifact/page partially answers it: Post-tuning realism report, queue governance proof, Control Room Summary
- Why the current answer is or is not strong enough: The realism report demonstrates variation, but the small dataset makes the cleanliness visible.
- Recommended response in demo: "Do not say aging is realistic because it exists. Say it is stage-specific, visible, and intentionally governed."
- Future build fix or only better framing: better framing

### 3. Routing and ownership may be visible but not operationally validated

- Objection statement: "I can see accountable ownership, but I do not yet know if those are the owners a real billing team would accept."
- Severity: major
- What current artifact/page partially answers it: Queue governance proof, reviewer scorecard, selected case evidence trace
- Why the current answer is or is not strong enough: The logic is explicit, but external reviewer acceptance of the owner model is still unproven.
- Recommended response in demo: "Present owner routing as a reviewer-testable operating hypothesis, not as settled production truth."
- Future build fix or only better framing: better framing

### 4. Correction / rebill workflow remains thin

- Objection statement: "The correction-path support is useful, but it is not yet deep enough to feel like billing operations, only billing-aware evidence."
- Severity: major
- What current artifact/page partially answers it: Action Tracker follow-through proof, Decision Pack audit, Denial/CDM audit
- Why the current answer is or is not strong enough: The repo already states this is intentionally thin. That honesty helps, but it does not remove the gap.
- Recommended response in demo: "Say directly that correction/rebill is a support layer, not a full rebill operations platform."
- Future build fix or only better framing: future build fix

### 5. Backlog assumptions are too small to prove queue usefulness

- Objection statement: "Twenty-four active queue items may prove logic, but not whether the queue would really help me run a billing backlog."
- Severity: major
- What current artifact/page partially answers it: Control Room Summary, realism report, reviewer proof pack
- Why the current answer is or is not strong enough: Current proof shows structure, not operational scale.
- Recommended response in demo: "Do not overclaim operational scale. Keep the claim limited to coherence, prioritization discipline, and reviewer trust."
- Future build fix or only better framing: future build fix

### 6. Operational validation structure is still artifact-heavy

- Objection statement: "I see audits and reports, but I do not yet see enough evidence of how this would be operated day to day."
- Severity: major
- What current artifact/page partially answers it: Reviewer proof pack, demo script, operating runbook
- Why the current answer is or is not strong enough: The runbook and proof pack help, but the current repo still reads more like a strong prototype than a daily ops control system.
- Recommended response in demo: "Use the phrase `reviewer-ready prototype` instead of `operations-ready product`."
- Future build fix or only better framing: better framing

### 7. The sample Decision Pack undermines governance by showing `Validation status: Not yet run`

- Objection statement: "Why would I trust the memo layer if the sample artifact itself says the validation status is not yet run?"
- Severity: critical
- What current artifact/page partially answers it: Decision Pack sample, Decision Pack audit, reviewer proof pack
- Why the current answer is or is not strong enough: It is not strong enough. This is an avoidable trust dent in a reviewer-facing artifact.
- Recommended response in demo: "Do not show the stale sample. Use validated proof elsewhere or regenerate the sample before external review."
- Future build fix or only better framing: small artifact update

### 8. Phase drift can confuse the billing story

- Objection statement: "Older scope docs stage scenario and memo work later, so why are those surfaces now part of the current reviewer pitch?"
- Severity: major
- What current artifact/page partially answers it: Reviewer proof pack caveats, proof asset index
- Why the current answer is or is not strong enough: The proof pack admits the drift, but a skeptical reviewer may still see it as scope creep or polish-first behavior.
- Recommended response in demo: "Frame Scenario Lab, Denial/CDM, and Decision Pack as thin extensions layered on top of the deterministic core, not as evidence that the product center moved."
- Future build fix or only better framing: small artifact update

## Reviewer 3 - Coding / CDI / Clinical Operations SME

### 1. Documentation dependencies may still be too standardized

- Objection statement: "The documentation gaps are believable, but they can still read like a controlled list rather than the messy variation clinical operations really see."
- Severity: major
- What current artifact/page partially answers it: Documentation Support Exceptions, manual audit sample, department-story report
- Why the current answer is or is not strong enough: The current patterns are distinct by department, which helps. The limitation is breadth.
- Recommended response in demo: "Use department-specific examples, not generic statements about documentation gaps."
- Future build fix or only better framing: future build fix

### 2. Modifier realism may be too narrow

- Objection statement: "A few modifier patterns are present, but that may not be enough to convince coding leadership that modifier logic is really hospital-native."
- Severity: major
- What current artifact/page partially answers it: Modifiers / Edits / Prebill Holds page, department-story report, manual audit sample
- Why the current answer is or is not strong enough: The current examples are valid, but still narrow.
- Recommended response in demo: "Show one infusion modifier dependency and one radiology distinctness dependency rather than trying to claim broad modifier completeness."
- Future build fix or only better framing: future build fix

### 3. Expected-charge from documented performed activity is claimed more often than it is demonstrated

- Objection statement: "I need to see performed activity drive the expected opportunity, not just hear that it does."
- Severity: critical
- What current artifact/page partially answers it: Selected case expected-vs-actual trace, manual audit sample, reviewer proof pack
- Why the current answer is or is not strong enough: The proof exists, but the demo can still skip it if rushed.
- Recommended response in demo: "Spend real time on one case trace before any high-level narrative."
- Future build fix or only better framing: better framing

### 4. Service-line workflow realism is credible but still narrow

- Objection statement: "The three anchor stories are fine, but they are still only three story families and may not survive deeper SME challenge."
- Severity: major
- What current artifact/page partially answers it: Department-story report, post-tuning realism report, manual audit sample
- Why the current answer is or is not strong enough: Good enough for a prototype defense, not strong enough for overclaiming.
- Recommended response in demo: "Frame the three departments as frozen anchor stories, not as a hospital-wide expected-charge engine."
- Future build fix or only better framing: better framing

### 5. Coding, documentation, charge entry, and downstream billing can still blur in summary views

- Objection statement: "The repo says these are distinct, but summary screens can still make them feel blended."
- Severity: major
- What current artifact/page partially answers it: Selected case `Classification`, Documentation Support Exceptions, Denial/CDM monitor
- Why the current answer is or is not strong enough: The distinction is strongest in case detail, weakest in fast summary narration.
- Recommended response in demo: "Name the issue domain and root cause separately out loud every time you open a case."
- Future build fix or only better framing: better framing

### 6. Packaged / non-billable suppression is still too easy to miss

- Objection statement: "If I do not see suppression clearly, I will assume the missed-charge story is overstated."
- Severity: major
- What current artifact/page partially answers it: Manual audit sample, realism report suppression section, selected case suppression note
- Why the current answer is or is not strong enough: The proof is there, but it is not the first thing a reviewer sees.
- Recommended response in demo: "Use one suppressed case explicitly so the reviewer sees that the product does not treat every documented activity as billable."
- Future build fix or only better framing: better framing

### 7. Denial/CDM monitor could blur downstream billing signal with upstream clinical truth if overplayed

- Objection statement: "If this page gets too much airtime, it starts to look like denials logic is steering the product."
- Severity: major
- What current artifact/page partially answers it: Denial/CDM audit note, reviewer proof pack, proof asset index
- Why the current answer is or is not strong enough: The artifacts clearly say denials are downstream-only. The risk is demo emphasis, not model intent.
- Recommended response in demo: "Keep this page late and brief. Present it as downstream validation only."
- Future build fix or only better framing: better framing

### 8. Some realism artifacts sound too absolute

- Objection statement: "When a realism report says `what still feels fake: none`, it sounds like the repo is trying too hard to close the argument."
- Severity: minor
- What current artifact/page partially answers it: Department-story report, post-tuning realism report
- Why the current answer is or is not strong enough: The underlying metrics are good. The absolute wording is not.
- Recommended response in demo: "Acknowledge directly that synthetic work always leaves room for SME challenge."
- Future build fix or only better framing: small artifact update
