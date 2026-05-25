import { scenarioCaps, scenarioLeverMetadata } from '../data/scenarioLab'
import type {
  RevenueIntegrityCase,
  ScenarioBaselineInput,
  ScenarioComputationResult,
  ScenarioLeverConfig,
  ScenarioProjection,
} from '../data/types'
import { formatCurrency, formatNumber } from './formatters'

const RECOVERABLE_STATES = new Set([
  'Pre-final-bill recoverable',
  'Post-final-bill recoverable by correction / rebill',
])

const NON_WITHIN_SLA_DAYS = 7

interface BaselineState {
  openExceptions: number
  nonWithinSlaCount: number
  agedRecoverableDollars: number
  prebillOpen: RevenueIntegrityCase[]
  correctionOpen: RevenueIntegrityCase[]
  handoffOpen: RevenueIntegrityCase[]
  recoverable: RevenueIntegrityCase[]
  prebillClearanceBaseline: number
  correctionTurnaroundBaseline: number
  routingSpeedBaseline: number
  withinSlaBaselineRate: number
}

interface ScenarioTargets {
  prebillClearanceRate: number
  correctionTurnaroundDays: number
  routingSpeedDays: number
}

export function computeScenarioLab(cases: RevenueIntegrityCase[], targets?: Partial<ScenarioTargets>): ScenarioComputationResult {
  const baseline = deriveBaselineState(cases)
  const leverConfigs = buildLeverConfigs(baseline, targets)

  const projection = projectScenario(
    baseline,
    {
      prebillClearanceRate: leverConfigs.find((item) => item.key === 'prebillClearanceRate')?.targetValue ?? baseline.prebillClearanceBaseline,
      correctionTurnaroundDays:
        leverConfigs.find((item) => item.key === 'correctionTurnaroundDays')?.targetValue ??
        baseline.correctionTurnaroundBaseline,
      routingSpeedDays:
        leverConfigs.find((item) => item.key === 'routingSpeedDays')?.targetValue ??
        baseline.routingSpeedBaseline,
    },
  )

  return {
    leverConfigs,
    baselineInputs: buildBaselineInputs(baseline),
    projection,
  }
}

function deriveBaselineState(cases: RevenueIntegrityCase[]): BaselineState {
  const recoverable = cases.filter((caseItem) => RECOVERABLE_STATES.has(caseItem.recoverabilityStatus))
  const nonWithinSlaCases = cases.filter((caseItem) => caseItem.agingDays > NON_WITHIN_SLA_DAYS)
  const agedRecoverable = recoverable.filter((caseItem) => caseItem.agingDays > NON_WITHIN_SLA_DAYS)

  const prebillOpen = cases.filter((caseItem) => caseItem.queue === 'Prebill edit / hold')
  const correctionOpen = cases.filter((caseItem) => caseItem.queue === 'Correction / rebill pending')
  const handoffOpen = cases.filter((caseItem) =>
    caseItem.queue === 'Charge capture pending' ||
    caseItem.queue === 'Documentation pending' ||
    caseItem.queue === 'Coding pending',
  )

  const prebillTouched = cases.filter((caseItem) =>
    caseItem.queue === 'Prebill edit / hold' ||
    caseItem.queue === 'Correction / rebill pending' ||
    caseItem.queue === 'Coding pending' ||
    caseItem.queue === 'Ready to final bill' ||
    caseItem.queue === 'Final billed',
  )
  const prebillRecoverable = prebillTouched.filter(
    (caseItem) => caseItem.recoverabilityStatus === 'Pre-final-bill recoverable',
  )

  const prebillClearanceBaseline = safePercent(prebillRecoverable.length, prebillTouched.length)
  const correctionTurnaroundBaseline = safeMean(correctionOpen.map((item) => item.agingDays))
  const routingSpeedBaseline = safeMean(handoffOpen.map((item) => item.agingDays))
  const withinSlaBaselineRate = safePercent(
    cases.filter((caseItem) => caseItem.agingDays <= NON_WITHIN_SLA_DAYS).length,
    cases.length,
  )

  return {
    openExceptions: cases.length,
    nonWithinSlaCount: nonWithinSlaCases.length,
    agedRecoverableDollars: agedRecoverable.reduce(
      (runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk,
      0,
    ),
    prebillOpen,
    correctionOpen,
    handoffOpen,
    recoverable,
    prebillClearanceBaseline,
    correctionTurnaroundBaseline,
    routingSpeedBaseline,
    withinSlaBaselineRate,
  }
}

function buildLeverConfigs(baseline: BaselineState, targets?: Partial<ScenarioTargets>): ScenarioLeverConfig[] {
  const clearanceBaseline = baseline.prebillClearanceBaseline
  const correctionBaseline = baseline.correctionTurnaroundBaseline
  const routingBaseline = baseline.routingSpeedBaseline

  return [
    {
      key: 'prebillClearanceRate',
      label: scenarioLeverMetadata.prebillClearanceRate.label,
      baselineValue: clearanceBaseline,
      targetValue: clamp(
        targets?.prebillClearanceRate ?? defaultTargetPercent(clearanceBaseline),
        clearanceBaseline,
        95,
      ),
      minValue: clearanceBaseline,
      maxValue: 95,
      step: scenarioLeverMetadata.prebillClearanceRate.step,
      unitLabel: scenarioLeverMetadata.prebillClearanceRate.unitLabel,
      deltaLabel: scenarioLeverMetadata.prebillClearanceRate.deltaLabel,
      assumptionNote: scenarioLeverMetadata.prebillClearanceRate.assumptionNote,
    },
    {
      key: 'correctionTurnaroundDays',
      label: scenarioLeverMetadata.correctionTurnaroundDays.label,
      baselineValue: correctionBaseline,
      targetValue: clamp(
        targets?.correctionTurnaroundDays ?? defaultTargetDays(correctionBaseline),
        correctionBaseline === 0 ? 0 : 0.5,
        Math.max(correctionBaseline, 0.5),
      ),
      minValue: correctionBaseline === 0 ? 0 : 0.5,
      maxValue: Math.max(correctionBaseline, 0.5),
      step: scenarioLeverMetadata.correctionTurnaroundDays.step,
      unitLabel: scenarioLeverMetadata.correctionTurnaroundDays.unitLabel,
      deltaLabel: scenarioLeverMetadata.correctionTurnaroundDays.deltaLabel,
      assumptionNote: scenarioLeverMetadata.correctionTurnaroundDays.assumptionNote,
    },
    {
      key: 'routingSpeedDays',
      label: scenarioLeverMetadata.routingSpeedDays.label,
      baselineValue: routingBaseline,
      targetValue: clamp(
        targets?.routingSpeedDays ?? defaultTargetDays(routingBaseline),
        routingBaseline === 0 ? 0 : 0.5,
        Math.max(routingBaseline, 0.5),
      ),
      minValue: routingBaseline === 0 ? 0 : 0.5,
      maxValue: Math.max(routingBaseline, 0.5),
      step: scenarioLeverMetadata.routingSpeedDays.step,
      unitLabel: scenarioLeverMetadata.routingSpeedDays.unitLabel,
      deltaLabel: scenarioLeverMetadata.routingSpeedDays.deltaLabel,
      assumptionNote: scenarioLeverMetadata.routingSpeedDays.assumptionNote,
    },
  ]
}

function projectScenario(baseline: BaselineState, targets: ScenarioTargets): ScenarioProjection {
  const clearanceGain = gainPoints(
    baseline.prebillClearanceBaseline,
    targets.prebillClearanceRate,
    scenarioCaps.clearanceGain,
  )
  const turnaroundGain = gainRatio(
    baseline.correctionTurnaroundBaseline,
    targets.correctionTurnaroundDays,
    scenarioCaps.turnaroundGain,
  )
  const routingGain = gainRatio(
    baseline.routingSpeedBaseline,
    targets.routingSpeedDays,
    scenarioCaps.routingGain,
  )

  const backlogReductionRaw =
    baseline.prebillOpen.length * clearanceGain + baseline.handoffOpen.length * routingGain
  const projectedBacklogReduction = Math.round(
    Math.min(baseline.openExceptions * scenarioCaps.backlogReduction, backlogReductionRaw),
  )

  const improvedSlaCasesRaw =
    baseline.prebillOpen.filter((item) => item.agingDays > NON_WITHIN_SLA_DAYS).length * clearanceGain +
    baseline.handoffOpen.filter((item) => item.agingDays > NON_WITHIN_SLA_DAYS).length * routingGain +
    baseline.correctionOpen.filter((item) => item.agingDays > NON_WITHIN_SLA_DAYS).length * turnaroundGain
  const improvedSlaCases = Math.round(Math.min(baseline.nonWithinSlaCount, improvedSlaCasesRaw))

  const projectedWithinSlaRate = safePercent(
    baseline.openExceptions - baseline.nonWithinSlaCount + improvedSlaCases,
    baseline.openExceptions,
  )
  const projectedSlaImprovementPoints = roundTo(
    projectedWithinSlaRate - baseline.withinSlaBaselineRate,
    1,
  )

  const prebillRecoverableDollars = sumRecoverableDollars(baseline.prebillOpen)
  const correctionRecoverableDollars = sumRecoverableDollars(baseline.correctionOpen)
  const handoffRecoverableDollars = sumRecoverableDollars(baseline.handoffOpen)

  const projectedRecoverableDollarLift = roundTo(
    Math.min(
      baseline.agedRecoverableDollars * scenarioCaps.dollarLift,
      prebillRecoverableDollars * clearanceGain +
        correctionRecoverableDollars * turnaroundGain +
        handoffRecoverableDollars * routingGain,
    ),
    2,
  )

  const ninetyDayImpactEstimate = roundTo(projectedRecoverableDollarLift * 3, 2)

  const implementationEffort = deriveImplementationEffort(
    Math.max(targets.prebillClearanceRate - baseline.prebillClearanceBaseline, 0),
    Math.max(baseline.correctionTurnaroundBaseline - targets.correctionTurnaroundDays, 0),
    Math.max(baseline.routingSpeedBaseline - targets.routingSpeedDays, 0),
  )

  return {
    projectedRecoverableDollarLift,
    projectedBacklogReduction,
    projectedSlaImprovementPoints,
    ninetyDayImpactEstimate,
    implementationEffort,
    baselineWithinSlaRate: baseline.withinSlaBaselineRate,
    projectedWithinSlaRate,
  }
}

function buildBaselineInputs(baseline: BaselineState): ScenarioBaselineInput[] {
  return [
    {
      metric: 'Open exceptions in current slice',
      valueDisplay: formatNumber(baseline.openExceptions),
      note: 'Current active filtered backlog used for backlog and SLA scenario outputs.',
    },
    {
      metric: 'Non-within-SLA exceptions',
      valueDisplay: formatNumber(baseline.nonWithinSlaCount),
      note: 'Current at-risk plus overdue exceptions used for SLA improvement math.',
    },
    {
      metric: 'Aged recoverable dollars in current slice',
      valueDisplay: formatCurrency(baseline.agedRecoverableDollars),
      note: 'Current recoverable dollars already carrying at-risk or overdue pressure.',
    },
    {
      metric: 'Correction turnaround baseline',
      valueDisplay: `${formatNumber(roundTo(baseline.correctionTurnaroundBaseline, 1))} days`,
      note: 'Average aging on open correction / rebill items in current filtered scope.',
    },
    {
      metric: 'Routing speed to owner teams baseline',
      valueDisplay: `${formatNumber(roundTo(baseline.routingSpeedBaseline, 1))} days`,
      note: 'Average aging proxy for active handoff queues in current filtered scope.',
    },
    {
      metric: 'Prebill edit clearance baseline proxy',
      valueDisplay: `${formatNumber(roundTo(baseline.prebillClearanceBaseline, 1))}%`,
      note: 'Share of prebill-touched items still on a pre-final-bill recoverable path.',
    },
  ]
}

function sumRecoverableDollars(cases: RevenueIntegrityCase[]): number {
  return cases
    .filter((caseItem) => RECOVERABLE_STATES.has(caseItem.recoverabilityStatus))
    .reduce((runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk, 0)
}

function deriveImplementationEffort(
  clearanceDeltaPoints: number,
  turnaroundDaysSaved: number,
  routingDaysSaved: number,
): 'Low' | 'Moderate' | 'Moderate-high' {
  let effortScore = 0

  if (clearanceDeltaPoints >= 10) {
    effortScore += 1
  }

  if (turnaroundDaysSaved >= 1) {
    effortScore += 1
  }

  if (routingDaysSaved >= 0.5) {
    effortScore += 1
  }

  if (effortScore <= 1) {
    return 'Low'
  }

  if (effortScore === 2) {
    return 'Moderate'
  }

  return 'Moderate-high'
}

function gainRatio(current: number, target: number, cap: number): number {
  if (current <= 0) {
    return 0
  }

  const improvement = Math.max(current - target, 0)
  return roundTo(Math.min(improvement / current, cap), 4)
}

function gainPoints(current: number, target: number, cap: number): number {
  const improvement = Math.max(target - current, 0)
  return roundTo(Math.min(improvement / 100, cap), 4)
}

function safeMean(values: number[]): number {
  if (values.length === 0) {
    return 0
  }

  return roundTo(values.reduce((total, value) => total + value, 0) / values.length, 2)
}

function safePercent(numerator: number, denominator: number): number {
  if (denominator <= 0) {
    return 0
  }

  return roundTo((numerator / denominator) * 100, 1)
}

function defaultTargetPercent(baseline: number): number {
  return roundTo(Math.min(90, baseline + 10), 1)
}

function defaultTargetDays(baseline: number): number {
  if (baseline <= 0) {
    return 0
  }

  return roundTo(Math.max(0.5, baseline - 0.5), 1)
}

function clamp(value: number, minValue: number, maxValue: number): number {
  return Math.min(Math.max(value, minValue), maxValue)
}

function roundTo(value: number, decimals: number): number {
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}
