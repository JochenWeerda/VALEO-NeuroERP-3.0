import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useControllingActions,
  useCreateAction,
  useDeleteAction,
  useUpdateAction,
  useControllingDashboards,
  useControllingKpis,
  type ActionInput,
  type ControllingAction,
} from '@/lib/api/controlling'
import { useToast } from '@/components/ui/toast-provider'

const EMPTY: ActionInput = {
  kpi_id: '',
  dashboard_id: '',
  title: '',
  description: '',
  owner_user_id: '',
  status: 'open',
  due_date: '',
}

export default function MassnahmenPage(): JSX.Element {
  const { push } = useToast()
  const { data: actions, isLoading } = useControllingActions()
  const { data: kpis } = useControllingKpis()
  const { data: dashboards } = useControllingDashboards()
  const createMutation = useCreateAction()
  const updateMutation = useUpdateAction()
  const deleteMutation = useDeleteAction()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<ActionInput>(EMPTY)

  const list = useMemo(() => actions ?? [], [actions])
  const busy = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  const reset = (): void => {
    setEditingId(null)
    setForm(EMPTY)
  }

  const startEdit = (item: ControllingAction): void => {
    setEditingId(item.id)
    setForm({
      kpi_id: item.kpi_id ?? '',
      dashboard_id: item.dashboard_id ?? '',
      title: item.title,
      description: item.description ?? '',
      owner_user_id: item.owner_user_id ?? '',
      status: item.status || 'open',
      due_date: item.due_date ?? '',
    })
  }

  const save = (): void => {
    if (!form.title?.trim()) {
      push('Bitte Titel angeben.')
      return
    }
    const payload: ActionInput = {
      ...form,
      kpi_id: form.kpi_id || undefined,
      dashboard_id: form.dashboard_id || undefined,
      owner_user_id: form.owner_user_id || undefined,
      due_date: form.due_date || undefined,
    }
    const onError = (error: unknown): void => {
      push(error instanceof Error ? error.message : 'Speichern fehlgeschlagen.')
    }

    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data: payload },
        {
          onSuccess: () => {
            push('Massnahme aktualisiert.')
            reset()
          },
          onError,
        },
      )
      return
    }
    createMutation.mutate(payload, {
      onSuccess: () => {
        push('Massnahme angelegt.')
        reset()
      },
      onError,
    })
  }

  const remove = (id: string): void => {
    deleteMutation.mutate(id, {
      onSuccess: () => push('Massnahme geloescht.'),
      onError: (error) => push(error instanceof Error ? error.message : 'Loeschen fehlgeschlagen.'),
    })
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Massnahmen</h1>
        <p className="text-muted-foreground">Abweichungsanalyse und Follow-up-Aufgaben</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editingId ? 'Massnahme bearbeiten' : 'Massnahme anlegen'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="action-title">Titel</Label>
            <Input id="action-title" value={form.title ?? ''} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="action-description">Beschreibung</Label>
            <Input id="action-description" value={form.description ?? ''} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="grid gap-2">
              <Label htmlFor="action-kpi">KPI</Label>
              <select
                id="action-kpi"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.kpi_id ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, kpi_id: e.target.value }))}
              >
                <option value="">Keine KPI</option>
                {(kpis ?? []).map((kpi) => (
                  <option key={kpi.id} value={kpi.id}>
                    {kpi.kpi_code} - {kpi.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="action-dashboard">Dashboard</Label>
              <select
                id="action-dashboard"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.dashboard_id ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, dashboard_id: e.target.value }))}
              >
                <option value="">Kein Dashboard</option>
                {(dashboards ?? []).map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.dashboard_code} - {d.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="action-status">Status</Label>
              <select
                id="action-status"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.status}
                onChange={(e) => setForm((p) => ({ ...p, status: e.target.value }))}
              >
                <option value="open">open</option>
                <option value="in_progress">in_progress</option>
                <option value="done">done</option>
                <option value="cancelled">cancelled</option>
              </select>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="action-owner">Owner (User-ID)</Label>
              <Input id="action-owner" value={form.owner_user_id ?? ''} onChange={(e) => setForm((p) => ({ ...p, owner_user_id: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="action-due">Faellig bis</Label>
              <Input id="action-due" type="date" value={form.due_date ?? ''} onChange={(e) => setForm((p) => ({ ...p, due_date: e.target.value }))} />
            </div>
          </div>
          <div className="flex gap-2">
            {editingId ? (
              <Button variant="outline" onClick={reset} disabled={busy}>
                Abbrechen
              </Button>
            ) : null}
            <Button onClick={save} disabled={busy}>
              {busy ? 'Speichert...' : editingId ? 'Aktualisieren' : 'Anlegen'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Massnahmenliste</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : null}
          {list.map((item) => (
            <div key={item.id} className="rounded-md border p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-semibold">{item.title}</div>
                  <div className="text-sm text-muted-foreground">{item.description || '-'}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={item.status === 'done' ? 'outline' : item.status === 'open' ? 'secondary' : 'destructive'}>
                    {item.status}
                  </Badge>
                  <Button size="sm" variant="outline" onClick={() => startEdit(item)}>
                    Bearbeiten
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => remove(item.id)}>
                    Loeschen
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
