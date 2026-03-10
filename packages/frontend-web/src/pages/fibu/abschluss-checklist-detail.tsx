/**
 * Detail-UI für eine Abschluss-Checkliste (FIBU-CLS-01).
 * Lädt GET /api/v1/finance/closing-checklists/:id und erlaubt Erledigen von Aufgaben.
 */

import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { ArrowLeft, CheckCircle2, Circle } from 'lucide-react'
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'closing-checklist', id] })
      queryClient.invalidateQueries({ queryKey: ['finance', 'closing-cockpit-summary'] })
      toast.success('Aufgabe als erledigt markiert.')
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Aktion fehlgeschlagen'
      toast.error(msg)
    },
  })

  if (!id || !isValidChecklistId) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">Keine Checkliste ausgewählt.</p>
        <Button variant="link" onClick={() => navigate('/fibu/abschluss-cockpit')}>← Zum Cockpit</Button>
      </div>
    )
  }

  if (isLoading) return <div className="p-6 text-sm text-muted-foreground">Lade Checkliste…</div>
  if (error) return <div className="p-6 text-sm text-red-600">Checkliste konnte nicht geladen werden.</div>

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/fibu/abschluss-cockpit')}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Cockpit
        </Button>
      </div>
      <div>
        <h1 className="text-2xl font-bold">Checkliste: {checklist.period} · {checklist.closing_type}</h1>
        <p className="text-muted-foreground">
          Fortschritt: {checklist.completed_items}/{checklist.total_items} · Pflicht: {checklist.completed_required_items}/{checklist.required_items} · {checklist.progress_percentage.toFixed(0)}%
        </p>
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
                  <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0" />
                ) : (
                  <Circle className="h-5 w-5 text-muted-foreground shrink-0" />
                )}
                <div>
                  <div className="font-medium">{item.description || item.item_code}</div>
                  {item.completed_at && (
                    <div className="text-xs text-muted-foreground">
                      Erledigt am {new Date(item.completed_at).toLocaleDateString('de-DE')}
                      {item.completed_by ? ` von ${item.completed_by}` : ''}
                    </div>
                  )}
                </div>
                {item.required && <Badge variant="outline" className="text-xs">Pflicht</Badge>}
              </div>
              {item.status !== 'completed' && (
                <Button
                  size="sm"
                  onClick={() => completeMutation.mutate({ itemCode: item.item_code })}
                  disabled={completeMutation.isPending}
                >
                  Erledigen
                </Button>
              )}
              {item.status === 'completed' && <Badge variant="secondary">Erledigt</Badge>}
            </div>
          ))}
          {(!checklist.items || checklist.items.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Aufgaben in dieser Checkliste.</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}



