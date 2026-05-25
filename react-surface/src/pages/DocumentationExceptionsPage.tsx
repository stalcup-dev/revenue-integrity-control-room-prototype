import { ClipboardCheck, FileWarning, LifeBuoy, NotebookPen, ShieldAlert } from 'lucide-react'
import type { ReactNode } from 'react'

import { CaseDetailPanel } from '../components/CaseDetailPanel'
import { ExceptionWorklist } from '../components/ExceptionWorklist'
import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface DocumentationExceptionsMetrics {
  documentationExceptionCases: number
  unsupportedChargePressure: number
  averageExceptionAging: number
  activeDocumentationPendingRate: number
  activeDocumentationPendingCount: number
  postWindowDocumentationLoss: number
}

interface DocumentationExceptionsPageProps {
  cases: RevenueIntegrityCase[]
  selectedCaseId: string | null
  onSelectCase: (caseId: string) => void
  metrics: DocumentationExceptionsMetrics
}

export function DocumentationExceptionsPage({
  cases,
  selectedCaseId,
  onSelectCase,
  metrics,
}: DocumentationExceptionsPageProps) {
  const selectedCase = cases.find((caseItem) => caseItem.id === selectedCaseId) ?? cases[0] ?? null
  const serviceLinePressure = buildServiceLinePressure(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-teal-200/70 bg-teal-950 text-teal-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(45,212,191,0.26),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.2),transparent_40%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-200">
            Documentation Support Exceptions
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which unsupported documentation gaps are holding valid outpatient facility charges
            and where has delay already created avoidable loss?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-teal-100">
            Deterministic documentation support view connecting performed activity to required
            support elements, current blocker, owner, and recoverability status.
          </p>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <DocumentationFact
              icon={<ClipboardCheck size={15} />}
              label="Support requirements"
              value="Performed activity is present, but billable support is incomplete or late."
            />
            <DocumentationFact
              icon={<ShieldAlert size={15} />}
              label="Risk framing"
              value="Gaps can be recoverable pre-final bill or become post-window loss."
            />
            <DocumentationFact
              icon={<NotebookPen size={15} />}
              label="Owner action"
              value="Close support documentation defects and enforce final-bill guardrails."
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
        <MetricCard
          label="Documentation exception cases"
          value={formatNumber(metrics.documentationExceptionCases)}
          note="Filtered routed cases in documentation-support exception scope."
          icon={<NotebookPen size={18} />}
        />
        <MetricCard
          label="Unsupported charge pressure"
          value={formatCurrency(metrics.unsupportedChargePressure)}
          note="At-risk dollars attached to unresolved or recently failed support validation."
          tone="warning"
          icon={<FileWarning size={18} />}
        />
        <MetricCard
          label="Average exception aging"
          value={`${formatNumber(metrics.averageExceptionAging)} days`}
          note="Mean blocker aging across documentation-support exception cases."
          icon={<LifeBuoy size={18} />}
        />
        <MetricCard
          label="Active documentation pending rate"
          value={`${formatNumber(metrics.activeDocumentationPendingRate)}%`}
          note={`${formatNumber(metrics.activeDocumentationPendingCount)} cases currently pending documentation completion.`}
          tone="warning"
          icon={<ClipboardCheck size={18} />}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <article className="rounded-2xl border border-rose-200 bg-rose-50 p-4 shadow-sm lg:col-span-1">
          <p className="text-xs uppercase tracking-[0.12em] text-rose-600">
            Post-window documentation loss
          </p>
          <p className="mt-2 text-2xl font-semibold text-rose-700">
            {formatCurrency(metrics.postWindowDocumentationLoss)}
          </p>
          <p className="mt-2 text-sm text-rose-700/90">
            Financial exposure already lost due to documentation completion beyond the recovery
            window.
          </p>
        </article>

        {serviceLinePressure.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600 lg:col-span-2">
            No documentation service-line pressure is visible for current filters.
          </div>
        ) : (
          <div className="grid gap-4 lg:col-span-2 lg:grid-cols-2">
            {serviceLinePressure.map((item) => (
              <article
                key={item.serviceLine}
                className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
              >
                <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Service line</p>
                <h3 className="mt-1 text-base font-semibold text-slate-900">{item.serviceLine}</h3>
                <p className="mt-2 text-sm text-slate-600">
                  {formatNumber(item.caseCount)} cases | {formatCurrency(item.dollarsAtRisk)} at
                  risk
                </p>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-4">
            <h3 className="font-heading text-2xl text-slate-900">
              Prioritized Documentation Exception Worklist
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Select a case to inspect support gaps, failed control narrative, and required next
              documentation action.
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

interface DocumentationFactProps {
  icon: ReactNode
  label: string
  value: string
}

function DocumentationFact({ icon, label, value }: DocumentationFactProps) {
  return (
    <article className="rounded-xl border border-teal-900 bg-teal-950/35 p-3">
      <div className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-teal-700/70 text-teal-50">
        {icon}
      </div>
      <p className="mt-2 text-xs uppercase tracking-[0.12em] text-teal-300">{label}</p>
      <p className="mt-1 text-sm text-teal-50">{value}</p>
    </article>
  )
}

interface ServiceLinePressureItem {
  serviceLine: string
  caseCount: number
  dollarsAtRisk: number
}

function buildServiceLinePressure(cases: RevenueIntegrityCase[]): ServiceLinePressureItem[] {
  const serviceLineMap = new Map<string, ServiceLinePressureItem>()

  for (const caseItem of cases) {
    const existing = serviceLineMap.get(caseItem.serviceLine)

    if (!existing) {
      serviceLineMap.set(caseItem.serviceLine, {
        serviceLine: caseItem.serviceLine,
        caseCount: 1,
        dollarsAtRisk: caseItem.dollarsAtRisk,
      })
      continue
    }

    existing.caseCount += 1
    existing.dollarsAtRisk += caseItem.dollarsAtRisk
  }

  return Array.from(serviceLineMap.values()).sort((first, second) => {
    if (second.dollarsAtRisk !== first.dollarsAtRisk) {
      return second.dollarsAtRisk - first.dollarsAtRisk
    }

    return second.caseCount - first.caseCount
  })
}
