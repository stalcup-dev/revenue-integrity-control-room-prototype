import type { InterventionTrackingItem } from './types'

export const interventionTracking: InterventionTrackingItem[] = [
  {
    id: 'INT-01',
    title: 'OR prebill distinctness checkpoint',
    owner: 'Prebill Edit RN',
    targetCompletionDate: '2026-06-15',
    checkpointStatus: 'In progress',
    baselineMetric: 'Prebill edit aging: 10.9 days',
    currentMetric: 'Prebill edit aging: 8.1 days',
    recommendation: 'Expand',
    validationNote:
      'Early trend shows fewer >7 day holds after daily coder-prebill huddle.',
    linkedCaseIds: ['RI-OR-0017', 'RI-OR-0099'],
    baselineImpact: {
      caseCount: 3,
      dollarsAtRisk: 68100,
      recoverableNow: 51200,
      averageAgingDays: 11.3,
    },
    currentImpact: {
      caseCount: 2,
      dollarsAtRisk: 56950,
      recoverableNow: 51200,
      averageAgingDays: 10.8,
    },
  },
  {
    id: 'INT-02',
    title: 'IR interface retry guardrail',
    owner: 'Revenue Systems Analyst',
    targetCompletionDate: '2026-06-10',
    checkpointStatus: 'Validated',
    baselineMetric: 'IR missing-charge cases: 14 per month',
    currentMetric: 'IR missing-charge cases: 5 per month',
    recommendation: 'Hold',
    validationNote:
      'Three-week validation confirms stable event delivery and reduced manual posting.',
    linkedCaseIds: ['RI-IR-0031', 'RI-IR-0088'],
    baselineImpact: {
      caseCount: 4,
      dollarsAtRisk: 58850,
      recoverableNow: 45600,
      averageAgingDays: 9.6,
    },
    currentImpact: {
      caseCount: 2,
      dollarsAtRisk: 30450,
      recoverableNow: 30450,
      averageAgingDays: 8,
    },
  },
  {
    id: 'INT-03',
    title: 'Infusion support documentation sprint',
    owner: 'Infusion Documentation Liaison',
    targetCompletionDate: '2026-06-20',
    checkpointStatus: 'Needs revision',
    baselineMetric: 'Unsupported infusion charges: 18.6%',
    currentMetric: 'Unsupported infusion charges: 16.8%',
    recommendation: 'Revise',
    validationNote:
      'Improvement is modest; second-hour support templates need tighter adoption.',
    linkedCaseIds: ['RI-INF-0044', 'RI-INF-0075'],
    baselineImpact: {
      caseCount: 2,
      dollarsAtRisk: 17100,
      recoverableNow: 11850,
      averageAgingDays: 17.8,
    },
    currentImpact: {
      caseCount: 2,
      dollarsAtRisk: 17100,
      recoverableNow: 9800,
      averageAgingDays: 17.8,
    },
  },
  {
    id: 'INT-04',
    title: 'Denial-to-edit feedback rule tuning',
    owner: 'Denial Feedback Analyst',
    targetCompletionDate: '2026-06-28',
    checkpointStatus: 'Not started',
    baselineMetric: 'Repeat denial signal cases: 11',
    currentMetric: 'Repeat denial signal cases: 11',
    recommendation: 'Revise',
    validationNote:
      'No change yet; implementation work has not started in current cycle.',
    linkedCaseIds: ['RI-IR-0106', 'RI-OR-0052'],
    baselineImpact: {
      caseCount: 2,
      dollarsAtRisk: 31300,
      recoverableNow: 18100,
      averageAgingDays: 16,
    },
    currentImpact: {
      caseCount: 2,
      dollarsAtRisk: 31300,
      recoverableNow: 18100,
      averageAgingDays: 16,
    },
  },
]
