import { describe, expect, it } from 'vitest'

import { revenueIntegrityCases } from '../data/revenueIntegrityCases'
import { computeDenialFeedbackCdmMonitor } from './denialFeedbackCdmMonitor'

describe('denialFeedbackCdmMonitor', () => {
  it('computes deterministic denial and governance view', () => {
    const view = computeDenialFeedbackCdmMonitor(revenueIntegrityCases)

    expect(view.denialSignalCount).toBe(6)
    expect(view.denialDollars).toBe(5765)
    expect(view.patternSelectorOptions.length).toBeGreaterThan(0)
    expect(view.defaultSelectedPatternId).toBe('DEN-PAT-01')
    expect(view.denialSignalPatterns[0]?.denialReasonGroup).toBe('postbill_rebill_variance')
    expect(view.cdmGovernanceMonitor.length).toBeGreaterThan(0)
  })

  it('scopes results to the current filtered case set', () => {
    const scopedCases = revenueIntegrityCases.filter(
      (caseItem) => caseItem.department === 'OR / Hospital Outpatient Surgery / Procedural Areas',
    )

    const view = computeDenialFeedbackCdmMonitor(scopedCases)

    expect(view.denialSignalCount).toBe(4)
    expect(view.denialDollars).toBe(4485)
    expect(view.denialSignalPatterns.some((item) => item.payerGroup === 'Medicare Advantage')).toBe(
      false,
    )
  })
})
