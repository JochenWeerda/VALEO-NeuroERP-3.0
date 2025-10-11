import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BarChart3, Euro, TrendingUp, Users } from 'lucide-react'

export default function UmsatzReportPage(): JSX.Element {
  const umsatz = {
    gesamt: 1250000,
    vorjahr: 1150000,
    wachstum: 8.7,
    topKunden: [
      { name: 'Landhandel Nord', umsatz: 320000 },
      { name: 'Agrar-Zentrum Süd', umsatz: 280000 },
      { name: 'Müller Landwirtschaft', umsatz: 150000 },
    ],
    topArtikel: [
      { name: 'Weizen Premium', umsatz: 450000 },
      { name: 'NPK-Dünger', umsatz: 280000 },
      { name: 'Sojaschrot', umsatz: 220000 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Umsatz-Report</h1>
        <p className="text-muted-foreground">Verkaufsauswertung 2025</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Umsatz Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(umsatz.gesamt)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Vorjahr</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(umsatz.vorjahr)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Wachstum</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">+{umsatz.wachstum}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-2xl font-bold">142</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Top-Kunden
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {umsatz.topKunden.map((kunde, i) => (
                <div key={i} className="flex justify-between rounded-lg border p-3">
                  <div>
                    <div className="font-semibold">{kunde.name}</div>
                    <Badge variant="outline">#{i + 1}</Badge>
                  </div>
                  <div className="font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.umsatz)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Top-Artikel
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {umsatz.topArtikel.map((artikel, i) => (
                <div key={i} className="flex justify-between rounded-lg border p-3">
                  <div>
                    <div className="font-semibold">{artikel.name}</div>
                    <Badge variant="outline">#{i + 1}</Badge>
                  </div>
                  <div className="font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(artikel.umsatz)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
