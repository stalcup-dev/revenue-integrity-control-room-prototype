import {
  BadgeCheck,
  CalendarClock,
  FileText,
  ShieldAlert,
  Sparkles,
  TriangleAlert,
} from 'lucide-react'

import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'
import { computeDecisionPackFreshnessView } from '../lib/decisionPackFreshness'

interface DecisionPackFreshnessLensPageProps {
  cases: RevenueIntegrityCase[]
}

export function DecisionPackFreshnessLensPage({
  cases,
}: DecisionPackFreshnessLensPageProps) {
  const view = computeDecisionPackFreshnessView(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-sky-900/20 bg-sky-950 text-sky-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(96,165,250,0.34),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.22),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-200">
            Decision Pack Freshness Lens
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Is the decision pack being read as a current deterministic snapshot, or as stale
            validation proof?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-sky-100">
            Runtime lens only. This route surfaces validation-state framing, current-slice proof,
            and what-if caveats without changing the decision pack logic itself.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="flex flex-wrap items-center gap-3">
          <BadgeCheck className="text-emerald-600" size={18} />
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              Build snapshot
            </p>
            <p className="text-sm text-slate-700">Build timestamp (UTC): {view.buildTimestamp}</p>
            <p className="mt-1 text-sm font-semibold text-slate-900">{view.validationStatus}</p>
          </div>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {view.disclaimerLines.map((line) => (
            <div key={line} className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
              {line}
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        {view.metrics.map((metric) => (
          <MetricCard
            key={metric.label}
            label={metric.label}
            value={metric.value}
            note={metric.note}
            tone={metric.label.includes('already lost') ? 'warning' : metric.label.includes('Top owner queue') ? 'highlight' : 'default'}
            icon={<FileText size={18} />}
          />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <h3 className="font-heading text-2xl text-slate-900">Current Summary Signal</h3>
          <p className="mt-2 text-sm text-slate-700">{view.currentSummarySignal}</p>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <FreshnessTile label="Top owner queue" value={view.topOwnerQueue} />
            <FreshnessTile label="Top service line" value={view.topServiceLine} />
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              Explicit caveats retained
            </p>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              <li>Scenario results are what-if estimates, not forecasts.</li>
              <li>Denial signals remain downstream evidence only.</li>
              <li>Validation status should be read exactly as shown from the current run manifest.</li>
            </ul>
          </div>
        </article>

        <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <h3 className="font-heading text-2xl text-slate-900">Decision Pack Snapshot Framing</h3>
          <p className="mt-2 text-sm text-slate-600">
            Preferred wording keeps the memo bounded to the current filtered slice and current
            build state.
          </p>

          <div className="mt-4 space-y-3 text-sm text-slate-700">
            <RuleRow
              label="Validation status"
              value="Validation status from current run manifest: Passed"
            />
            <RuleRow
              label="Recoverability phrasing"
              value="Recoverable now vs already lost in the current governed slice"
            />
            <RuleRow
              label="Queue phrasing"
              value="Top owner queue in the current slice"
            />
            <RuleRow
              label="Service-line phrasing"
              value="Top service line / department in the current slice"
            />
            <RuleRow
              label="Control story phrasing"
              value={view.currentSummarySignal}
            />
          </div>
        </article>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Scenario Snapshot</h3>
          <p className="mt-1 text-sm text-slate-600">
            Scenario values are intentionally framed as capped what-if estimates and should not be
            presented as forecasts.
          </p>
        </header>

        <div className="mt-4 grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
          <MetricCard
            label="Projected backlog reduction"
            value={formatNumber(view.scenarioSnapshot.projectedBacklogReduction)}
            note="What-if estimate for the current governed slice."
            icon={<Sparkles size={18} />}
          />
          <MetricCard
            label="Projected SLA improvement"
            value={`+${formatNumber(view.scenarioSnapshot.projectedSlaImprovementPoints)} pts`}
            note="Scenario Lab v0 default lever target estimate."
            icon={<CalendarClock size={18} />}
          />
          <MetricCard
            label="Projected recoverable dollar lift"
            value={formatCurrency(view.scenarioSnapshot.projectedRecoverableDollarLift)}
            note="Capped what-if estimate only."
            tone="highlight"
            icon={<TriangleAlert size={18} />}
          />
          <MetricCard
            label="90-day impact estimate"
            value={formatCurrency(view.scenarioSnapshot.ninetyDayImpactEstimate)}
            note="Roll-forward what-if view for reviewer framing."
            icon={<ShieldAlert size={18} />}
          />
        </div>
      </section>

      <section className="rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900 shadow-sm">
        Current deterministic snapshot only. If the run manifest is not current, this page should
        be read as a snapshot sample rather than validation proof.
      </section>
    </div>
  )
}

interface FreshnessTileProps {
  label: string
  value: string
}

function FreshnessTile({ label, value }: FreshnessTileProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
    </div>
  )
}

interface RuleRowProps {
  label: string
  value: string
}

function RuleRow({ label, value }: RuleRowProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-800">{value}</p>
    </div>
  )
}
