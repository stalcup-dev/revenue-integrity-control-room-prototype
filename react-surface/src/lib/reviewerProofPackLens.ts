import type { RevenueIntegrityCase } from '../data/types'

export type ProofType = 'Narrative proof' | 'Export proof' | 'Test proof' | 'Browser proof'

export interface ProofAsset {
  asset: string
  whatItProves: string
  demoUse: string
  proofType: ProofType
  priority: 'Core' | 'Supporting'
}

export interface ReviewerProofPackLensView {
  assets: ProofAsset[]
  coreCount: number
  supportingCount: number
  testProofCount: number
  browserProofCount: number
  currentSliceCaseCount: number
  recommendedReadOrder: string[]
}

const proofAssets: ProofAsset[] = [
  {
    asset: 'artifacts/reviewer_walkthrough_pack/or_prebill_hold_story_walkthrough.md',
    whatItProves:
      'One deterministic operating story holds from summary surface to opened proof to exported memo.',
    demoUse: 'Use first in the demo or as the first public proof artifact.',
    proofType: 'Narrative proof',
    priority: 'Core',
  },
  {
    asset: 'artifacts/decision_pack/revenue_integrity_decision_pack.md',
    whatItProves: 'The same current control story survives into a clean exported memo.',
    demoUse: 'Use immediately after the walkthrough.',
    proofType: 'Export proof',
    priority: 'Core',
  },
  {
    asset: 'artifacts/realism/post_tuning_realism_report.md',
    whatItProves:
      'Current shipped realism state across workflow, recoverability, queue history, suppression, and intervention follow-through.',
    demoUse: 'Use first when a reviewer asks why to trust synthetic realism.',
    proofType: 'Test proof',
    priority: 'Core',
  },
  {
    asset: 'artifacts/realism/realism_before_after_diff.md',
    whatItProves: 'Before/after remediation proof for historical realism dents.',
    demoUse: 'Use after the current report if someone asks what changed.',
    proofType: 'Test proof',
    priority: 'Core',
  },
  {
    asset: 'tests/test_case_detail_payload.py',
    whatItProves:
      'Business-facing assertions enforce case detail, blocker logic, routing history, suppression context, and correction follow-through.',
    demoUse: 'Use as the first code-backed credibility cue.',
    proofType: 'Test proof',
    priority: 'Core',
  },
  {
    asset: 'artifacts/queue_governance_browser_audit.md',
    whatItProves:
      'Current queue, blocker, ownership, SLA, recoverability, and queue-governance context are visible on app surfaces.',
    demoUse: 'Use when showing one-current-blocker, aging, and ownership.',
    proofType: 'Browser proof',
    priority: 'Supporting',
  },
  {
    asset: 'artifacts/browser_audit/action_tracker_follow_through.md',
    whatItProves:
      'Action Tracker follow-through shows baseline/current movement and recommendation evidence.',
    demoUse: 'Use during intervention follow-through step.',
    proofType: 'Browser proof',
    priority: 'Supporting',
  },
  {
    asset: 'artifacts/scenario_lab_v0_audit.md',
    whatItProves: 'Scenario Lab v0 uses operational levers, visible formulas, and caps.',
    demoUse: 'Use only after the core control-room proof path is established.',
    proofType: 'Narrative proof',
    priority: 'Supporting',
  },
  {
    asset: 'artifacts/denial_feedback_cdm_monitor_audit.md',
    whatItProves:
      'Denials remain downstream-only evidence while linking back to upstream issue domain and owner/action path.',
    demoUse: 'Use after core control-room proof path is established.',
    proofType: 'Narrative proof',
    priority: 'Supporting',
  },
  {
    asset: 'docs/MANUAL_AUDIT_SAMPLE.md',
    whatItProves:
      'Case traceability from performed activity through expected opportunity, billed state, queue owner, and recoverability.',
    demoUse: 'Use when a reviewer asks for a paper-trail example after walkthrough.',
    proofType: 'Narrative proof',
    priority: 'Supporting',
  },
]

export function computeReviewerProofPackLensView(
  cases: RevenueIntegrityCase[],
): ReviewerProofPackLensView {
  return {
    assets: proofAssets,
    coreCount: proofAssets.filter((item) => item.priority === 'Core').length,
    supportingCount: proofAssets.filter((item) => item.priority === 'Supporting').length,
    testProofCount: proofAssets.filter((item) => item.proofType === 'Test proof').length,
    browserProofCount: proofAssets.filter((item) => item.proofType === 'Browser proof').length,
    currentSliceCaseCount: cases.length,
    recommendedReadOrder: [
      'Start with the walkthrough.',
      'Open the exported Decision Pack.',
      'Use the current shipped realism report, then the before/after diff if needed.',
      'Use test_case_detail_payload.py as the first code-backed credibility cue.',
      'Use queue-governance, Action Tracker, Scenario Lab, and Denial/CDM artifacts only as supporting proof after the core path is clear.',
    ],
  }
}
