import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency } from '../lib/formatters'
import { EvidenceTrace } from './EvidenceTrace'

interface CaseDetailPanelProps {
  caseItem: RevenueIntegrityCase | null
}

export function CaseDetailPanel({ caseItem }: CaseDetailPanelProps) {
  if (!caseItem) {
    return (
      <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
        <h3 className="font-heading text-xl text-slate-900">Select a case</h3>
        <p className="mt-2 text-sm text-slate-600">
          Choose a case from the prioritized worklist to review failed control evidence,
          owner, aging, and recommended next action.
        </p>
      </section>
    )
  }

  return (
    <section className="space-y-4">
      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-slate-300 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700">
            {caseItem.id}
          </span>
          <span className="rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
            {caseItem.issueDomain}
          </span>
        </div>

        <h2 className="font-heading mt-3 text-2xl text-slate-900">{caseItem.department}</h2>
        <p className="mt-1 text-sm text-slate-600">
          Service line: <span className="font-medium text-slate-700">{caseItem.serviceLine}</span>
        </p>

        <dl className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <KeyValue label="Current queue" value={caseItem.queue} />
          <KeyValue label="Current owner" value={caseItem.owner} />
          <KeyValue label="Primary blocker" value={caseItem.currentPrimaryBlocker} />
          <KeyValue label="Root cause mechanism" value={caseItem.rootCauseMechanism} />
          <KeyValue
            label="Recoverability status"
            value={caseItem.recoverabilityStatus}
            emphasis
          />
          <KeyValue label="Blocker aging" value={`${caseItem.agingDays} days`} />
        </dl>
      </article>

      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="font-heading text-xl text-slate-900">Recoverability and Financial View</h3>
        <dl className="mt-4 grid gap-3 sm:grid-cols-3">
          <ValueTile label="Dollars at risk" value={formatCurrency(caseItem.dollarsAtRisk)} />
          <ValueTile
            label="Recoverable now"
            value={formatCurrency(caseItem.dollarsRecoverableNow)}
          />
          <ValueTile
            label="Already lost"
            value={formatCurrency(caseItem.dollarsAlreadyLost)}
          />
        </dl>
      </article>

      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="font-heading text-xl text-slate-900">Failed Control Narrative</h3>
        <p className="mt-2 text-sm text-slate-700">{caseItem.controlFailureNarrative}</p>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <NarrativeBlock title="Expected summary" value={caseItem.expectedSummary} />
          <NarrativeBlock title="Actual summary" value={caseItem.actualSummary} />
        </div>

        <NarrativeBlock
          title="Recommended next action"
          value={caseItem.recommendedAction}
          className="mt-4"
        />

        {caseItem.suppressionNote ? (
          <div className="mt-4 rounded-xl border border-violet-200 bg-violet-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-violet-700">
              Suppression note
            </p>
            <p className="mt-1 text-sm text-violet-800">{caseItem.suppressionNote}</p>
          </div>
        ) : null}
      </article>

      <EvidenceTrace items={caseItem.evidenceTrace} />
    </section>
  )
}

interface KeyValueProps {
  label: string
  value: string
  emphasis?: boolean
}

function KeyValue({ label, value, emphasis = false }: KeyValueProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</dt>
      <dd className={['mt-1 text-sm', emphasis ? 'font-semibold text-emerald-700' : 'text-slate-800'].join(' ')}>
        {value}
      </dd>
    </div>
  )
}

interface ValueTileProps {
  label: string
  value: string
}

function ValueTile({ label, value }: ValueTileProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-900">{value}</p>
    </div>
  )
}

interface NarrativeBlockProps {
  title: string
  value: string
  className?: string
}

function NarrativeBlock({ title, value, className }: NarrativeBlockProps) {
  return (
    <section className={className}>
      <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
      <p className="mt-1 text-sm text-slate-700">{value}</p>
    </section>
  )
}
