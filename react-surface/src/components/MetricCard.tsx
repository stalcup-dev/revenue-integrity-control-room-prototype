import type { ReactNode } from 'react'

interface MetricCardProps {
  label: string
  value: string
  note: string
  icon: ReactNode
  tone?: 'default' | 'highlight' | 'warning'
}

const toneClassName: Record<NonNullable<MetricCardProps['tone']>, string> = {
  default: 'border-slate-200 bg-white',
  highlight: 'border-emerald-200 bg-emerald-50/70',
  warning: 'border-amber-200 bg-amber-50/80',
}

export function MetricCard({
  label,
  value,
  note,
  icon,
  tone = 'default',
}: MetricCardProps) {
  return (
    <article
      className={[
        'rounded-2xl border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md',
        toneClassName[tone],
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-600">
            {label}
          </p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{value}</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-2 text-slate-700">
          {icon}
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-600">{note}</p>
    </article>
  )
}
