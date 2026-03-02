import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Euro, TrendingUp } from 'lucide-react'
import { useKostenstellen, useKostenstellenTimeseries } from '@/lib/api/controlling'

const fmt = (n: number) =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n)

export default function KostenstellenrechnungPage(): JSX.Element {
  const { data: kpis = [], isLoading: kpisLoading } = useKostenstellen()
  const { data: timeseries = [], isLoading: tsLoading } = useKostenstellenTimeseries()

  const isLoading = kpisLoading || tsLoading

  // Berechne Gesamt-Kosten und Budget aus den API-Daten
  const gesamtKosten = timeseries.reduce((sum, t) => sum + Number(t.value), 0)
  const budget = kpis.reduce((sum, k) => sum + (Number(k.target_value) || 0), 0)
  const auslastung = budget > 0 ? (gesamtKosten / budget) * 100 : 0

  // Baue Kostenstellen-Übersicht aus KPI-Definitionen + letztem Timeseries-Wert
  const kostenstellen = kpis
    .filter((k) => k.is_active)
    .map((k) => {
      const last = timeseries.filter((t) => t.kpi_id === k.id).sort((a, b) => b.period_start.localeCompare(a.period_start))[0]
      const kosten = last ? Number(last.value) : 0
      const kst_budget = Number(k.target_value) || 0
      const kst_auslastung = kst_budget > 0 ? (kosten / kst_budget) * 100 : 0
      return { name: k.name, kosten, budget: kst_budget, auslastung: kst_auslastung }
    })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 p-6">
        <span className="text-muted-foreground">Lade Kostenstellen-Daten…</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Kostenstellenrechnung</h1>
        <p className="text-muted-foreground">Aktueller Zeitraum</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kosten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{fmt(gesamtKosten)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Budget</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{fmt(budget)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">{auslastung.toFixed(1)}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verfügbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{fmt(budget - gesamtKosten)}</span>
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
          {kostenstellen.length === 0 ? (
            <p className="text-muted-foreground text-sm">Keine Kostenstellen-Daten vorhanden.</p>
          ) : (
            <div className="space-y-3">
              {kostenstellen.map((kst, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="font-semibold">{kst.name}</div>
                    <div className="text-right">
                      <div className="font-bold">{fmt(kst.kosten)}</div>
                      <div className="text-sm text-muted-foreground">Budget: {fmt(kst.budget)}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full ${kst.auslastung > 95 ? 'bg-red-600' : kst.auslastung > 90 ? 'bg-orange-600' : 'bg-green-600'}`}
                        style={{ width: `${Math.min(kst.auslastung, 100)}%` }}
                      />
                    </div>
                    <Badge variant={kst.auslastung > 95 ? 'destructive' : 'outline'}>
                      {kst.auslastung.toFixed(1)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
