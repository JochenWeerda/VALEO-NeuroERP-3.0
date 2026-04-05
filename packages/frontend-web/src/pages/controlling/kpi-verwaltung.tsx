import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useControllingKpis,
  useCreateKpi,
  useDeleteKpi,
  useUpdateKpi,
  type KpiDefinition,
  type KpiInput,
} from '@/lib/api/controlling'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useToast } from '@/components/ui/toast-provider'

const EMPTY_FORM: KpiInput = {
  kpi_code: '',
  name: '',
  description: '',
  formula: '',
  unit: '',
  is_active: true,
}

export default function KpiVerwaltungPage(): JSX.Element {
  const { push } = useToast()
  const { data, isLoading } = useControllingKpis()
  const createMutation = useCreateKpi()
  const updateMutation = useUpdateKpi()
  const deleteMutation = useDeleteKpi()

  const [form, setForm] = useState<KpiInput>(EMPTY_FORM)
  const [targetValue, setTargetValue] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)

  const list = useMemo(() => data ?? [], [data])

  const reset = (): void => {
    setForm(EMPTY_FORM)
    setTargetValue('')
    setEditingId(null)
  }

  const startEdit = (item: KpiDefinition): void => {
    setEditingId(item.id)
    setForm({
      kpi_code: item.kpi_code,
      name: item.name,
      description: item.description ?? '',
      formula: item.formula ?? '',
      target_value: item.target_value,
      unit: item.unit ?? '',
      is_active: item.is_active,
    })
    setTargetValue(item.target_value != null ? String(item.target_value) : '')
  }

  const save = (): void => {
    if (!form.kpi_code.trim() || !form.name.trim()) {
      push('Bitte KPI-Code und Name angeben.')
      return
    }
    const payload: KpiInput = {
      ...form,
      target_value: targetValue.trim() ? Number(targetValue) : undefined,
    }
    const onError = (error: unknown): void => {
      push(getAxiosErrorMessage(error))
    }

    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data: payload },
        {
          onSuccess: () => {
            push('KPI aktualisiert.')
            reset()
          },
          onError,
        },
      )
      return
    }

    createMutation.mutate(payload, {
      onSuccess: () => {
        push('KPI angelegt.')
        reset()
      },
      onError,
    })
  }

  const remove = (id: string): void => {
    deleteMutation.mutate(id, {
      onSuccess: () => push('KPI geloescht.'),
      onError: (error) => push(getAxiosErrorMessage(error)),
    })
  }

  const busy = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">KPI-Verwaltung</h1>
        <p className="text-muted-foreground">Controlling-KPIs anlegen und pflegen</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editingId ? 'KPI bearbeiten' : 'KPI anlegen'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="kpi-code">KPI-Code</Label>
              <Input id="kpi-code" value={form.kpi_code} onChange={(e) => setForm((p) => ({ ...p, kpi_code: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="kpi-name">Name</Label>
              <Input id="kpi-name" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="grid gap-2">
              <Label htmlFor="target-value">Zielwert</Label>
              <Input id="target-value" value={targetValue} onChange={(e) => setTargetValue(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="unit">Einheit</Label>
              <Input id="unit" value={form.unit ?? ''} onChange={(e) => setForm((p) => ({ ...p, unit: e.target.value }))} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="active">Aktiv</Label>
              <select
                id="active"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={form.is_active ? 'true' : 'false'}
                onChange={(e) => setForm((p) => ({ ...p, is_active: e.target.value === 'true' }))}
              >
                <option value="true">ja</option>
                <option value="false">nein</option>
              </select>
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="description">Beschreibung</Label>
            <Input id="description" value={form.description ?? ''} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="formula">Formel</Label>
            <Input id="formula" value={form.formula ?? ''} onChange={(e) => setForm((p) => ({ ...p, formula: e.target.value }))} />
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
          <CardTitle>KPI-Liste</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : null}
          {list.map((item) => (
            <div key={item.id} className="rounded-md border p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-semibold">
                    {item.name} <span className="text-muted-foreground">({item.kpi_code})</span>
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
