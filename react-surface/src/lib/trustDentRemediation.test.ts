import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeTrustDentRemediationView } from './trustDentRemediation'

describe('trustDentRemediation', () => {
  it('returns deterministic trust-dent remediation inventory', () => {
    const view = computeTrustDentRemediationView(revenueIntegrityCases)

    expect(view.items).toHaveLength(4)
    expect(view.remediatedCount).toBe(4)
    expect(view.watchlistCount).toBe(0)
    expect(view.noBuildBoundaryCount).toBe(4)
  })

  it('reflects current filtered-slice case count', () => {
    const scoped = revenueIntegrityCases.filter(
      (item) => item.department === 'Radiology / Interventional Radiology',
    )

    const view = computeTrustDentRemediationView(scoped)

    expect(view.currentSliceCaseCount).toBe(scoped.length)
  })
})
