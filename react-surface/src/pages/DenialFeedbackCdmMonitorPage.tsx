import {
  Activity,
  ArrowRightLeft,
  ClipboardCheck,
  Database,
  Landmark,
  ShieldCheck,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'
import {
  buildPatternLabel,
  computeDenialFeedbackCdmMonitor,
  getPatternLinkageDetail,
} from '../lib/denialFeedbackCdmMonitor'

interface DenialFeedbackCdmMonitorPageProps {
  cases: RevenueIntegrityCase[]
}

export function DenialFeedbackCdmMonitorPage({ cases }: DenialFeedbackCdmMonitorPageProps) {
  const view = useMemo(() => computeDenialFeedbackCdmMonitor(cases), [cases])
  const [selectedPatternId, setSelectedPatternId] = useState<string | null>(
    view.defaultSelectedPatternId,
  )

  const linkageDetail = useMemo(() => {
    if (!selectedPatternId) {
      return []
    }

    return getPatternLinkageDetail(view.denialSignalPatterns, selectedPatternId)
  }, [selectedPatternId, view.denialSignalPatterns])

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-rose-950/15 bg-rose-950 text-rose-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(251,113,133,0.35),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(253,186,116,0.25),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-rose-200">
            Denial Feedback + CDM Governance Monitor
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which downstream denial patterns point to upstream CDM or rule governance gaps
            that leadership should remediate next?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-rose-100">
            Thin downstream signal layer only. No appeals workflow, no payer adjudication
            orchestration, and no predictive denial model.
          </p>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Downstream denial signals"
          value={formatNumber(view.denialSignalCount)}
          note="Evidence-only denial signal rows for the current global slice."
          icon={<Activity size={18} />}
        />
        <MetricCard
          label="Downstream denial dollars"
          value={formatCurrency(view.denialDollars)}
          note="Summed denial signal dollars in the selected operational scope."
          tone="warning"
          icon={<Landmark size={18} />}
        />
        <MetricCard
          label="Governed prebill edit aging"
          value={`${formatNumber(view.governedPrebillEditAging)} days`}
          note="Reference aging for active prebill and coding queues under governance."
          icon={<ArrowRightLeft size={18} />}
        />
        <MetricCard
          label="Governed recoverable dollars still open"
          value={formatCurrency(view.governedRecoverableDollarsStillOpen)}
          note="Published recoverable exposure still active in open operational queues."
          tone="highlight"
          icon={<ClipboardCheck size={18} />}
        />
        <MetricCard
          label="Correction turnaround days"
          value={`${formatNumber(view.correctionTurnaroundDays)} days`}
          note="Observed correction/rebill turnaround from linked denial signal events."
          icon={<ShieldCheck size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Denial Signal Monitor</h3>
          <p className="mt-1 text-sm text-slate-600">
            Top downstream denial patterns mapped to upstream issue domain, likely root cause,
            and owner/action hints.
          </p>
        </header>

        {view.denialSignalPatterns.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No denial signal patterns match the current global filters.
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
              <thead>
                <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                  <th className="border-b border-slate-200 px-3 py-2">Pattern</th>
                  <th className="border-b border-slate-200 px-3 py-2">Payer</th>
                  <th className="border-b border-slate-200 px-3 py-2">Denial amount</th>
                  <th className="border-b border-slate-200 px-3 py-2">Linked issue domain</th>
                  <th className="border-b border-slate-200 px-3 py-2">Root cause</th>
                  <th className="border-b border-slate-200 px-3 py-2">Repeat signal</th>
                  <th className="border-b border-slate-200 px-3 py-2">Signal strength</th>
                  <th className="border-b border-slate-200 px-3 py-2">Owner/action hint</th>
                </tr>
              </thead>
              <tbody>
                {view.denialSignalPatterns.map((item) => (
                  <tr key={item.patternId} className="text-slate-700">
                    <td className="border-b border-slate-100 px-3 py-2 font-semibold text-slate-900">
                      {item.denialReasonGroup}
                    </td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.payerGroup}</td>
                    <td className="border-b border-slate-100 px-3 py-2">
                      {formatCurrency(item.denialAmount)}
                    </td>
                    <td className="border-b border-slate-100 px-3 py-2">
                      {item.linkedUpstreamIssueDomain}
                    </td>
                    <td className="border-b border-slate-100 px-3 py-2">
                      {item.linkedRootCauseMechanism}
                    </td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.repeatPatternSignal}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.denialSignalStrength}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.ownerActionHint}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">CDM Governance Monitor</h3>
          <p className="mt-1 text-sm text-slate-600">
            Expected code, modifier, and revenue-code governance checks tied to the same
            operating slice.
          </p>
        </header>

        {view.cdmGovernanceMonitor.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No CDM governance rows are currently in-scope for this filter combination.
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
              <thead>
                <tr className="text-xs uppercase tracking-[0.12em] text-slate-500">
                  <th className="border-b border-slate-200 px-3 py-2">Department</th>
                  <th className="border-b border-slate-200 px-3 py-2">Service line</th>
                  <th className="border-b border-slate-200 px-3 py-2">Expected code</th>
                  <th className="border-b border-slate-200 px-3 py-2">Expected modifier</th>
                  <th className="border-b border-slate-200 px-3 py-2">Revenue code</th>
                  <th className="border-b border-slate-200 px-3 py-2">Rule status</th>
                  <th className="border-b border-slate-200 px-3 py-2">Governance status</th>
                  <th className="border-b border-slate-200 px-3 py-2">Suggested action</th>
                </tr>
              </thead>
              <tbody>
                {view.cdmGovernanceMonitor.map((item) => (
                  <tr
                    key={`${item.department}-${item.serviceLine}-${item.expectedCode}`}
                    className="text-slate-700"
                  >
                    <td className="border-b border-slate-100 px-3 py-2">{item.department}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.serviceLine}</td>
                    <td className="border-b border-slate-100 px-3 py-2 font-semibold text-slate-900">
                      {item.expectedCode}
                    </td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.expectedModifier}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.revenueCode}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.ruleStatus}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.cdmGovernanceFlag}</td>
                    <td className="border-b border-slate-100 px-3 py-2">{item.suggestedGovernanceAction}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Linked Interpretation</h3>
          <p className="mt-1 text-sm text-slate-600">
            Select a denial pattern to inspect upstream linkage, likely owner path, and the
            recommended deterministic next step.
          </p>
        </header>

        {view.patternSelectorOptions.length === 0 ? null : (
          <label className="mt-4 block text-sm text-slate-700" htmlFor="denial-pattern-selector">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              Denial pattern
            </span>
            <select
              id="denial-pattern-selector"
              value={selectedPatternId ?? ''}
              onChange={(event) => setSelectedPatternId(event.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-rose-400 focus:ring-2 focus:ring-rose-200"
            >
              {view.denialSignalPatterns.map((item) => (
                <option key={item.patternId} value={item.patternId}>
                  {buildPatternLabel(item)}
                </option>
              ))}
            </select>
          </label>
        )}

        {linkageDetail.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No linked interpretation is available for the current filters.
          </div>
        ) : (
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            {linkageDetail.map((item) => (
              <article key={item.field} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
                  {item.field}
                </p>
                <p className="mt-1 text-sm text-slate-800">{item.value}</p>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900 shadow-sm">
        <div className="flex items-start gap-3">
          <Database className="mt-0.5" size={16} />
          <p>
            This monitor keeps denials as downstream evidence only. It does not add appeals
            tracking, payer adjudication logic, routing changes, or predictive denial modeling.
          </p>
        </div>
      </section>
    </div>
  )
}
