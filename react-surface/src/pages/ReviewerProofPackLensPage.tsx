import { BookCheck, BookMarked, ClipboardCheck, Library, ScrollText } from 'lucide-react'

import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatNumber } from '../lib/formatters'
import { computeReviewerProofPackLensView } from '../lib/reviewerProofPackLens'

interface ReviewerProofPackLensPageProps {
  cases: RevenueIntegrityCase[]
}

export function ReviewerProofPackLensPage({ cases }: ReviewerProofPackLensPageProps) {
  const view = computeReviewerProofPackLensView(cases)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-cyan-900/20 bg-cyan-950 text-cyan-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(45,212,191,0.34),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.22),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">
            Reviewer Proof Pack Lens
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Are reviewer claims anchored to the strongest proof path first, with supporting artifacts
            clearly separated from core evidence?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-cyan-100">
            Runtime mapping only. This lens reflects proof-index order and usage guidance without
            altering control-room or scenario logic.
          </p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Proof assets"
          value={formatNumber(view.assets.length)}
          note="Total proof entries currently visible in the reviewer pack lens."
          icon={<Library size={18} />}
        />
        <MetricCard
          label="Core proof"
          value={formatNumber(view.coreCount)}
          note="Assets that should be used before supporting evidence."
          tone="highlight"
          icon={<BookCheck size={18} />}
        />
        <MetricCard
          label="Supporting proof"
          value={formatNumber(view.supportingCount)}
          note="Assets used after the core walkthrough and export path are clear."
          icon={<BookMarked size={18} />}
        />
        <MetricCard
          label="Test-backed assets"
          value={formatNumber(view.testProofCount)}
          note="Artifacts that validate realism or behavior with explicit checks."
          icon={<ClipboardCheck size={18} />}
        />
        <MetricCard
          label="Current slice cases"
          value={formatNumber(view.currentSliceCaseCount)}
          note="Filtered case count while reviewing the proof map in this session."
          icon={<ScrollText size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Proof Asset Mapping</h3>
          <p className="mt-1 text-sm text-slate-600">
            Core versus supporting assets, with what each item proves and how it should be used in a
            skeptical walkthrough.
          </p>
        </header>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                <th className="border-b border-slate-200 px-3 py-2">Priority</th>
                <th className="border-b border-slate-200 px-3 py-2">Asset</th>
                <th className="border-b border-slate-200 px-3 py-2">What it proves</th>
                <th className="border-b border-slate-200 px-3 py-2">Demo use</th>
                <th className="border-b border-slate-200 px-3 py-2">Proof type</th>
              </tr>
            </thead>
            <tbody>
              {view.assets.map((item) => (
                <tr key={item.asset} className="text-slate-700">
                  <td className="border-b border-slate-100 px-3 py-2">
                    <span
                      className={[
                        'rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.1em]',
                        item.priority === 'Core'
                          ? 'border-emerald-200 bg-emerald-100 text-emerald-700'
                          : 'border-slate-200 bg-slate-100 text-slate-700',
                      ].join(' ')}
                    >
                      {item.priority}
                    </span>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2 font-mono text-xs text-slate-900">
                    {item.asset}
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2">{item.whatItProves}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{item.demoUse}</td>
                  <td className="border-b border-slate-100 px-3 py-2">{item.proofType}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Recommended Read Order</h3>
          <p className="mt-1 text-sm text-slate-600">
            Keep reviewer flow disciplined: core proof first, supporting proof only after the core
            path is established.
          </p>
        </header>

        <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-slate-700">
          {view.recommendedReadOrder.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      </section>

      <section className="rounded-2xl border border-cyan-200 bg-cyan-50 p-4 text-sm text-cyan-900 shadow-sm">
        Scope note: this page maps the reviewer proof path and ordering guidance. It does not alter
        queue governance, scenario math, denial scope, or deterministic decision logic.
      </section>
    </div>
  )
}
