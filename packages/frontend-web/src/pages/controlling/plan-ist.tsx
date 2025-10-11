import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingDown, TrendingUp } from 'lucide-react'

export default function PlanIstPage(): JSX.Element {
  const planist = {
    umsatz: { plan: 1200000, ist: 1250000, abweichung: 4.2 },
    kosten: { plan: 850000, ist: 820000, abweichung: -3.5 },
    ertrag: { plan: 350000, ist: 430000, abweichung: 22.9 },
    bereiche: [
      { bereich: 'Verkauf Getreide', plan: 480000, ist: 525000, abweichung: 9.4 },
      { bereich: 'Verkauf Saatgut', plan: 320000, ist: 295000, abweichung: -7.8 },
      { bereich: 'Verkauf Dünger', plan: 280000, ist: 310000, abweichung: 10.7 },
      { bereich: 'Verkauf Futter', plan: 120000, ist: 120000, abweichung: 0.0 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Plan-Ist-Vergleich</h1>
        <p className="text-muted-foreground">Oktober 2025</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Umsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Plan:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(planist.umsatz.plan)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ist:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(planist.umsatz.ist)}
                </span>
              </div>
              <div className="flex items-center justify-between border-t pt-2">
                <span className="text-sm font-medium">Abweichung:</span>
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-lg font-bold text-green-600">+{planist.umsatz.abweichung}%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Kosten</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Plan:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(planist.kosten.plan)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ist:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(planist.kosten.ist)}
                </span>
              </div>
              <div className="flex items-center justify-between border-t pt-2">
                <span className="text-sm font-medium">Abweichung:</span>
                <div className="flex items-center gap-1">
                  <TrendingDown className="h-4 w-4 text-green-600" />
                  <span className="text-lg font-bold text-green-600">{planist.kosten.abweichung}%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Ertrag</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Plan:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(planist.ertrag.plan)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ist:</span>
                <span className="font-semibold">
                  {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(planist.ertrag.ist)}
                </span>
              </div>
              <div className="flex items-center justify-between border-t pt-2">
                <span className="text-sm font-medium">Abweichung:</span>
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-lg font-bold text-green-600">+{planist.ertrag.abweichung}%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
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
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="font-bold text-green-600">+{bereich.abweichung}%</span>
                      </>
                    ) : bereich.abweichung < 0 ? (
                      <>
                        <TrendingDown className="h-4 w-4 text-red-600" />
                        <span className="font-bold text-red-600">{bereich.abweichung}%</span>
                      </>
                    ) : (
                      <Badge variant="outline">±0%</Badge>
                    )}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Plan:</span>
                    <span className="font-semibold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bereich.plan)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Ist:</span>
                    <span className="font-semibold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bereich.ist)}
                    </span>
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
