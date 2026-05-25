import { describe, expect, it } from 'vitest'

import type { GlobalFiltersState } from '../data/types'
import { computeDocumentationTrendView } from './documentationTrend'

const baseFilters: GlobalFiltersState = {
  department: 'All',
  serviceLine: 'All',
  queue: 'All',
  recoverability: 'All',
  search: '',
}

describe('documentationTrend', () => {
  it('matches validated all-departments backlog and dollars', () => {
    const view = computeDocumentationTrendView(baseFilters)

    expect(view.currentBacklog).toBe(7)
    expect(view.currentDollarsOpen).toBe(4310)
    expect(view.netThirtyDayBacklogChange).toBe(2)
    expect(view.points.at(-1)?.date).toBe('2026-02-17')
  })

  it('matches validated Radiology / IR slice state', () => {
    const view = computeDocumentationTrendView({
      ...baseFilters,
      department: 'Radiology / Interventional Radiology',
    })

    expect(view.currentBacklog).toBe(3)
    expect(view.currentDollarsOpen).toBe(1360)
    expect(view.selectedDepartments).toEqual(['Radiology / Interventional Radiology'])
  })
})
