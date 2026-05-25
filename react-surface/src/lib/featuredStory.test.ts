import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { selectFeaturedStory } from './featuredStory'

describe('featuredStory', () => {
  it('selects a deterministic featured case', () => {
    const featured = selectFeaturedStory(revenueIntegrityCases)

    expect(featured).not.toBeNull()
    expect(featured?.caseId).toBe('RI-OR-0017')
    expect(featured?.score).toBeGreaterThan(0)
  })

  it('returns null for empty case arrays', () => {
    const featured = selectFeaturedStory([])

    expect(featured).toBeNull()
  })
})
