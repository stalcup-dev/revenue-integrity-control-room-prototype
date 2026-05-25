import {
  AlertOctagon,
  BarChart3,
  Clock3,
  Coins,
  FileCheck2,
  Stethoscope,
  UsersRound,
} from 'lucide-react'
import type { ReactNode } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { CaseDetailPanel } from '../components/CaseDetailPanel'
import { ExceptionWorklist } from '../components/ExceptionWorklist'
import { InterventionCard } from '../components/InterventionCard'
import { MetricCard } from '../components/MetricCard'
import type { InterventionTrackingItem, RevenueIntegrityCase } from '../data/types'
import type { selectFeaturedStory } from '../lib/featuredStory'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface SummaryMetrics {
  dollarsAtRisk: number
  recoverableNow: number
  averageAging: number
  activeCases: number
}

interface ControlRoomSummaryPageProps {
  filteredCases: RevenueIntegrityCase[]
  selectedCaseId: string | null
  onSelectCase: (caseId: string) => void
  interventions: InterventionTrackingItem[]
  metrics: SummaryMetrics
  featuredStory: ReturnType<typeof selectFeaturedStory>
}

export function ControlRoomSummaryPage({
  filteredCases,
  selectedCaseId,
  onSelectCase,
  interventions,
  metrics,
  featuredStory,
}: ControlRoomSummaryPageProps) {
  const selectedCase =
    filteredCases.find((caseItem) => caseItem.id === selectedCaseId) ?? filteredCases[0] ?? null
  const departmentPressure = buildDepartmentPressure(filteredCases)
  const chartHeight = Math.max(250, departmentPressure.length * 56)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-slate-900/10 bg-slate-900 text-slate-100 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(96,165,250,0.35),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(16,185,129,0.3),transparent_40%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
            Control Room Summary
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which outpatient queues should leadership work first to reduce recoverable
            revenue leakage and compliance risk?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-slate-200">
            Deterministic owner-routed exception management focused on current blocker,
            recoverability, aging, and next action across infusion, radiology/IR, and OR
            procedural workflows.
          </p>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <HeroFact
              icon={<AlertOctagon size={15} />}
              label="Failed control visibility"
              value="Expected vs actual evidence trace"
            />
            <HeroFact
              icon={<UsersRound size={15} />}
              label="Owner accountability"
              value="Single current blocker with routed queue owner"
            />
            <HeroFact
              icon={<FileCheck2 size={15} />}
              label="Action expectation"
              value="Hold, expand, or revise intervention governance"
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
        <MetricCard
          label="Dollars at risk"
          value={formatCurrency(metrics.dollarsAtRisk)}
          note="Active filtered case exposure under current queue pressure."
          tone="warning"
          icon={<Coins size={18} />}
        />
        <MetricCard
          label="Recoverable now"
          value={formatCurrency(metrics.recoverableNow)}
          note="Amount still actionable before timing windows close."
          tone="highlight"
          icon={<Stethoscope size={18} />}
        />
        <MetricCard
          label="Average blocker aging"
          value={`${formatNumber(metrics.averageAging)} days`}
          note="Mean age of the current primary blocker for filtered cases."
          icon={<Clock3 size={18} />}
        />
        <MetricCard
          label="Active cases"
          value={formatNumber(metrics.activeCases)}
          note="Filtered routed exceptions currently visible to leadership."
          icon={<UsersRound size={18} />}
        />
      </section>

      {featuredStory ? (
        <section className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 shadow-sm sm:p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-700">
                Featured deterministic story
              </p>
              <h3 className="font-heading mt-1 text-2xl text-emerald-900">
                {featuredStory.caseId}
              </h3>
              <p className="mt-1 text-sm text-emerald-900/90">{featuredStory.rationale}</p>
            </div>
            <button
              type="button"
              onClick={() => onSelectCase(featuredStory.caseId)}
              className="rounded-xl border border-emerald-300 bg-white px-3 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-emerald-700 transition hover:border-emerald-400 hover:bg-emerald-100 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              Focus featured case
            </button>
          </div>
        </section>
      ) : null}

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h3 className="font-heading text-2xl text-slate-900">Department Pressure View</h3>
            <p className="mt-1 text-sm text-slate-600">
              Compare total dollars at risk versus immediately recoverable dollars by
              department under current filters.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-2 text-slate-700">
            <BarChart3 size={18} aria-hidden="true" />
          </div>
        </header>

        {departmentPressure.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No department pressure data is available for the current filter selection.
          </div>
        ) : (
          <div style={{ height: chartHeight }}>
            <ResponsiveContainer width="100%" height="100%" minWidth={320} minHeight={250}>
              <BarChart data={departmentPressure} layout="vertical" margin={{ top: 8, right: 12, bottom: 8, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fill: '#475569', fontSize: 12 }}
                  tickFormatter={(value) => formatCompactCurrency(value)}
                />
                <YAxis
                  type="category"
                  dataKey="departmentLabel"
                  width={175}
                  tick={{ fill: '#334155', fontSize: 12 }}
                />
                <Tooltip
                  formatter={(value) => formatCurrency(Number(value ?? 0))}
                />
                <Bar
                  dataKey="dollarsAtRisk"
                  name="Dollars at risk"
                  radius={[0, 8, 8, 0]}
                  fill="#f97316"
                  maxBarSize={20}
                />
                <Bar
                  dataKey="dollarsRecoverableNow"
                  name="Recoverable now"
                  radius={[0, 8, 8, 0]}
                  fill="#0ea5e9"
                  maxBarSize={20}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-4">
            <h3 className="font-heading text-2xl text-slate-900">Prioritized Exception Worklist</h3>
            <p className="mt-1 text-sm text-slate-600">
              Select a case to inspect failed control evidence, current owner queue, aging,
              and recoverability.
            </p>
          </div>
          <ExceptionWorklist
            cases={filteredCases}
            selectedCaseId={selectedCase?.id ?? null}
            onSelectCase={onSelectCase}
          />
        </div>

        <CaseDetailPanel caseItem={selectedCase} />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Intervention Follow-through</h3>
          <p className="mt-1 text-sm text-slate-600">
            Governance preview for hold / expand / revise decisions tied to measured
            operating outcomes.
          </p>
        </header>

        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          {interventions.map((item) => (
            <InterventionCard key={item.id} item={item} />
          ))}
        </div>
      </section>
    </div>
  )
}

interface DepartmentPressureRow {
  department: string
  departmentLabel: string
  dollarsAtRisk: number
  dollarsRecoverableNow: number
}

function buildDepartmentPressure(cases: RevenueIntegrityCase[]): DepartmentPressureRow[] {
  const pressureByDepartment = new Map<string, DepartmentPressureRow>()

  for (const caseItem of cases) {
    const existing = pressureByDepartment.get(caseItem.department)

    if (existing) {
      existing.dollarsAtRisk += caseItem.dollarsAtRisk
      existing.dollarsRecoverableNow += caseItem.dollarsRecoverableNow
      continue
    }

    pressureByDepartment.set(caseItem.department, {
      department: caseItem.department,
      departmentLabel: abbreviateDepartment(caseItem.department),
      dollarsAtRisk: caseItem.dollarsAtRisk,
      dollarsRecoverableNow: caseItem.dollarsRecoverableNow,
    })
  }

  return Array.from(pressureByDepartment.values()).sort(
    (first, second) => second.dollarsAtRisk - first.dollarsAtRisk,
  )
}

function abbreviateDepartment(department: string): string {
  if (department === 'Outpatient Infusion / Oncology Infusion') {
    return 'Infusion / Oncology'
  }

  if (department === 'Radiology / Interventional Radiology') {
    return 'Radiology / IR'
  }

  if (department === 'OR / Hospital Outpatient Surgery / Procedural Areas') {
    return 'OR / Outpatient Surgery'
  }

  return department
}

function formatCompactCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

interface HeroFactProps {
  icon: ReactNode
  label: string
  value: string
}

function HeroFact({ icon, label, value }: HeroFactProps) {
  return (
    <article className="rounded-xl border border-slate-700 bg-slate-900/55 p-3">
      <div className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-slate-700/70 text-slate-100">
        {icon}
      </div>
      <p className="mt-2 text-xs uppercase tracking-[0.12em] text-slate-400">{label}</p>
      <p className="mt-1 text-sm text-slate-200">{value}</p>
    </article>
  )
}
