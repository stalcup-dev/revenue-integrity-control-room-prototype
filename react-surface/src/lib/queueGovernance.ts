import type {
  QueueName,
  RecoverabilityStatus,
  RevenueIntegrityCase,
  RootCauseMechanism,
} from '../data/types'

export type QueueSlaStatus = 'Within target' | 'At-risk' | 'Overdue escalation'

export interface QueueGovernanceCase {
  caseId: string
  currentQueue: QueueName
  currentStage: string
  accountableOwner: string
  supportingOwner: string
  escalationOwner: string
  daysInStage: number
  slaStatus: QueueSlaStatus
  slaTargetDays: number
  overdueThresholdDays: number
  queueBusinessPurpose: string
  queueEntryRule: string
  queueExitRule: string
  escalationTrigger: string
  routingReason: string
  recoverabilityStatus: RecoverabilityStatus
  dollarsRecoverableNow: number
}

export interface QueueGovernanceSummaryRow {
  queue: QueueName
  activeCases: number
  overdueCases: number
  atRiskCases: number
  recoverableNow: number
}

export interface QueueGovernanceView {
  cases: QueueGovernanceCase[]
  queueSummary: QueueGovernanceSummaryRow[]
  overdueCount: number
  atRiskCount: number
  escalationNowCount: number
  governedRecoverableNow: number
}

interface QueueRule {
  stage: string
  purpose: string
  entryRule: string
  exitRule: string
  slaTargetDays: number
  overdueThresholdDays: number
}

const queueRules: Record<QueueName, QueueRule> = {
  'Open encounter': {
    stage: 'Encounter open review',
    purpose: 'Initial integrity signal screening before downstream routing.',
    entryRule: 'Encounter opens with deterministic mismatch candidate.',
    exitRule: 'Route to specialized queue once blocker is classified.',
    slaTargetDays: 2,
    overdueThresholdDays: 5,
  },
  'Charge capture pending': {
    stage: 'Charge capture remediation',
    purpose: 'Recover expected technical/professional charge events before billing.',
    entryRule: 'Expected charge event missing after documented activity.',
    exitRule: 'Charge posted and validated or rerouted to coding/prebill.',
    slaTargetDays: 5,
    overdueThresholdDays: 10,
  },
  'Documentation pending': {
    stage: 'Documentation support completion',
    purpose: 'Close support gaps required for billable claim integrity.',
    entryRule: 'Required support element incomplete or missing.',
    exitRule: 'Support complete and case returns to coding/prebill path.',
    slaTargetDays: 4,
    overdueThresholdDays: 8,
  },
  'Coding pending': {
    stage: 'Coding validation',
    purpose: 'Ensure code/modifier assignment aligns with performed activity.',
    entryRule: 'Coding-level ambiguity blocks deterministic release.',
    exitRule: 'Coding validated and case advances to prebill/final bill.',
    slaTargetDays: 6,
    overdueThresholdDays: 12,
  },
  'Prebill edit / hold': {
    stage: 'Prebill claim-edit hold',
    purpose: 'Resolve hard-stop edits before final bill release.',
    entryRule: 'Claim edit or modifier gate blocks final bill.',
    exitRule: 'Edit clears and claim transitions to ready-to-bill.',
    slaTargetDays: 4,
    overdueThresholdDays: 9,
  },
  'Ready to final bill': {
    stage: 'Final release staging',
    purpose: 'Confirm release readiness and close residual blockers.',
    entryRule: 'All deterministic blockers resolved pending release cycle.',
    exitRule: 'Claim released to final bill.',
    slaTargetDays: 2,
    overdueThresholdDays: 4,
  },
  'Final billed': {
    stage: 'Post-bill observation',
    purpose: 'Monitor billed state for downstream correction needs.',
    entryRule: 'Claim finalized.',
    exitRule: 'Case closed or routed to correction/rebill if variance appears.',
    slaTargetDays: 3,
    overdueThresholdDays: 7,
  },
  'Correction / rebill pending': {
    stage: 'Correction and rebill',
    purpose: 'Recover post-final-bill opportunity before payer window closes.',
    entryRule: 'Post-bill variance requires corrected submission.',
    exitRule: 'Corrected claim accepted or recoverability window closes.',
    slaTargetDays: 7,
    overdueThresholdDays: 14,
  },
  'Closed / monitored through denial feedback only': {
    stage: 'Closed downstream signal monitoring',
    purpose: 'Track repeat denial/control signals without reopening workflow.',
    entryRule: 'Financial workflow closed; governance signal retained.',
    exitRule: 'Signal trend stabilizes or governance update is validated.',
    slaTargetDays: 21,
    overdueThresholdDays: 35,
  },
}

export function computeQueueGovernanceView(cases: RevenueIntegrityCase[]): QueueGovernanceView {
  const governanceCases = cases.map((caseItem) => toGovernanceCase(caseItem))
  const summaryMap = new Map<QueueName, QueueGovernanceSummaryRow>()

  for (const item of governanceCases) {
    const existing = summaryMap.get(item.currentQueue)

    if (!existing) {
      summaryMap.set(item.currentQueue, {
        queue: item.currentQueue,
        activeCases: 1,
        overdueCases: item.slaStatus === 'Overdue escalation' ? 1 : 0,
        atRiskCases: item.slaStatus === 'At-risk' ? 1 : 0,
        recoverableNow: item.dollarsRecoverableNow,
      })
      continue
    }

    existing.activeCases += 1
    existing.overdueCases += item.slaStatus === 'Overdue escalation' ? 1 : 0
    existing.atRiskCases += item.slaStatus === 'At-risk' ? 1 : 0
    existing.recoverableNow += item.dollarsRecoverableNow
  }

  const queueSummary = Array.from(summaryMap.values()).sort((first, second) => {
    if (second.recoverableNow !== first.recoverableNow) {
      return second.recoverableNow - first.recoverableNow
    }

    if (second.overdueCases !== first.overdueCases) {
      return second.overdueCases - first.overdueCases
    }

    return first.queue.localeCompare(second.queue)
  })

  const overdueCount = governanceCases.filter((item) => item.slaStatus === 'Overdue escalation').length
  const atRiskCount = governanceCases.filter((item) => item.slaStatus === 'At-risk').length
  const escalationNowCount = governanceCases.filter(
    (item) => item.slaStatus === 'Overdue escalation' || item.daysInStage >= item.overdueThresholdDays,
  ).length

  return {
    cases: governanceCases,
    queueSummary,
    overdueCount,
    atRiskCount,
    escalationNowCount,
    governedRecoverableNow: governanceCases.reduce(
      (runningTotal, item) => runningTotal + item.dollarsRecoverableNow,
      0,
    ),
  }
}

function toGovernanceCase(caseItem: RevenueIntegrityCase): QueueGovernanceCase {
  const rule = queueRules[caseItem.queue]
  const slaStatus = classifySlaStatus(caseItem.agingDays, rule.slaTargetDays, rule.overdueThresholdDays)

  return {
    caseId: caseItem.id,
    currentQueue: caseItem.queue,
    currentStage: rule.stage,
    accountableOwner: caseItem.owner,
    supportingOwner: supportingOwnerForRootCause(caseItem.rootCauseMechanism),
    escalationOwner: escalationOwnerForQueue(caseItem.queue),
    daysInStage: caseItem.agingDays,
    slaStatus,
    slaTargetDays: rule.slaTargetDays,
    overdueThresholdDays: rule.overdueThresholdDays,
    queueBusinessPurpose: rule.purpose,
    queueEntryRule: rule.entryRule,
    queueExitRule: rule.exitRule,
    escalationTrigger: `Escalate when stage age exceeds ${rule.overdueThresholdDays} days or blocker impact increases.`,
    routingReason: routingReason(caseItem),
    recoverabilityStatus: caseItem.recoverabilityStatus,
    dollarsRecoverableNow: caseItem.dollarsRecoverableNow,
  }
}

function classifySlaStatus(
  daysInStage: number,
  slaTargetDays: number,
  overdueThresholdDays: number,
): QueueSlaStatus {
  if (daysInStage > overdueThresholdDays) {
    return 'Overdue escalation'
  }

  if (daysInStage > slaTargetDays) {
    return 'At-risk'
  }

  return 'Within target'
}

function supportingOwnerForRootCause(rootCause: RootCauseMechanism): string {
  switch (rootCause) {
    case 'System build / interface':
      return 'Revenue systems analyst'
    case 'CDM / rule configuration':
      return 'CDM governance lead'
    case 'Documentation behavior':
      return 'Clinical documentation lead'
    case 'Coding practice':
      return 'Coding quality lead'
    case 'Billing edit management':
      return 'Billing edit governance lead'
    case 'Workflow / handoff':
      return 'Revenue operations manager'
    case 'People / training':
      return 'Department educator'
    default:
      return 'Revenue integrity lead'
  }
}

function escalationOwnerForQueue(queue: QueueName): string {
  if (queue === 'Closed / monitored through denial feedback only') {
    return 'Denial governance committee'
  }

  if (queue === 'Correction / rebill pending') {
    return 'Corrections and rebill manager'
  }

  return 'Revenue integrity operations lead'
}

function routingReason(caseItem: RevenueIntegrityCase): string {
  const routingEvidence = caseItem.evidenceTrace.find((item) => item.step === 'Routing decision')

  if (routingEvidence) {
    return routingEvidence.detail
  }

  return `Routed to ${caseItem.queue} because ${caseItem.currentPrimaryBlocker.toLowerCase()}`
}
