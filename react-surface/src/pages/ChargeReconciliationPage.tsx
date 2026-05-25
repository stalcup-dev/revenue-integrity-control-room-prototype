import { AlertCircle, Clock3, DatabaseZap, Layers3, TimerReset } from 'lucide-react'
import type { ReactNode } from 'react'

import { CaseDetailPanel } from '../components/CaseDetailPanel'
import { ExceptionWorklist } from '../components/ExceptionWorklist'
import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface ChargeReconciliationMetrics {
  reconciliationCases: number
  unreconciledRate: number
  lateChargePressure: number
  averageAging: number
}

interface ChargeReconciliationPageProps {
  cases: RevenueIntegrityCase[]
  selectedCaseId: string | null
  onSelectCase: (caseId: string) => void
  metrics: ChargeReconciliationMetrics
}

export function ChargeReconciliationPage({
  cases,
  selectedCaseId,
  onSelectCase,
  metrics,
}: ChargeReconciliationPageProps) {
  const selectedCase = cases.find((caseItem) => caseItem.id === selectedCaseId) ?? cases[0] ?? null
  const queuePressure = buildQueuePressure(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-200/70 bg-cyan-950 text-cyan-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.28),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.3),transparent_40%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">
            Charge Reconciliation Monitor
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Where are documented outpatient services not yet reconciled into a clean
            facility billing state?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-cyan-100">
            This lane focuses on unreconciled workflow pressure from charge capture through
            coding, prebill edit, and correction/rebill follow-through.
          </p>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <ReconciliationFact
              icon={<DatabaseZap size={15} />}
              label="Control objective"
              value="Documented performed activity reconciles to expected facility charge state."
            />
            <ReconciliationFact
              icon={<TimerReset size={15} />}
              label="Aging risk"
              value="Late reconciliation drives post-window loss and correction complexity."
            />
            <ReconciliationFact
              icon={<Layers3 size={15} />}
              label="Operational owner"
              value="One current blocker and queue owner drive next deterministic action."
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
        <MetricCard
          label="Reconciliation cases"
          value={formatNumber(metrics.reconciliationCases)}
          note="Filtered cases currently in reconciliation scope."
          icon={<DatabaseZap size={18} />}
        />
        <MetricCard
          label="Unreconciled rate"
          value={`${formatNumber(metrics.unreconciledRate)}%`}
          note="Share of reconciliation-scope cases not yet in final or closed monitoring state."
          tone="warning"
          icon={<AlertCircle size={18} />}
        />
        <MetricCard
          label="Late-charge pressure"
          value={formatCurrency(metrics.lateChargePressure)}
          note="At-risk dollars on unresolved cases aged beyond 7 days."
          tone="warning"
          icon={<TimerReset size={18} />}
        />
        <MetricCard
          label="Average unresolved aging"
          value={`${formatNumber(metrics.averageAging)} days`}
          note="Mean blocker aging across unresolved reconciliation cases."
          icon={<Clock3 size={18} />}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {queuePressure.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600 lg:col-span-3">
            No reconciliation queue pressure available for the current filters.
          </div>
        ) : (
          queuePressure.map((item) => (
            <article
              key={item.queue}
              className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Owner queue</p>
              <h3 className="mt-1 text-base font-semibold text-slate-900">{item.queue}</h3>
              <p className="mt-2 text-sm text-slate-600">
                {formatNumber(item.caseCount)} cases | {formatCurrency(item.dollarsAtRisk)} at risk
              </p>
            </article>
          ))
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-4">
            <h3 className="font-heading text-2xl text-slate-900">Prioritized Reconciliation Worklist</h3>
            <p className="mt-1 text-sm text-slate-600">
              Cases are sorted by priority, at-risk dollars, and aging to surface immediate
              reconciliation action.
            </p>
          </div>

          <ExceptionWorklist
            cases={cases}
            selectedCaseId={selectedCase?.id ?? null}
            onSelectCase={onSelectCase}
          />
        </div>

        <CaseDetailPanel caseItem={selectedCase} />
      </section>
    </div>
  )
}

interface ReconciliationFactProps {
  icon: ReactNode
  label: string
  value: string
}

function ReconciliationFact({ icon, label, value }: ReconciliationFactProps) {
  return (
    <article className="rounded-xl border border-cyan-800 bg-cyan-950/40 p-3">
      <div className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-cyan-700/60 text-cyan-50">
        {icon}
      </div>
      <p className="mt-2 text-xs uppercase tracking-[0.12em] text-cyan-300">{label}</p>
      <p className="mt-1 text-sm text-cyan-50">{value}</p>
    </article>
  )
}

interface QueuePressureItem {
  queue: string
  caseCount: number
  dollarsAtRisk: number
}

function buildQueuePressure(cases: RevenueIntegrityCase[]): QueuePressureItem[] {
  const queueMap = new Map<string, QueuePressureItem>()

  for (const caseItem of cases) {
    const existing = queueMap.get(caseItem.queue)

    if (!existing) {
      queueMap.set(caseItem.queue, {
        queue: caseItem.queue,
        caseCount: 1,
        dollarsAtRisk: caseItem.dollarsAtRisk,
      })
      continue
    }

    existing.caseCount += 1
    existing.dollarsAtRisk += caseItem.dollarsAtRisk
  }

  return Array.from(queueMap.values()).sort((first, second) => {
    if (second.dollarsAtRisk !== first.dollarsAtRisk) {
      return second.dollarsAtRisk - first.dollarsAtRisk
    }

    return second.caseCount - first.caseCount
  })
}
