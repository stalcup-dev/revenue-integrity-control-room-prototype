import { AlertTriangle, Ban, CheckCircle2, PauseCircle } from 'lucide-react'

import type { EvidenceTraceItem } from '../data/types'

interface EvidenceTraceProps {
  items: EvidenceTraceItem[]
}

export function EvidenceTrace({ items }: EvidenceTraceProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="font-heading text-xl text-slate-900">Deterministic Evidence Trace</h3>
      <p className="mt-2 text-sm text-slate-600">
        Documented performed activity to routing decision, including suppression logic when
        applicable.
      </p>

      <ol className="mt-4 space-y-3">
        {items.map((item, index) => {
          const status = resolveStatus(item.status)

          return (
            <li
              key={`${item.step}-${index}`}
              className="rounded-xl border border-slate-200 bg-slate-50 p-3"
            >
              <div className="flex items-start gap-3">
                <span
                  className={[
                    'mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-full border',
                    status.badgeClassName,
                  ].join(' ')}
                  aria-hidden="true"
                >
                  <status.Icon size={14} />
                </span>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{item.step}</p>
                  <p className="mt-1 text-sm text-slate-600">{item.detail}</p>
                </div>
              </div>
            </li>
          )
        })}
      </ol>
    </section>
  )
}

function resolveStatus(status: EvidenceTraceItem['status']) {
  switch (status) {
    case 'complete':
      return {
        Icon: CheckCircle2,
        badgeClassName: 'border-emerald-200 bg-emerald-100 text-emerald-700',
      }
    case 'warning':
      return {
        Icon: AlertTriangle,
        badgeClassName: 'border-amber-200 bg-amber-100 text-amber-700',
      }
    case 'blocked':
      return {
        Icon: Ban,
        badgeClassName: 'border-rose-200 bg-rose-100 text-rose-700',
      }
    case 'suppressed':
      return {
        Icon: PauseCircle,
        badgeClassName: 'border-violet-200 bg-violet-100 text-violet-700',
      }
    default:
      return {
        Icon: AlertTriangle,
        badgeClassName: 'border-slate-200 bg-slate-100 text-slate-700',
      }
  }
}
