import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, TrendingDown, TrendingUp } from 'lucide-react'
import { usePlanIst } from '@/lib/api/misc-modules'

export default function PlanIstPage(): JSX.Element {
  const { data: planist, isLoading } = usePlanIst()

  if (isLoading || !planist) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-36" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  const fmt = (v: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v)

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Plan-Ist-Vergleich</h1>
        <p className="text-muted-foreground">{planist.periode}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          { label: 'Umsatz', data: planist.umsatz },
          { label: 'Kosten', data: planist.kosten },
          { label: 'Ertrag', data: planist.ertrag },
        ].map(({ label, data }) => (
          <Card key={label}>
            <CardHeader><CardTitle className="text-sm">{label}</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Plan:</span>
                  <span className="font-semibold">{fmt(data.plan)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Ist:</span>
                  <span className="font-semibold">{fmt(data.ist)}</span>
                </div>
                <div className="flex items-center justify-between border-t pt-2">
                  <span className="text-sm font-medium">Abweichung:</span>
                  <div className="flex items-center gap-1">
                    {data.abweichung >= 0
                      ? <TrendingUp className="h-4 w-4 text-status-success" />
                      : <TrendingDown className="h-4 w-4 text-status-error" />}
                    <span className={`text-lg font-bold ${data.abweichung >= 0 ? 'text-status-success' : 'text-status-error'}`}>
                      {data.abweichung > 0 ? '+' : ''}{data.abweichung}%
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Plan-Ist nach Bereich
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {planist.bereiche.map((bereich, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-semibold">{bereich.bereich}</div>
                  <div className="flex items-center gap-2">
                    {bereich.abweichung > 0 ? (
                      <>
                        <TrendingUp className="h-4 w-4 text-status-success" />
                        <span className="font-bold text-status-success">+{bereich.abweichung}%</span>
                      </>
                    ) : bereich.abweichung < 0 ? (
                      <>
                        <TrendingDown className="h-4 w-4 text-status-error" />
                        <span className="font-bold text-status-error">{bereich.abweichung}%</span>
                      </>
                    ) : (
                      <Badge variant="outline">+0%</Badge>
                    )}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Plan:</span>
                    <span className="font-semibold">{fmt(bereich.plan)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Ist:</span>
                    <span className="font-semibold">{fmt(bereich.ist)}</span>
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
