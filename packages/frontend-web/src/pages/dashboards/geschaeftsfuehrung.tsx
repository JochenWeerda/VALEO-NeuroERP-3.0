import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Euro, TrendingUp, Users } from 'lucide-react'

export default function GeschaeftsfuehrungDashboardPage(): JSX.Element {
  const dashboard = {
    umsatz: 1250000,
    ertrag: 430000,
    wachstum: 8.7,
    kunden: 142,
    mitarbeiter: 27,
    kennzahlen: [
      { label: 'Umsatzrendite', wert: '34.4%', trend: '+2.1%' },
      { label: 'Eigenkapitalquote', wert: '58.2%', trend: '+3.5%' },
      { label: 'Lagerumschlag', wert: '8.2', trend: '+0.8' },
    ],
    bereiche: [
      { name: 'Verkauf Getreide', umsatz: 525000, anteil: 42 },
      { name: 'Verkauf Futtermittel', umsatz: 380000, anteil: 30 },
      { name: 'Verkauf Betriebsmittel', umsatz: 345000, anteil: 28 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Geschäftsführungs-Dashboard</h1>
        <p className="text-muted-foreground">Executive Summary</p>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Jahresumsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.umsatz)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Jahresertrag</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(dashboard.ertrag)}
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
              <span className="text-2xl font-bold text-green-600">+{dashboard.wachstum}%</span>
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
              <span className="text-2xl font-bold">{dashboard.kunden}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{dashboard.mitarbeiter}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Wichtige Kennzahlen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboard.kennzahlen.map((kz, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <div className="font-semibold">{kz.label}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold">{kz.wert}</div>
                    <div className="text-sm font-semibold text-green-600">{kz.trend}</div>
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
              Umsatz nach Bereichen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboard.bereiche.map((bereich, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{bereich.name}</div>
                    <div className="text-right">
                      <div className="font-bold">
                        {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(bereich.umsatz)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-blue-600" style={{ width: `${bereich.anteil}%` }} />
                    </div>
                    <Badge variant="outline">{bereich.anteil}%</Badge>
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
