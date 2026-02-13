import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
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
      const r = await apiClient.get<PreisHistorie>('/api/v1/preise/historie')
      return r.data
    },
    staleTime: 5 * 60 * 1000,
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

  if (isError || !preise) {
    return <ErrorState error={(error as Error) ?? new Error('Preishistorie konnte nicht geladen werden')} onRetry={() => { void refetch() }} />
  }

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
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(preise.aktuell)} / t
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Vorwoche</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(preise.vorwoche)} / t
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Veraenderung (Woche)</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">+{preise.veraenderung.woche}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Veraenderung (Monat)</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">+{preise.veraenderung.monat}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Preisverlauf (4 Wochen)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {preise.verlauf.map((v, i) => {
              const isLast = i === preise.verlauf.length - 1
              const trend = i > 0 ? v.preis - preise.verlauf[i - 1].preis : 0
              return (
                <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">{new Date(v.datum).toLocaleDateString('de-DE')}</div>
                    {isLast && <Badge variant="outline" className="mt-1">Aktuell</Badge>}
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v.preis)} / t
                    </div>
                    {trend !== 0 && (
                      <div className={`text-sm font-semibold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trend > 0 ? <TrendingUp className="inline h-3 w-3" /> : <TrendingDown className="inline h-3 w-3" />}
                        {trend > 0 ? '+' : ''}{trend.toFixed(2)} EUR
                      </div>
                    )}
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
