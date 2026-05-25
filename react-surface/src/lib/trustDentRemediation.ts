import type { RevenueIntegrityCase } from '../data/types'

export type TrustDentStatus = 'Remediated' | 'Watchlist'

export interface TrustDentItem {
  id: string
  dent: string
  whyItMatters: string
  remediationStrategy: string
  status: TrustDentStatus
  proofAnchor: string
  noBuildBoundary: boolean
}

export interface TrustDentRemediationView {
  items: TrustDentItem[]
  remediatedCount: number
  watchlistCount: number
  noBuildBoundaryCount: number
  currentSliceCaseCount: number
}

const trustDentItems: TrustDentItem[] = [
  {
    id: 'TRUST-01',
    dent: 'Stale Decision Pack validation state',
    whyItMatters:
      'Stale validation wording reads as governance weakness even when core logic is sound.',
    remediationStrategy:
      'Use freshness disclaimers, current-snapshot framing, and explicit validation-state caveats.',
    status: 'Remediated',
    proofAnchor: 'decision_pack_freshness_patch.md',
    noBuildBoundary: true,
  },
  {
    id: 'TRUST-02',
    dent: 'Phase-drift confusion',
    whyItMatters:
      'Phase language drift can make current capability feel mis-scoped or over-claimed.',
    remediationStrategy:
      'Replace phase-forward language with current implemented capability and deferred roadmap framing.',
    status: 'Remediated',
    proofAnchor: 'trust_dent_remediation_plan.md',
    noBuildBoundary: true,
  },
  {
    id: 'TRUST-03',
    dent: 'Scenario thinness overinterpretation risk',
    whyItMatters:
      'Scenario cues can be misread as forecasting maturity if claims exceed bounded deterministic evidence.',
    remediationStrategy:
      'Keep scenario wording deterministic, transparent, capped, and what-if only.',
    status: 'Remediated',
    proofAnchor: 'demo_script_claim_tightening.md',
    noBuildBoundary: true,
  },
  {
    id: 'TRUST-04',
    dent: 'Over-smooth artifact language',
    whyItMatters:
      'Overly clean language reduces skeptical reviewer trust in synthetic prototype evidence.',
    remediationStrategy:
      'Use short claim -> proof -> caveat phrasing and remove absolute wording.',
    status: 'Remediated',
    proofAnchor: 'artifact_language_patch_log.md',
    noBuildBoundary: true,
  },
]

export function computeTrustDentRemediationView(
  cases: RevenueIntegrityCase[],
): TrustDentRemediationView {
  const remediatedCount = trustDentItems.filter((item) => item.status === 'Remediated').length
  const watchlistCount = trustDentItems.filter((item) => item.status === 'Watchlist').length
  const noBuildBoundaryCount = trustDentItems.filter((item) => item.noBuildBoundary).length

  return {
    items: trustDentItems,
    remediatedCount,
    watchlistCount,
    noBuildBoundaryCount,
    currentSliceCaseCount: cases.length,
  }
}
