import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeQueueGovernanceView } from './queueGovernance'

describe('queueGovernance', () => {
  it('builds deterministic governance summary from case population', () => {
    const view = computeQueueGovernanceView(revenueIntegrityCases)

    expect(view.cases.length).toBe(revenueIntegrityCases.length)
    expect(view.queueSummary.length).toBeGreaterThan(0)
    expect(view.overdueCount).toBeGreaterThan(0)
    expect(view.atRiskCount).toBeGreaterThan(0)
    expect(view.governedRecoverableNow).toBe(
      revenueIntegrityCases.reduce(
        (runningTotal, item) => runningTotal + item.dollarsRecoverableNow,
        0,
      ),
    )
  })

  it('marks closed denial-feedback case as non-overdue under closed monitoring threshold', () => {
    const view = computeQueueGovernanceView(
      revenueIntegrityCases.filter((item) => item.id === 'RI-OR-0099'),
    )

    expect(view.cases[0]?.slaStatus).toBe('At-risk')
    expect(view.escalationNowCount).toBe(0)
  })
})
