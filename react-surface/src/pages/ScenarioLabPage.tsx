import { Calculator, ListChecks, SlidersHorizontal, TrendingUp, Zap } from 'lucide-react'
import { type Dispatch, type SetStateAction, useMemo, useState } from 'react'

import { MetricCard } from '../components/MetricCard'
import type { RevenueIntegrityCase, ScenarioLeverKey } from '../data/types'
import { formatCurrency, formatNumber } from '../lib/formatters'
import { computeScenarioLab } from '../lib/scenarioLab'

interface ScenarioLabPageProps {
  cases: RevenueIntegrityCase[]
}

interface ScenarioTargetState {
  prebillClearanceRate: number
  correctionTurnaroundDays: number
  routingSpeedDays: number
}

export function ScenarioLabPage({ cases }: ScenarioLabPageProps) {
  const baselineResult = useMemo(() => computeScenarioLab(cases), [cases])

  const [targets, setTargets] = useState<ScenarioTargetState>({
    prebillClearanceRate:
      baselineResult.leverConfigs.find((item) => item.key === 'prebillClearanceRate')?.targetValue ??
      0,
    correctionTurnaroundDays:
      baselineResult.leverConfigs.find((item) => item.key === 'correctionTurnaroundDays')?.targetValue ??
      0,
    routingSpeedDays:
      baselineResult.leverConfigs.find((item) => item.key === 'routingSpeedDays')?.targetValue ?? 0,
  })

  const scenarioResult = useMemo(
    () => computeScenarioLab(cases, targets),
    [cases, targets],
  )

  return (
    <div className="space-y-6">
      <section className="overflow-hidden rounded-3xl border border-sky-900/20 bg-sky-950 text-sky-50 shadow-xl">
        <div className="bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.35),transparent_45%),radial-gradient(circle_at_bottom_right,rgba(20,184,166,0.24),transparent_42%)] p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-200">
            Scenario Lab
          </p>
          <h2 className="font-heading mt-2 text-3xl leading-tight sm:text-4xl">
            Which operational lever shift has the strongest bounded impact on recoverable
            dollars, backlog reduction, and SLA improvement?
          </h2>
          <p className="mt-3 max-w-4xl text-sm text-sky-100">
            Deterministic what-if only. No hidden weights, no predictive model, no queue routing
            logic changes.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-sky-100 bg-white p-4 shadow-sm sm:p-5">
        <header>
          <h3 className="font-heading text-2xl text-slate-900">Operational Levers</h3>
          <p className="mt-1 text-sm text-slate-600">
            Move three transparent levers within bounded ranges. Baselines are pulled from the
            current filtered operational slice.
          </p>
        </header>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          {scenarioResult.leverConfigs.map((lever) => (
            <article key={lever.key} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
              <label className="text-sm font-semibold text-slate-900" htmlFor={`scenario-${lever.key}`}>
                {lever.label}
              </label>
              <p className="mt-1 text-xs uppercase tracking-[0.12em] text-slate-500">
                Baseline: {formatBaseline(lever.baselineValue, lever.unitLabel)}
              </p>
              <input
                id={`scenario-${lever.key}`}
                type="range"
                min={lever.minValue}
                max={lever.maxValue}
                step={lever.step}
                value={targets[lever.key]}
                onChange={(event) =>
                  updateTarget(setTargets, lever.key, Number(event.target.value))
                }
                className="mt-3 w-full accent-sky-600"
              />
              <input
                id={`scenario-${lever.key}-number`}
                aria-label={`${lever.label} target`}
                type="number"
                min={lever.minValue}
                max={lever.maxValue}
                step={lever.step}
                value={targets[lever.key]}
                onChange={(event) =>
                  updateTarget(setTargets, lever.key, Number(event.target.value))
                }
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200"
              />
              <p className="mt-2 text-sm text-slate-700">
                Delta from baseline: {formatDelta(lever.baselineValue, targets[lever.key], lever.unitLabel)} {lever.deltaLabel}
              </p>
              <p className="mt-2 text-xs text-slate-600">{lever.assumptionNote}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-5">
        <MetricCard
          label="Projected recoverable dollar lift"
          value={formatCurrency(scenarioResult.projection.projectedRecoverableDollarLift)}
          note="Monthly directional lift under current capped assumptions."
          tone="highlight"
          icon={<TrendingUp size={18} />}
        />
        <MetricCard
          label="Projected open-exception reduction"
          value={`${formatNumber(scenarioResult.projection.projectedBacklogReduction)} fewer`}
          note="90-day reduction from current prebill and handoff pressure."
          icon={<ListChecks size={18} />}
        />
        <MetricCard
          label="Projected SLA improvement"
          value={`+${formatNumber(scenarioResult.projection.projectedSlaImprovementPoints)} pts`}
          note={`${formatNumber(scenarioResult.projection.baselineWithinSlaRate)}% -> ${formatNumber(scenarioResult.projection.projectedWithinSlaRate)}% within SLA.`}
          icon={<SlidersHorizontal size={18} />}
        />
        <MetricCard
          label="90-day impact estimate"
          value={formatCurrency(scenarioResult.projection.ninetyDayImpactEstimate)}
          note="Simple three-month roll-forward of projected monthly lift."
          icon={<Zap size={18} />}
        />
        <MetricCard
          label="Implementation effort framing"
          value={scenarioResult.projection.implementationEffort}
          note="Larger lever shifts imply broader operational follow-through."
          icon={<Calculator size={18} />}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <h3 className="font-heading text-2xl text-slate-900">Baseline Inputs Used</h3>
          <p className="mt-1 text-sm text-slate-600">
            Inputs are deterministic and sourced from the current filtered case population.
          </p>
          <div className="mt-4 space-y-3">
            {scenarioResult.baselineInputs.map((item) => (
              <div key={item.metric} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-xs uppercase tracking-[0.12em] text-slate-500">{item.metric}</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{item.valueDisplay}</p>
                <p className="mt-1 text-xs text-slate-600">{item.note}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <h3 className="font-heading text-2xl text-slate-900">How This Is Calculated</h3>
          <p className="mt-1 text-sm text-slate-600">
            Formulas are explicit. Caps prevent unrealistic claim inflation.
          </p>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            <FormulaBlock
              title="Backlog reduction"
              formula="min(30% of current open exceptions, prebill open * clearance gain + active handoff items * routing gain)"
              result={`${formatNumber(scenarioResult.projection.projectedBacklogReduction)} fewer open exceptions`}
              guardrail="Prebill clearance gain capped at 20%; routing gain capped at 25%."
            />
            <FormulaBlock
              title="SLA improvement"
              formula="Baseline within-SLA rate plus improved cases from prebill, routing, and correction levers."
              result={`+${formatNumber(scenarioResult.projection.projectedSlaImprovementPoints)} within-SLA pts`}
              guardrail="Only current at-risk and overdue items are eligible to improve."
            />
            <FormulaBlock
              title="Recoverable dollar lift"
              formula="min(35% of aged recoverable dollars, prebill recoverable $ * clearance gain + correction recoverable $ * turnaround gain + handoff recoverable $ * routing gain)"
              result={formatCurrency(scenarioResult.projection.projectedRecoverableDollarLift)}
              guardrail="Not every open exception dollar is treated as recoverable or equally achievable."
            />
            <FormulaBlock
              title="90-day impact"
              formula="Projected monthly recoverable dollar lift * 3 months"
              result={formatCurrency(scenarioResult.projection.ninetyDayImpactEstimate)}
              guardrail="Roll-forward estimate only; this is not a predictive forecast."
            />
          </div>
        </article>
      </section>

      <section className="rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900 shadow-sm">
        What-if operational improvement only. This page does not change queue routing logic,
        priority formulas, denial workflows, or introduce any predictive model.
      </section>
    </div>
  )
}

function updateTarget(
  setTargets: Dispatch<SetStateAction<ScenarioTargetState>>,
  key: ScenarioLeverKey,
  value: number,
) {
  setTargets((previous) => {
    if (!Number.isFinite(value)) {
      return previous
    }

    return {
      ...previous,
      [key]: value,
    }
  })
}

function formatBaseline(value: number, unitLabel: '%' | 'days'): string {
  if (unitLabel === '%') {
    return `${formatNumber(value)}%`
  }

  return `${formatNumber(value)} days`
}

function formatDelta(
  baselineValue: number,
  targetValue: number,
  unitLabel: '%' | 'days',
): string {
  if (unitLabel === '%') {
    return `${formatNumber(targetValue - baselineValue)}`
  }

  return `${formatNumber(Math.max(baselineValue - targetValue, 0))}`
}

interface FormulaBlockProps {
  title: string
  formula: string
  result: string
  guardrail: string
}

function FormulaBlock({ title, formula, result, guardrail }: FormulaBlockProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{title}</p>
      <p className="mt-1 text-sm text-slate-700">{formula}</p>
      <p className="mt-2 text-sm font-semibold text-slate-900">Result: {result}</p>
      <p className="mt-1 text-xs text-slate-600">{guardrail}</p>
    </div>
  )
}
