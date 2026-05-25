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
  linkedCaseIds: string[]
  baselineImpact: InterventionImpactSnapshot
  currentImpact: InterventionImpactSnapshot
}

export interface InterventionImpactSnapshot {
  caseCount: number
  dollarsAtRisk: number
  recoverableNow: number
  averageAgingDays: number
}

export interface GlobalFiltersState {
  department: string
  serviceLine: string
  queue: QueueName | 'All'
  recoverability: RecoverabilityStatus | 'All'
  search: string
}

export type ScenarioLeverKey =
  | 'prebillClearanceRate'
  | 'correctionTurnaroundDays'
  | 'routingSpeedDays'

export interface ScenarioLeverConfig {
  key: ScenarioLeverKey
  label: string
  baselineValue: number
  targetValue: number
  minValue: number
  maxValue: number
  step: number
  unitLabel: '%' | 'days'
  deltaLabel: string
  assumptionNote: string
}

export interface ScenarioBaselineInput {
  metric: string
  valueDisplay: string
  note: string
}

export interface ScenarioProjection {
  projectedRecoverableDollarLift: number
  projectedBacklogReduction: number
  projectedSlaImprovementPoints: number
  ninetyDayImpactEstimate: number
  implementationEffort: 'Low' | 'Moderate' | 'Moderate-high'
  baselineWithinSlaRate: number
  projectedWithinSlaRate: number
}

export interface ScenarioComputationResult {
  leverConfigs: ScenarioLeverConfig[]
  baselineInputs: ScenarioBaselineInput[]
  projection: ScenarioProjection
}

export interface DenialSignalEvent {
  id: string
  caseId: string
  denialCategory: string
  denialReasonGroup: string
  payerGroup: string
  denialAmount: number
  linkedUpstreamIssueDomain: string
  linkedRootCauseMechanism: string
  linkedOwnerTeam: string
  expectedCode: string
  expectedModifierHint: string
  cdmExpectedModifier: string
  revenueCode: string
  activeFlag: boolean
  ruleStatus: 'active' | 'stale' | 'review_needed' | 'inactive_reference'
  defaultUnits: number
  lastUpdateDatetime: string
  commonFailureMode: string
  operationalOwnerHint: string
  correctionTurnaroundDays: number
}

export interface DenialSignalPattern {
  patternId: string
  denialCategory: string
  denialReasonGroup: string
  payerGroup: string
  denialAmount: number
  linkedUpstreamIssueDomain: string
  linkedRootCauseMechanism: string
  linkedOwnerTeam: string
  repeatPatternSignal: 'Repeat pattern' | 'Single signal'
  denialSignalStrength: 'High' | 'Moderate' | 'Low'
  ownerActionHint: string
  likelyOwnerPath: string
  upstreamValidationNote: string
  whyThisMattersOperationally: string
}

export interface CdmGovernanceMonitorItem {
  department: string
  serviceLine: string
  expectedCode: string
  expectedModifier: string
  defaultUnits: number
  revenueCode: string
  activeFlag: boolean
  ruleStatus: 'active' | 'stale' | 'review_needed' | 'inactive_reference'
  lastUpdateDatetime: string
  cdmGovernanceFlag: string
  suggestedGovernanceAction: string
  denialSignalRows: number
  denialAmount: number
  upstreamValidationNote: string
}

export interface DenialLinkageDetailRow {
  field: string
  value: string
}

export interface DenialFeedbackCdmMonitorView {
  denialSignalPatterns: DenialSignalPattern[]
  cdmGovernanceMonitor: CdmGovernanceMonitorItem[]
  linkageDetail: DenialLinkageDetailRow[]
  patternSelectorOptions: string[]
  defaultSelectedPatternId: string | null
  denialSignalCount: number
  denialDollars: number
  governedPrebillEditAging: number
  governedRecoverableDollarsStillOpen: number
  correctionTurnaroundDays: number
}
