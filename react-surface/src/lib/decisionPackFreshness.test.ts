import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeDecisionPackFreshnessView } from './decisionPackFreshness'

describe('decisionPackFreshness', () => {
  it('builds a bounded current-snapshot view', () => {
    const view = computeDecisionPackFreshnessView(revenueIntegrityCases)

    expect(view.validationStatus).toContain('Passed')
    expect(view.metrics[0]?.label).toBe('Total open exceptions')
    expect(view.metrics[1]?.label).toContain('Recoverable now vs already lost')
    expect(view.proofAnchors).toContain('artifacts/decision_pack/revenue_integrity_decision_pack.md')
  })

  it('keeps the current-slice summary signal explicit', () => {
    const view = computeDecisionPackFreshnessView(revenueIntegrityCases)

    expect(view.currentSummarySignal).toMatch(/current slice/i)
    expect(view.scenarioSnapshot.projectedRecoverableDollarLift).toBeGreaterThan(0)
  })
})
