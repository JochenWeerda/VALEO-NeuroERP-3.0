import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Euro, TrendingUp } from 'lucide-react'

export default function DeckungsbeitragPage(): JSX.Element {
  const db = {
    gesamt: 450000,
    vorjahr: 420000,
    wachstum: 7.1,
    nachKultur: [
      { kultur: 'Weizen', db: 180000, flaeche: 120, dbProHa: 1500 },
      { kultur: 'Raps', db: 150000, flaeche: 80, dbProHa: 1875 },
      { kultur: 'Mais', db: 120000, flaeche: 50, dbProHa: 2400 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Deckungsbeitrags-Rechnung</h1>
          <p className="text-muted-foreground">Wirtschaftsjahr 2024/25</p>
        </div>
        <Button variant="outline">Zeitraum ändern</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Deckungsbeitrag Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(db.gesamt)}
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
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(db.vorjahr)}
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
              <span className="text-2xl font-bold text-green-600">+{db.wachstum}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Deckungsbeitrag nach Kultur
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {db.nachKultur.map((k, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{k.kultur}</div>
                  <div className="text-sm text-muted-foreground">{k.flaeche} ha</div>
                  <Badge variant="outline" className="mt-1">#{i + 1}</Badge>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.db)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(k.dbProHa)} / ha
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
