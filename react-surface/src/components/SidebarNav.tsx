import type { LucideIcon } from 'lucide-react'
import { NavLink } from 'react-router-dom'

export interface SidebarItem {
  label: string
  path: string
  icon: LucideIcon
  enabled: boolean
  end?: boolean
}

interface SidebarNavProps {
  items: SidebarItem[]
}

export function SidebarNav({ items }: SidebarNavProps) {
  return (
    <div className="flex h-full flex-col bg-slate-950 px-5 pb-6 pt-7 text-slate-100">
      <div>
        <p className="text-xs uppercase tracking-[0.26em] text-slate-400">
          Revenue Integrity
        </p>
        <h1 className="font-heading mt-2 text-2xl leading-tight text-slate-100">
          Control Room
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Facility-side outpatient deterministic workflow.
        </p>
      </div>

      <nav aria-label="Primary navigation" className="mt-8 space-y-2">
        {items.map((item) => {
          const Icon = item.icon

          if (!item.enabled) {
            return (
              <div
                key={item.path}
                className="flex cursor-not-allowed items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/40 px-3 py-3 text-sm text-slate-500"
                aria-disabled="true"
              >
                <Icon size={16} aria-hidden="true" />
                <span>{item.label}</span>
                <span className="ml-auto rounded-full border border-slate-700 px-2 py-0.5 text-[11px]">
                  Soon
                </span>
              </div>
            )
          }

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 rounded-xl border px-3 py-3 text-sm font-medium transition',
                  isActive
                    ? 'border-emerald-300/40 bg-emerald-400/10 text-emerald-100 shadow-[0_8px_20px_rgba(16,185,129,0.18)]'
                    : 'border-slate-800 bg-slate-900/60 text-slate-200 hover:border-slate-600 hover:bg-slate-800',
                ].join(' ')
              }
            >
              <Icon size={16} aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="mt-auto rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-xs text-slate-400">
        <p className="font-semibold uppercase tracking-[0.14em] text-slate-300">
          V1 Scope
        </p>
        <p className="mt-2">
          Outpatient infusion, radiology/IR, and OR procedural flows only.
        </p>
      </div>
    </div>
  )
}
