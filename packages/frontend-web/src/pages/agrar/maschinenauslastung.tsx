import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, RefreshCw, Tractor, TrendingUp, Wrench } from 'lucide-react'
import { useMaschinen } from '@/lib/api/agrar'

const statusVariant = (s: string): 'default' | 'secondary' | 'outline' | 'destructive' => {
  if (s === 'im-einsatz') return 'secondary'
  if (s === 'werkstatt') return 'default'
  if (s === 'stillgelegt') return 'destructive'
  return 'outline'
}

const statusLabel = (s: string) => {
  if (s === 'im-einsatz') return 'Im Einsatz'
  if (s === 'werkstatt') return 'Werkstatt'
  if (s === 'stillgelegt') return 'Stillgelegt'
  return 'Verfügbar'
}

const auslastungFarbe = (pct: number) => {
  if (pct > 80) return 'bg-green-500'
  if (pct > 50) return 'bg-yellow-500'
  return 'bg-orange-500'
}

export default function MaschinenauslastungPage(): JSX.Element {
  const [statusFilter, setStatusFilter] = useState<string>('alle')
  const [typFilter, setTypFilter] = useState<string>('alle')

  const { data, isLoading, refetch } = useMaschinen({
    status: statusFilter !== 'alle' ? statusFilter : undefined,
    typ: typFilter !== 'alle' ? typFilter : undefined,
  })

  const maschinen = data?.items ?? []
  const stats = data?.stats ?? {}
  const typen = Array.from(new Set(maschinen.map((m) => m.typ))).sort()
  const statusOptions = [
    { value: 'alle', label: 'Alle Status' },
    { value: 'verfuegbar', label: 'Verfügbar' },
    { value: 'im-einsatz', label: 'Im Einsatz' },
    { value: 'werkstatt', label: 'Werkstatt' },
    { value: 'stillgelegt', label: 'Stillgelegt' },
  ]
  const typOptions = [
    { value: 'alle', label: 'Alle Typen' },
    ...typen.map((typ) => ({ value: typ, label: typ })),
  ]

  const mitAuslastung = maschinen.filter((m) => m.auslastung !== undefined && m.auslastung !== null)
  const avgAuslastung = mitAuslastung.length > 0
    ? mitAuslastung.reduce((sum, m) => sum + (m.auslastung ?? 0), 0) / mitAuslastung.length
    : 0

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Maschinen-Auslastung</h1>
          <p className="text-muted-foreground">Betriebsstunden & Auslastung des Maschinenparks</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void refetch()} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Aktualisieren
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Maschinen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-16" /> : <div className="flex items-center gap-2"><Tractor className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{stats.gesamt ?? maschinen.length}</span></div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Im Einsatz</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-16" /> : <span className="text-2xl font-bold text-status-success">{stats.im_einsatz ?? 0}</span>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Werkstatt</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-16" /> : <span className="text-2xl font-bold text-status-warning">{stats.werkstatt ?? 0}</span>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-20" /> : <div className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-status-success" /><span className="text-2xl font-bold text-status-success">{avgAuslastung.toFixed(1)}%</span></div>}
          </CardContent>
        </Card>
      </div>

      {!isLoading && (stats.wartung_faellig ?? 0) > 0 && (
        <Card className="border-orange-400 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-800">
              <AlertTriangle className="h-5 w-5 shrink-0" />
              <span className="font-medium">
                {stats.wartung_faellig} Maschine{(stats.wartung_faellig ?? 0) > 1 ? 'n' : ''} mit überfälliger Wartung
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex gap-3">
        <NativeSelect className="w-44" value={statusFilter} onValueChange={setStatusFilter} options={statusOptions} />
        <NativeSelect className="w-44" value={typFilter} onValueChange={setTypFilter} options={typOptions} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Maschinen & Auslastung</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28" />)}
            </div>
          ) : maschinen.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">Keine Maschinen gefunden.</p>
          ) : (
            <div className="space-y-3">
              {maschinen.map((m) => {
                const auslastung = m.auslastung ?? 0
                return (
                  <div key={m.id} className={`rounded-lg border p-4 ${m.wartung_faellig ? 'border-orange-400' : ''}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-lg truncate">{m.name}</div>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <Badge variant="outline">{m.typ}</Badge>
                          <Badge variant={statusVariant(m.status)}>{statusLabel(m.status)}</Badge>
                          {m.wartung_faellig && <Badge variant="destructive" className="gap-1"><Wrench className="h-3 w-3" />Wartung fällig</Badge>}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1 space-x-3">
                          {m.hersteller && <span>{m.hersteller}{m.modell ? ` ${m.modell}` : ''}</span>}
                          {m.baujahr && <span>Bj. {m.baujahr}</span>}
                          {m.kennzeichen && <span>{m.kennzeichen}</span>}
                          {m.standort && <span>?? {m.standort}</span>}
                        </div>
                      </div>
                      <div className="text-right shrink-0 ml-4">
                        <div className="text-2xl font-bold">{auslastung.toFixed(0)}%</div>
                        <div className="text-sm text-muted-foreground">{m.betriebsstunden.toFixed(0)} h</div>
                        {m.naechste_wartung_stunden !== undefined && m.naechste_wartung_stunden !== null && <div className="text-xs text-muted-foreground">Wartung bei {m.naechste_wartung_stunden.toFixed(0)} h</div>}
                        {m.naechste_wartung_datum && <div className="text-xs text-muted-foreground">{new Date(m.naechste_wartung_datum).toLocaleDateString('de-DE')}</div>}
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                      <div className={`h-4 rounded-full ${auslastungFarbe(auslastung)}`} style={{ width: `${Math.min(auslastung, 100)}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
