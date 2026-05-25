import { describe, expect, it } from 'vitest'

import { interventionTracking } from '../data/interventionTracking'
import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeStorytellingValidationView } from './pageStorytellingValidation'

describe('pageStorytellingValidation', () => {
  it('builds page storytelling cue cards with full and thin framing modes', () => {
    const view = computeStorytellingValidationView(revenueIntegrityCases, interventionTracking)

    expect(view.cards).toHaveLength(5)
    expect(view.fullCuePages).toBe(4)
    expect(view.thinCuePages).toBe(1)
    expect(view.validatedPages).toBe(5)
    expect(view.failedPages).toBe(0)
  })

  it('keeps scenario cue intentionally thin', () => {
    const view = computeStorytellingValidationView(revenueIntegrityCases, interventionTracking)
    const scenario = view.cards.find((item) => item.page === 'Scenario Lab')

    expect(scenario?.mode).toBe('thin')
    expect(scenario?.ownerNextMove).toMatch(/not required/i)
  })
})
