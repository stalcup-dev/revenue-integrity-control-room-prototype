import { CheckCircle2, ClipboardCheck, Compass, Sparkles, Users2, XCircle } from 'lucide-react'

import { MetricCard } from '../components/MetricCard'
import { interventionTracking } from '../data/interventionTracking'
import type { RevenueIntegrityCase } from '../data/types'
import { formatNumber } from '../lib/formatters'
import { computeStorytellingValidationView } from '../lib/pageStorytellingValidation'

interface PageStorytellingValidationPageProps {
  cases: RevenueIntegrityCase[]
}

export function PageStorytellingValidationPage({ cases }: PageStorytellingValidationPageProps) {
  const view = computeStorytellingValidationView(cases, interventionTracking)

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-fuchsia-900/20 bg-fuchsia-950 text-fuchsia-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(244,114,182,0.34),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(217,70,239,0.24),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-fuchsia-200">
            Page Storytelling Validation
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Do non-summary work pages consistently answer what control is monitored, where
            pressure sits, and who owns the next move?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-fuchsia-100">
            Secondary storytelling pattern only: compact page-native cues for work surfaces,
            while Scenario Lab keeps intentionally thinner framing.
          </p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Pages validated"
          value={formatNumber(view.validatedPages)}
          note="Pages currently passing required storytelling cue checks."
          tone="highlight"
          icon={<CheckCircle2 size={18} />}
        />
        <MetricCard
          label="Full-cue pages"
          value={formatNumber(view.fullCuePages)}
          note="Pages expected to show control, pressure, and owner-next-move cues."
          icon={<ClipboardCheck size={18} />}
        />
        <MetricCard
          label="Thin-cue pages"
          value={formatNumber(view.thinCuePages)}
          note="Pages intentionally scoped to lightweight framing only."
          icon={<Sparkles size={18} />}
        />
        <MetricCard
          label="Pages requiring update"
          value={formatNumber(view.failedPages)}
          note="Pages missing one or more required storytelling cues."
          tone={view.failedPages > 0 ? 'warning' : 'default'}
          icon={<XCircle size={18} />}
        />
        <MetricCard
          label="Current slice cases"
          value={formatNumber(cases.length)}
          note="Filtered case population driving this storytelling validation."
          icon={<Users2 size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Secondary Storytelling Pattern Audit</h3>
          <p className="mt-1 text-sm text-slate-600">
            Each work page should carry a compact cue: monitored control, current pressure, and
            owner next move. Scenario Lab remains intentionally thinner.
          </p>
        </header>

        <div className="mt-4 space-y-3">
          {view.cards.map((card) => (
            <article key={card.page} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-base font-semibold text-slate-900">{card.page}</h4>
                <div className="flex items-center gap-2">
                  <span className="rounded-full border border-slate-300 bg-white px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.1em] text-slate-600">
                    {card.mode}
                  </span>
                  <span
                    className={[
                      'rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.1em]',
                      card.passes
                        ? 'border-emerald-200 bg-emerald-100 text-emerald-700'
                        : 'border-rose-200 bg-rose-100 text-rose-700',
                    ].join(' ')}
                  >
                    {card.passes ? 'Pass' : 'Needs update'}
                  </span>
                </div>
              </div>

              <div className="mt-3 grid gap-3 md:grid-cols-3">
                <CueBlock label="Control monitored" value={card.controlStatement} />
                <CueBlock label="Current pressure" value={card.pressureStatement} />
                <CueBlock label="Owner next move" value={card.ownerNextMove} />
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-fuchsia-200 bg-fuchsia-50 p-4 text-sm text-fuchsia-900 shadow-sm">
        <div className="flex items-start gap-2">
          <Compass className="mt-0.5" size={16} />
          <p>
            Scope note: this validates chapter-page storytelling consistency for the current
            deterministic browser slice. It does not alter routing logic, KPI formulas, or model
            assumptions.
          </p>
        </div>
      </section>
    </div>
  )
}

interface CueBlockProps {
  label: string
  value: string
}

function CueBlock({ label, value }: CueBlockProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-800">{value}</p>
    </div>
  )
}
