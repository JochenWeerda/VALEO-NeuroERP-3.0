import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, Box } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type SiloData = {
  gesamt: number
  kapazitaet: number
  belegt: number
  liste: { id: string; nummer: string; artikel: string; kapazitaet: number; belegt: number; prozent: number }[]
}

type SiloDetail = {
  silo: { id: string; silo_number: string; name?: string; article_id?: string; capacity_tons: number }
  snapshot: {
    total_quantity_tons: number
    moisture_avg_pct: number | null
    protein_avg_pct: number | null
    impurities_avg_pct: number | null
    hl_weight_avg: number | null
    lot_count: number
    created_at?: string
  }
  lots: {
    id: string
    virtual_lot_number: string
    source_ticket_id?: string
    source_partner_id?: string
    quantity_tons: number
    moisture_pct: number | null
    protein_pct: number | null
    impurities_pct: number | null
    hl_weight: number | null
    status: string
    created_at?: string
  }[]
}

export default function SiloKapazitaetenPage(): JSX.Element {
  const [selectedSiloId, setSelectedSiloId] = useState<string | null>(null)

  const { data: silos, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['silo', 'kapazitaeten'],
    queryFn: async () => {
      const r = await apiClient.get<SiloData>('/api/v1/silo/kapazitaeten')
      return r.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const resolvedSiloId = useMemo(() => {
    if (selectedSiloId) return selectedSiloId
    return silos?.liste?.[0]?.id ?? null
  }, [selectedSiloId, silos?.liste])

  const {
    data: siloDetails,
    isLoading: isDetailsLoading,
    isError: isDetailsError,
    error: detailsError,
    refetch: refetchDetails,
  } = useQuery({
    queryKey: ['silo', 'details', resolvedSiloId],
    queryFn: async () => {
      const r = await apiClient.get<SiloDetail>(`/api/v1/silo/silos/${resolvedSiloId}/details`)
      return r.data
    },
    enabled: !!resolvedSiloId,
    staleTime: 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-9 w-48" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError || !silos) {
    return <ErrorState error={(error as Error) ?? new Error('Silo-Kapazitaeten konnten nicht geladen werden')} onRetry={() => { void refetch() }} />
  }

  const auslastung = silos.kapazitaet > 0 ? ((silos.belegt / silos.kapazitaet) * 100).toFixed(1) : '0.0'
  const kritisch = silos.liste.filter((s) => s.prozent > 85).length

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Silo-Kapazitaeten</h1>
        <p className="text-muted-foreground">Auslastung, Partien und Qualitaetssnapshot</p>
      </div>

      {kritisch > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{kritisch} Silo(s) ueber 85% Auslastung!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Silos Gesamt</CardTitle></CardHeader>
          <CardContent><div className="flex items-center gap-2"><Box className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{silos.gesamt}</span></div></CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Kapazitaet</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{silos.kapazitaet} t</span></CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Belegt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{silos.belegt} t</span></CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Auslastung</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-blue-600">{auslastung}%</span></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Silos & Auslastung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 mb-6">
            {silos.liste.map((silo) => (
              <button
                key={silo.id}
                type="button"
                onClick={() => setSelectedSiloId(silo.id)}
                className={`w-full rounded-lg border p-4 text-left transition-colors ${resolvedSiloId === silo.id ? 'border-blue-600 bg-blue-50' : ''}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-semibold text-lg flex items-center gap-2">
                      <span className="font-mono">{silo.nummer}</span>
                      {silo.prozent > 85 && <Badge variant="secondary">Kritisch</Badge>}
                    </div>
                    <div className="text-sm text-muted-foreground">{silo.artikel}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{silo.prozent.toFixed(1)}%</div>
                    <div className="text-sm text-muted-foreground">{silo.belegt} / {silo.kapazitaet} t</div>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-4 rounded-full ${silo.prozent > 85 ? 'bg-orange-500' : silo.prozent > 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${silo.prozent}%` }}
                  />
                </div>
              </button>
            ))}
          </div>

          {isDetailsLoading && <Skeleton className="h-48 w-full" />}

          {isDetailsError && (
            <ErrorState
              error={(detailsError as Error) ?? new Error('Silo-Details konnten nicht geladen werden')}
              onRetry={() => {
                void refetchDetails()
              }}
            />
          )}

          {!isDetailsLoading && !isDetailsError && siloDetails && (
            <div className="space-y-4 border-t pt-6">
              <div className="grid gap-3 md:grid-cols-5">
                <div className="rounded border p-3">
                  <div className="text-xs text-muted-foreground">Silo</div>
                  <div className="font-semibold">{siloDetails.silo.silo_number}</div>
                </div>
                <div className="rounded border p-3">
                  <div className="text-xs text-muted-foreground">Partien</div>
                  <div className="font-semibold">{siloDetails.snapshot.lot_count}</div>
                </div>
                <div className="rounded border p-3">
                  <div className="text-xs text-muted-foreground">Feuchte Ø</div>
                  <div className="font-semibold">{siloDetails.snapshot.moisture_avg_pct ?? '-'} %</div>
                </div>
                <div className="rounded border p-3">
                  <div className="text-xs text-muted-foreground">Protein Ø</div>
                  <div className="font-semibold">{siloDetails.snapshot.protein_avg_pct ?? '-'} %</div>
                </div>
                <div className="rounded border p-3">
                  <div className="text-xs text-muted-foreground">Besatz Ø</div>
                  <div className="font-semibold">{siloDetails.snapshot.impurities_avg_pct ?? '-'} %</div>
                </div>
              </div>

              <div>
                <h3 className="mb-2 text-sm font-semibold">Aktive/erfasste Partien</h3>
                <div className="space-y-2">
                  {siloDetails.lots.length === 0 && (
                    <div className="rounded border p-3 text-sm text-muted-foreground">Keine Partien vorhanden.</div>
                  )}
                  {siloDetails.lots.map((lot) => (
                    <div key={lot.id} className="rounded border p-3 text-sm">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono font-semibold">{lot.virtual_lot_number}</span>
                        <Badge variant={lot.status === 'active' ? 'default' : 'secondary'}>{lot.status}</Badge>
                      </div>
                      <div className="mt-1 text-muted-foreground">
                        Menge: {lot.quantity_tons} t | Feuchte: {lot.moisture_pct ?? '-'} % | Protein: {lot.protein_pct ?? '-'} %
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
