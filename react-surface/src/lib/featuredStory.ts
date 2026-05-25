import type { Priority, RecoverabilityStatus, RevenueIntegrityCase } from '../data/types'

interface FeaturedStory {
  caseId: string
  score: number
  rationale: string
}

const priorityWeight: Record<Priority, number> = {
  Critical: 100,
  High: 75,
  Medium: 45,
  Low: 20,
}

const recoverabilityWeight: Record<RecoverabilityStatus, number> = {
  'Pre-final-bill recoverable': 30,
  'Post-final-bill recoverable by correction / rebill': 18,
  'Post-window financially lost': 10,
  'Financially closed but still compliance-relevant': 6,
}

const activeQueueBonus = new Set([
  'Prebill edit / hold',
  'Charge capture pending',
  'Documentation pending',
  'Coding pending',
  'Correction / rebill pending',
])

export function selectFeaturedStory(cases: RevenueIntegrityCase[]): FeaturedStory | null {
  if (cases.length === 0) {
    return null
  }

  let featured: FeaturedStory | null = null

  for (const caseItem of cases) {
    const score = computeFeaturedStoryScore(caseItem)

    if (!featured || score > featured.score) {
      featured = {
        caseId: caseItem.id,
        score,
        rationale: buildRationale(caseItem),
      }
      continue
    }

    if (score === featured.score) {
      const featuredCase = cases.find((item) => item.id === featured?.caseId)

      if (featuredCase && caseItem.dollarsAtRisk > featuredCase.dollarsAtRisk) {
        featured = {
          caseId: caseItem.id,
          score,
          rationale: buildRationale(caseItem),
        }
      }
    }
  }

  return featured
}

function computeFeaturedStoryScore(caseItem: RevenueIntegrityCase): number {
  const priorityScore = priorityWeight[caseItem.priority]
  const recoverabilityScore = recoverabilityWeight[caseItem.recoverabilityStatus]
  const dollarsScore = Math.min(caseItem.dollarsAtRisk / 1000, 45)
  const agingScore = Math.min(caseItem.agingDays, 35) * 1.2
  const queueScore = activeQueueBonus.has(caseItem.queue) ? 12 : 0
  const blockerSignalScore = /missing|unresolved|failed|hold|expired/i.test(
    caseItem.currentPrimaryBlocker,
  )
    ? 8
    : 0

  return roundTo(
    priorityScore +
      recoverabilityScore +
      dollarsScore +
      agingScore +
      queueScore +
      blockerSignalScore,
    2,
  )
}

function buildRationale(caseItem: RevenueIntegrityCase): string {
  return `${caseItem.priority} priority with ${caseItem.recoverabilityStatus.toLowerCase()} status, ${caseItem.agingDays} day blocker aging, and ${new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(caseItem.dollarsAtRisk)} at risk.`
}

function roundTo(value: number, decimals: number): number {
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}
