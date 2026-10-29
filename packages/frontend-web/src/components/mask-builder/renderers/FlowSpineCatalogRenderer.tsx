import { useNavigate } from '@/app/routing/typed-router'
import type { FlowSpineCatalogState } from '../runtime/useFlowSpineCatalogRuntime'

/** Accessible, theme-aware catalog primitive; data and reads belong to runtime. */
export function FlowSpineCatalogRenderer({ state }: { state?: FlowSpineCatalogState }): JSX.Element {
  const navigate = useNavigate()
  if (!state || state.loading) return <p role="status">Prozesskatalog wird geladen…</p>
  if (state.failed) return <section role="alert"><p>Prozesskatalog nicht verfügbar.</p><button type="button" className="rounded border border-border px-3 py-2" onClick={state.retry}>Erneut versuchen</button></section>
  const processes = state.catalog?.processes ?? []
  return <section aria-label="Prozesskatalog" className="space-y-4 p-4">
    <p className="text-muted-foreground">Alle Prozessräume auf einen Blick — {processes.length} Prozesse verfügbar</p>
    {processes.length === 0 && <p role="status">Keine Prozesse verfügbar.</p>}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{processes.map(process => {
      const validRoute = /^\/workflow\/flow-spine-[a-z0-9-]+$/.test(process.route_path)
      return <button type="button" key={process.key} disabled={!validRoute} onClick={() => navigate(process.route_path)}
        className="rounded-lg border border-border bg-card p-4 text-left text-card-foreground transition hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50">
        <span className="flex items-start justify-between gap-3"><span className="font-semibold">{process.label}</span><span className="rounded border border-border px-2 py-0.5 text-xs text-muted-foreground">{process.domain}</span></span>
        <span className="mt-2 block text-sm text-muted-foreground">{process.summary}</span>
        {!validRoute && <span className="block text-sm text-destructive">Prozessziel nicht verfügbar.</span>}
      </button>
    })}</div>
  </section>
}
