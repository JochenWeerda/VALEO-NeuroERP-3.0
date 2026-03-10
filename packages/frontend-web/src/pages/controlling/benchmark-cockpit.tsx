/**
 * Branchenbenchmark-Cockpit (Gap 047): Vergleich eigene KPIs vs. Branchendurchschnitt Landhandel.
 */

import { useMemo, useState } from 'react'
import { useBenchmark } from '@/lib/api/controlling'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus, BarChart3, Loader2 } from 'lucide-react'

const KPI_LABELS: Record<string, string> = {
  revenue: 'Umsatz',
  orders: 'Aufträge',
  customers: 'Aktive Kunden',
  conversion_rate: 'Konversionsrate (%)',
  avg_order_value: 'Durchschn. Auftragswert (€)',
  revenue_per_customer: 'Umsatz pro Kunde (€)',
}

function formatValue(key: string, val: number): string {
  if (key === 'conversion_rate') return `${val.toFixed(1)} %`
  if (key.includes('revenue') || key.includes('value')) return val.toLocaleString('de-DE', { maximumFractionDigits: 0 })
  return val.toLocaleString('de-DE')
}

export default function BenchmarkCockpitPage(): JSX.Element {
  const [period, setPeriod] = useState<'month' | 'quarter' | 'year'>('month')

  const { start_date, end_date } = useMemo(() => {
    const end = new Date()
    end.setHours(0, 0, 0, 0)
    const start = new Date(end)
    if (period === 'month') start.setMonth(start.getMonth() - 1)
    else if (period === 'quarter') start.setMonth(start.getMonth() - 3)
    else start.setFullYear(start.getFullYear() - 1)
    return {
      start_date: start.toISOString().slice(0, 10),
      end_date: end.toISOString().slice(0, 10),
    }
  }, [period])

  const { data, isLoading, isError, error } = useBenchmark(start_date, end_date)

  const comparisonEntries = useMemo(() => {
    if (!data?.comparison) return []
    return Object.entries(data.comparison).filter(
      ([k]) => ['revenue', 'orders', 'customers', 'conversion_rate', 'avg_order_value', 'revenue_per_customer'].includes(k)
    )
  }, [data])

  if (isError) {
    return (
      <div className="space-y-6 p-6">
        <h1 className="text-2xl font-semibold">Branchenbenchmark</h1>
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">
              {error instanceof Error ? error.message : 'Fehler beim Laden des Benchmarks'}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold">
          <BarChart3 className="h-6 w-6" />
          Branchenbenchmark
        </h1>
        <p className="mt-1 text-muted-foreground">
          Vergleich Ihrer KPIs mit dem Branchendurchschnitt Landhandel (Gap 047). Referenzwerte sind Platzhalter.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <NativeSelect
          value={period}
          onValueChange={(v) => setPeriod(v as 'month' | 'quarter' | 'year')}
          options={[
            { value: 'month', label: 'Letzter Monat' },
            { value: 'quarter', label: 'Letztes Quartal' },
            { value: 'year', label: 'Letztes Jahr' },
          ]}
          className="w-[180px]"
        />
        {data?.period && (
          <span className="text-sm text-muted-foreground">
            {data.period.start_date} – {data.period.end_date}
          </span>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 py-12 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Lade Benchmark-Daten...</span>
        </div>
      ) : data ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {comparisonEntries.map(([key, comp]) => {
            const ownVal = comp.own ?? 0
            const branchVal = comp.branch
            const pct = comp.deviation_pct
            const label = KPI_LABELS[key] ?? key

            let statusIcon = <Minus className="h-4 w-4 text-muted-foreground" />
            let statusBadge: React.ReactNode = null
            if (pct != null) {
              if (pct > 0) {
                statusIcon = <TrendingUp className="h-4 w-4 text-green-600" />
                statusBadge = <Badge variant="default" className="bg-green-600">+{pct} %</Badge>
              } else if (pct < 0) {
                statusIcon = <TrendingDown className="h-4 w-4 text-amber-600" />
                statusBadge = <Badge variant="secondary">{pct} %</Badge>
              } else {
                statusBadge = <Badge variant="outline">0 %</Badge>
              }
            }

            return (
              <Card key={key}>
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between text-sm font-medium">
                    {label}
                    {statusIcon}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex items-baseline justify-between">
                    <span className="text-2xl font-bold">{formatValue(key, ownVal)}</span>
                    {statusBadge}
                  </div>
                  {branchVal != null && (
                    <p className="text-xs text-muted-foreground">
                      Branche: {formatValue(key, Number(branchVal))}
                    </p>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : null}
    </div>
  )
}
