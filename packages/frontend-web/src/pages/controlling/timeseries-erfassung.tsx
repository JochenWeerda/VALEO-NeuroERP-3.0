import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useControllingKpis,
  useCreateTimeseriesItem,
  useDeleteTimeseriesItem,
  useKpiTimeseries,
} from '@/lib/api/controlling'
import { useToast } from '@/components/ui/toast-provider'

export default function TimeseriesErfassungPage(): JSX.Element {
  const { push } = useToast()
  const { data: kpis } = useControllingKpis()

  const [kpiId, setKpiId] = useState('')
  const [periodStart, setPeriodStart] = useState('')
  const [periodEnd, setPeriodEnd] = useState('')
  const [value, setValue] = useState('')
  const [source, setSource] = useState('')

  const { data: items, isLoading } = useKpiTimeseries(kpiId || undefined)
  const createMutation = useCreateTimeseriesItem()
  const deleteMutation = useDeleteTimeseriesItem()

  const list = useMemo(() => items ?? [], [items])

  const save = (): void => {
    if (!kpiId || !periodStart || !periodEnd || !value.trim()) {
      push('Bitte KPI, Periodenstart, Periodenende und Wert angeben.')
      return
    }
    const parsedValue = Number(value)
    if (!Number.isFinite(parsedValue)) {
      push('Wert muss numerisch sein.')
      return
    }
    createMutation.mutate(
      {
        kpi_id: kpiId,
        period_start: periodStart,
        period_end: periodEnd,
        value: parsedValue,
        source: source || undefined,
      },
      {
        onSuccess: () => {
          push('Zeitreihe gespeichert.')
          setPeriodStart('')
          setPeriodEnd('')
          setValue('')
          setSource('')
        },
        onError: (error) => push(error instanceof Error ? error.message : 'Speichern fehlgeschlagen.'),
      },
    )
  }

  const remove = (id: string): void => {
    deleteMutation.mutate(id, {
      onSuccess: () => push('Zeitreiheneintrag geloescht.'),
      onError: (error) => push(error instanceof Error ? error.message : 'Loeschen fehlgeschlagen.'),
    })
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Timeseries-Erfassung</h1>
        <p className="text-muted-foreground">KPI-Zeitreihen manuell erfassen</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neuer Eintrag</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="kpi-id">KPI</Label>
              <select
                id="kpi-id"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={kpiId}
                onChange={(e) => setKpiId(e.target.value)}
              >
                <option value="">Bitte waehlen</option>
                {(kpis ?? []).map((kpi) => (
                  <option key={kpi.id} value={kpi.id}>
                    {kpi.kpi_code} - {kpi.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="source">Quelle</Label>
              <Input id="source" value={source} onChange={(e) => setSource(e.target.value)} placeholder="z. B. ERP-Import" />
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="grid gap-2">
              <Label htmlFor="period-start">Periode Start</Label>
              <Input id="period-start" type="date" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="period-end">Periode Ende</Label>
              <Input id="period-end" type="date" value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="value">Wert</Label>
              <Input id="value" value={value} onChange={(e) => setValue(e.target.value)} />
            </div>
          </div>
          <Button onClick={save} disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Speichert...' : 'Speichern'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Eintraege</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : null}
          {list.map((entry) => (
            <div key={entry.id} className="rounded-md border p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm">
                  <div>
                    <strong>{entry.period_start}</strong> bis <strong>{entry.period_end}</strong>
                  </div>
                  <div className="text-muted-foreground">
                    Wert: {entry.value} {entry.source ? `| Quelle: ${entry.source}` : ''}
                  </div>
                </div>
                <Button size="sm" variant="destructive" onClick={() => remove(entry.id)}>
                  Loeschen
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
