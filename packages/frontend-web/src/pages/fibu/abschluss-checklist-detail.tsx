import { useParams, useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { ArrowLeft, CheckCircle2, Circle } from 'lucide-react'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { toast } from 'sonner'

type ChecklistItem = {
  item_code: string
  description: string
  required?: boolean
  status: string
  completed_by?: string | null
  completed_at?: string | null
  notes?: string | null
}

type Checklist = {
  id: string
  period: string
  closing_type: string
  status: string
  progress_percentage: number
  total_items: number
  completed_items: number
  required_items: number
  completed_required_items: number
  items: ChecklistItem[]
  updated_at?: string | null
}

const EMPTY_CHECKLIST: Checklist = {
  id: '',
  period: '',
  closing_type: '',
  status: '',
  progress_percentage: 0,
  total_items: 0,
  completed_items: 0,
  required_items: 0,
  completed_required_items: 0,
  items: [],
  updated_at: null,
}

export default function AbschlussChecklistDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const isValidChecklistId = typeof id === 'string'
    && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id)

  const { data: checklist, isLoading, error } = useQuery({
    queryKey: ['finance', 'closing-checklist', id],
    queryFn: async () => (await apiClient.get<Checklist>(`/api/v1/finance/closing-checklists/${id}`)).data,
    enabled: !!id && isValidChecklistId,
    initialData: EMPTY_CHECKLIST,
  })

  const completeMutation = useMutation({
    mutationFn: async ({ itemCode }: { itemCode: string }) =>
      apiClient.post(`/api/v1/finance/closing-checklists/${id}/items/${itemCode}/complete`, {
        status: 'completed',
        completed_by: 'current-user',
      }),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'closing-checklist', id] })
      queryClient.invalidateQueries({ queryKey: ['finance', 'closing-cockpit-summary'] })
      toast.success('Aufgabe als erledigt markiert.')
      if (workflowInstanceId && workflowProcess) {
        try {
          const updated = (await apiClient.get<Checklist>(`/api/v1/finance/closing-checklists/${id}`)).data
          if (updated.completed_required_items >= updated.required_items) {
            await apiClient.post(`/api/v1/process/flow-spines/${workflowProcess}/instances/${workflowInstanceId}/transitions`, {
              node_id: 'abschluss-check',
              new_status: 'ok',
            })
          }
        } catch {
          // best effort only
        }
      }
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Aktion fehlgeschlagen'
      toast.error(msg)
    },
  })

  if (!id || !isValidChecklistId) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">Keine Checkliste ausgewaehlt.</p>
        <Button variant="link" onClick={() => navigate('/fibu/abschluss-cockpit')}>Zurueck zum Cockpit</Button>
      </div>
    )
  }

  if (isLoading) return <div className="p-6 text-sm text-muted-foreground">Lade Checkliste...</div>
  if (error) return <div className="p-6 text-sm text-red-600">Checkliste konnte nicht geladen werden.</div>

  const openRequiredItems = checklist.required_items - checklist.completed_required_items
  const openItems = checklist.total_items - checklist.completed_items
  const operationalStatus = normalizeOperationalStatus(
    checklist.status === 'completed'
      ? 'abgeschlossen'
      : openRequiredItems > 0
        ? 'wartet_auf_mensch'
        : openItems > 0
          ? 'in_pruefung'
          : 'abgeschlossen',
  )
  const contextSections = [
    {
      title: 'Abschlusslage',
      items: [
        { label: 'Periode', value: checklist.period || '-' },
        { label: 'Abschlussart', value: checklist.closing_type || '-' },
        { label: 'Pflicht offen', value: `${openRequiredItems}` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Workflow', value: workflowCase || workflowProcess || 'Lokaler Close-Fall' },
        { label: 'Fortschritt', value: `${checklist.progress_percentage.toFixed(0)}%` },
        { label: 'Naechste Aktion', value: openRequiredItems > 0 ? 'Pflichtpositionen schliessen' : openItems > 0 ? 'Restaufgaben finalisieren' : 'Close-Fall uebergeben' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: workflowInstanceId ? 'Flow-Spine-Verknuepfung aktiv' : 'Checkliste lokal geoeffnet',
      detail: workflowInstanceId
        ? `Instanz ${workflowInstanceId.slice(0, 8)} ist mit dem Abschlussfall verknuepft.`
        : 'Die Checkliste laeuft ohne explizite Flow-Spine-Instanz.',
      timestamp: checklist.updated_at ?? null,
    },
    {
      label: openRequiredItems > 0 ? 'Pflichtaufgaben offen' : 'Pflichtaufgaben geschlossen',
      detail: openRequiredItems > 0
        ? `${openRequiredItems} Pflichtpunkte blockieren den Abschluss weiterhin.`
        : 'Alle Pflichtpunkte sind erledigt und der Abschluss kann weitergezogen werden.',
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/fibu/abschluss-cockpit')}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Cockpit
        </Button>
      </div>
      {workflowInstanceId ? (
        <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
          Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      ) : null}
      <div>
        <h1 className="text-2xl font-bold">Checkliste: {checklist.period} - {checklist.closing_type}</h1>
        <p className="text-muted-foreground">
          Fortschritt: {checklist.completed_items}/{checklist.total_items} - Pflicht: {checklist.completed_required_items}/{checklist.required_items} - {checklist.progress_percentage.toFixed(0)}%
        </p>
      </div>

      <OperationalCaseHeader
        title={`Abschluss-Checkliste ${checklist.period}`}
        description="Pflichtpositionen, Owner und Flow-Spine-Lage werden oberhalb der Checkliste verdichtet."
        status={operationalStatus}
        owner="Finance Close"
        blocker={openRequiredItems > 0 ? `${openRequiredItems} Pflichtaufgaben blockieren den Abschluss.` : null}
        nextAction={openRequiredItems > 0 ? 'Pflichtaufgaben erledigen und Close erneut pruefen' : openItems > 0 ? 'Optionale Restaufgaben schliessen' : 'Abschluss in den naechsten Schritt uebergeben'}
        caseLabel="Vorgang: Abschluss-Check"
        tags={['FIBU', 'Close', workflowInstanceId ? 'Flow Spine' : 'Lokal']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Close-Verlauf" items={timelineItems} />
        <OperationalContextPanel title="Abschlusskontext" sections={contextSections} />
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Aufgaben</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(checklist.items ?? []).map((item) => (
            <div
              key={item.item_code}
              className="flex items-center justify-between rounded border p-3"
            >
              <div className="flex items-center gap-3">
                {item.status === 'completed' ? (
                  <CheckCircle2 className="h-5 w-5 shrink-0 text-green-600" />
                ) : (
                  <Circle className="h-5 w-5 shrink-0 text-muted-foreground" />
                )}
                <div>
                  <div className="font-medium">{item.description || item.item_code}</div>
                  {item.completed_at ? (
                    <div className="text-xs text-muted-foreground">
                      Erledigt am {new Date(item.completed_at).toLocaleDateString('de-DE')}
                      {item.completed_by ? ` von ${item.completed_by}` : ''}
                    </div>
                  ) : null}
                </div>
                {item.required ? <Badge variant="outline" className="text-xs">Pflicht</Badge> : null}
              </div>
              {item.status !== 'completed' ? (
                <Button
                  size="sm"
                  onClick={() => completeMutation.mutate({ itemCode: item.item_code })}
                  disabled={completeMutation.isPending}
                >
                  Erledigen
                </Button>
              ) : <Badge variant="secondary">Erledigt</Badge>}
            </div>
          ))}
          {(!checklist.items || checklist.items.length === 0) ? (
            <p className="text-sm text-muted-foreground">Keine Aufgaben in dieser Checkliste.</p>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}
