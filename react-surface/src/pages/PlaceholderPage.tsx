interface PlaceholderPageProps {
  title: string
}

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="font-heading text-3xl text-slate-900">{title}</h2>
      <p className="mt-3 max-w-2xl text-sm text-slate-600">
        This route is intentionally stubbed for the first implementation slice. Global
        filters remain active and persisted while navigation is being scaffolded.
      </p>
    </section>
  )
}
