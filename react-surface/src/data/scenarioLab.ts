import type { ScenarioLeverKey } from './types'

export const scenarioCaps = {
  clearanceGain: 0.2,
  turnaroundGain: 0.35,
  routingGain: 0.25,
  backlogReduction: 0.3,
  dollarLift: 0.35,
} as const

export const scenarioLeverMetadata: Record<
  ScenarioLeverKey,
  {
    label: string
    unitLabel: '%' | 'days'
    step: number
    deltaLabel: string
    assumptionNote: string
  }
> = {
  prebillClearanceRate: {
    label: 'Prebill edit clearance rate',
    unitLabel: '%',
    step: 1,
    deltaLabel: 'pts',
    assumptionNote:
      'Improvement only; capped so prebill clearance cannot claim more than 20% of current backlog release in 90 days.',
  },
  correctionTurnaroundDays: {
    label: 'Correction turnaround days',
    unitLabel: 'days',
    step: 0.5,
    deltaLabel: 'days faster',
    assumptionNote:
      'Improvement only; faster correction turnaround is capped at 35% of current open correction impact.',
  },
  routingSpeedDays: {
    label: 'Routing speed to owner teams',
    unitLabel: 'days',
    step: 0.1,
    deltaLabel: 'days faster',
    assumptionNote:
      'Improvement only; routing relief is capped at 25% of active handoff pressure to avoid treating every handoff day as removable.',
  },
}
