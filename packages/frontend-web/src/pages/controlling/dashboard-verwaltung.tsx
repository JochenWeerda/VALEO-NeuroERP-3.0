import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useControllingDashboards,
  useCreateDashboard,
  useDeleteDashboard,
  useUpdateDashboard,
  type ControllingDashboard,
  type DashboardInput,
} from '@/lib/api/controlling'
import { useToast } from '@/components/ui/toast-provider'

const EMPTY_FORM: DashboardInput = {
  dashboard_code: '',
  name: '',
  description: '',
  is_active: true,
}

export default function DashboardVerwaltungPage(): JSX.Element {
  const { push } = useToast()
  const { data, isLoading } = useControllingDashboards()
  const createMutation = useCreateDashboard()
  const updateMutation = useUpdateDashboard()
  const deleteMutation = useDeleteDashboard()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<DashboardInput>(EMPTY_FORM)

  const dashboards = useMemo(() => data ?? [], [data])

  const reset = (): void => {
    setEditingId(null)
    setForm(EMPTY_FORM)
  }

  const startEdit = (item: ControllingDashboard): void => {
    setEditingId(item.id)
    setForm({
      dashboard_code: item.dashboard_code,
      name: item.name,
      description: item.description ?? '',
      is_active: item.is_active,
    })
  }

  const save = (): void => {
    if (!form.dashboard_code.trim() || !form.name.trim()) {
      push('Bitte Dashboard-Code und Name angeben.')
      return
    }
    const onError = (error: unknown): void => {
      push(error instanceof Error ? error.message : 'Speichern fehlgeschlagen.')
    }
    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data: form },
        {
          onSuccess: () => {
            push('Dashboard aktualisiert.')
            reset()
          },
          onError,
        },
      )
      return
    }

    createMutation.mutate(form, {
      onSuccess: () => {
        push('Dashboard angelegt.')
        reset()
      },
      onError,
    })
  }

  const remove = (id: string): void => {
    deleteMutation.mutate(id, {
      onSuccess: () => push('Dashboard geloescht.'),
      onError: (error) => push(error instanceof Error ? error.message : 'Loeschen fehlgeschlagen.'),
    })
  }

  const busy = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard-Verwaltung</h1>
        <p className="text-muted-foreground">Controlling-Dashboards pflegen</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editingId ? 'Dashboard bearbeiten' : 'Dashboard anlegen'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="dashboard-code">Dashboard-Code</Label>
              <Input id="dashboard-code" value={form.dashboard_code} onChange={(e) => setForm((p) => ({ ...p, dashboard_code: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="dashboard-name">Name</Label>
              <Input id="dashboard-name" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="dashboard-description">Beschreibung</Label>
              <Input id="dashboard-description" value={form.description ?? ''} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="dashboard-active">Aktiv</Label>
              <select
                id="dashboard-active"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.is_active ? 'true' : 'false'}
                onChange={(e) => setForm((p) => ({ ...p, is_active: e.target.value === 'true' }))}
              >
                <option value="true">ja</option>
                <option value="false">nein</option>
              </select>
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
          <CardTitle>Dashboards</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : null}
          {dashboards.map((item) => (
            <div key={item.id} className="rounded-md border p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-semibold">
                    {item.name} <span className="text-muted-foreground">({item.dashboard_code})</span>
                  </div>
                  <div className="text-sm text-muted-foreground">{item.description || '-'}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={item.is_active ? 'outline' : 'secondary'}>{item.is_active ? 'aktiv' : 'inaktiv'}</Badge>
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
