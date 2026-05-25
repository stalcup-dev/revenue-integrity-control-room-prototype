import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeScenarioClaimTighteningLensView } from './scenarioClaimTighteningLens'

describe('scenarioClaimTighteningLens', () => {
  it('returns deterministic claim-tightening inventory', () => {
    const view = computeScenarioClaimTighteningLensView(revenueIntegrityCases)

    expect(view.entries).toHaveLength(3)
    expect(view.lowRiskCount).toBe(2)
    expect(view.moderateRiskCount).toBe(1)
    expect(view.claimsWithExplicitCaveat).toBe(3)
  })

  it('surfaces current scenario output values for in-context framing', () => {
    const view = computeScenarioClaimTighteningLensView(revenueIntegrityCases)

    expect(view.projectedRecoverableDollarLift).toBeGreaterThan(0)
    expect(view.projectedBacklogReduction).toBeGreaterThanOrEqual(0)
    expect(view.projectedSlaImprovementPoints).toBeGreaterThanOrEqual(0)
  })
})
