import { denialSignalEvents } from '../data/denialFeedbackSignals'
import type {
  CdmGovernanceMonitorItem,
  DenialFeedbackCdmMonitorView,
  DenialLinkageDetailRow,
  DenialSignalEvent,
  DenialSignalPattern,
  RevenueIntegrityCase,
} from '../data/types'

export function computeDenialFeedbackCdmMonitor(
  cases: RevenueIntegrityCase[],
): DenialFeedbackCdmMonitorView {
  const scopedCaseMap = new Map(cases.map((caseItem) => [caseItem.id, caseItem]))
  const scopedEvents = denialSignalEvents.filter((event) => scopedCaseMap.has(event.caseId))

  const denialSignalPatterns = buildDenialSignalPatterns(scopedEvents)
  const patternSelectorOptions = denialSignalPatterns.map((item) => item.patternId)
  const defaultSelectedPatternId = patternSelectorOptions[0] ?? null
  const linkageDetail = getPatternLinkageDetail(denialSignalPatterns, defaultSelectedPatternId)

  const correctionRows = scopedEvents.filter((event) => event.correctionTurnaroundDays > 0)
  const prebillCases = cases.filter((caseItem) =>
    caseItem.queue === 'Prebill edit / hold' || caseItem.queue === 'Coding pending',
  )

  return {
    denialSignalPatterns,
    cdmGovernanceMonitor: buildCdmGovernanceMonitor(scopedEvents, scopedCaseMap),
    linkageDetail,
    patternSelectorOptions,
    defaultSelectedPatternId,
    denialSignalCount: scopedEvents.length,
    denialDollars: roundTo(
      scopedEvents.reduce((runningTotal, event) => runningTotal + event.denialAmount, 0),
      2,
    ),
    governedPrebillEditAging:
      prebillCases.length === 0
        ? 0
        : roundTo(
            prebillCases.reduce((runningTotal, caseItem) => runningTotal + caseItem.agingDays, 0) /
              prebillCases.length,
            1,
          ),
    governedRecoverableDollarsStillOpen: roundTo(
      cases.reduce((runningTotal, caseItem) => {
        if (
          caseItem.queue === 'Final billed' ||
          caseItem.queue === 'Closed / monitored through denial feedback only'
        ) {
          return runningTotal
        }

        return runningTotal + caseItem.dollarsRecoverableNow
      }, 0),
      0,
    ),
    correctionTurnaroundDays:
      correctionRows.length === 0
        ? 0
        : roundTo(
            correctionRows.reduce(
              (runningTotal, event) => runningTotal + event.correctionTurnaroundDays,
              0,
            ) / correctionRows.length,
            1,
          ),
  }
}

export function buildPatternLabel(pattern: DenialSignalPattern): string {
  return `${pattern.denialReasonGroup} | ${pattern.payerGroup} | ${formatCurrency(pattern.denialAmount)}`
}

function buildDenialSignalPatterns(events: DenialSignalEvent[]): DenialSignalPattern[] {
  const groupedMap = new Map<string, DenialSignalPattern & { rowCount: number }>()

  for (const event of events) {
    const key = [
      event.denialCategory,
      event.denialReasonGroup,
      event.payerGroup,
      event.linkedUpstreamIssueDomain,
      event.linkedRootCauseMechanism,
      event.linkedOwnerTeam,
    ].join('::')

    const existing = groupedMap.get(key)

    if (existing) {
      existing.rowCount += 1
      existing.denialAmount = roundTo(existing.denialAmount + event.denialAmount, 2)
      continue
    }

    const governanceFlag = cdmGovernanceFlag(event)
    const interpretation = interpretationBucket(event, governanceFlag)
    const ownerActionHint = suggestedAction(interpretation, governanceFlag)
    const ownerPath = ownerPathHint(event, ownerActionHint)

    groupedMap.set(key, {
      patternId: '',
      denialCategory: event.denialCategory,
      denialReasonGroup: event.denialReasonGroup,
      payerGroup: event.payerGroup,
      denialAmount: roundTo(event.denialAmount, 2),
      linkedUpstreamIssueDomain: event.linkedUpstreamIssueDomain,
      linkedRootCauseMechanism: event.linkedRootCauseMechanism,
      linkedOwnerTeam: event.linkedOwnerTeam,
      repeatPatternSignal: 'Single signal',
      denialSignalStrength: 'Low',
      ownerActionHint,
      likelyOwnerPath: ownerPath,
      upstreamValidationNote: `${event.linkedUpstreamIssueDomain} signal linked to expected code ${event.expectedCode}.`,
      whyThisMattersOperationally: `Downstream denial signal points back to ${event.linkedUpstreamIssueDomain.toLowerCase()}: ${event.commonFailureMode.toLowerCase()}`,
      rowCount: 1,
    })
  }

  return Array.from(groupedMap.values())
    .sort((first, second) => {
      if (second.denialAmount !== first.denialAmount) {
        return second.denialAmount - first.denialAmount
      }

      if (second.rowCount !== first.rowCount) {
        return second.rowCount - first.rowCount
      }

      return first.denialReasonGroup.localeCompare(second.denialReasonGroup)
    })
    .map((pattern, index) => ({
      patternId: `DEN-PAT-${String(index + 1).padStart(2, '0')}`,
      denialCategory: pattern.denialCategory,
      denialReasonGroup: pattern.denialReasonGroup,
      payerGroup: pattern.payerGroup,
      denialAmount: pattern.denialAmount,
      linkedUpstreamIssueDomain: pattern.linkedUpstreamIssueDomain,
      linkedRootCauseMechanism: pattern.linkedRootCauseMechanism,
      linkedOwnerTeam: pattern.linkedOwnerTeam,
      repeatPatternSignal: pattern.rowCount > 1 ? 'Repeat pattern' : 'Single signal',
      denialSignalStrength: denialSignalStrength(pattern.rowCount, pattern.denialAmount),
      ownerActionHint: pattern.ownerActionHint,
      likelyOwnerPath: pattern.likelyOwnerPath,
      upstreamValidationNote: pattern.upstreamValidationNote,
      whyThisMattersOperationally: pattern.whyThisMattersOperationally,
    }))
}

function buildCdmGovernanceMonitor(
  events: DenialSignalEvent[],
  scopedCaseMap: Map<string, RevenueIntegrityCase>,
): CdmGovernanceMonitorItem[] {
  const grouped = new Map<string, CdmGovernanceMonitorItem>()

  for (const event of events) {
    const caseItem = scopedCaseMap.get(event.caseId)

    if (!caseItem) {
      continue
    }

    const governance = cdmGovernanceFlag(event)

    if (governance === 'Active aligned reference' && event.denialAmount <= 0) {
      continue
    }

    const interpretation = interpretationBucket(event, governance)
    const key = `${caseItem.department}::${caseItem.serviceLine}::${event.expectedCode}`
    const existing = grouped.get(key)

    if (existing) {
      existing.denialSignalRows += 1
      existing.denialAmount = roundTo(existing.denialAmount + event.denialAmount, 2)
      continue
    }

    grouped.set(key, {
      department: caseItem.department,
      serviceLine: caseItem.serviceLine,
      expectedCode: event.expectedCode,
      expectedModifier: event.cdmExpectedModifier || 'None',
      defaultUnits: event.defaultUnits,
      revenueCode: event.revenueCode || 'Missing',
      activeFlag: event.activeFlag,
      ruleStatus: event.ruleStatus,
      lastUpdateDatetime: event.lastUpdateDatetime,
      cdmGovernanceFlag: governance,
      suggestedGovernanceAction: suggestedAction(interpretation, governance),
      denialSignalRows: 1,
      denialAmount: roundTo(event.denialAmount, 2),
      upstreamValidationNote: event.commonFailureMode,
    })
  }

  return Array.from(grouped.values()).sort((first, second) => {
    if (second.denialSignalRows !== first.denialSignalRows) {
      return second.denialSignalRows - first.denialSignalRows
    }

    if (second.denialAmount !== first.denialAmount) {
      return second.denialAmount - first.denialAmount
    }

    return first.expectedCode.localeCompare(second.expectedCode)
  })
}

export function getPatternLinkageDetail(
  patterns: DenialSignalPattern[],
  selectedPatternId: string | null,
): DenialLinkageDetailRow[] {
  if (!selectedPatternId) {
    return []
  }

  const selectedPattern = patterns.find((item) => item.patternId === selectedPatternId)

  if (!selectedPattern) {
    return []
  }

  return [
    {
      field: 'Downstream signal',
      value: `${selectedPattern.denialCategory} / ${selectedPattern.denialReasonGroup}`,
    },
    { field: 'Payer group', value: selectedPattern.payerGroup },
    {
      field: 'Upstream issue domain',
      value: selectedPattern.linkedUpstreamIssueDomain,
    },
    {
      field: 'Likely root cause mechanism',
      value: selectedPattern.linkedRootCauseMechanism,
    },
    {
      field: 'Likely owner / action path',
      value: selectedPattern.likelyOwnerPath,
    },
    {
      field: 'Why this matters operationally',
      value: selectedPattern.whyThisMattersOperationally,
    },
    {
      field: 'Suggested next step',
      value: selectedPattern.ownerActionHint,
    },
    {
      field: 'Upstream validation note',
      value: selectedPattern.upstreamValidationNote,
    },
  ]
}

function denialSignalStrength(rowCount: number, denialAmount: number): 'High' | 'Moderate' | 'Low' {
  if (rowCount >= 3 || denialAmount >= 1000) {
    return 'High'
  }

  if (rowCount >= 2 || denialAmount >= 300) {
    return 'Moderate'
  }

  return 'Low'
}

function cdmGovernanceFlag(event: DenialSignalEvent): string {
  if (!event.expectedCode) {
    return 'Missing CDM reference'
  }

  if (!event.activeFlag || event.ruleStatus === 'stale' || event.ruleStatus === 'inactive_reference') {
    return 'Stale / inactive reference'
  }

  if (event.expectedModifierHint && event.cdmExpectedModifier !== event.expectedModifierHint) {
    return 'Modifier mismatch'
  }

  if (!event.revenueCode) {
    return 'Revenue-code gap'
  }

  if (event.ruleStatus === 'review_needed') {
    return 'Rule review needed'
  }

  return 'Active aligned reference'
}

function interpretationBucket(event: DenialSignalEvent, governanceFlag: string): string {
  if (
    governanceFlag === 'Missing CDM reference' ||
    governanceFlag === 'Stale / inactive reference' ||
    governanceFlag === 'Modifier mismatch' ||
    governanceFlag === 'Revenue-code gap' ||
    governanceFlag === 'Rule review needed'
  ) {
    return 'CDM / rule configuration'
  }

  if (
    event.denialReasonGroup === 'technical_rebill_review' ||
    event.denialReasonGroup === 'postbill_rebill_variance'
  ) {
    return 'Billing edit management'
  }

  if (event.denialReasonGroup === 'modifier_validation') {
    return 'Coding practice'
  }

  if (event.denialCategory === 'documentation_support_denial') {
    return 'Documentation behavior'
  }

  return event.linkedRootCauseMechanism || 'Payer-policy variance'
}

function suggestedAction(interpretationBucketValue: string, governanceFlag: string): string {
  if (governanceFlag === 'Missing CDM reference' || governanceFlag === 'Stale / inactive reference') {
    return 'CDM maintenance review'
  }

  if (
    governanceFlag === 'Modifier mismatch' ||
    governanceFlag === 'Rule review needed' ||
    governanceFlag === 'Revenue-code gap'
  ) {
    return 'Build review'
  }

  if (interpretationBucketValue === 'Coding practice') {
    return 'Modifier logic review'
  }

  if (interpretationBucketValue === 'Billing edit management') {
    return 'Billing edit management review'
  }

  if (interpretationBucketValue === 'Documentation behavior') {
    return 'Education / documentation follow-up'
  }

  return 'Payer-variance watchlist'
}

function ownerPathHint(event: DenialSignalEvent, action: string): string {
  if (event.linkedOwnerTeam) {
    return `${event.linkedOwnerTeam} -> ${action}`
  }

  if (event.operationalOwnerHint) {
    return `${event.operationalOwnerHint} -> ${action}`
  }

  return action
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(amount)
}

function roundTo(value: number, precision: number): number {
  const factor = 10 ** precision
  return Math.round(value * factor) / factor
}
