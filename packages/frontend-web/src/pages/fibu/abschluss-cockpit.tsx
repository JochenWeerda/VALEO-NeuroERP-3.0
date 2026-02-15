import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'

type CockpitChecklist = {
  id: string
  period: string
  closing_type: string
  status: string
  progress_percentage: number
  completed_required_items: number
  required_items: number
  updated_at?: string | null
}

type ClosingCockpitSummary = {
  tenant_id: string
  period?: string | null
  periods: { open: number; closed: number; adjusting: number }
  checklists: { total: number; completed: number; in_progress: number; blocked: number; avg_progress: number }
  blockers: CockpitChecklist[]
  latest_checklists: CockpitChecklist[]
}

export default function AbschlussCockpitPage(): JSX.Element {
  const { data, isLoading, error } = useQuery({
    queryKey: ['finance', 'closing-cockpit-summary'],
    queryFn: async () => (await apiClient.get<ClosingCockpitSummary>('/api/v1/finance/closing-checklists/cockpit/summary')).data,
    staleTime: 30_000,
  })

  const blockers = useMemo(() => data?.blockers ?? [], [data])

  if (isLoading) {
    return <div className="p-6 text-sm text-muted-foreground">Lade Abschluss-Cockpit...</div>
  }

  if (error || !data) {
    return <div className="p-6 text-sm text-red-600">Abschluss-Cockpit konnte nicht geladen werden.</div>
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Abschluss-Cockpit</h1>
        <p className="text-muted-foreground">Status der Perioden und Abschluss-Checklisten inkl. Blocker-Uebersicht.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Perioden offen</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{data.periods.open}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Checklisten total</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{data.checklists.total}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Abgeschlossen</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{data.checklists.completed}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Blocker</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{blockers.length}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Aktuelle Checklisten</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {data.latest_checklists.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded border p-3">
              <div>
                <div className="font-medium">{item.period} · {item.closing_type}</div>
                <div className="text-xs text-muted-foreground">
                  Pflicht: {item.completed_required_items}/{item.required_items} · Fortschritt: {item.progress_percentage.toFixed(1)}%
                </div>
              </div>
              <Badge variant={item.status === 'blocked' ? 'destructive' : 'outline'}>{item.status}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
