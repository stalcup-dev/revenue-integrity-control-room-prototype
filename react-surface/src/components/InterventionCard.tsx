import type { InterventionTrackingItem } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface InterventionCardProps {
  item: InterventionTrackingItem
  impactSummary?: {
    affectedCases: number
    dollarsAtRisk: number
    recoverableNow: number
    averageAgingDays: number
  }
  impactDelta?: {
    dollarsAtRisk: number
    caseCount: number
  }
  isSelected?: boolean
  onViewImpactedCases?: () => void
}

const recommendationClassName: Record<InterventionTrackingItem['recommendation'], string> = {
  Hold: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  Expand: 'border-blue-200 bg-blue-50 text-blue-700',
  Revise: 'border-amber-200 bg-amber-50 text-amber-700',
}

const checkpointClassName: Record<InterventionTrackingItem['checkpointStatus'], string> = {
  'Not started': 'text-slate-600',
  'In progress': 'text-blue-700',
  Validated: 'text-emerald-700',
  'Needs revision': 'text-amber-700',
}

export function InterventionCard({
  item,
  impactSummary,
  impactDelta,
  isSelected = false,
  onViewImpactedCases,
}: InterventionCardProps) {
  return (
    <article
      className={[
        'rounded-2xl border bg-white p-4 shadow-sm transition',
        isSelected ? 'border-indigo-300 ring-1 ring-indigo-200' : 'border-slate-200',
      ].join(' ')}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h4 className="text-base font-semibold text-slate-900">{item.title}</h4>
          <p className="mt-1 text-sm text-slate-600">Owner: {item.owner}</p>
        </div>
        <span
          className={[
            'rounded-full border px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.1em]',
            recommendationClassName[item.recommendation],
          ].join(' ')}
        >
          {item.recommendation}
        </span>
      </div>

      <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
        <div className="rounded-lg bg-slate-50 p-2">
          <p className="text-xs uppercase tracking-[0.1em] text-slate-500">Checkpoint</p>
          <p className={['mt-1 font-semibold', checkpointClassName[item.checkpointStatus]].join(' ')}>
            {item.checkpointStatus}
          </p>
        </div>
        <div className="rounded-lg bg-slate-50 p-2">
          <p className="text-xs uppercase tracking-[0.1em] text-slate-500">
            Target completion
          </p>
          <p className="mt-1 font-semibold text-slate-800">{item.targetCompletionDate}</p>
        </div>
      </div>

      <p className="mt-3 text-sm text-slate-700">
        <span className="font-semibold">Baseline:</span> {item.baselineMetric}
      </p>
      <p className="mt-1 text-sm text-slate-700">
        <span className="font-semibold">Current:</span> {item.currentMetric}
      </p>

      {impactSummary ? (
        <div className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
          <div className="rounded-lg bg-slate-50 p-2">
            <p className="text-xs uppercase tracking-[0.1em] text-slate-500">Impacted cases</p>
            <p className="mt-1 font-semibold text-slate-800">
              {formatNumber(impactSummary.affectedCases)}
            </p>
          </div>
          <div className="rounded-lg bg-slate-50 p-2">
            <p className="text-xs uppercase tracking-[0.1em] text-slate-500">Dollars at risk</p>
            <p className="mt-1 font-semibold text-slate-800">
              {formatCurrency(impactSummary.dollarsAtRisk)}
            </p>
          </div>
          <div className="rounded-lg bg-slate-50 p-2">
            <p className="text-xs uppercase tracking-[0.1em] text-slate-500">Recoverable now</p>
            <p className="mt-1 font-semibold text-slate-800">
              {formatCurrency(impactSummary.recoverableNow)}
            </p>
          </div>
          <div className="rounded-lg bg-slate-50 p-2">
            <p className="text-xs uppercase tracking-[0.1em] text-slate-500">Average aging</p>
            <p className="mt-1 font-semibold text-slate-800">
              {formatNumber(impactSummary.averageAgingDays)} days
            </p>
          </div>
        </div>
      ) : null}

      {impactDelta ? (
        <p className="mt-3 text-sm text-slate-700">
          <span className="font-semibold">Impact delta:</span>{' '}
          {impactDelta.dollarsAtRisk === 0
            ? 'No dollar-risk change from baseline.'
            : `${impactDelta.dollarsAtRisk < 0 ? 'Down' : 'Up'} ${formatCurrency(Math.abs(impactDelta.dollarsAtRisk))} vs baseline`}
          {` | Cases: ${impactDelta.caseCount === 0 ? 'no change' : impactDelta.caseCount < 0 ? `${Math.abs(impactDelta.caseCount)} fewer` : `${impactDelta.caseCount} more`}`}
        </p>
      ) : null}

      <p className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{item.validationNote}</p>

      {onViewImpactedCases ? (
        <button
          type="button"
          onClick={onViewImpactedCases}
          className="mt-3 rounded-xl border border-indigo-200 bg-indigo-50 px-3 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-indigo-700 transition hover:border-indigo-300 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-300"
          aria-label={`View impacted cases for ${item.title}`}
        >
          View impacted cases
        </button>
      ) : null}
    </article>
  )
}
