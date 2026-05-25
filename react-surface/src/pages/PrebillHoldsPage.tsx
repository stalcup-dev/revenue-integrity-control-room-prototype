import { Clock3, FileWarning, LockKeyhole, ShieldCheck, SlidersHorizontal } from 'lucide-react'
import type { ReactNode } from 'react'

import { CaseDetailPanel } from '../components/CaseDetailPanel'
import { ExceptionWorklist } from '../components/ExceptionWorklist'
import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface PrebillHoldsMetrics {
  activeHolds: number
  dollarsHeldPreFinalBill: number
  averageHoldAging: number
  overSevenDayHoldRate: number
  overSevenDayHoldCount: number
}

interface PrebillHoldsPageProps {
  cases: RevenueIntegrityCase[]
  selectedCaseId: string | null
  onSelectCase: (caseId: string) => void
  metrics: PrebillHoldsMetrics
}

export function PrebillHoldsPage({
  cases,
  selectedCaseId,
  onSelectCase,
  metrics,
}: PrebillHoldsPageProps) {
  const selectedCase = cases.find((caseItem) => caseItem.id === selectedCaseId) ?? cases[0] ?? null
  const ownerPressure = buildOwnerPressure(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-amber-200/60 bg-amber-950 text-amber-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(251,191,36,0.28),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(249,115,22,0.24),transparent_40%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-200">
            Modifiers / Edits / Prebill Holds
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which pre-final-bill blockers should be cleared first to prevent avoidable delay
            and timing-window loss?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-amber-100">
            Deterministic prebill governance view for coding and claim-edit blockers requiring
            fast owner action before final billing.
          </p>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <PrebillFact
              icon={<LockKeyhole size={15} />}
              label="Hold clarity"
              value="One current blocker determines owner queue and release path."
            />
            <PrebillFact
              icon={<ShieldCheck size={15} />}
              label="Deterministic controls"
              value="Expected performed activity is already present; blocker is prebill execution."
            />
            <PrebillFact
              icon={<SlidersHorizontal size={15} />}
              label="Operational decision"
              value="Escalate, clear edit, and release to final bill before aging drifts."
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
        <MetricCard
          label="Active prebill holds"
          value={formatNumber(metrics.activeHolds)}
          note="Filtered prebill and coding hold cases currently in active resolution."
          icon={<LockKeyhole size={18} />}
        />
        <MetricCard
          label="Dollars held pre-final bill"
          value={formatCurrency(metrics.dollarsHeldPreFinalBill)}
          note="At-risk dollars tied to active holds before final billing release."
          tone="warning"
          icon={<FileWarning size={18} />}
        />
        <MetricCard
          label="Average hold aging"
          value={`${formatNumber(metrics.averageHoldAging)} days`}
          note="Mean age of active prebill blockers in the filtered hold lane."
          icon={<Clock3 size={18} />}
        />
        <MetricCard
          label=">7 day hold rate"
          value={`${formatNumber(metrics.overSevenDayHoldRate)}%`}
          note={`${formatNumber(metrics.overSevenDayHoldCount)} active holds exceed seven days.`}
          tone="warning"
          icon={<Clock3 size={18} />}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {ownerPressure.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600 lg:col-span-3">
            No prebill owner pressure is visible for current filters.
          </div>
        ) : (
          ownerPressure.map((item) => (
            <article
              key={item.owner}
              className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Owner lane</p>
              <h3 className="mt-1 text-base font-semibold text-slate-900">{item.owner}</h3>
              <p className="mt-2 text-sm text-slate-600">
                {formatNumber(item.caseCount)} holds | {formatCurrency(item.dollarsAtRisk)} at
                risk
              </p>
            </article>
          ))
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-4">
            <h3 className="font-heading text-2xl text-slate-900">Prioritized Prebill Hold Worklist</h3>
            <p className="mt-1 text-sm text-slate-600">
              Review modifier/edit and coding blockers driving delayed billing release.
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

interface PrebillFactProps {
  icon: ReactNode
  label: string
  value: string
}

function PrebillFact({ icon, label, value }: PrebillFactProps) {
  return (
    <article className="rounded-xl border border-amber-900 bg-amber-950/35 p-3">
      <div className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-amber-700/70 text-amber-50">
        {icon}
      </div>
      <p className="mt-2 text-xs uppercase tracking-[0.12em] text-amber-300">{label}</p>
      <p className="mt-1 text-sm text-amber-50">{value}</p>
    </article>
  )
}

interface OwnerPressureItem {
  owner: string
  caseCount: number
  dollarsAtRisk: number
}

function buildOwnerPressure(cases: RevenueIntegrityCase[]): OwnerPressureItem[] {
  const ownerMap = new Map<string, OwnerPressureItem>()

  for (const caseItem of cases) {
    const existing = ownerMap.get(caseItem.owner)

    if (!existing) {
      ownerMap.set(caseItem.owner, {
        owner: caseItem.owner,
        caseCount: 1,
        dollarsAtRisk: caseItem.dollarsAtRisk,
      })
      continue
    }

    existing.caseCount += 1
    existing.dollarsAtRisk += caseItem.dollarsAtRisk
  }

  return Array.from(ownerMap.values()).sort((first, second) => {
    if (second.dollarsAtRisk !== first.dollarsAtRisk) {
      return second.dollarsAtRisk - first.dollarsAtRisk
    }

    return second.caseCount - first.caseCount
  })
}
