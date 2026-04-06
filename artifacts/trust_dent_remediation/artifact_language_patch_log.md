# Artifact Language Patch Log

## Purpose

This log captures wording that sounds too smooth, too absolute, too stale, or too broad for skeptical review.

| # | Source artifact | Current phrase or risky phrasing | Why a skeptical reviewer would challenge it | Replacement wording | Classification |
| --- | --- | --- | --- | --- | --- |
| 1 | `artifacts/decision_pack/revenue_integrity_decision_pack.md` | `Validation status: Not yet run` | Reads stale and undercuts governance if shown without context. | `Validation status from current run manifest: Not yet run. Treat this memo as a current snapshot sample until the manifest is refreshed.` | stale/freshness risk |
| 2 | `artifacts/decision_pack/revenue_integrity_decision_pack.md` | `Top owner queue` | Can read like a broad institutional ranking rather than a current slice view. | `Top owner queue in the current slice` | stale/freshness risk |
| 3 | `artifacts/decision_pack/revenue_integrity_decision_pack.md` | `Top service line / department of concern` | Sounds broader and more definitive than the current slice supports. | `Top service line / department in the current slice` | stale/freshness risk |
| 4 | `artifacts/decision_pack/revenue_integrity_decision_pack.md` | `The current pattern is mostly documentation-related.` | Overstates a single-cause interpretation and clashes with the ranked queue section. | `The current slice is documentation-heavy at the issue-domain level, while queue urgency remains distributed across documentation, billing/edit, and coding work.` | realism wording mismatch |
| 5 | `artifacts/decision_pack/revenue_integrity_decision_pack_audit.md` | `single reviewer-ready memo` | `Reviewer-ready` sounds cleaner and more settled than the current sample supports. | `single bounded snapshot memo for reviewer use` | overclaim |
| 6 | `artifacts/scenario_lab_v0_audit.md` | `Page added: Scenario Lab` | Sounds like a phase marker rather than a bounded current capability. | `Current implemented thin what-if surface: Scenario Lab v0` | phase-drift confusion |
| 7 | `artifacts/scenario_lab_v0_audit.md` | `Projected recoverable dollar lift` without repeated caveat nearby | Can be heard as finance-forecast language if read quickly. | `Projected recoverable dollar lift as a capped what-if estimate` | scenario overreach |
| 8 | `artifacts/reviewer_proof_pack/reviewer_proof_pack.md` | `hospital-native` | Strong phrase, but a skeptical reviewer may hear overclaim unless evidence is named immediately. | `hospital-oriented facility-side prototype with current realism evidence` | overclaim |
| 9 | `artifacts/reviewer_proof_pack/reviewer_proof_pack.md` | `current implemented product` | Can blur prototype status and maturity. | `current implemented prototype` | overclaim |
| 10 | `artifacts/reviewer_proof_pack/reviewer_proof_pack.md` | `supports thin follow-through, what-if, and downstream evidence layers` | `Supports` is fine, but the phrase can still make the extension layers sound broader than they are. | `includes thin follow-through, what-if, and downstream evidence layers that stay secondary to the control core` | phase-drift confusion |
| 11 | `artifacts/reviewer_proof_pack/reviewer_proof_pack.md` | `enough proof to survive a serious reviewer walkthrough` | Sounds like a verdict before the skeptical reviewer gives one. | `enough current evidence to justify a reviewer walkthrough if the demo stays bounded and caveated` | overclaim |
| 12 | `artifacts/reviewer_proof_pack/demo_script_7min.md` | `This is the operating heartbeat of the product` | Sounds mature and scale-proven. | `This is the current deterministic control snapshot for the filtered slice` | overclaim |
| 13 | `artifacts/reviewer_proof_pack/demo_script_7min.md` | `This page turns exception ranking into operational follow-through` | Sounds like a fuller workflow platform than the repo actually implements. | `This page adds thin follow-through evidence to ranked exception work` | overclaim |
| 14 | `artifacts/reviewer_proof_pack/demo_script_7min.md` | `Scenario Lab stays in-bounds` | Still too broad unless paired with what-if-only language. | `Scenario Lab is a thin deterministic what-if surface with visible formulas and caps` | scenario overreach |
| 15 | `artifacts/reviewer_proof_pack/demo_script_7min.md` | `leadership-ready artifact` | `Leadership-ready` sounds more validated than the current sample state. | `short deterministic snapshot artifact for reviewer or leadership readout` | stale/freshness risk |
| 16 | `artifacts/realism/department_story_report.md` | `what still feels fake: none` | Absolute language weakens trust, especially in a synthetic prototype. | `what still feels least tested: broader edge-case depth outside the current anchor stories` | realism wording mismatch |

## Patch rule

When in doubt:

1. Tighten the claim.
2. Name the evidence.
3. Add the caveat.
4. Stop there.
