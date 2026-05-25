import { Activity, Clock3, Gauge, LineChart as LineChartIcon, ShieldCheck } from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { MetricCard } from '../components/MetricCard'
import type { GlobalFiltersState } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'
import { computeDocumentationTrendView } from '../lib/documentationTrend'

interface DocumentationTrendRealismPageProps {
  filters: GlobalFiltersState
}

export function DocumentationTrendRealismPage({ filters }: DocumentationTrendRealismPageProps) {
  const view = computeDocumentationTrendView(filters)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-900/20 bg-cyan-950 text-cyan-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.35),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(16,185,129,0.24),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">
            Documentation Trend Realism
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Is documentation queue movement behaving like real operational entry/exit flow, or
            are we showing a cosmetically flat trend?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-cyan-100">
            Queue-history-driven trend only. Latest point must match current backlog and dollars
            for the selected slice.
          </p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Current backlog"
          value={formatNumber(view.currentBacklog)}
          note="Latest unsupported documentation backlog for the selected department slice."
          icon={<Gauge size={18} />}
        />
        <MetricCard
          label="Current documentation dollars open"
          value={formatCurrency(view.currentDollarsOpen)}
          note="Latest dollars still open under documentation support blockers."
          tone="warning"
          icon={<LineChartIcon size={18} />}
        />
        <MetricCard
          label="30-day backlog net change"
          value={formatNetChange(view.netThirtyDayBacklogChange)}
          note="Latest backlog minus first backlog point in this trend window."
          icon={<Activity size={18} />}
        />
        <MetricCard
          label="Plateau duration"
          value={`${formatNumber(view.plateauWeeks)} weeks`}
          note="Consecutive trailing weeks with unchanged backlog count."
          icon={<Clock3 size={18} />}
        />
        <MetricCard
          label="Late re-entry signal"
          value={view.hasLateReentrySignal ? 'Present' : 'Not present'}
          note="True when backlog re-enters after an earlier period of workdown."
          tone={view.hasLateReentrySignal ? 'highlight' : 'default'}
          icon={<ShieldCheck size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Unsupported Charge Trend</h3>
          <p className="mt-1 text-sm text-slate-600">
            Documentation backlog and dollars are aggregated directly from queue-history snapshots
            for the selected department filter state.
          </p>
        </header>

        {view.points.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No trend points are available for this department filter selection.
          </div>
        ) : (
          <div className="mt-4 h-72 rounded-xl border border-slate-200 bg-slate-50 p-3">
            <ResponsiveContainer width="100%" height="100%" minWidth={320} minHeight={250}>
              <LineChart data={view.points} margin={{ top: 12, right: 12, left: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="date" stroke="#475569" tick={{ fill: '#475569', fontSize: 11 }} />
                <YAxis yAxisId="backlog" stroke="#0369a1" tick={{ fill: '#0369a1', fontSize: 11 }} />
                <YAxis
                  yAxisId="dollars"
                  orientation="right"
                  stroke="#0f766e"
                  tick={{ fill: '#0f766e', fontSize: 11 }}
                />
                <Tooltip
                  formatter={(value, name) => {
                    if (name === 'dollarsOpen') {
                      return [formatCurrency(Number(value)), 'Documentation dollars open']
                    }

                    return [formatNumber(Number(value)), 'Backlog']
                  }}
                  labelFormatter={(label) => `Week of ${label}`}
                />
                <Line
                  yAxisId="backlog"
                  type="monotone"
                  dataKey="backlog"
                  stroke="#0284c7"
                  strokeWidth={3}
                  dot={{ r: 3, fill: '#0284c7' }}
                  activeDot={{ r: 5 }}
                  name="backlog"
                />
                <Line
                  yAxisId="dollars"
                  type="monotone"
                  dataKey="dollarsOpen"
                  stroke="#0d9488"
                  strokeWidth={3}
                  dot={{ r: 3, fill: '#0d9488' }}
                  activeDot={{ r: 5 }}
                  name="dollarsOpen"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Trend Decomposition</h3>
          <p className="mt-1 text-sm text-slate-600">
            Week-level entry and resolution signals keep the trend grounded in realistic queue
            behavior.
          </p>
        </header>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <th className="border-b border-slate-200 px-3 py-2">Week</th>
                <th className="border-b border-slate-200 px-3 py-2">Entries</th>
                <th className="border-b border-slate-200 px-3 py-2">Resolved</th>
                <th className="border-b border-slate-200 px-3 py-2">Net change</th>
                <th className="border-b border-slate-200 px-3 py-2">Backlog</th>
                <th className="border-b border-slate-200 px-3 py-2">Dollars open</th>
              </tr>
            </thead>
            <tbody>
              {view.points.map((point) => (
                <tr key={point.date} className="text-slate-700">
                  <td className="border-b border-slate-100 px-3 py-2">{point.date}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{formatNumber(point.entries)}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{formatNumber(point.resolved)}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{formatNetChange(point.netChange)}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{formatNumber(point.backlog)}</td>
                  <td className="border-b border-slate-100 px-3 py-2">
                    {formatCurrency(point.dollarsOpen)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-cyan-200 bg-cyan-50 p-4 text-sm text-cyan-900 shadow-sm">
        Trend realism guardrails: latest point equals the current slice state, queue movement is
        driven by observed entry/exit deltas, and flat lines appear only when the backlog truly
        stabilizes.
      </section>
    </div>
  )
}

function formatNetChange(value: number): string {
  if (value > 0) {
    return `+${formatNumber(value)}`
  }

  return formatNumber(value)
}
