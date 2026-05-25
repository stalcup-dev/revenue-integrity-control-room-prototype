import { documentationTrendHistory } from '../data/documentationTrendHistory'
import type { GlobalFiltersState } from '../data/types'

export interface DocumentationTrendPoint {
  date: string
  backlog: number
  dollarsOpen: number
  netChange: number
  entries: number
  resolved: number
}

export interface DocumentationTrendView {
  selectedDepartments: string[]
  points: DocumentationTrendPoint[]
  currentBacklog: number
  currentDollarsOpen: number
  netThirtyDayBacklogChange: number
  plateauWeeks: number
  hasLateReentrySignal: boolean
}

export function computeDocumentationTrendView(filters: GlobalFiltersState): DocumentationTrendView {
  const selectedDepartments = getSelectedDepartments(filters)
  const scopedRows = documentationTrendHistory.filter((row) =>
    selectedDepartments.includes(row.department),
  )

  const points = buildPoints(scopedRows)
  const latestPoint = points[points.length - 1]
  const firstPoint = points[0]

  return {
    selectedDepartments,
    points,
    currentBacklog: latestPoint?.backlog ?? 0,
    currentDollarsOpen: latestPoint?.dollarsOpen ?? 0,
    netThirtyDayBacklogChange:
      latestPoint && firstPoint ? latestPoint.backlog - firstPoint.backlog : 0,
    plateauWeeks: computePlateauWeeks(points),
    hasLateReentrySignal: points.slice(1).some((point) => point.netChange > 0),
  }
}

function getSelectedDepartments(filters: GlobalFiltersState): string[] {
  const departments = Array.from(new Set(documentationTrendHistory.map((row) => row.department)))

  if (filters.department === 'All') {
    return departments
  }

  if (departments.includes(filters.department)) {
    return [filters.department]
  }

  return []
}

function buildPoints(
  rows: Array<{ date: string; backlog: number; dollarsOpen: number }>,
): DocumentationTrendPoint[] {
  const grouped = new Map<string, { backlog: number; dollarsOpen: number }>()

  for (const row of rows) {
    const existing = grouped.get(row.date)

    if (existing) {
      existing.backlog += row.backlog
      existing.dollarsOpen += row.dollarsOpen
      continue
    }

    grouped.set(row.date, {
      backlog: row.backlog,
      dollarsOpen: row.dollarsOpen,
    })
  }

  const dates = Array.from(grouped.keys()).sort((first, second) => first.localeCompare(second))

  return dates.map((date, index) => {
    const current = grouped.get(date)
    const previous = index === 0 ? undefined : grouped.get(dates[index - 1])
    const netChange = previous ? current!.backlog - previous.backlog : 0

    return {
      date,
      backlog: current?.backlog ?? 0,
      dollarsOpen: current?.dollarsOpen ?? 0,
      netChange,
      entries: Math.max(netChange, 0),
      resolved: Math.max(netChange * -1, 0),
    }
  })
}

function computePlateauWeeks(points: DocumentationTrendPoint[]): number {
  if (points.length <= 1) {
    return points.length
  }

  let plateauWeeks = 1

  for (let index = points.length - 1; index > 0; index -= 1) {
    const current = points[index]
    const previous = points[index - 1]

    if (!current || !previous || current.backlog !== previous.backlog) {
      break
    }

    plateauWeeks += 1
  }

  return plateauWeeks
}
