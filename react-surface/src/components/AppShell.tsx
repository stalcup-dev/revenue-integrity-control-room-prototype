import type { ReactNode } from 'react'

interface AppShellProps {
  sidebar: ReactNode
  filters: ReactNode
  children: ReactNode
}

export function AppShell({ sidebar, filters, children }: AppShellProps) {
  return (
    <div className="min-h-screen">
      <div className="mx-auto w-full max-w-[1600px] lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="lg:sticky lg:top-0 lg:h-screen lg:border-r lg:border-slate-900/80">
          {sidebar}
        </aside>

        <div className="min-w-0 px-4 pb-8 pt-4 sm:px-6 lg:px-8 lg:pt-8">
          <div className="mb-6 rounded-2xl border border-slate-200/80 bg-white/90 p-4 shadow-sm backdrop-blur-sm">
            {filters}
          </div>
          <main>{children}</main>
        </div>
      </div>
    </div>
  )
}
