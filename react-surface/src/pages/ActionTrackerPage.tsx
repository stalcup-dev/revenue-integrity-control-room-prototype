import {
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  Coins,
  Filter,
  ListChecks,
  Sparkles,
  Timer,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import { CaseDetailPanel } from '../components/CaseDetailPanel'
import { ExceptionWorklist } from '../components/ExceptionWorklist'
import { InterventionCard } from '../components/InterventionCard'
import { MetricCard } from '../components/MetricCard'
import type { InterventionTrackingItem, RevenueIntegrityCase } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'

interface ActionTrackerPageProps {
  interventions: InterventionTrackingItem[]
  cases: RevenueIntegrityCase[]
}

type StatusFilter = InterventionTrackingItem['checkpointStatus'] | 'All'
type RecommendationFilter = InterventionTrackingItem['recommendation'] | 'All'

export function ActionTrackerPage({ interventions, cases }: ActionTrackerPageProps) {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('All')
  const [recommendationFilter, setRecommendationFilter] = useState<RecommendationFilter>('All')
  const [selectedInterventionId, setSelectedInterventionId] = useState<string | null>(
    interventions[0]?.id ?? null,
  )
  const [selectedImpactedCaseId, setSelectedImpactedCaseId] = useState<string | null>(null)

  const filteredInterventions = useMemo(
    () =>
      interventions.filter((item) => {
        if (statusFilter !== 'All' && item.checkpointStatus !== statusFilter) {
          return false
        }

        if (recommendationFilter !== 'All' && item.recommendation !== recommendationFilter) {
          return false
        }

        return true
      }),
    [interventions, recommendationFilter, statusFilter],
  )

  const interventionImpactMap = useMemo(() => {
    const nextMap = new Map<
      string,
      {
        cases: RevenueIntegrityCase[]
        summary: {
          affectedCases: number
          dollarsAtRisk: number
          recoverableNow: number
          averageAgingDays: number
        }
      }
    >()

    for (const intervention of filteredInterventions) {
      const linkedCaseIds = new Set(intervention.linkedCaseIds)
      const linkedCases = cases.filter((caseItem) => linkedCaseIds.has(caseItem.id))
      const dollarsAtRisk = linkedCases.reduce(
        (runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk,
        0,
      )
      const recoverableNow = linkedCases.reduce(
        (runningTotal, caseItem) => runningTotal + caseItem.dollarsRecoverableNow,
        0,
      )
      const averageAgingDays =
        linkedCases.length === 0
          ? 0
          : linkedCases.reduce((runningTotal, caseItem) => runningTotal + caseItem.agingDays, 0) /
            linkedCases.length

      nextMap.set(intervention.id, {
        cases: linkedCases,
        summary: {
          affectedCases: linkedCases.length,
          dollarsAtRisk,
          recoverableNow,
          averageAgingDays: Math.round(averageAgingDays * 10) / 10,
        },
      })
    }

    return nextMap
  }, [cases, filteredInterventions])

  const selectedIntervention = useMemo(() => {
    if (filteredInterventions.length === 0) {
      return null
    }

    if (
      selectedInterventionId &&
      filteredInterventions.some((item) => item.id === selectedInterventionId)
    ) {
      return filteredInterventions.find((item) => item.id === selectedInterventionId) ?? null
    }

    return filteredInterventions[0]
  }, [filteredInterventions, selectedInterventionId])

  const selectedInterventionCases = useMemo(() => {
    if (!selectedIntervention) {
      return []
    }

    return interventionImpactMap.get(selectedIntervention.id)?.cases ?? []
  }, [interventionImpactMap, selectedIntervention])

  const selectedInterventionSummary =
    selectedIntervention ? interventionImpactMap.get(selectedIntervention.id)?.summary ?? null : null

  const selectedInterventionCase = useMemo(() => {
    if (selectedInterventionCases.length === 0) {
      return null
    }

    if (
      selectedImpactedCaseId &&
      selectedInterventionCases.some((caseItem) => caseItem.id === selectedImpactedCaseId)
    ) {
      return (
        selectedInterventionCases.find((caseItem) => caseItem.id === selectedImpactedCaseId) ?? null
      )
    }

    return selectedInterventionCases[0]
  }, [selectedImpactedCaseId, selectedInterventionCases])

  const metrics = useMemo(() => {
    const total = filteredInterventions.length
    const validated = filteredInterventions.filter(
      (item) => item.checkpointStatus === 'Validated',
    ).length
    const needsRevision = filteredInterventions.filter(
      (item) => item.checkpointStatus === 'Needs revision',
    ).length
    const notStarted = filteredInterventions.filter(
      (item) => item.checkpointStatus === 'Not started',
    ).length

    return {
      total,
      validated,
      needsRevision,
      notStarted,
    }
  }, [filteredInterventions])

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-indigo-950/15 bg-indigo-950 text-indigo-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(196,181,253,0.35),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(244,114,182,0.25),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-200">
            Opportunity and Action Tracker
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which interventions should leadership hold, expand, or revise to reduce queue
            pressure and protect recoverable dollars?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-indigo-100">
            Follow-through governance for deterministic control failures across outpatient
            infusion, radiology/IR, and OR procedural workflows.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-indigo-100 bg-white p-4 shadow-sm sm:p-5">
        <div className="flex flex-wrap items-end gap-3">
          <label className="block min-w-[220px] flex-1 text-sm text-slate-700" htmlFor="action-status-filter">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              Checkpoint status
            </span>
            <select
              id="action-status-filter"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-200"
            >
              <option value="All">All statuses</option>
              <option value="Not started">Not started</option>
              <option value="In progress">In progress</option>
              <option value="Validated">Validated</option>
              <option value="Needs revision">Needs revision</option>
            </select>
          </label>

          <label className="block min-w-[220px] flex-1 text-sm text-slate-700" htmlFor="action-recommendation-filter">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
              Recommendation
            </span>
            <select
              id="action-recommendation-filter"
              value={recommendationFilter}
              onChange={(event) =>
                setRecommendationFilter(event.target.value as RecommendationFilter)
              }
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-200"
            >
              <option value="All">All recommendations</option>
              <option value="Hold">Hold</option>
              <option value="Expand">Expand</option>
              <option value="Revise">Revise</option>
            </select>
          </label>

          <div className="inline-flex h-10 items-center gap-2 rounded-xl border border-indigo-100 bg-indigo-50 px-3 text-xs font-semibold uppercase tracking-[0.12em] text-indigo-700">
            <Filter size={14} aria-hidden="true" />
            Filters active
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
        <MetricCard
          label="Total interventions"
          value={formatNumber(metrics.total)}
          note="Actions currently visible under selected filters."
          icon={<ClipboardList size={18} />}
        />
        <MetricCard
          label="Validated"
          value={formatNumber(metrics.validated)}
          note="Interventions with measured, sustained control improvement."
          tone="highlight"
          icon={<CheckCircle2 size={18} />}
        />
        <MetricCard
          label="Needs revision"
          value={formatNumber(metrics.needsRevision)}
          note="Interventions with insufficient or unstable impact."
          tone="warning"
          icon={<AlertTriangle size={18} />}
        />
        <MetricCard
          label="Not started"
          value={formatNumber(metrics.notStarted)}
          note="Planned interventions awaiting execution this cycle."
          icon={<Sparkles size={18} />}
        />
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Intervention Portfolio</h3>
          <p className="mt-1 text-sm text-slate-600">
            Evaluate checkpoint status, trend movement, and recommendation confidence before
            scaling or revising interventions.
          </p>
        </header>

        {filteredInterventions.length === 0 ? (
          <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-600">
            No interventions match the current status and recommendation filters.
          </div>
        ) : (
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            {filteredInterventions.map((item) => (
              <InterventionCard
                key={item.id}
                item={item}
                impactSummary={interventionImpactMap.get(item.id)?.summary}
                impactDelta={{
                  dollarsAtRisk:
                    item.currentImpact.dollarsAtRisk - item.baselineImpact.dollarsAtRisk,
                  caseCount: item.currentImpact.caseCount - item.baselineImpact.caseCount,
                }}
                isSelected={selectedIntervention?.id === item.id}
                onViewImpactedCases={() => {
                  setSelectedInterventionId(item.id)
                  const firstCaseId = interventionImpactMap.get(item.id)?.cases[0]?.id ?? null
                  setSelectedImpactedCaseId(firstCaseId)
                }}
              />
            ))}
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Impacted Case Worklist</h3>
          <p className="mt-1 text-sm text-slate-600">
            Drill into the current intervention cohort to see linked queue pressure and
            deterministic case detail.
          </p>
        </header>

        <div className="mt-4 grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
          <MetricCard
            label="Impacted cases"
            value={formatNumber(selectedInterventionSummary?.affectedCases ?? 0)}
            note="Linked cases visible under current global filters."
            icon={<ListChecks size={18} />}
          />
          <MetricCard
            label="Impacted dollars at risk"
            value={formatCurrency(selectedInterventionSummary?.dollarsAtRisk ?? 0)}
            note="Total exposure attached to this intervention linkage."
            tone="warning"
            icon={<Coins size={18} />}
          />
          <MetricCard
            label="Linked recoverable now"
            value={formatCurrency(selectedInterventionSummary?.recoverableNow ?? 0)}
            note="Amount still actionable in linked intervention cases."
            tone="highlight"
            icon={<ClipboardList size={18} />}
          />
          <MetricCard
            label="Linked average aging"
            value={`${formatNumber(selectedInterventionSummary?.averageAgingDays ?? 0)} days`}
            note="Mean blocker aging across the selected intervention cohort."
            icon={<Timer size={18} />}
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
            <p className="mb-4 text-sm text-slate-600">
              {selectedIntervention
                ? `Showing cases linked to ${selectedIntervention.title}.`
                : 'Select an intervention to view linked cases.'}
            </p>
            <ExceptionWorklist
              cases={selectedInterventionCases}
              selectedCaseId={selectedInterventionCase?.id ?? null}
              onSelectCase={setSelectedImpactedCaseId}
            />
          </div>

          <CaseDetailPanel caseItem={selectedInterventionCase} />
        </div>
      </section>
    </div>
  )
}
