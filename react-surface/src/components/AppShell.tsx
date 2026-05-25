import type { ReactNode } from 'react'

interface AppShellProps {
  sidebar: ReactNode
  children: ReactNode
}

export function AppShell({ sidebar, children }: AppShellProps) {
  return (
    <div className="min-h-screen">
      <div className="mx-auto w-full max-w-[1600px] lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="lg:sticky lg:top-0 lg:h-screen lg:border-r lg:border-slate-900/80">
          {sidebar}
        </aside>

        <div className="min-w-0 px-4 pb-8 pt-4 sm:px-6 lg:px-8 lg:pt-8">
          <main>{children}</main>
        </div>
      </div>
    </div>
  )
}
