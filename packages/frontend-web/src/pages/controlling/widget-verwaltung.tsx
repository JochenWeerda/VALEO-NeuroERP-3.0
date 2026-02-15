import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useControllingDashboards,
  useControllingKpis,
  useCreateWidget,
  useDashboardWidgets,
  useDeleteWidget,
  useUpdateWidget,
  type DashboardWidget,
  type WidgetInput,
} from '@/lib/api/controlling'
import { useToast } from '@/components/ui/toast-provider'

const EMPTY: WidgetInput = {
  widget_type: '',
  title: '',
  kpi_id: '',
  position_x: 0,
  position_y: 0,
  size_w: 4,
  size_h: 3,
}

export default function WidgetVerwaltungPage(): JSX.Element {
  const { push } = useToast()
  const { data: dashboards } = useControllingDashboards()
  const { data: kpis } = useControllingKpis()
  const [dashboardId, setDashboardId] = useState('')
  const { data: widgets } = useDashboardWidgets(dashboardId || undefined)

  const createMutation = useCreateWidget(dashboardId || '')
  const updateMutation = useUpdateWidget()
  const deleteMutation = useDeleteWidget(dashboardId || '')

  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<WidgetInput>(EMPTY)

  const list = useMemo(() => widgets ?? [], [widgets])

  const reset = (): void => {
    setEditingId(null)
    setForm(EMPTY)
  }

  const startEdit = (item: DashboardWidget): void => {
    setEditingId(item.id)
    setForm({
      widget_type: item.widget_type,
      title: item.title,
      kpi_id: item.kpi_id,
      position_x: item.position_x,
      position_y: item.position_y,
      size_w: item.size_w,
      size_h: item.size_h,
    })
  }

  const save = (): void => {
    if (!dashboardId) {
      push('Bitte zuerst ein Dashboard waehlen.')
      return
    }
    if (!form.widget_type?.trim() || !form.title?.trim()) {
      push('Bitte Widget-Typ und Titel angeben.')
      return
    }
    const onError = (error: unknown): void => {
      push(error instanceof Error ? error.message : 'Speichern fehlgeschlagen.')
    }
    if (editingId) {
      updateMutation.mutate(
        { id: editingId, dashboardId, data: form },
        {
          onSuccess: () => {
            push('Widget aktualisiert.')
            reset()
          },
          onError,
        },
      )
      return
    }
    createMutation.mutate(form, {
      onSuccess: () => {
        push('Widget angelegt.')
        reset()
      },
      onError,
    })
  }

  const remove = (id: string): void => {
    deleteMutation.mutate(id, {
      onSuccess: () => push('Widget geloescht.'),
      onError: (error) => push(error instanceof Error ? error.message : 'Loeschen fehlgeschlagen.'),
    })
  }

  const busy = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Widget-Verwaltung</h1>
        <p className="text-muted-foreground">Widgets je Dashboard konfigurieren</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dashboard waehlen</CardTitle>
        </CardHeader>
        <CardContent>
          <select
            className="w-full rounded-md border border-input bg-background px-3 py-2"
            value={dashboardId}
            onChange={(e) => setDashboardId(e.target.value)}
          >
            <option value="">Bitte waehlen</option>
            {(dashboards ?? []).map((d) => (
              <option key={d.id} value={d.id}>
                {d.dashboard_code} - {d.name}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{editingId ? 'Widget bearbeiten' : 'Widget anlegen'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="widget-type">Widget-Typ</Label>
              <Input id="widget-type" value={form.widget_type ?? ''} onChange={(e) => setForm((p) => ({ ...p, widget_type: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="widget-title">Titel</Label>
              <Input id="widget-title" value={form.title ?? ''} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="widget-kpi">KPI (optional)</Label>
              <select
                id="widget-kpi"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.kpi_id ?? ''}
                onChange={(e) => setForm((p) => ({ ...p, kpi_id: e.target.value || undefined }))}
              >
                <option value="">Keine KPI</option>
                {(kpis ?? []).map((k) => (
                  <option key={k.id} value={k.id}>
                    {k.kpi_code} - {k.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="widget-size">Groesse (W/H)</Label>
              <div className="grid grid-cols-2 gap-2">
                <Input
                  id="widget-size"
                  type="number"
                  value={form.size_w ?? 4}
                  onChange={(e) => setForm((p) => ({ ...p, size_w: Number(e.target.value) }))}
                />
                <Input
                  type="number"
                  value={form.size_h ?? 3}
                  onChange={(e) => setForm((p) => ({ ...p, size_h: Number(e.target.value) }))}
                />
              </div>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="widget-pos-x">Position X</Label>
              <Input
                id="widget-pos-x"
                type="number"
                value={form.position_x ?? 0}
                onChange={(e) => setForm((p) => ({ ...p, position_x: Number(e.target.value) }))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="widget-pos-y">Position Y</Label>
              <Input
                id="widget-pos-y"
                type="number"
                value={form.position_y ?? 0}
                onChange={(e) => setForm((p) => ({ ...p, position_y: Number(e.target.value) }))}
              />
            </div>
          </div>
          <div className="flex gap-2">
            {editingId ? (
              <Button variant="outline" onClick={reset} disabled={busy}>
                Abbrechen
              </Button>
            ) : null}
            <Button onClick={save} disabled={busy || !dashboardId}>
              {busy ? 'Speichert...' : editingId ? 'Aktualisieren' : 'Anlegen'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Widgets</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {list.map((item) => (
            <div key={item.id} className="rounded-md border p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm">
                  <div className="font-semibold">
                    {item.title} ({item.widget_type})
                  </div>
                  <div className="text-muted-foreground">
                    Pos: {item.position_x}/{item.position_y} | Size: {item.size_w}x{item.size_h}
                  </div>
                </div>
                <div className="flex gap-2">
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
