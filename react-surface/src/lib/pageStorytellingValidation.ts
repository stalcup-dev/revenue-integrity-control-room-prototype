import type { InterventionTrackingItem, RevenueIntegrityCase } from '../data/types'

export type StoryCueMode = 'full' | 'thin'

export interface StoryCueCard {
  page: string
  mode: StoryCueMode
  controlStatement: string
  pressureStatement: string
  ownerNextMove: string
  passes: boolean
}

export interface StorytellingValidationView {
  cards: StoryCueCard[]
  validatedPages: number
  fullCuePages: number
  thinCuePages: number
  failedPages: number
}

export function computeStorytellingValidationView(
  cases: RevenueIntegrityCase[],
  interventions: InterventionTrackingItem[],
): StorytellingValidationView {
  const chargeCases = cases.filter(
    (item) =>
      item.issueDomain === 'Charge capture failure' ||
      item.issueDomain === 'Charge integrity / configuration failure' ||
      item.issueDomain === 'Patient status / case classification failure' ||
      item.issueDomain === 'Coding failure' ||
      item.issueDomain === 'Billing / claim-edit failure',
  )
  const prebillCases = cases.filter(
    (item) =>
      item.queue === 'Prebill edit / hold' ||
      item.queue === 'Coding pending' ||
      item.issueDomain === 'Billing / claim-edit failure' ||
      item.issueDomain === 'Coding failure',
  )
  const documentationCases = cases.filter(
    (item) => item.issueDomain === 'Documentation support failure' || item.queue === 'Documentation pending',
  )

  const cards: StoryCueCard[] = [
    buildChargeReconciliationCue(chargeCases),
    buildPrebillCue(prebillCases),
    buildDocumentationCue(documentationCases),
    buildActionTrackerCue(cases, interventions),
    buildScenarioLabCue(),
  ]

  const validatedPages = cards.filter((item) => item.passes).length
  const fullCuePages = cards.filter((item) => item.mode === 'full').length
  const thinCuePages = cards.filter((item) => item.mode === 'thin').length

  return {
    cards,
    validatedPages,
    fullCuePages,
    thinCuePages,
    failedPages: cards.length - validatedPages,
  }
}

function buildChargeReconciliationCue(cases: RevenueIntegrityCase[]): StoryCueCard {
  const unresolved = cases.filter(
    (item) =>
      item.queue !== 'Final billed' && item.queue !== 'Closed / monitored through denial feedback only',
  )
  const topServiceLine = topBy(unresolved, (item) => item.dollarsAtRisk, (item) => item.serviceLine)
  const topCase = unresolved[0] ?? cases[0]

  return fullCue(
    'Charge Reconciliation Monitor',
    'Reconciliation control is monitoring whether expected charge opportunities are posted and reconciled before financial leakage compounds.',
    unresolved.length === 0
      ? 'No unresolved reconciliation pressure is currently visible in this filtered slice.'
      : `${topServiceLine ?? 'Current slice'} is driving ${unresolved.length} unresolved reconciliation case(s).`,
    topCase
      ? `${topCase.owner} should clear reconciliation blocker on ${topCase.id}.`
      : 'No owner next move is required for current reconciliation scope.',
  )
}

function buildPrebillCue(cases: RevenueIntegrityCase[]): StoryCueCard {
  const activeHolds = cases.filter(
    (item) =>
      item.recoverabilityStatus === 'Pre-final-bill recoverable' &&
      item.queue !== 'Ready to final bill' &&
      item.queue !== 'Final billed' &&
      item.queue !== 'Closed / monitored through denial feedback only',
  )
  const topRootCause = topBy(activeHolds, () => 1, (item) => item.rootCauseMechanism)
  const topCase = activeHolds[0] ?? cases[0]

  return fullCue(
    'Modifiers / Edits / Prebill Holds',
    'Prebill-edit control is monitoring unresolved hard-stop edits before final bill release.',
    activeHolds.length === 0
      ? 'No active prebill hold pressure is currently visible in this filtered slice.'
      : `${activeHolds.length} active hold case(s) are concentrated around ${topRootCause ?? 'mixed'} handoff patterns.`,
    topCase
      ? `${topCase.owner} should clear prebill hold blocker on ${topCase.id}.`
      : 'No billing-owner next move is required for the current prebill scope.',
  )
}

function buildDocumentationCue(cases: RevenueIntegrityCase[]): StoryCueCard {
  const unsupportedDollars = cases.reduce((runningTotal, item) => runningTotal + item.dollarsAtRisk, 0)
  const topCase = cases[0]
  const gapLabel = deriveDocumentationGap(cases)

  return fullCue(
    'Documentation Support Exceptions',
    'Documentation-support control is monitoring where performed activity still lacks billable support evidence.',
    cases.length === 0
      ? 'No documentation-support pressure is currently visible in this filtered slice.'
      : `${gapLabel} is driving ${cases.length} open documentation exception(s) with ${formatCurrency(unsupportedDollars)} at risk.`,
    topCase
      ? `${topCase.owner} should close documentation support gap on ${topCase.id}.`
      : 'No documentation owner next move is required for the current slice.',
  )
}

function buildActionTrackerCue(
  cases: RevenueIntegrityCase[],
  interventions: InterventionTrackingItem[],
): StoryCueCard {
  const caseIds = new Set(cases.map((item) => item.id))
  const scopedInterventions = interventions.filter((item) =>
    item.linkedCaseIds.some((caseId) => caseIds.has(caseId)),
  )
  const needsRevision = scopedInterventions.filter((item) => item.checkpointStatus === 'Needs revision').length
  const topIntervention = scopedInterventions.sort((first, second) => {
    if (second.currentImpact.recoverableNow !== first.currentImpact.recoverableNow) {
      return second.currentImpact.recoverableNow - first.currentImpact.recoverableNow
    }

    return first.title.localeCompare(second.title)
  })[0]

  return fullCue(
    'Opportunity & Action Tracker',
    'Intervention follow-through control is monitoring checkpoint pressure and recommendation stability across routed exceptions.',
    scopedInterventions.length === 0
      ? 'No intervention checkpoint pressure is visible for this filtered slice.'
      : `${needsRevision} intervention(s) currently need revision across ${scopedInterventions.length} active intervention(s).`,
    topIntervention
      ? `${topIntervention.owner} should execute next checkpoint on ${topIntervention.title}.`
      : 'No intervention owner next move is required for the current slice.',
  )
}

function buildScenarioLabCue(): StoryCueCard {
  return thinCue(
    'Scenario Lab',
    'Scenario Lab remains a deterministic, capped what-if surface and is not a queue-story replacement.',
  )
}

function fullCue(
  page: string,
  controlStatement: string,
  pressureStatement: string,
  ownerNextMove: string,
): StoryCueCard {
  const passes =
    controlStatement.trim().length > 0 &&
    pressureStatement.trim().length > 0 &&
    ownerNextMove.trim().length > 0

  return {
    page,
    mode: 'full',
    controlStatement,
    pressureStatement,
    ownerNextMove,
    passes,
  }
}

function thinCue(page: string, controlStatement: string): StoryCueCard {
  const passes = controlStatement.trim().length > 0

  return {
    page,
    mode: 'thin',
    controlStatement,
    pressureStatement: 'Intentionally light framing for what-if scope.',
    ownerNextMove: 'Not required for thin scenario framing.',
    passes,
  }
}

function topBy(
  cases: RevenueIntegrityCase[],
  score: (item: RevenueIntegrityCase) => number,
  value: (item: RevenueIntegrityCase) => string,
): string | null {
  if (cases.length === 0) {
    return null
  }

  const grouped = new Map<string, number>()

  for (const item of cases) {
    const key = value(item)
    grouped.set(key, (grouped.get(key) ?? 0) + score(item))
  }

  return Array.from(grouped.entries()).sort((first, second) => second[1] - first[1])[0]?.[0] ?? null
}

function deriveDocumentationGap(cases: RevenueIntegrityCase[]): string {
  const blockers = cases.map((item) => item.currentPrimaryBlocker.toLowerCase())

  if (blockers.some((item) => item.includes('timestamp'))) {
    return 'Missing case time support'
  }

  if (blockers.some((item) => item.includes('laterality') || item.includes('device'))) {
    return 'Laterality or device-linkage support gap'
  }

  if (blockers.some((item) => item.includes('stop') || item.includes('hour'))) {
    return 'Infusion support timestamp gap'
  }

  return 'Documentation support gap'
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(amount)
}
