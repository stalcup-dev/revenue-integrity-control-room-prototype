import type { InterventionTrackingItem } from '../data/types'

interface InterventionCardProps {
  item: InterventionTrackingItem
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

export function InterventionCard({ item }: InterventionCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
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

      <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
        <div className="rounded-lg bg-slate-50 p-2">
          <dt className="text-xs uppercase tracking-[0.1em] text-slate-500">Checkpoint</dt>
          <dd className={['mt-1 font-semibold', checkpointClassName[item.checkpointStatus]].join(' ')}>
            {item.checkpointStatus}
          </dd>
        </div>
        <div className="rounded-lg bg-slate-50 p-2">
          <dt className="text-xs uppercase tracking-[0.1em] text-slate-500">
            Target completion
          </dt>
          <dd className="mt-1 font-semibold text-slate-800">{item.targetCompletionDate}</dd>
        </div>
      </dl>

      <p className="mt-3 text-sm text-slate-700">
        <span className="font-semibold">Baseline:</span> {item.baselineMetric}
      </p>
      <p className="mt-1 text-sm text-slate-700">
        <span className="font-semibold">Current:</span> {item.currentMetric}
      </p>
      <p className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{item.validationNote}</p>
    </article>
  )
}
