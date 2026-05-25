import {
  ClipboardList,
  FileClock,
  FileSearch,
  LayoutDashboard,
  ShieldAlert,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from './components/AppShell'
import { GlobalFilters } from './components/GlobalFilters'
import { SidebarNav, type SidebarItem } from './components/SidebarNav'
import { interventionTracking } from './data/interventionTracking'
import { revenueIntegrityCases } from './data/revenueIntegrityCases'
import type { GlobalFiltersState, Priority, RevenueIntegrityCase } from './data/types'
import { ChargeReconciliationPage } from './pages/ChargeReconciliationPage'
import { ControlRoomSummaryPage } from './pages/ControlRoomSummaryPage'
import { DocumentationExceptionsPage } from './pages/DocumentationExceptionsPage'
import { PrebillHoldsPage } from './pages/PrebillHoldsPage'
import { PlaceholderPage } from './pages/PlaceholderPage'

const navigationItems: SidebarItem[] = [
  {
    label: 'Control Room Summary',
    path: '/',
    icon: LayoutDashboard,
    enabled: true,
    end: true,
  },
  {
    label: 'Charge Reconciliation',
    path: '/charge-reconciliation',
    icon: FileSearch,
    enabled: true,
  },
  {
    label: 'Prebill Holds',
    path: '/prebill-holds',
    icon: FileClock,
    enabled: true,
  },
  {
    label: 'Documentation Exceptions',
    path: '/documentation-exceptions',
    icon: ShieldAlert,
    enabled: true,
  },
  {
    label: 'Action Tracker',
    path: '/action-tracker',
    icon: ClipboardList,
    enabled: false,
  },
]

const defaultFilters: GlobalFiltersState = {
  department: 'All',
  serviceLine: 'All',
  queue: 'All',
  recoverability: 'All',
  search: '',
}

const priorityRank: Record<Priority, number> = {
  Critical: 0,
  High: 1,
  Medium: 2,
  Low: 3,
}

function App() {
  const [filters, setFilters] = useState<GlobalFiltersState>(defaultFilters)
  const [selectedSummaryCaseId, setSelectedSummaryCaseId] = useState<string | null>(
    revenueIntegrityCases[0]?.id ?? null,
  )
  const [selectedReconciliationCaseId, setSelectedReconciliationCaseId] = useState<string | null>(
    revenueIntegrityCases[0]?.id ?? null,
  )
  const [selectedPrebillCaseId, setSelectedPrebillCaseId] = useState<string | null>(
    revenueIntegrityCases[0]?.id ?? null,
  )
  const [selectedDocumentationCaseId, setSelectedDocumentationCaseId] = useState<string | null>(
    revenueIntegrityCases[0]?.id ?? null,
  )

  const filterOptions = useMemo(
    () => ({
      departments: uniqueSortedValues(revenueIntegrityCases.map((caseItem) => caseItem.department)),
      serviceLines: uniqueSortedValues(
        revenueIntegrityCases.map((caseItem) => caseItem.serviceLine),
      ),
      queues: uniqueSortedValues(revenueIntegrityCases.map((caseItem) => caseItem.queue)),
      recoverability: uniqueSortedValues(
        revenueIntegrityCases.map((caseItem) => caseItem.recoverabilityStatus),
      ),
    }),
    [],
  )

  const filteredCases = useMemo(() => {
    const normalizedQuery = filters.search.trim().toLowerCase()

    return revenueIntegrityCases
      .filter((caseItem) => {
        if (filters.department !== 'All' && caseItem.department !== filters.department) {
          return false
        }

        if (filters.serviceLine !== 'All' && caseItem.serviceLine !== filters.serviceLine) {
          return false
        }

        if (filters.queue !== 'All' && caseItem.queue !== filters.queue) {
          return false
        }

        if (
          filters.recoverability !== 'All' &&
          caseItem.recoverabilityStatus !== filters.recoverability
        ) {
          return false
        }

        if (!normalizedQuery) {
          return true
        }

        return (
          caseItem.id.toLowerCase().includes(normalizedQuery) ||
          caseItem.owner.toLowerCase().includes(normalizedQuery) ||
          caseItem.currentPrimaryBlocker.toLowerCase().includes(normalizedQuery) ||
          caseItem.department.toLowerCase().includes(normalizedQuery) ||
          caseItem.serviceLine.toLowerCase().includes(normalizedQuery)
        )
      })
      .sort((a, b) => {
        if (priorityRank[a.priority] !== priorityRank[b.priority]) {
          return priorityRank[a.priority] - priorityRank[b.priority]
        }

        if (b.dollarsAtRisk !== a.dollarsAtRisk) {
          return b.dollarsAtRisk - a.dollarsAtRisk
        }

        return b.agingDays - a.agingDays
      })
  }, [filters])

  const effectiveSelectedCaseId = useMemo(() => {
    if (filteredCases.length === 0) {
      return null
    }

    if (
      selectedSummaryCaseId &&
      filteredCases.some((caseItem) => caseItem.id === selectedSummaryCaseId)
    ) {
      return selectedSummaryCaseId
    }

    return filteredCases[0].id
  }, [filteredCases, selectedSummaryCaseId])

  const reconciliationCases = useMemo(
    () => filteredCases.filter((caseItem) => isReconciliationCase(caseItem)),
    [filteredCases],
  )

  const effectiveSelectedReconciliationCaseId = useMemo(() => {
    if (reconciliationCases.length === 0) {
      return null
    }

    if (
      selectedReconciliationCaseId &&
      reconciliationCases.some((caseItem) => caseItem.id === selectedReconciliationCaseId)
    ) {
      return selectedReconciliationCaseId
    }

    return reconciliationCases[0].id
  }, [reconciliationCases, selectedReconciliationCaseId])

  const prebillCases = useMemo(
    () => filteredCases.filter((caseItem) => isPrebillHoldCase(caseItem)),
    [filteredCases],
  )

  const effectiveSelectedPrebillCaseId = useMemo(() => {
    if (prebillCases.length === 0) {
      return null
    }

    if (selectedPrebillCaseId && prebillCases.some((caseItem) => caseItem.id === selectedPrebillCaseId)) {
      return selectedPrebillCaseId
    }

    return prebillCases[0].id
  }, [prebillCases, selectedPrebillCaseId])

  const documentationCases = useMemo(
    () => filteredCases.filter((caseItem) => isDocumentationExceptionCase(caseItem)),
    [filteredCases],
  )

  const effectiveSelectedDocumentationCaseId = useMemo(() => {
    if (documentationCases.length === 0) {
      return null
    }

    if (
      selectedDocumentationCaseId &&
      documentationCases.some((caseItem) => caseItem.id === selectedDocumentationCaseId)
    ) {
      return selectedDocumentationCaseId
    }

    return documentationCases[0].id
  }, [documentationCases, selectedDocumentationCaseId])

  const metrics = useMemo(() => {
    if (filteredCases.length === 0) {
      return {
        dollarsAtRisk: 0,
        recoverableNow: 0,
        averageAging: 0,
        activeCases: 0,
      }
    }

    const dollarsAtRisk = filteredCases.reduce(
      (runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk,
      0,
    )
    const recoverableNow = filteredCases.reduce(
      (runningTotal, caseItem) => runningTotal + caseItem.dollarsRecoverableNow,
      0,
    )
    const averageAging =
      filteredCases.reduce((runningTotal, caseItem) => runningTotal + caseItem.agingDays, 0) /
      filteredCases.length

    return {
      dollarsAtRisk,
      recoverableNow,
      averageAging: Math.round(averageAging * 10) / 10,
      activeCases: filteredCases.length,
    }
  }, [filteredCases])

  const reconciliationMetrics = useMemo(() => {
    if (reconciliationCases.length === 0) {
      return {
        reconciliationCases: 0,
        unreconciledRate: 0,
        lateChargePressure: 0,
        averageAging: 0,
      }
    }

    const unresolvedCases = reconciliationCases.filter((caseItem) =>
      isUnresolvedReconciliationCase(caseItem),
    )

    const lateChargePressure = unresolvedCases
      .filter((caseItem) => caseItem.agingDays > 7)
      .reduce((runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk, 0)

    const averageAging =
      unresolvedCases.length === 0
        ? 0
        : unresolvedCases.reduce((runningTotal, caseItem) => runningTotal + caseItem.agingDays, 0) /
          unresolvedCases.length

    return {
      reconciliationCases: reconciliationCases.length,
      unreconciledRate: Math.round((unresolvedCases.length / reconciliationCases.length) * 100),
      lateChargePressure,
      averageAging: Math.round(averageAging * 10) / 10,
    }
  }, [reconciliationCases])

  const prebillMetrics = useMemo(() => {
    if (prebillCases.length === 0) {
      return {
        activeHolds: 0,
        dollarsHeldPreFinalBill: 0,
        averageHoldAging: 0,
        overSevenDayHoldRate: 0,
        overSevenDayHoldCount: 0,
      }
    }

    const activeHolds = prebillCases.filter((caseItem) => isActivePrebillHoldCase(caseItem))
    const dollarsHeldPreFinalBill = activeHolds.reduce(
      (runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk,
      0,
    )
    const averageHoldAging =
      activeHolds.length === 0
        ? 0
        : activeHolds.reduce((runningTotal, caseItem) => runningTotal + caseItem.agingDays, 0) /
          activeHolds.length
    const overSevenDayHoldCount = activeHolds.filter((caseItem) => caseItem.agingDays > 7).length

    return {
      activeHolds: activeHolds.length,
      dollarsHeldPreFinalBill,
      averageHoldAging: Math.round(averageHoldAging * 10) / 10,
      overSevenDayHoldRate:
        activeHolds.length === 0 ? 0 : Math.round((overSevenDayHoldCount / activeHolds.length) * 100),
      overSevenDayHoldCount,
    }
  }, [prebillCases])

  const documentationMetrics = useMemo(() => {
    if (documentationCases.length === 0) {
      return {
        documentationExceptionCases: 0,
        unsupportedChargePressure: 0,
        averageExceptionAging: 0,
        activeDocumentationPendingRate: 0,
        activeDocumentationPendingCount: 0,
        postWindowDocumentationLoss: 0,
      }
    }

    const activeDocumentationPendingCases = documentationCases.filter((caseItem) =>
      isActiveDocumentationExceptionCase(caseItem),
    )
    const unsupportedChargePressure = documentationCases.reduce(
      (runningTotal, caseItem) => runningTotal + caseItem.dollarsAtRisk,
      0,
    )
    const averageExceptionAging =
      documentationCases.reduce((runningTotal, caseItem) => runningTotal + caseItem.agingDays, 0) /
      documentationCases.length
    const postWindowDocumentationLoss = documentationCases
      .filter((caseItem) => caseItem.recoverabilityStatus === 'Post-window financially lost')
      .reduce((runningTotal, caseItem) => runningTotal + caseItem.dollarsAlreadyLost, 0)

    return {
      documentationExceptionCases: documentationCases.length,
      unsupportedChargePressure,
      averageExceptionAging: Math.round(averageExceptionAging * 10) / 10,
      activeDocumentationPendingRate: Math.round(
        (activeDocumentationPendingCases.length / documentationCases.length) * 100,
      ),
      activeDocumentationPendingCount: activeDocumentationPendingCases.length,
      postWindowDocumentationLoss,
    }
  }, [documentationCases])

  return (
    <BrowserRouter>
      <AppShell
        sidebar={<SidebarNav items={navigationItems} />}
        filters={
          <GlobalFilters
            filters={filters}
            options={filterOptions}
            onChange={setFilters}
          />
        }
      >
        <Routes>
          <Route
            path="/"
            element={
              <ControlRoomSummaryPage
                filteredCases={filteredCases}
                selectedCaseId={effectiveSelectedCaseId}
                onSelectCase={setSelectedSummaryCaseId}
                interventions={interventionTracking}
                metrics={metrics}
              />
            }
          />
          <Route
            path="/control-room-summary"
            element={
              <ControlRoomSummaryPage
                filteredCases={filteredCases}
                selectedCaseId={effectiveSelectedCaseId}
                onSelectCase={setSelectedSummaryCaseId}
                interventions={interventionTracking}
                metrics={metrics}
              />
            }
          />
          <Route
            path="/charge-reconciliation"
            element={
              <ChargeReconciliationPage
                cases={reconciliationCases}
                selectedCaseId={effectiveSelectedReconciliationCaseId}
                onSelectCase={setSelectedReconciliationCaseId}
                metrics={reconciliationMetrics}
              />
            }
          />
          <Route
            path="/prebill-holds"
            element={
              <PrebillHoldsPage
                cases={prebillCases}
                selectedCaseId={effectiveSelectedPrebillCaseId}
                onSelectCase={setSelectedPrebillCaseId}
                metrics={prebillMetrics}
              />
            }
          />
          <Route
            path="/documentation-exceptions"
            element={
              <DocumentationExceptionsPage
                cases={documentationCases}
                selectedCaseId={effectiveSelectedDocumentationCaseId}
                onSelectCase={setSelectedDocumentationCaseId}
                metrics={documentationMetrics}
              />
            }
          />
          <Route path="/action-tracker" element={<PlaceholderPage title="Action Tracker" />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

function uniqueSortedValues<T extends string>(values: T[]): T[] {
  return Array.from(new Set(values)).sort((first, second) => first.localeCompare(second))
}

function isReconciliationCase(caseItem: RevenueIntegrityCase): boolean {
  switch (caseItem.issueDomain) {
    case 'Charge capture failure':
    case 'Charge integrity / configuration failure':
    case 'Patient status / case classification failure':
    case 'Coding failure':
    case 'Billing / claim-edit failure':
      return true
    default:
      return false
  }
}

function isUnresolvedReconciliationCase(caseItem: RevenueIntegrityCase): boolean {
  return (
    caseItem.queue !== 'Final billed' &&
    caseItem.queue !== 'Closed / monitored through denial feedback only'
  )
}

function isPrebillHoldCase(caseItem: RevenueIntegrityCase): boolean {
  return (
    caseItem.queue === 'Prebill edit / hold' ||
    caseItem.queue === 'Coding pending' ||
    caseItem.issueDomain === 'Billing / claim-edit failure' ||
    caseItem.issueDomain === 'Coding failure'
  )
}

function isActivePrebillHoldCase(caseItem: RevenueIntegrityCase): boolean {
  return (
    caseItem.recoverabilityStatus === 'Pre-final-bill recoverable' &&
    caseItem.queue !== 'Ready to final bill' &&
    caseItem.queue !== 'Final billed' &&
    caseItem.queue !== 'Closed / monitored through denial feedback only'
  )
}

function isDocumentationExceptionCase(caseItem: RevenueIntegrityCase): boolean {
  return (
    caseItem.issueDomain === 'Documentation support failure' ||
    caseItem.queue === 'Documentation pending'
  )
}

function isActiveDocumentationExceptionCase(caseItem: RevenueIntegrityCase): boolean {
  return (
    caseItem.queue === 'Documentation pending' &&
    caseItem.recoverabilityStatus === 'Pre-final-bill recoverable'
  )
}

export default App
