import type { RevenueIntegrityCase } from '../data/types'
import { computeScenarioLab } from './scenarioLab'

export type ClaimRiskLevel = 'Low' | 'Moderate'

export interface ScenarioClaimEntry {
  area: string
  tightenedClaim: string
  proofToPointAt: string
  caveat: string
  riskLevel: ClaimRiskLevel
}

export interface ScenarioClaimTighteningLensView {
  entries: ScenarioClaimEntry[]
  lowRiskCount: number
  moderateRiskCount: number
  claimsWithExplicitCaveat: number
  projectedRecoverableDollarLift: number
  projectedBacklogReduction: number
  projectedSlaImprovementPoints: number
}

const entries: ScenarioClaimEntry[] = [
  {
    area: 'Scenario Lab positioning',
    tightenedClaim:
      'Scenario Lab is a thin deterministic what-if surface that uses visible levers, formulas, and caps to test operational assumptions against the current slice.',
    proofToPointAt:
      'Three levers, projected impact cards, formula blocks, and Scenario Lab v0 audit screenshots.',
    caveat:
      'This is not a forecast engine and not a finance planning model; it is transparent what-if support only.',
    riskLevel: 'Low',
  },
  {
    area: 'Scenario output interpretation',
    tightenedClaim:
      'Projected outputs are capped what-if estimates for the current governed slice and should be read as directional operational support.',
    proofToPointAt:
      'Projected backlog reduction, projected SLA improvement, and projected recoverable dollar lift in Scenario Lab.',
    caveat:
      'Do not present these values as enterprise forecasts, optimization results, or validated ROI commitments.',
    riskLevel: 'Moderate',
  },
  {
    area: 'Scope discipline',
    tightenedClaim:
      'Scenario Lab remains secondary to deterministic queue and case-proof surfaces and does not replace the operating control core.',
    proofToPointAt:
      'Control Room Summary, Queue Governance Browser, and selected-case deterministic proof surfaces.',
    caveat:
      'Use scenario proof after core queue evidence is established in the walkthrough sequence.',
    riskLevel: 'Low',
  },
]

export function computeScenarioClaimTighteningLensView(
  cases: RevenueIntegrityCase[],
): ScenarioClaimTighteningLensView {
  const scenarioResult = computeScenarioLab(cases)

  return {
    entries,
    lowRiskCount: entries.filter((item) => item.riskLevel === 'Low').length,
    moderateRiskCount: entries.filter((item) => item.riskLevel === 'Moderate').length,
    claimsWithExplicitCaveat: entries.filter((item) => item.caveat.trim().length > 0).length,
    projectedRecoverableDollarLift: scenarioResult.projection.projectedRecoverableDollarLift,
    projectedBacklogReduction: scenarioResult.projection.projectedBacklogReduction,
    projectedSlaImprovementPoints: scenarioResult.projection.projectedSlaImprovementPoints,
  }
}
