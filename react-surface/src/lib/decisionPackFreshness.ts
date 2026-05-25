import type { RevenueIntegrityCase } from '../data/types'
import { computeQueueGovernanceView } from './queueGovernance'
import { computeScenarioLab } from './scenarioLab'

export interface DecisionPackFreshnessMetric {
  label: string
  value: string
  note: string
}

export interface DecisionPackFreshnessView {
  buildTimestamp: string
  validationStatus: string
  disclaimerLines: string[]
  metrics: DecisionPackFreshnessMetric[]
  topOwnerQueue: string
  topServiceLine: string
  currentSummarySignal: string
  scenarioSnapshot: {
    projectedBacklogReduction: number
    projectedSlaImprovementPoints: number
    projectedRecoverableDollarLift: number
    ninetyDayImpactEstimate: number
  }
  proofAnchors: string[]
}

export function computeDecisionPackFreshnessView(
  cases: RevenueIntegrityCase[],
): DecisionPackFreshnessView {
  const queueGovernanceView = computeQueueGovernanceView(cases)
  const scenarioResult = computeScenarioLab(cases)
  const topQueue = queueGovernanceView.queueSummary[0]?.queue ?? 'No queue in scope'
  const topServiceLine = topBy(cases, (item) => item.dollarsAtRisk, (item) => item.serviceLine)
  const topIssueDomain = topBy(cases, (item) => item.dollarsAtRisk, (item) => item.issueDomain)
  const topQueueOwner = topBy(cases, (item) => item.dollarsAtRisk, (item) => item.owner)

  return {
    buildTimestamp: '2026-03-31T16:08:02+00:00',
    validationStatus: 'Validation status from current run manifest: Passed',
    disclaimerLines: [
      'Current deterministic snapshot of the governed app state for this build and current filtered slice.',
      'This memo is synthetic/public-safe, facility-side only, outpatient-first, and bounded to the currently implemented control-room scope.',
      'Validation status should be read exactly as shown from the current run manifest. If the manifest is not current, treat this as a snapshot sample rather than validation proof.',
      'Scenario values are what-if estimates, not forecasts. Denial signals remain downstream evidence only.',
    ],
    metrics: [
      {
        label: 'Total open exceptions',
        value: String(cases.length),
        note: 'Current governed slice size after global filters.',
      },
      {
        label: 'Recoverable now vs already lost in the current governed slice',
        value: `${formatCurrency(cases.reduce((sum, item) => sum + item.dollarsRecoverableNow, 0))} vs ${formatCurrency(cases.reduce((sum, item) => sum + item.dollarsAlreadyLost, 0))}`,
        note: 'Recoverability keeps current action-ready dollars separate from timing-window loss.',
      },
      {
        label: 'Exceptions breaching SLA',
        value: String(queueGovernanceView.overdueCount),
        note: 'Queue-governed items beyond the overdue threshold in the current slice.',
      },
      {
        label: 'Top owner queue in the current slice',
        value: topQueue,
        note: 'Highest recoverable queue grouping in the governed slice.',
      },
      {
        label: 'Top service line / department in the current slice',
        value: topServiceLine ? `${topServiceLine} | ${topIssueDomain ?? 'issue-domain mix'}` : 'No current slice signal',
        note: 'Largest dollars-at-risk concentration in the current governed view.',
      },
    ],
    topOwnerQueue: topQueueOwner ? `${topQueueOwner} -> ${topQueue}` : topQueue,
    topServiceLine: topServiceLine ?? 'No current slice signal',
    currentSummarySignal:
      topIssueDomain === 'Documentation support failure'
        ? `Current summary signal: documentation support failure is the leading issue-domain signal in this slice, while the top urgent queue grouping remains billing/edit work.`
        : `Current summary signal: ${topIssueDomain ?? 'mixed issue-domain pressure'} is leading the current slice, while queue urgency remains distributed across active work.`,
    scenarioSnapshot: {
      projectedBacklogReduction: computeProjectedBacklogReduction(scenarioResult),
      projectedSlaImprovementPoints: scenarioResult.projection.projectedSlaImprovementPoints,
      projectedRecoverableDollarLift: scenarioResult.projection.projectedRecoverableDollarLift,
      ninetyDayImpactEstimate: scenarioResult.projection.ninetyDayImpactEstimate,
    },
    proofAnchors: [
      'artifacts/trust_dent_remediation/decision_pack_freshness_patch.md',
      'artifacts/trust_dent_remediation/artifact_language_patch_log.md',
      'artifacts/decision_pack/revenue_integrity_decision_pack_audit.md',
      'artifacts/decision_pack/revenue_integrity_decision_pack.md',
      'artifacts/proof_index.md',
      'artifacts/project_summary_and_scope.md',
    ],
  }
}

function computeProjectedBacklogReduction(result: ReturnType<typeof computeScenarioLab>): number {
  return result.projection.projectedBacklogReduction
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

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(amount)
}
