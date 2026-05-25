import { AlertTriangle, BookOpenCheck, ClipboardCheck, ShieldCheck, Sparkles } from 'lucide-react'

import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'
import { computeScenarioClaimTighteningLensView } from '../lib/scenarioClaimTighteningLens'

interface ScenarioClaimTighteningLensPageProps {
  cases: RevenueIntegrityCase[]
}

export function ScenarioClaimTighteningLensPage({ cases }: ScenarioClaimTighteningLensPageProps) {
  const view = computeScenarioClaimTighteningLensView(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-indigo-900/20 bg-indigo-950 text-indigo-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(129,140,248,0.34),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(96,165,250,0.22),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-200">
            Scenario Claim-Tightening Lens
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Is Scenario Lab messaging staying in deterministic what-if bounds, with explicit proof
            and caveats for skeptical reviewers?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-indigo-100">
            Runtime messaging lens only. This page evaluates claim framing discipline and does not
            change Scenario Lab formulas, levers, or outputs.
          </p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Scenario claims tracked"
          value={formatNumber(view.entries.length)}
          note="Current scenario claim areas under tightening review."
          icon={<ClipboardCheck size={18} />}
        />
        <MetricCard
          label="Low-risk claims"
          value={formatNumber(view.lowRiskCount)}
          note="Claims currently phrased with bounded deterministic wording."
          tone="highlight"
          icon={<ShieldCheck size={18} />}
        />
        <MetricCard
          label="Moderate-risk claims"
          value={formatNumber(view.moderateRiskCount)}
          note="Claims requiring stronger caveat emphasis in live walkthroughs."
          tone="warning"
          icon={<AlertTriangle size={18} />}
        />
        <MetricCard
          label="Claims with explicit caveat"
          value={formatNumber(view.claimsWithExplicitCaveat)}
          note="Claim entries carrying an explicit boundary caveat sentence."
          icon={<BookOpenCheck size={18} />}
        />
        <MetricCard
          label="Current projected lift"
          value={formatCurrency(view.projectedRecoverableDollarLift)}
          note="Scenario output shown as capped what-if estimate only."
          icon={<Sparkles size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Claim to Proof to Caveat Mapping</h3>
          <p className="mt-1 text-sm text-slate-600">
            Keep scenario phrasing bounded: tightened claim, visible proof anchor, explicit caveat.
          </p>
        </header>

        <div className="mt-4 space-y-3">
          {view.entries.map((entry) => (
            <article key={entry.area} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-base font-semibold text-slate-900">{entry.area}</h4>
                <span
                  className={[
                    'rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.1em]',
                    entry.riskLevel === 'Low'
                      ? 'border-emerald-200 bg-emerald-100 text-emerald-700'
                      : 'border-amber-200 bg-amber-100 text-amber-700',
                  ].join(' ')}
                >
                  {entry.riskLevel}
                </span>
              </div>

              <div className="mt-3 grid gap-3 md:grid-cols-3">
                <LensBlock label="Tightened claim" value={entry.tightenedClaim} />
                <LensBlock label="Proof to point at" value={entry.proofToPointAt} />
                <LensBlock label="Caveat to say out loud" value={entry.caveat} />
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <MetricCard
          label="Projected backlog reduction"
          value={formatNumber(view.projectedBacklogReduction)}
          note="Current scenario what-if output for reviewer framing only."
          icon={<ClipboardCheck size={18} />}
        />
        <MetricCard
          label="Projected SLA improvement"
          value={`+${formatNumber(view.projectedSlaImprovementPoints)} pts`}
          note="Current scenario what-if output, not forecast certainty."
          icon={<ShieldCheck size={18} />}
        />
        <MetricCard
          label="Scenario positioning"
          value="Thin what-if"
          note="Scenario Lab remains secondary to deterministic queue and case evidence surfaces."
          icon={<Sparkles size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-indigo-200 bg-indigo-50 p-4 text-sm text-indigo-900 shadow-sm">
        Scope note: Scenario Lab is not a forecast engine, optimization platform, or enterprise
        planning model. It is a transparent, capped, deterministic what-if support surface.
      </section>
    </div>
  )
}

interface LensBlockProps {
  label: string
  value: string
}

function LensBlock({ label, value }: LensBlockProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-800">{value}</p>
    </div>
  )
}
