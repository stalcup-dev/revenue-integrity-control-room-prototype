import { Filter, Search, X } from 'lucide-react'

import type {
  GlobalFiltersState,
  QueueName,
  RecoverabilityStatus,
} from '../data/types'

interface FilterOptions {
  departments: string[]
  serviceLines: string[]
  queues: QueueName[]
  recoverability: RecoverabilityStatus[]
}

interface GlobalFiltersProps {
  filters: GlobalFiltersState
  options: FilterOptions
  onChange: (next: GlobalFiltersState) => void
}

interface ActiveFilterChip {
  id: keyof Omit<GlobalFiltersState, 'search'> | 'search'
  label: string
}

export function GlobalFilters({ filters, options, onChange }: GlobalFiltersProps) {
  const chips: ActiveFilterChip[] = [
    filters.department !== 'All'
      ? { id: 'department', label: `Department: ${filters.department}` }
      : null,
    filters.serviceLine !== 'All'
      ? { id: 'serviceLine', label: `Service line: ${filters.serviceLine}` }
      : null,
    filters.queue !== 'All' ? { id: 'queue', label: `Queue: ${filters.queue}` } : null,
    filters.recoverability !== 'All'
      ? { id: 'recoverability', label: `Recoverability: ${filters.recoverability}` }
      : null,
    filters.search.trim().length > 0
      ? { id: 'search', label: `Search: ${filters.search.trim()}` }
      : null,
  ].filter((chip): chip is ActiveFilterChip => chip !== null)

  function updateFilter<K extends keyof GlobalFiltersState>(
    key: K,
    value: GlobalFiltersState[K],
  ) {
    onChange({ ...filters, [key]: value })
  }

  function clearChip(chip: ActiveFilterChip) {
    if (chip.id === 'search') {
      updateFilter('search', '')
      return
    }

    updateFilter(chip.id, 'All')
  }

  return (
    <section aria-label="Global filters">
      <div className="flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-slate-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">
          <Filter size={14} aria-hidden="true" />
          Global Filters
        </span>
        <p className="text-sm text-slate-600">
          Persisted across routes for department, queue, and recoverability scope.
        </p>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <label className="text-sm font-semibold text-slate-700" htmlFor="filter-department">
          Department
          <select
            id="filter-department"
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            value={filters.department}
            onChange={(event) => updateFilter('department', event.target.value)}
          >
            <option value="All">All departments</option>
            {options.departments.map((department) => (
              <option key={department} value={department}>
                {department}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm font-semibold text-slate-700" htmlFor="filter-service-line">
          Service line
          <select
            id="filter-service-line"
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            value={filters.serviceLine}
            onChange={(event) => updateFilter('serviceLine', event.target.value)}
          >
            <option value="All">All service lines</option>
            {options.serviceLines.map((serviceLine) => (
              <option key={serviceLine} value={serviceLine}>
                {serviceLine}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm font-semibold text-slate-700" htmlFor="filter-queue">
          Queue
          <select
            id="filter-queue"
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            value={filters.queue}
            onChange={(event) => updateFilter('queue', event.target.value as QueueName | 'All')}
          >
            <option value="All">All queues</option>
            {options.queues.map((queue) => (
              <option key={queue} value={queue}>
                {queue}
              </option>
            ))}
          </select>
        </label>

        <label
          className="text-sm font-semibold text-slate-700"
          htmlFor="filter-recoverability"
        >
          Recoverability
          <select
            id="filter-recoverability"
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            value={filters.recoverability}
            onChange={(event) =>
              updateFilter(
                'recoverability',
                event.target.value as RecoverabilityStatus | 'All',
              )
            }
          >
            <option value="All">All recoverability states</option>
            {options.recoverability.map((recoverability) => (
              <option key={recoverability} value={recoverability}>
                {recoverability}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm font-semibold text-slate-700" htmlFor="filter-search">
          Search
          <span className="relative mt-1 block">
            <Search
              size={16}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
              aria-hidden="true"
            />
            <input
              id="filter-search"
              type="search"
              placeholder="Case ID, owner, blocker, department"
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              value={filters.search}
              onChange={(event) => updateFilter('search', event.target.value)}
            />
          </span>
        </label>
      </div>

      <div className="mt-4 min-h-[2rem]">
        {chips.length === 0 ? (
          <p className="text-sm text-slate-500">No active filters. Showing all cases.</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {chips.map((chip) => (
              <li key={chip.id}>
                <button
                  type="button"
                  className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 transition hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  onClick={() => clearChip(chip)}
                >
                  {chip.label}
                  <X size={12} aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
