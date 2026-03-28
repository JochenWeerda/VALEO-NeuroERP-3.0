import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, Euro, TrendingUp, Users } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

type KundenumsatzData = {
  gesamtumsatz: number
  kunden: number
  durchschnitt: number
  wachstum: number
  segmente: Array<{ segment: string; anzahl: number; umsatz: number; anteil: number }>
  topKunden: Array<{ name: string; umsatz: number; wachstum: number }>
}

const FALLBACK: KundenumsatzData = {
  gesamtumsatz: 0,
  kunden: 0,
  durchschnitt: 0,
  wachstum: 0,
  segmente: [],
  topKunden: [],
}

export default function KundenumsatzPage(): JSX.Element {
  const { data: analyse = FALLBACK, isLoading } = useQuery({
    queryKey: ['crm', 'kundenumsatz'],
    queryFn: async () => {
      const customersRes = await apiClient.get<{ items: Array<{ id: string; name: string; revenue?: number }>, total: number }>('/api/v1/crm/customers?limit=500')
      const customers = customersRes.data?.items ?? []

      const totalRevenue = customers.reduce((s, c) => s + (c.revenue ?? 0), 0)
      const count = customers.length
      const avg = count > 0 ? Math.round(totalRevenue / count) : 0

      const sorted = [...customers].sort((a, b) => (b.revenue ?? 0) - (a.revenue ?? 0))
      const aThreshold = 50000
      const bThreshold = 20000

      const aKunden = sorted.filter((c) => (c.revenue ?? 0) >= aThreshold)
      const bKunden = sorted.filter((c) => (c.revenue ?? 0) >= bThreshold && (c.revenue ?? 0) < aThreshold)
      const cKunden = sorted.filter((c) => (c.revenue ?? 0) < bThreshold)

      const aUmsatz = aKunden.reduce((s, c) => s + (c.revenue ?? 0), 0)
      const bUmsatz = bKunden.reduce((s, c) => s + (c.revenue ?? 0), 0)
      const cUmsatz = cKunden.reduce((s, c) => s + (c.revenue ?? 0), 0)

      return {
        gesamtumsatz: totalRevenue,
        kunden: count,
        durchschnitt: avg,
        wachstum: 0,
        segmente: [
          { segment: `A-Kunden (>${(aThreshold / 1000).toFixed(0)}k)`, anzahl: aKunden.length, umsatz: aUmsatz, anteil: totalRevenue > 0 ? Math.round((aUmsatz / totalRevenue) * 100) : 0 },
          { segment: `B-Kunden (${(bThreshold / 1000).toFixed(0)}-${(aThreshold / 1000).toFixed(0)}k)`, anzahl: bKunden.length, umsatz: bUmsatz, anteil: totalRevenue > 0 ? Math.round((bUmsatz / totalRevenue) * 100) : 0 },
          { segment: `C-Kunden (<${(bThreshold / 1000).toFixed(0)}k)`, anzahl: cKunden.length, umsatz: cUmsatz, anteil: totalRevenue > 0 ? Math.round((cUmsatz / totalRevenue) * 100) : 0 },
        ],
        topKunden: sorted.slice(0, 5).map((c) => ({
          name: c.name,
          umsatz: c.revenue ?? 0,
          wachstum: 0,
        })),
      } as KundenumsatzData
    },
    staleTime: 60_000,
  })

  const fmt = (v: number) =>
    new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v)

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Kundenumsatz-Analyse</h1>
        <p className="text-muted-foreground">ABC-Analyse & Segmentierung</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtumsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{fmt(analyse.gesamtumsatz)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-2xl font-bold">{analyse.kunden}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Umsatz/Kunde</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{fmt(analyse.durchschnitt)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Wachstum</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {analyse.wachstum > 0 ? '+' : ''}{analyse.wachstum}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            ABC-Segmentierung
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analyse.segmente.map((seg, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="font-semibold">{seg.segment}</div>
                    <div className="text-sm text-muted-foreground">{seg.anzahl} Kunden</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">{fmt(seg.umsatz)}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${i === 0 ? 'bg-green-600' : i === 1 ? 'bg-blue-600' : 'bg-gray-400'}`}
                      style={{ width: `${seg.anteil}%` }}
                    />
                  </div>
                  <Badge variant="outline">{seg.anteil}%</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Kunden</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analyse.topKunden.map((kunde, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{kunde.name}</div>
                  <Badge variant="outline" className="mt-1">#{i + 1}</Badge>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold">{fmt(kunde.umsatz)}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
