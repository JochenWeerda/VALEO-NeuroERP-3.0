import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BarChart3, TrendingDown, TrendingUp, Warehouse } from 'lucide-react'

export default function BestandsuebersichtPage(): JSX.Element {
  const bestand = {
    gesamtmenge: 1250.5,
    gesamtwert: 275000,
    bewegungenHeute: 45,
    reichweite: 28,
    topArtikel: [
      { name: 'Weizen Premium', menge: 450, wert: 99000 },
      { name: 'Sojaschrot 44%', menge: 280, wert: 84000 },
      { name: 'NPK-Dünger', menge: 220, wert: 44000 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Bestandsübersicht</h1>
        <p className="text-muted-foreground">Lagerbestände & Kennzahlen</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtbestand</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Warehouse className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{bestand.gesamtmenge.toLocaleString('de-DE')} t</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtwert</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(bestand.gesamtwert)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bewegungen heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{bestand.bewegungenHeute}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Reichweite (Tage)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{bestand.reichweite}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Top-Artikel nach Wert
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {bestand.topArtikel.map((artikel, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{artikel.name}</div>
                  <div className="text-sm text-muted-foreground">{artikel.menge} t</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(artikel.wert)}
                  </div>
                  <Badge variant="outline">#{i + 1}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
