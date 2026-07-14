import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, Flower2, Info, Leaf, MapPin } from 'lucide-react'

type CategorySummary = {
  kategorie: string
  position_count: number
  co2e_kg: number
}

type ReadModel = {
  catalog: {
    total_co2e_kg: number
    total_co2e_t: number
    categories: CategorySummary[]
    year: number
  }
  coverage_notes: string[]
}

// Map backend Nachhaltigkeitsziele to German display labels
const KATEGORIE_LABELS: Record<string, string> = {
  TRANSPORT_LKW: 'Transport (LKW)',
  TRANSPORT_BAHN: 'Transport (Bahn)',
  TRANSPORT_SCHIFF: 'Transport (Schiff)',
  ENERGIE_STROM: 'Energie (Strom)',
  ENERGIE_WAERME: 'Energie (Wärme)',
  LANDWIRTSCHAFT: 'Landwirtschaft',
  DUENGUNG: 'Düngung',
  PFLANZENSCHUTZ: 'Pflanzenschutz',
  TROCKNUNG: 'Trocknung',
  VERWALTUNG: 'Verwaltung',
}

export default function BiodiversitaetPage(): JSX.Element {
  const currentYear = new Date().getFullYear()
  const [year] = useState(currentYear)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['sustainability', 'read-model', year],
    queryFn: async () => (await apiClient.get<ReadModel>(`/api/v1/sustainability/read-model?jahr=${year}`)).data,
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-9 w-64" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const catalog = data?.catalog
  const categories = catalog?.categories ?? []
  const totalCo2eT = catalog?.total_co2e_t ?? 0
  const reportYear = catalog?.year ?? year

  // Agricultural categories with biodiversity relevance
  const agrarKategorien = categories.filter((c) =>
    ['LANDWIRTSCHAFT', 'DUENGUNG', 'PFLANZENSCHUTZ'].includes(c.kategorie)
  )
  const agrarCo2e = agrarKategorien.reduce((sum, c) => sum + c.co2e_kg, 0)

  const maxCo2e = Math.max(...categories.map((c) => c.co2e_kg), 1)

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Biodiversitäts-Monitoring</h1>
        <p className="text-muted-foreground">Ökologische Nachhaltigkeit {reportYear}</p>
      </div>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <div className="flex items-start gap-2">
          <Info className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
          <div className="text-sm text-blue-900">
            <p className="font-semibold">Nachhaltigkeits-Datenquelle: ESG Read-Model ({reportYear})</p>
            <p className="mt-1">
              Flächenbezogene Biodiversitäts-Maßnahmen (Blühstreifen, Brachflächen) werden über
              das Feldbuch-Modul erfasst. Hier werden CO₂e-relevante Agrarkategorien ausgewiesen.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">CO₂e gesamt (t)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Leaf className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">
                {totalCo2eT.toLocaleString('de-DE', { maximumFractionDigits: 2 })} t
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Agrar-CO₂e (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Flower2 className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">
                {agrarCo2e.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kg
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kategorien erfasst</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{categories.length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            CO₂e nach Emissionskategorie
          </CardTitle>
        </CardHeader>
        <CardContent>
          {categories.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Keine Kategoriedaten für {reportYear} verfügbar.
            </p>
          ) : (
            <div className="space-y-3">
              {categories.map((cat) => {
                const anteil = maxCo2e > 0 ? (cat.co2e_kg / maxCo2e) * 100 : 0
                const isAgrar = ['LANDWIRTSCHAFT', 'DUENGUNG', 'PFLANZENSCHUTZ'].includes(cat.kategorie)
                return (
                  <div key={cat.kategorie} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">
                          {KATEGORIE_LABELS[cat.kategorie] ?? cat.kategorie}
                        </span>
                        {isAgrar && (
                          <Badge variant="secondary" className="text-xs">Agrar-relevant</Badge>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="font-bold">
                          {cat.co2e_kg.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kg CO₂e
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${isAgrar ? 'bg-green-600' : 'bg-blue-500'}`}
                          style={{ width: `${anteil}%` }}
                        />
                      </div>
                      <Badge variant="outline">{anteil.toFixed(0)}%</Badge>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {agrarKategorien.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Agrarbezogene Emissionskategorien
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {agrarKategorien.map((cat) => (
                <div key={cat.kategorie} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <div className="font-semibold">{KATEGORIE_LABELS[cat.kategorie] ?? cat.kategorie}</div>
                    <div className="text-sm text-muted-foreground">{cat.position_count} Positionen</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-700">
                      {cat.co2e_kg.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kg CO₂e
                    </div>
                    <Badge variant="outline">Aktiv</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
