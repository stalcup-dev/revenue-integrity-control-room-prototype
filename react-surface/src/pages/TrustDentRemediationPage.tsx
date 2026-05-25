import { Archive, BadgeCheck, BookOpenCheck, FileCheck2, ShieldCheck } from 'lucide-react'

import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatNumber } from '../lib/formatters'
import { computeTrustDentRemediationView } from '../lib/trustDentRemediation'

interface TrustDentRemediationPageProps {
  cases: RevenueIntegrityCase[]
}

export function TrustDentRemediationPage({ cases }: TrustDentRemediationPageProps) {
  const view = computeTrustDentRemediationView(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-lime-900/20 bg-lime-950 text-lime-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(163,230,53,0.3),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(132,204,22,0.22),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-lime-200">
            Trust Dent Remediation
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Have the highest-risk reviewer trust dents been remediated with explicit evidence and
            no-build-boundary discipline?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-lime-100">
            Archive-backed packaging remediation only. This route tracks wording/framing trust
            fixes without changing deterministic queue or recoverability logic.
          </p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Trust dents tracked"
          value={formatNumber(view.items.length)}
          note="High-priority packaging trust dents from skeptical reviewer pass."
          icon={<FileCheck2 size={18} />}
        />
        <MetricCard
          label="Remediated"
          value={formatNumber(view.remediatedCount)}
          note="Trust dents currently marked remediated by artifact-level fixes."
          tone="highlight"
          icon={<BadgeCheck size={18} />}
        />
        <MetricCard
          label="Watchlist"
          value={formatNumber(view.watchlistCount)}
          note="Dents still requiring additional remediation tightening."
          tone={view.watchlistCount > 0 ? 'warning' : 'default'}
          icon={<ShieldCheck size={18} />}
        />
        <MetricCard
          label="No-build-boundary fixes"
          value={formatNumber(view.noBuildBoundaryCount)}
          note="Remediations completed through wording/framing/structure without code-path changes."
          icon={<BookOpenCheck size={18} />}
        />
        <MetricCard
          label="Current slice cases"
          value={formatNumber(view.currentSliceCaseCount)}
          note="Filtered case slice currently in view while reviewing remediation status."
          icon={<Archive size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Remediation Ledger</h3>
          <p className="mt-1 text-sm text-slate-600">
            Each dent includes why it matters, fix strategy, status, and archived proof anchor.
          </p>
        </header>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <th className="border-b border-slate-200 px-3 py-2">Dent</th>
                <th className="border-b border-slate-200 px-3 py-2">Why it matters</th>
                <th className="border-b border-slate-200 px-3 py-2">Remediation strategy</th>
                <th className="border-b border-slate-200 px-3 py-2">Status</th>
                <th className="border-b border-slate-200 px-3 py-2">Proof anchor</th>
                <th className="border-b border-slate-200 px-3 py-2">No-build boundary</th>
              </tr>
            </thead>
            <tbody>
              {view.items.map((item) => (
                <tr key={item.id} className="text-slate-700">
                  <td className="border-b border-slate-100 px-3 py-2 font-semibold text-slate-900">
                    {item.dent}
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2">{item.whyItMatters}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{item.remediationStrategy}</td>
                  <td className="border-b border-slate-100 px-3 py-2">
                    <span
                      className={[
                        'rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.1em]',
                        item.status === 'Remediated'
                          ? 'border-emerald-200 bg-emerald-100 text-emerald-700'
                          : 'border-amber-200 bg-amber-100 text-amber-700',
                      ].join(' ')}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2">{item.proofAnchor}</td>
                  <td className="border-b border-slate-100 px-3 py-2">
                    {item.noBuildBoundary ? 'Preserved' : 'Not preserved'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-lime-200 bg-lime-50 p-4 text-sm text-lime-900 shadow-sm">
        Scope note: this remediation ledger tracks packaging trust dents and artifact framing fixes.
        It does not change deterministic exception logic, queue routing logic, scenario formulas,
        or feature scope boundaries.
      </section>
    </div>
  )
}
