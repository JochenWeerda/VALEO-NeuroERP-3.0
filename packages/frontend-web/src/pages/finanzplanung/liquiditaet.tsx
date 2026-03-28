import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, BarChart3, Euro, Loader2, TrendingDown, TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

type PrognoseMonat = {
  monat: string
  einnahmen: number
  ausgaben: number
  saldo: number
}

type LiquiditaetOverview = {
  aktuell: number
  ziel: number
  vormonat: number
  prognose: PrognoseMonat[]
  waehrung: string
}

const eurFormat = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })

function useLiquiditaetOverview() {
  return useQuery({
    queryKey: ['finance', 'liquidity', 'overview'],
    queryFn: async () => {
      const response = await apiClient.get<LiquiditaetOverview>('/api/v1/finance/liquidity/overview')
      return response.data
    },
    staleTime: 60 * 1000, // 1 Min
  })
}

export default function LiquiditaetPage(): JSX.Element {
  const { data: liquiditaet, isLoading } = useLiquiditaetOverview()

  if (isLoading || !liquiditaet) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <span className="ml-3 text-muted-foreground">Liquiditätsdaten werden geladen...</span>
      </div>
    )
  }

  const veraenderung = liquiditaet.aktuell - liquiditaet.vormonat
  const reserve = liquiditaet.aktuell - liquiditaet.ziel

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Liquiditaetsplanung</h1>
        <p className="text-muted-foreground">Cash-Flow & Prognose</p>
      </div>

      {liquiditaet.aktuell < liquiditaet.ziel && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Liquiditaet unter Zielwert!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktuelle Liquiditaet</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{eurFormat.format(liquiditaet.aktuell)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zielwert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{eurFormat.format(liquiditaet.ziel)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Veraenderung (Monat)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {veraenderung >= 0 ? (
                <TrendingUp className="h-5 w-5 text-green-600" />
              ) : (
                <TrendingDown className="h-5 w-5 text-red-600" />
              )}
              <span className={`text-2xl font-bold ${veraenderung >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {veraenderung >= 0 ? '+' : ''}{eurFormat.format(veraenderung)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reserve gg. Ziel</CardTitle>
          </CardHeader>
          <CardContent>
            <span className={`text-2xl font-bold ${reserve >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {reserve >= 0 ? '+' : ''}{eurFormat.format(reserve)}
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Liquiditaets-Prognose (3 Monate)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {liquiditaet.prognose.length === 0 && (
            <p className="text-muted-foreground">Noch keine Prognosedaten vorhanden.</p>
          )}
          <div className="space-y-3">
            {liquiditaet.prognose.map((p, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="font-semibold text-lg">{p.monat}</div>
                  <Badge variant={p.saldo >= 0 ? 'outline' : 'destructive'}>
                    Saldo: {eurFormat.format(p.saldo)}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Einnahmen:</span>
                    <span className="font-semibold text-green-600">{eurFormat.format(p.einnahmen)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Ausgaben:</span>
                    <span className="font-semibold text-red-600">{eurFormat.format(p.ausgaben)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
