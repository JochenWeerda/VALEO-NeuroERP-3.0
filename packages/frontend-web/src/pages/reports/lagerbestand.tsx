import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Package, TrendingDown, Warehouse } from 'lucide-react'

export default function LagerbestandReportPage(): JSX.Element {
  const lager = {
    gesamtmenge: 1250,
    gesamtwert: 275000,
    artikel: 45,
    untermindest: 5,
    topArtikel: [
      { name: 'Weizen Premium', menge: 450, wert: 99000, tage: 35 },
      { name: 'Sojaschrot 44%', menge: 280, wert: 84000, tage: 42 },
      { name: 'NPK-Dünger', menge: 220, wert: 44000, tage: 15 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Lagerbestands-Report</h1>
        <p className="text-muted-foreground">Stichtag: {new Date().toLocaleDateString('de-DE')}</p>
      </div>

      {lager.untermindest > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{lager.untermindest} Artikel unter Mindestbestand!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtbestand</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Warehouse className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{lager.gesamtmenge.toLocaleString('de-DE')} t</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtwert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(lager.gesamtwert)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Artikel</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              <span className="text-2xl font-bold">{lager.artikel}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unter Mindestbestand</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold text-orange-600">{lager.untermindest}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top-Artikel nach Wert</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {lager.topArtikel.map((artikel, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{artikel.name}</div>
                  <div className="text-sm text-muted-foreground">{artikel.menge} t</div>
                  <Badge variant="outline" className="mt-1">#{i + 1}</Badge>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(artikel.wert)}
                  </div>
                  <div className={`text-sm font-semibold ${artikel.tage < 20 ? 'text-orange-600' : 'text-green-600'}`}>
                    {artikel.tage < 20 ? <TrendingDown className="inline h-3 w-3" /> : null}
                    {artikel.tage} Tage Reichweite
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
