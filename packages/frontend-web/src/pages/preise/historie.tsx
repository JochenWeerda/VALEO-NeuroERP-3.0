import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { usePriceLists } from '@/lib/api/price-lists'
import { buildPriceWorkspace, formatCurrency } from '@/lib/professional-workspaces'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, TrendingDown, TrendingUp } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type PreisHistorie = {
  artikel: string
  aktuell: number
  vorwoche: number
  vormonat: number
  veraenderung: { woche: number; monat: number }
  verlauf: { datum: string; preis: number }[]
}

export default function PreishistoriePage(): JSX.Element {
  const { data: preise, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['preise', 'historie'],
    queryFn: async () => {
      const response = await apiClient.get<PreisHistorie>('/api/v1/preise/historie')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
  const { data: priceLists = [] } = usePriceLists()

  const workspace = useMemo(() => {
    if (!preise) return null
    const tierBreaks = priceLists.flatMap((priceList) =>
      (priceList.items ?? []).map((item) => ({
        minQuantity: Number(item.min_quantity ?? 0),
        maxQuantity: item.max_quantity == null ? undefined : Number(item.max_quantity),
        price: Number(item.unit_price ?? 0),
        discountPercent: Number(item.discount_percent ?? 0),
        sourceLabel: priceList.name,
      })),
    )
    return buildPriceWorkspace({
      listPrice: preise.aktuell,
      purchasePrice: preise.vormonat,
      agreements: preise.verlauf.map((entry) => ({
        partnerName: preise.artikel,
        priceNet: entry.preis,
        validFrom: entry.datum,
      })),
      tierBreaks,
    })
  }, [preise, priceLists])

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

  if (isError || !preise || !workspace) {
    return <ErrorState error={(error as Error) ?? new Error('Preishistorie konnte nicht geladen werden')} onRetry={() => { void refetch() }} />
  }

  const weeklyTrendUp = preise.veraenderung.woche >= 0
  const monthlyTrendUp = preise.veraenderung.monat >= 0

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Preishistorie</h1>
          <p className="text-muted-foreground">{preise.artikel}</p>
        </div>
        <Button variant="outline">Artikel wechseln</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktueller Preis</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{formatCurrency(preise.aktuell)} / t</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Vorwoche</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{formatCurrency(preise.vorwoche)} / t</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Veraenderung (Woche)</CardTitle></CardHeader>
          <CardContent>
            <div className={`flex items-center gap-2 ${weeklyTrendUp ? 'text-green-600' : 'text-red-600'}`}>
              {weeklyTrendUp ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
              <span className="text-2xl font-bold">{preise.veraenderung.woche > 0 ? '+' : ''}{preise.veraenderung.woche}%</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Veraenderung (Monat)</CardTitle></CardHeader>
          <CardContent>
            <div className={`flex items-center gap-2 ${monthlyTrendUp ? 'text-green-600' : 'text-red-600'}`}>
              {monthlyTrendUp ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
              <span className="text-2xl font-bold">{preise.veraenderung.monat > 0 ? '+' : ''}{preise.veraenderung.monat}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="grid gap-3 p-6 md:grid-cols-3">
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Trendbild</div>
            <div className="mt-2 font-semibold">{weeklyTrendUp ? 'Kurzfristig steigend' : 'Kurzfristig ruecklaeufig'}</div>
            <div className="mt-1 text-sm text-muted-foreground">Wochen- und Monatsveraenderung fuer Angebots- und Einkaufsgespraeche.</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Preisdruck</div>
            <div className="mt-2"><Badge variant={workspace.pricePressure === 'hoch' ? 'destructive' : 'outline'}>{workspace.pricePressure}</Badge></div>
            <div className="mt-1 text-sm text-muted-foreground">{workspace.tierBreakCount} Preislistenpositionen im Hintergrund.</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Naechste Aktion</div>
            <div className="mt-2 font-semibold">{workspace.nextAction}</div>
            <div className="mt-1 text-sm text-muted-foreground">Historie, Staffelung und Marge gemeinsam bewerten.</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Preisverlauf (4 Wochen)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {preise.verlauf.map((entry, index) => {
              const isLast = index === preise.verlauf.length - 1
              const trend = index > 0 ? entry.preis - preise.verlauf[index - 1].preis : 0
              return (
                <div key={entry.datum} className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">{new Date(entry.datum).toLocaleDateString('de-DE')}</div>
                    {isLast ? <Badge variant="outline" className="mt-1">Aktuell</Badge> : null}
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">{formatCurrency(entry.preis)} / t</div>
                    {trend !== 0 ? (
                      <div className={`text-sm font-semibold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trend > 0 ? <TrendingUp className="inline h-3 w-3" /> : <TrendingDown className="inline h-3 w-3" />}
                        {trend > 0 ? '+' : ''}{trend.toFixed(2)} EUR
                      </div>
                    ) : null}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
