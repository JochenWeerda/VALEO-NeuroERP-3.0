import { useMemo } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api-client'
import { useAccountingPeriods, useFibuCockpit } from '@/lib/api/fibu'

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

const EMPTY_CLOSING_COCKPIT_SUMMARY: ClosingCockpitSummary = {
  tenant_id: '',
  period: null,
  periods: { open: 0, closed: 0, adjusting: 0 },
  checklists: { total: 0, completed: 0, in_progress: 0, blocked: 0, avg_progress: 0 },
  blockers: [],
  latest_checklists: [],
}

export default function AbschlussCockpitPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')

  const { data, isLoading, error } = useQuery({
    queryKey: ['finance', 'closing-cockpit-summary'],
    queryFn: async () => (await apiClient.get<ClosingCockpitSummary>('/api/v1/finance/closing-checklists/cockpit/summary')).data,
    initialData: EMPTY_CLOSING_COCKPIT_SUMMARY,
    staleTime: 30_000,
  })
  const { data: fibuCockpit } = useFibuCockpit()
  const { data: periods } = useAccountingPeriods()

  const blockers = useMemo(() => data.blockers, [data])
  const adjustingPeriods = periods.filter((period) => period.status === 'ADJUSTING').length

  if (isLoading) {
    return <div className="p-6 text-sm text-muted-foreground">Lade Abschluss-Cockpit...</div>
  }

  if (error) {
    return <div className="p-6 text-sm text-red-600">Abschluss-Cockpit konnte nicht geladen werden.</div>
  }

  return (
    <div className="space-y-6 p-6">
      {workflowInstanceId && (
        <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
          Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      )}
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

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Jahreswechsel</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Reorganisator</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{adjustingPeriods}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Exportläufe</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{fibuCockpit.revision.export_runs}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Mahn-/Zinsparameter</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.master_data.dunning_parameters_ready && fibuCockpit.master_data.interest_groups_ready ? 'vollständig' : 'prüfen'}</div></CardContent>
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
              <div className="flex items-center gap-2">
                <Badge variant={item.status === 'blocked' ? 'destructive' : 'outline'}>{item.status}</Badge>
                <Button variant="outline" size="sm" asChild>
                  <Link to={`/fibu/abschluss-checklist-detail/${item.id}${workflowInstanceId ? `?workflowInstanceId=${workflowInstanceId}&workflowProcess=${workflowProcess ?? ''}&workflowCase=${workflowCase ?? ''}` : ''}`}>Details</Link>
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
