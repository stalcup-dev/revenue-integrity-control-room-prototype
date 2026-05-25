import { Activity, ArrowRightLeft, Clock3, ShieldAlert, Workflow } from 'lucide-react'
import { useMemo, useState } from 'react'

import { ExceptionWorklist } from '../components/ExceptionWorklist'
import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'
import { computeQueueGovernanceView, type QueueSlaStatus } from '../lib/queueGovernance'

interface QueueGovernanceBrowserPageProps {
  cases: RevenueIntegrityCase[]
}

type LocalQueueFilter = RevenueIntegrityCase['queue'] | 'All'
type LocalSlaFilter = QueueSlaStatus | 'All'

export function QueueGovernanceBrowserPage({ cases }: QueueGovernanceBrowserPageProps) {
  const [queueFilter, setQueueFilter] = useState<LocalQueueFilter>('All')
  const [slaFilter, setSlaFilter] = useState<LocalSlaFilter>('All')
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(cases[0]?.id ?? null)

  const filteredCases = useMemo(() => {
    const view = computeQueueGovernanceView(cases)

    return cases.filter((caseItem) => {
      if (queueFilter !== 'All' && caseItem.queue !== queueFilter) {
        return false
      }

      if (slaFilter === 'All') {
        return true
      }

      const governanceCase = view.cases.find((item) => item.caseId === caseItem.id)
      return governanceCase?.slaStatus === slaFilter
    })
  }, [cases, queueFilter, slaFilter])

  const governanceView = useMemo(() => computeQueueGovernanceView(filteredCases), [filteredCases])
  const selectedCase = useMemo(() => {
    if (filteredCases.length === 0) {
      return null
    }

    if (selectedCaseId && filteredCases.some((item) => item.id === selectedCaseId)) {
      return filteredCases.find((item) => item.id === selectedCaseId) ?? null
    }

    return filteredCases[0] ?? null
  }, [filteredCases, selectedCaseId])

  const selectedGovernanceCase = governanceView.cases.find((item) => item.caseId === selectedCase?.id) ?? null

  const queueOptions = useMemo(
    () => Array.from(new Set(cases.map((item) => item.queue))).sort((a, b) => a.localeCompare(b)),
    [cases],
  )

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-amber-900/20 bg-amber-950 text-amber-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(251,191,36,0.32),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.24),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-200">
            Queue Governance Browser
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which queue stages are absorbing recoverable opportunity, where are SLA thresholds
            breached, and who owns escalation now?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-amber-100">
            Deterministic queue-governance view only. One current blocker, one accountable owner,
            explicit stage SLA thresholds, and transparent routing evidence.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-amber-100 bg-white p-4 shadow-sm sm:p-5">
        <div className="flex flex-wrap items-end gap-3">
          <label className="block min-w-[240px] flex-1 text-sm text-slate-700" htmlFor="governance-queue-filter">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              Queue stage
            </span>
            <select
              id="governance-queue-filter"
              value={queueFilter}
              onChange={(event) => setQueueFilter(event.target.value as LocalQueueFilter)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
            >
              <option value="All">All queues</option>
              {queueOptions.map((queue) => (
                <option key={queue} value={queue}>
                  {queue}
                </option>
              ))}
            </select>
          </label>

          <label className="block min-w-[220px] flex-1 text-sm text-slate-700" htmlFor="governance-sla-filter">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              SLA status
            </span>
            <select
              id="governance-sla-filter"
              value={slaFilter}
              onChange={(event) => setSlaFilter(event.target.value as LocalSlaFilter)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
            >
              <option value="All">All statuses</option>
              <option value="Within target">Within target</option>
              <option value="At-risk">At-risk</option>
              <option value="Overdue escalation">Overdue escalation</option>
            </select>
          </label>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Governed active items"
          value={formatNumber(governanceView.cases.length)}
          note="Current queue-governed exception items in the filtered slice."
          icon={<Workflow size={18} />}
        />
        <MetricCard
          label="Overdue escalation"
          value={formatNumber(governanceView.overdueCount)}
          note="Items beyond queue overdue threshold and requiring escalation."
          tone="warning"
          icon={<ShieldAlert size={18} />}
        />
        <MetricCard
          label="At-risk stage age"
          value={formatNumber(governanceView.atRiskCount)}
          note="Items past SLA target but not yet in overdue escalation zone."
          icon={<Clock3 size={18} />}
        />
        <MetricCard
          label="Escalation-now items"
          value={formatNumber(governanceView.escalationNowCount)}
          note="Cases where queue policy currently triggers escalation ownership."
          tone="warning"
          icon={<Activity size={18} />}
        />
        <MetricCard
          label="Governed recoverable now"
          value={formatCurrency(governanceView.governedRecoverableNow)}
          note="Recoverable dollars still actionable in the visible governed queues."
          tone="highlight"
          icon={<ArrowRightLeft size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Queue Governance Summary</h3>
          <p className="mt-1 text-sm text-slate-600">
            Queue-level exposure ranked by recoverable dollars, with at-risk and overdue signal.
          </p>
        </header>

        {governanceView.queueSummary.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No queue-governance rows match the current local filters.
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
              <thead>
                <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                  <th className="border-b border-slate-200 px-3 py-2">Queue</th>
                  <th className="border-b border-slate-200 px-3 py-2">Active items</th>
                  <th className="border-b border-slate-200 px-3 py-2">At-risk</th>
                  <th className="border-b border-slate-200 px-3 py-2">Overdue</th>
                  <th className="border-b border-slate-200 px-3 py-2">Recoverable now</th>
                </tr>
              </thead>
              <tbody>
                {governanceView.queueSummary.map((row) => (
                  <tr key={row.queue} className="text-slate-700">
                    <td className="border-b border-slate-100 px-3 py-2 font-semibold text-slate-900">
                      {row.queue}
                    </td>
                    <td className="border-b border-slate-100 px-3 py-2">{formatNumber(row.activeCases)}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{formatNumber(row.atRiskCases)}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{formatNumber(row.overdueCases)}</td>
                    <td className="border-b border-slate-100 px-3 py-2">
                      {formatCurrency(row.recoverableNow)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <h3 className="font-heading text-2xl text-slate-900">Ranked Governance Worklist</h3>
          <p className="mt-1 text-sm text-slate-600">
            Select one case to inspect queue policy, owner path, and routing rationale.
          </p>
          <div className="mt-4">
            <ExceptionWorklist
              cases={filteredCases}
              selectedCaseId={selectedCase?.id ?? null}
              onSelectCase={setSelectedCaseId}
            />
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <h3 className="font-heading text-2xl text-slate-900">Selected Case Governance</h3>
          <p className="mt-1 text-sm text-slate-600">
            Current queue definition, owner/escalation chain, SLA basis, and routing history note.
          </p>

          {!selectedGovernanceCase ? (
            <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
              No selected case is available for the current local filter state.
            </div>
          ) : (
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <GovernanceFact label="Case" value={selectedGovernanceCase.caseId} />
              <GovernanceFact label="Current queue" value={selectedGovernanceCase.currentQueue} />
              <GovernanceFact label="Current stage" value={selectedGovernanceCase.currentStage} />
              <GovernanceFact label="SLA status" value={selectedGovernanceCase.slaStatus} />
              <GovernanceFact
                label="SLA threshold"
                value={`${selectedGovernanceCase.slaTargetDays} / ${selectedGovernanceCase.overdueThresholdDays} days`}
              />
              <GovernanceFact
                label="Days in stage"
                value={`${formatNumber(selectedGovernanceCase.daysInStage)} days`}
              />
              <GovernanceFact
                label="Accountable owner"
                value={selectedGovernanceCase.accountableOwner}
              />
              <GovernanceFact
                label="Supporting owner"
                value={selectedGovernanceCase.supportingOwner}
              />
              <GovernanceFact
                label="Escalation owner"
                value={selectedGovernanceCase.escalationOwner}
              />
              <GovernanceFact
                label="Recoverability"
                value={selectedGovernanceCase.recoverabilityStatus}
              />
              <GovernanceFact
                label="Queue entry rule"
                value={selectedGovernanceCase.queueEntryRule}
              />
              <GovernanceFact
                label="Queue exit rule"
                value={selectedGovernanceCase.queueExitRule}
              />
              <GovernanceFact
                label="Escalation trigger"
                value={selectedGovernanceCase.escalationTrigger}
              />
              <GovernanceFact
                label="Routing reason"
                value={selectedGovernanceCase.routingReason}
              />
              <GovernanceFact
                label="Queue business purpose"
                value={selectedGovernanceCase.queueBusinessPurpose}
              />
            </div>
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 shadow-sm">
        Queue-governance browser scope: deterministic operating evidence only. This page does not
        add workflow orchestration depth, task-engine automation, or live system integration.
      </section>
    </div>
  )
}

interface GovernanceFactProps {
  label: string
  value: string
}

function GovernanceFact({ label, value }: GovernanceFactProps) {
  return (
    <article className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-800">{value}</p>
    </article>
  )
}
