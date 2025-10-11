import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Euro, TrendingUp } from 'lucide-react'

export default function KostenstellenrechnungPage(): JSX.Element {
  const kosten = {
    gesamt: 385000,
    budget: 420000,
    auslastung: 91.7,
    kostenstellen: [
      { name: 'Lager & Logistik', kosten: 125000, budget: 140000, auslastung: 89.3 },
      { name: 'Annahme', kosten: 95000, budget: 100000, auslastung: 95.0 },
      { name: 'Verwaltung', kosten: 85000, budget: 90000, auslastung: 94.4 },
      { name: 'Vertrieb', kosten: 80000, budget: 90000, auslastung: 88.9 },
    ],
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Kostenstellenrechnung</h1>
        <p className="text-muted-foreground">Oktober 2025</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kosten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kosten.gesamt)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Budget</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kosten.budget)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{kosten.auslastung}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verfügbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kosten.budget - kosten.gesamt)}
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Kostenstellen-Übersicht
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {kosten.kostenstellen.map((kst, i) => (
              <div key={i} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-semibold">{kst.name}</div>
                  <div className="text-right">
                    <div className="font-bold">
                      {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kst.kosten)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Budget: {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(kst.budget)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${kst.auslastung > 95 ? 'bg-red-600' : kst.auslastung > 90 ? 'bg-orange-600' : 'bg-green-600'}`}
                      style={{ width: `${kst.auslastung}%` }}
                    />
                  </div>
                  <Badge variant={kst.auslastung > 95 ? 'destructive' : 'outline'}>
                    {kst.auslastung.toFixed(1)}%
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
