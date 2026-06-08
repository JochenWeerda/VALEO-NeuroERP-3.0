import { useEffect } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { ChevronRight, Layers } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useFlowSpineCatalogHook, warmFlowSpineCache } from '@/lib/api/flow-spines'

const DOMAIN_COLORS: Record<string, string> = {
  sales: 'bg-emerald-500/15 text-emerald-200',
  procurement: 'bg-blue-500/15 text-blue-200',
  inventory: 'bg-amber-500/15 text-amber-100',
  agrar: 'bg-lime-500/15 text-lime-200',
  contracts: 'bg-violet-500/15 text-violet-200',
  crm: 'bg-rose-500/15 text-rose-200',
  finance: 'bg-indigo-500/15 text-indigo-200',
  compliance: 'bg-slate-400/15 text-slate-200',
}

export default function FlowSpineStudioPage(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const catalogQuery = useFlowSpineCatalogHook()
  const { data: catalog, isLoading, isError } = catalogQuery

  // Warm the workspace cache for all flow-spine processes as soon as the
  // catalog has loaded, so navigation to any process page feels instant.
  useEffect(() => {
    if (catalogQuery.isSuccess) {
      warmFlowSpineCache(queryClient)
    }
  }, [catalogQuery.isSuccess, queryClient])

  if (isLoading) {
    return (
      <PageSurface data-page-surface="flow-spine-studio">
        <PageSection title="Flow Spine Studio" description="Prozesskatalog wird geladen…">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-32 animate-pulse rounded-2xl border border-white/5 bg-white/[0.03]" />
            ))}
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  if (isError || !catalog) {
    return (
      <PageSurface data-page-surface="flow-spine-studio">
        <PageSection title="Flow Spine Studio" description="Prozesskatalog nicht verfügbar.">
          <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-6 text-sm text-destructive">
            Backend-Verbindung prüfen: GET /api/v1/process/flow-spines/catalog
          </div>
        </PageSection>
      </PageSurface>
    )
  }

  const processes = catalog.processes ?? []

  return (
    <PageSurface
      data-page-surface="flow-spine-studio"
      className="bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.10),_transparent_30%),linear-gradient(180deg,#08101f,#0d1528)]"
    >
      <PageSection
        title=""
        description=""
        className="border-white/10 bg-slate-950/70 p-6 shadow-2xl shadow-indigo-950/20"
      >
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/20 text-indigo-300">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Flow Spine Studio</h1>
            <p className="text-sm text-slate-400">Alle Prozessräume auf einen Blick — {processes.length} Prozesse verfügbar</p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {processes.map((process) => (
            <Card
              key={process.key}
              className="cursor-pointer border-white/10 bg-white/[0.03] text-slate-100 transition hover:bg-white/[0.06] hover:shadow-lg hover:shadow-indigo-950/30"
              onClick={() => navigate(process.route_path)}
            >
              <CardHeader className="flex flex-row items-start justify-between gap-3 pb-2">
                <CardTitle className="text-base leading-snug">{process.label}</CardTitle>
                <Badge className={DOMAIN_COLORS[process.domain] ?? 'bg-slate-500/15 text-slate-300'}>
                  {process.domain}
                </Badge>
              </CardHeader>
              <CardContent className="flex items-end justify-between">
                <p className="text-sm text-slate-400">{process.summary}</p>
                <ChevronRight className="ml-3 h-4 w-4 shrink-0 text-slate-500" />
              </CardContent>
            </Card>
          ))}
        </div>
      </PageSection>
    </PageSurface>
  )
}
