import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeReviewerProofPackLensView } from './reviewerProofPackLens'

describe('reviewerProofPackLens', () => {
  it('returns core and supporting proof asset inventory', () => {
    const view = computeReviewerProofPackLensView(revenueIntegrityCases)

    expect(view.assets).toHaveLength(10)
    expect(view.coreCount).toBe(5)
    expect(view.supportingCount).toBe(5)
    expect(view.testProofCount).toBe(3)
    expect(view.browserProofCount).toBe(2)
  })

  it('keeps recommended read-order guidance intact', () => {
    const view = computeReviewerProofPackLensView(revenueIntegrityCases)

    expect(view.recommendedReadOrder).toHaveLength(5)
    expect(view.recommendedReadOrder[0]).toMatch(/walkthrough/i)
  })
})
