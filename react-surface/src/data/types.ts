export type Priority = 'Critical' | 'High' | 'Medium' | 'Low'

export type RecoverabilityStatus =
  | 'Pre-final-bill recoverable'
  | 'Post-final-bill recoverable by correction / rebill'
  | 'Post-window financially lost'
  | 'Financially closed but still compliance-relevant'

export type QueueName =
  | 'Open encounter'
  | 'Charge capture pending'
  | 'Documentation pending'
  | 'Coding pending'
  | 'Prebill edit / hold'
  | 'Ready to final bill'
  | 'Final billed'
  | 'Correction / rebill pending'
  | 'Closed / monitored through denial feedback only'

export type IssueDomain =
  | 'Charge capture failure'
  | 'Charge integrity / configuration failure'
  | 'Documentation support failure'
  | 'Patient status / case classification failure'
  | 'Coding failure'
  | 'Billing / claim-edit failure'
  | 'Packaged / non-billable / false-positive classification'
  | 'Denial feedback signal'

export type RootCauseMechanism =
  | 'People / training'
  | 'Workflow / handoff'
  | 'System build / interface'
  | 'CDM / rule configuration'
  | 'Documentation behavior'
  | 'Coding practice'
  | 'Billing edit management'
  | 'Payer-policy variance'

export interface RevenueIntegrityCase {
  id: string
  department: string
  serviceLine: string
  queue: QueueName
  owner: string
  priority: Priority
  issueDomain: IssueDomain
  rootCauseMechanism: RootCauseMechanism
  currentPrimaryBlocker: string
  agingDays: number
  recoverabilityStatus: RecoverabilityStatus
  dollarsAtRisk: number
  dollarsRecoverableNow: number
  dollarsAlreadyLost: number
  expectedSummary: string
  actualSummary: string
  controlFailureNarrative: string
  recommendedAction: string
  suppressionNote?: string
  evidenceTrace: EvidenceTraceItem[]
}

export interface EvidenceTraceItem {
  step: string
  status: 'complete' | 'warning' | 'blocked' | 'suppressed'
  detail: string
}

export interface InterventionTrackingItem {
  id: string
  title: string
  owner: string
  targetCompletionDate: string
  checkpointStatus: 'Not started' | 'In progress' | 'Validated' | 'Needs revision'
  baselineMetric: string
  currentMetric: string
  recommendation: 'Hold' | 'Expand' | 'Revise'
  validationNote: string
}

export interface GlobalFiltersState {
  department: string
  serviceLine: string
  queue: QueueName | 'All'
  recoverability: RecoverabilityStatus | 'All'
  search: string
}
