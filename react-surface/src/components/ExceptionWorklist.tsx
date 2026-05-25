import type { Priority, RecoverabilityStatus, RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface ExceptionWorklistProps {
  cases: RevenueIntegrityCase[]
  selectedCaseId: string | null
  onSelectCase: (caseId: string) => void
}

const priorityClassName: Record<Priority, string> = {
  Critical: 'bg-rose-100 text-rose-700 border-rose-200',
  High: 'bg-amber-100 text-amber-700 border-amber-200',
  Medium: 'bg-blue-100 text-blue-700 border-blue-200',
  Low: 'bg-slate-100 text-slate-700 border-slate-200',
}

const recoverabilityClassName: Record<RecoverabilityStatus, string> = {
  'Pre-final-bill recoverable': 'bg-emerald-100 text-emerald-700 border-emerald-200',
  'Post-final-bill recoverable by correction / rebill':
    'bg-cyan-100 text-cyan-700 border-cyan-200',
  'Post-window financially lost': 'bg-rose-100 text-rose-700 border-rose-200',
  'Financially closed but still compliance-relevant':
    'bg-violet-100 text-violet-700 border-violet-200',
}

export function ExceptionWorklist({
  cases,
  selectedCaseId,
  onSelectCase,
}: ExceptionWorklistProps) {
  if (cases.length === 0) {
    return (
      <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-center">
        <h3 className="font-heading text-xl text-slate-900">No cases match current filters</h3>
        <p className="mt-2 text-sm text-slate-600">
          Adjust department, queue, recoverability, or search criteria to resume the
          worklist.
        </p>
      </section>
    )
  }

  return (
    <section className="space-y-3">
      {cases.map((caseItem) => {
        const isSelected = selectedCaseId === caseItem.id

        return (
          <button
            key={caseItem.id}
            type="button"
            onClick={() => onSelectCase(caseItem.id)}
            className={[
              'w-full rounded-2xl border bg-white p-4 text-left shadow-sm transition',
              'focus:outline-none focus:ring-2 focus:ring-blue-300',
              isSelected
                ? 'border-blue-300 ring-1 ring-blue-200'
                : 'border-slate-200 hover:border-slate-300 hover:shadow-md',
            ].join(' ')}
            aria-pressed={isSelected}
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-slate-300 bg-slate-50 px-2.5 py-1 text-xs font-semibold tracking-wide text-slate-700">
                {caseItem.id}
              </span>
              <span
                className={[
                  'rounded-full border px-2.5 py-1 text-xs font-semibold tracking-wide',
                  priorityClassName[caseItem.priority],
                ].join(' ')}
              >
                {caseItem.priority} priority
              </span>
              <span
                className={[
                  'rounded-full border px-2.5 py-1 text-xs font-semibold',
                  recoverabilityClassName[caseItem.recoverabilityStatus],
                ].join(' ')}
              >
                {caseItem.recoverabilityStatus}
              </span>
            </div>

            <p className="mt-3 text-base font-semibold text-slate-900">{caseItem.department}</p>
            <p className="mt-1 text-sm text-slate-600">
              Queue: <span className="font-medium text-slate-700">{caseItem.queue}</span> | Owner:{' '}
              <span className="font-medium text-slate-700">{caseItem.owner}</span>
            </p>
            <p className="mt-2 text-sm text-slate-600">{caseItem.currentPrimaryBlocker}</p>

            <dl className="mt-3 grid grid-cols-3 gap-2 text-sm">
              <div className="rounded-lg bg-slate-50 p-2">
                <dt className="text-xs uppercase tracking-wide text-slate-500">At risk</dt>
                <dd className="font-semibold text-slate-900">
                  {formatCurrency(caseItem.dollarsAtRisk)}
                </dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-2">
                <dt className="text-xs uppercase tracking-wide text-slate-500">Aging</dt>
                <dd className="font-semibold text-slate-900">
                  {formatNumber(caseItem.agingDays)} days
                </dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-2">
                <dt className="text-xs uppercase tracking-wide text-slate-500">
                  Recoverable now
                </dt>
                <dd className="font-semibold text-slate-900">
                  {formatCurrency(caseItem.dollarsRecoverableNow)}
                </dd>
              </div>
            </dl>
          </button>
        )
      })}
    </section>
  )
}
