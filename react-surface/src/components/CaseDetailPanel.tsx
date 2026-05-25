import type { RevenueIntegrityCase } from '../data/types'
import { formatCurrency } from '../lib/formatters'
import { EvidenceTrace } from './EvidenceTrace'

interface CaseDetailPanelProps {
  caseItem: RevenueIntegrityCase | null
}

export function CaseDetailPanel({ caseItem }: CaseDetailPanelProps) {
  if (!caseItem) {
    return (
      <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
        <h3 className="font-heading text-xl text-slate-900">Select a case</h3>
        <p className="mt-2 text-sm text-slate-600">
          Choose a case from the prioritized worklist to review failed control evidence,
          owner, aging, and recommended next action.
        </p>
      </section>
    )
  }

  return (
    <section className="space-y-4">
      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-slate-300 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700">
            {caseItem.id}
          </span>
          <span className="rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
            {caseItem.issueDomain}
          </span>
        </div>

        <h2 className="font-heading mt-3 text-2xl text-slate-900">{caseItem.department}</h2>
        <p className="mt-1 text-sm text-slate-600">
          Service line: <span className="font-medium text-slate-700">{caseItem.serviceLine}</span>
        </p>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <KeyValue label="Current queue" value={caseItem.queue} />
          <KeyValue label="Current owner" value={caseItem.owner} />
          <KeyValue label="Primary blocker" value={caseItem.currentPrimaryBlocker} />
          <KeyValue label="Root cause mechanism" value={caseItem.rootCauseMechanism} />
          <KeyValue
            label="Recoverability status"
            value={caseItem.recoverabilityStatus}
            emphasis
          />
          <KeyValue label="Blocker aging" value={`${caseItem.agingDays} days`} />
        </div>
      </article>

      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="font-heading text-xl text-slate-900">Recoverability and Financial View</h3>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <ValueTile label="Dollars at risk" value={formatCurrency(caseItem.dollarsAtRisk)} />
          <ValueTile
            label="Recoverable now"
            value={formatCurrency(caseItem.dollarsRecoverableNow)}
          />
          <ValueTile
            label="Already lost"
            value={formatCurrency(caseItem.dollarsAlreadyLost)}
          />
        </div>
      </article>

      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="font-heading text-xl text-slate-900">Failed Control Narrative</h3>
        <p className="mt-2 text-sm text-slate-700">{caseItem.controlFailureNarrative}</p>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <NarrativeBlock title="Expected summary" value={caseItem.expectedSummary} />
          <NarrativeBlock title="Actual summary" value={caseItem.actualSummary} />
        </div>

        <NarrativeBlock
          title="Recommended next action"
          value={caseItem.recommendedAction}
          className="mt-4"
        />

        {caseItem.suppressionNote ? (
          <div className="mt-4 rounded-xl border border-violet-200 bg-violet-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-violet-700">
              Suppression note
            </p>
            <p className="mt-1 text-sm text-violet-800">{caseItem.suppressionNote}</p>
          </div>
        ) : null}
      </article>

      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="font-heading text-xl text-slate-900">Representative Deterministic Proof</h3>
        <p className="mt-2 text-sm text-slate-700">
          This proof block keeps the operating decision visible: what control failed, why it was
          routed, and what deterministic action should happen next.
        </p>

        <section className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <h4 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-600">
            Control Story
          </h4>
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {buildControlStory(caseItem).map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </section>

        <section className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
          <h4 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-600">
            Expected vs Actual
          </h4>
          <div className="mt-2 overflow-x-auto">
            <table className="min-w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-[0.12em] text-slate-500">
                  <th className="pb-2 pr-3 font-semibold">Checkpoint</th>
                  <th className="pb-2 pr-3 font-semibold">Expected</th>
                  <th className="pb-2 pr-3 font-semibold">Actual</th>
                  <th className="pb-2 font-semibold">Interpretation</th>
                </tr>
              </thead>
              <tbody>
                {buildExpectedActualRows(caseItem).map((row) => (
                  <tr key={row.checkpoint} className="border-b border-slate-100 align-top text-slate-700 last:border-b-0">
                    <td className="py-2 pr-3 font-medium text-slate-800">{row.checkpoint}</td>
                    <td className="py-2 pr-3">{row.expected}</td>
                    <td className="py-2 pr-3">{row.actual}</td>
                    <td className="py-2">{row.interpretation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <h4 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-600">
            Queue Governance
          </h4>
          <div className="mt-2 grid gap-2 text-sm sm:grid-cols-2">
            {buildQueueGovernanceRows(caseItem).map((row) => (
              <div key={row.label} className="rounded-lg border border-slate-200 bg-white p-3">
                <p className="text-xs uppercase tracking-[0.1em] text-slate-500">{row.label}</p>
                <p className="mt-1 font-semibold text-slate-800">{row.value}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
          <h4 className="text-sm font-semibold uppercase tracking-[0.12em] text-slate-600">
            Upstream Evidence
          </h4>
          <div className="mt-2 overflow-x-auto">
            <table className="min-w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-[0.12em] text-slate-500">
                  <th className="pb-2 pr-3 font-semibold">Step</th>
                  <th className="pb-2 pr-3 font-semibold">Status</th>
                  <th className="pb-2 font-semibold">Detail</th>
                </tr>
              </thead>
              <tbody>
                {caseItem.evidenceTrace.map((item) => (
                  <tr key={`${item.step}-${item.status}`} className="border-b border-slate-100 align-top text-slate-700 last:border-b-0">
                    <td className="py-2 pr-3 font-medium text-slate-800">{item.step}</td>
                    <td className="py-2 pr-3">
                      <span className="rounded-full border border-slate-300 bg-slate-50 px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.08em] text-slate-700">
                        {item.status}
                      </span>
                    </td>
                    <td className="py-2">{item.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </article>

      <EvidenceTrace items={caseItem.evidenceTrace} />
    </section>
  )
}

interface ProofRow {
  checkpoint: string
  expected: string
  actual: string
  interpretation: string
}

interface GovernanceRow {
  label: string
  value: string
}

function buildControlStory(caseItem: RevenueIntegrityCase): string[] {
  return [
    `Case ${caseItem.id} surfaced because ${caseItem.currentPrimaryBlocker.toLowerCase()}`,
    `Current routed owner is ${caseItem.owner} in ${caseItem.queue}.`,
    `Recoverability is ${caseItem.recoverabilityStatus.toLowerCase()} with ${formatCurrency(caseItem.dollarsRecoverableNow)} still actionable.`,
    `Blocker aging is ${caseItem.agingDays} days, which is ${classifyAging(caseItem.agingDays)}.`,
    `Deterministic next action: ${caseItem.recommendedAction}`,
  ]
}

function buildExpectedActualRows(caseItem: RevenueIntegrityCase): ProofRow[] {
  return [
    {
      checkpoint: 'Charge opportunity',
      expected: caseItem.expectedSummary,
      actual: caseItem.actualSummary,
      interpretation:
        'Performed activity and expected charge logic are visible, but the current blocker interrupted normal charge progression.',
    },
    {
      checkpoint: 'Recoverability path',
      expected: `${formatCurrency(caseItem.dollarsAtRisk)} tracked with timely correction path.`,
      actual: `${formatCurrency(caseItem.dollarsRecoverableNow)} recoverable now; ${formatCurrency(caseItem.dollarsAlreadyLost)} already lost.`,
      interpretation:
        'Deterministic recoverability split separates action-ready dollars from timing-window loss.',
    },
    {
      checkpoint: 'Owner routing',
      expected: 'Single current blocker determines accountable queue owner and next action.',
      actual: `${caseItem.owner} currently owns ${caseItem.queue}.`,
      interpretation:
        'One-current-blocker governance is preserved, avoiding ambiguous ownership drift.',
    },
  ]
}

function buildQueueGovernanceRows(caseItem: RevenueIntegrityCase): GovernanceRow[] {
  return [
    { label: 'Current queue', value: caseItem.queue },
    { label: 'Accountable owner', value: caseItem.owner },
    { label: 'Aging status', value: classifyAging(caseItem.agingDays) },
    {
      label: 'Queue policy note',
      value:
        caseItem.recoverabilityStatus === 'Post-window financially lost'
          ? 'Financial recovery is closed; keep case for compliance and control-learning follow-through.'
          : 'Case remains in active deterministic workflow until blocker resolves or recoverability closes.',
    },
  ]
}

function classifyAging(agingDays: number): string {
  if (agingDays > 14) {
    return 'Overdue escalation zone'
  }

  if (agingDays > 7) {
    return 'At-risk aging zone'
  }

  return 'Within current operating target'
}

interface KeyValueProps {
  label: string
  value: string
  emphasis?: boolean
}

function KeyValue({ label, value, emphasis = false }: KeyValueProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className={['mt-1 text-sm', emphasis ? 'font-semibold text-emerald-700' : 'text-slate-800'].join(' ')}>
        {value}
      </p>
    </div>
  )
}

interface ValueTileProps {
  label: string
  value: string
}

function ValueTile({ label, value }: ValueTileProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-900">{value}</p>
    </div>
  )
}

interface NarrativeBlockProps {
  title: string
  value: string
  className?: string
}

function NarrativeBlock({ title, value, className }: NarrativeBlockProps) {
  return (
    <section className={className}>
      <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
      <p className="mt-1 text-sm text-slate-700">{value}</p>
    </section>
  )
}
