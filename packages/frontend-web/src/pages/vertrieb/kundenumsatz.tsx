import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Euro, TrendingUp, Users } from 'lucide-react'

export default function KundenumsatzPage(): JSX.Element {
  const analyse = {
    gesamtumsatz: 1250000,
    kunden: 142,
    durchschnitt: 8803,
    wachstum: 8.7,
    segmente: [
      { segment: 'A-Kunden (>50k)', anzahl: 12, umsatz: 750000, anteil: 60 },
      { segment: 'B-Kunden (20-50k)', anzahl: 28, umsatz: 350000, anteil: 28 },
      { segment: 'C-Kunden (<20k)', anzahl: 102, umsatz: 150000, anteil: 12 },
    ],
    topKunden: [
      { name: 'Landhandel Nord', umsatz: 125000, wachstum: 12.5 },
      { name: 'Agrar Süd', umsatz: 98000, wachstum: 8.2 },
      { name: 'Müller GmbH', umsatz: 87000, wachstum: -3.1 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Kundenumsatz-Analyse</h1>
        <p className="text-muted-foreground">ABC-Analyse & Segmentierung</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtumsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(analyse.gesamtumsatz)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-2xl font-bold">{analyse.kunden}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Umsatz/Kunde</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(analyse.durchschnitt)}
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
              <span className="text-2xl font-bold text-green-600">+{analyse.wachstum}%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            ABC-Segmentierung
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analyse.segmente.map((seg, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="font-semibold">{seg.segment}</div>
                    <div className="text-sm text-muted-foreground">{seg.anzahl} Kunden</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(seg.umsatz)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${i === 0 ? 'bg-green-600' : i === 1 ? 'bg-blue-600' : 'bg-gray-400'}`}
                      style={{ width: `${seg.anteil}%` }}
                    />
                  </div>
                  <Badge variant="outline">{seg.anteil}%</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top 3 Kunden</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analyse.topKunden.map((kunde, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="font-semibold">{kunde.name}</div>
                  <Badge variant="outline" className="mt-1">#{i + 1}</Badge>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kunde.umsatz)}
                  </div>
                  <div className={`text-sm font-semibold ${kunde.wachstum > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {kunde.wachstum > 0 ? '+' : ''}{kunde.wachstum}%
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
