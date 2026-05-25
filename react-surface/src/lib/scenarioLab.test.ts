import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeScenarioLab } from './scenarioLab'

describe('scenarioLab', () => {
  it('builds three deterministic lever configs', () => {
    const result = computeScenarioLab(revenueIntegrityCases)

    expect(result.leverConfigs).toHaveLength(3)
    expect(result.leverConfigs.map((item) => item.key)).toEqual([
      'prebillClearanceRate',
      'correctionTurnaroundDays',
      'routingSpeedDays',
    ])
  })

  it('increases projected lift with stronger lever targets', () => {
    const baseline = computeScenarioLab(revenueIntegrityCases)
    const baselineTargets = Object.fromEntries(
      baseline.leverConfigs.map((item) => [item.key, item.baselineValue]),
    ) as {
      prebillClearanceRate: number
      correctionTurnaroundDays: number
      routingSpeedDays: number
    }

    const noImprovement = computeScenarioLab(revenueIntegrityCases, baselineTargets)

    const strongScenario = computeScenarioLab(revenueIntegrityCases, {
      prebillClearanceRate: 95,
      correctionTurnaroundDays: 0.5,
      routingSpeedDays: 0.5,
    })

    expect(strongScenario.projection.projectedRecoverableDollarLift).toBeGreaterThanOrEqual(
      noImprovement.projection.projectedRecoverableDollarLift,
    )
    expect(strongScenario.projection.projectedBacklogReduction).toBeGreaterThanOrEqual(
      noImprovement.projection.projectedBacklogReduction,
    )
  })

  it('keeps backlog reduction within the 30 percent cap', () => {
    const result = computeScenarioLab(revenueIntegrityCases, {
      prebillClearanceRate: 95,
      correctionTurnaroundDays: 0.5,
      routingSpeedDays: 0.5,
    })

    const maxAllowed = Math.round(revenueIntegrityCases.length * 0.3)

    expect(result.projection.projectedBacklogReduction).toBeLessThanOrEqual(maxAllowed)
  })
})
