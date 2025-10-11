import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, BarChart3, Euro, TrendingUp } from 'lucide-react'

export default function LiquiditaetPage(): JSX.Element {
  const liquiditaet = {
    aktuell: 285000,
    ziel: 250000,
    vormonat: 265000,
    prognose: [
      { monat: 'November', einnahmen: 320000, ausgaben: 280000, saldo: 40000 },
      { monat: 'Dezember', einnahmen: 350000, ausgaben: 310000, saldo: 40000 },
      { monat: 'Januar', einnahmen: 280000, ausgaben: 250000, saldo: 30000 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Liquiditätsplanung</h1>
        <p className="text-muted-foreground">Cash-Flow & Prognose</p>
      </div>

      {liquiditaet.aktuell < liquiditaet.ziel && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Liquidität unter Zielwert!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktuelle Liquidität</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(liquiditaet.aktuell)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zielwert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(liquiditaet.ziel)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Veränderung (Monat)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                +{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(liquiditaet.aktuell - liquiditaet.vormonat)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reserve gg. Ziel</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              +{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(liquiditaet.aktuell - liquiditaet.ziel)}
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Liquiditäts-Prognose (3 Monate)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {liquiditaet.prognose.map((p, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="font-semibold text-lg">{p.monat}</div>
                  <Badge variant={p.saldo > 0 ? 'outline' : 'destructive'}>
                    Saldo: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(p.saldo)}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Einnahmen:</span>
                    <span className="font-semibold text-green-600">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(p.einnahmen)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Ausgaben:</span>
                    <span className="font-semibold text-red-600">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(p.ausgaben)}
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
