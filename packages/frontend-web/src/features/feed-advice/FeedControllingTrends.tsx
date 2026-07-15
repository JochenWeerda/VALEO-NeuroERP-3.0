import { useCallback, useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
import { SimpleComparisonBars } from '@/components/charts/SimpleComparisonBars'
import { CHART_TARGET, chartSeriesColor } from '@/components/charts/chart-palette'
import { fetchFeedingGroups, type FeedingGroup } from '@/lib/api/rations-lifecycle'
import { fetchControllingSeries, type ControllingSeriesPoint } from '@/lib/api/feed-controlling'
import { getAxiosErrorMessage } from '@/lib/api-client'

const RANGES = [
  { days: 30, label: '30 Tage' },
  { days: 90, label: '90 Tage' },
  { days: 180, label: '180 Tage' },
] as const

type NumericKey =
  | 'actual_dmi_kg_cow' | 'target_dmi_kg_cow'
  | 'actual_cost_eur_cow' | 'target_cost_eur_cow'
  | 'actual_milk_kg_cow' | 'target_milk_kg_cow' | 'actual_ecm_kg_cow'
  | 'nitrogen_efficiency_pct'
  | 'actual_methane_kg_cow' | 'target_methane_kg_cow'

const BENCHMARK_KPIS: Array<{ key: NumericKey; label: string; unit: string; digits: number }> = [
  { key: 'actual_dmi_kg_cow', label: 'TM-Aufnahme', unit: 'kg/Kuh', digits: 1 },
  { key: 'actual_cost_eur_cow', label: 'Futterkosten', unit: 'EUR/Kuh', digits: 2 },
  { key: 'actual_ecm_kg_cow', label: 'ECM', unit: 'kg/Kuh', digits: 1 },
  { key: 'nitrogen_efficiency_pct', label: 'N-Effizienz', unit: '%', digits: 1 },
  { key: 'actual_methane_kg_cow', label: 'Methan', unit: 'kg/Kuh', digits: 2 },
]

function isoDaysAgo(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().slice(0, 10)
}

function shortDate(iso: string): string {
  const [, month, day] = iso.split('-')
  return `${day}.${month}.`
}

/** Mittelwert der bekannten Werte; kein Wert bekannt -> null (Luecke, nie 0). */
function meanOrNull(values: Array<number | null | undefined>): number | null {
  const known = values.filter((value): value is number => typeof value === 'number' && Number.isFinite(value))
  if (known.length === 0) return null
  return known.reduce((sum, value) => sum + value, 0) / known.length
}

/** Punkte je Tag verdichten (bei "Alle Gruppen" Mittel ueber die Gruppen desselben Tages). */
function dailySeries(points: ControllingSeriesPoint[], keys: NumericKey[]): Array<{ label: string;[key: string]: string | number | null }> {
  const byDate = new Map<string, ControllingSeriesPoint[]>()
  for (const point of points) {
    const existing = byDate.get(point.observation_date)
    if (existing) existing.push(point)
    else byDate.set(point.observation_date, [point])
  }
  return [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, dayPoints]) => {
      const row: { label: string;[key: string]: string | number | null } = { label: shortDate(date) }
      for (const key of keys) row[key] = meanOrNull(dayPoints.map((point) => point[key]))
      return row
    })
}

function formatNumber(value: number, digits: number): string {
  return value.toLocaleString('de-DE', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

export function FeedControllingTrends(): JSX.Element {
  const [groups, setGroups] = useState<FeedingGroup[]>([])
  const [groupId, setGroupId] = useState<string>('')
  const [rangeDays, setRangeDays] = useState<number>(30)
  const [benchmarkKpi, setBenchmarkKpi] = useState<NumericKey>('actual_dmi_kg_cow')
  const [points, setPoints] = useState<ControllingSeriesPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async (): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      const [groupList, series] = await Promise.all([
        fetchFeedingGroups(),
        fetchControllingSeries({ groupId: groupId || undefined, dateFrom: isoDaysAgo(rangeDays) }),
      ])
      setGroups(groupList)
      setPoints(series)
    } catch (loadError) {
      setError(getAxiosErrorMessage(loadError))
    } finally {
      setLoading(false)
    }
  }, [groupId, rangeDays])

  useEffect(() => { void load() }, [load])

  const hasEstimatedMethane = useMemo(
    () => points.some((point) => point.methane_estimated && point.actual_methane_kg_cow !== null && point.actual_methane_kg_cow !== undefined),
    [points],
  )

  const dmiData = useMemo(() => dailySeries(points, ['actual_dmi_kg_cow', 'target_dmi_kg_cow']), [points])
  const costData = useMemo(() => dailySeries(points, ['actual_cost_eur_cow', 'target_cost_eur_cow']), [points])
  const milkData = useMemo(() => dailySeries(points, ['actual_milk_kg_cow', 'actual_ecm_kg_cow', 'target_milk_kg_cow']), [points])
  const nitrogenData = useMemo(() => dailySeries(points, ['nitrogen_efficiency_pct']), [points])
  const methaneData = useMemo(() => dailySeries(points, ['actual_methane_kg_cow', 'target_methane_kg_cow']), [points])

  const benchmark = useMemo(() => {
    const byGroup = new Map<string, ControllingSeriesPoint[]>()
    for (const point of points) {
      const existing = byGroup.get(point.group_name)
      if (existing) existing.push(point)
      else byGroup.set(point.group_name, [point])
    }
    return [...byGroup.entries()]
      .map(([name, groupPoints]) => ({ name, value: meanOrNull(groupPoints.map((point) => point[benchmarkKpi])) }))
      .filter((entry): entry is { name: string; value: number } => entry.value !== null)
      .sort((a, b) => b.value - a.value)
  }, [points, benchmarkKpi])

  const benchmarkMeta = BENCHMARK_KPIS.find((kpi) => kpi.key === benchmarkKpi) ?? BENCHMARK_KPIS[0]
  const hasAnyValue = points.length > 0

  return (
    <section aria-label="Langfristtrends" className="space-y-6" data-testid="feed-controlling-trends">
      <div className="flex flex-wrap items-end gap-4">
        <div className="grid gap-1.5">
          <Label htmlFor="trend-group">Tiergruppe</Label>
          <select
            id="trend-group"
            className="h-10 rounded-md border bg-background px-3 text-sm"
            value={groupId}
            onChange={(event) => setGroupId(event.target.value)}
          >
            <option value="">Alle Gruppen</option>
            {groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}
          </select>
        </div>
        <div className="grid gap-1.5">
          <span className="text-sm font-medium leading-none">Zeitraum</span>
          <div className="flex gap-1" role="group" aria-label="Zeitraum wählen">
            {RANGES.map((range) => (
              <Button
                key={range.days}
                type="button"
                size="sm"
                variant={rangeDays === range.days ? 'default' : 'outline'}
                aria-pressed={rangeDays === range.days}
                onClick={() => setRangeDays(range.days)}
              >
                {range.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2" aria-hidden>
          {[0, 1, 2, 3].map((index) => <div key={index} className="h-64 animate-pulse rounded-lg bg-muted/40" />)}
        </div>
      ) : error ? (
        <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
          <p className="font-medium text-status-error">Trenddaten konnten nicht geladen werden.</p>
          <p className="mt-1 text-muted-foreground">{error}</p>
          <Button type="button" variant="outline" size="sm" className="mt-3" onClick={() => { void load() }}>Erneut laden</Button>
        </div>
      ) : !hasAnyValue ? (
        <div className="rounded-lg border bg-muted/30 p-6 text-sm text-muted-foreground" role="status">
          Im gewählten Zeitraum liegen noch keine Tageswerte vor. Bitte über „Tageswerte erfassen"
          Istwerte je Tiergruppe eintragen — die Trends erscheinen hier automatisch.
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <section className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 font-semibold">TM-Aufnahme (kg/Kuh)</h3>
              <SimpleLineChart
                data={dmiData}
                series={[
                  { key: 'actual_dmi_kg_cow', label: 'Ist', color: chartSeriesColor(0) },
                  { key: 'target_dmi_kg_cow', label: 'Soll (aktive Ration)', color: CHART_TARGET, dashed: true },
                ]}
                height={240}
                valueFormatter={(value) => formatNumber(value, 1)}
              />
            </section>
            <section className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 font-semibold">Futterkosten (EUR/Kuh/Tag)</h3>
              <SimpleLineChart
                data={costData}
                series={[
                  { key: 'actual_cost_eur_cow', label: 'Ist', color: chartSeriesColor(0) },
                  { key: 'target_cost_eur_cow', label: 'Soll (aktive Ration)', color: CHART_TARGET, dashed: true },
                ]}
                height={240}
                valueFormatter={(value) => formatNumber(value, 2)}
              />
            </section>
            <section className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 font-semibold">Milch und ECM (kg/Kuh)</h3>
              <SimpleLineChart
                data={milkData}
                series={[
                  { key: 'actual_milk_kg_cow', label: 'Milch Ist', color: chartSeriesColor(0) },
                  { key: 'actual_ecm_kg_cow', label: 'ECM Ist', color: chartSeriesColor(2) },
                  { key: 'target_milk_kg_cow', label: 'Milch Soll', color: CHART_TARGET, dashed: true },
                ]}
                height={240}
                valueFormatter={(value) => formatNumber(value, 1)}
              />
            </section>
            <section className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 font-semibold">Milch-N-Effizienz (%)</h3>
              <SimpleLineChart
                data={nitrogenData}
                series={[{ key: 'nitrogen_efficiency_pct', label: 'N-Effizienz', color: chartSeriesColor(0) }]}
                height={240}
                valueFormatter={(value) => formatNumber(value, 1)}
              />
            </section>
            <section className="rounded-lg border bg-card p-4 md:col-span-2">
              <h3 className="mb-1 font-semibold">Methan (kg/Kuh/Tag)</h3>
              {hasEstimatedMethane ? (
                <p className="mb-3 text-xs text-muted-foreground" data-testid="methane-estimated-note">
                  Enthält als Schätzung gekennzeichnete Werte.
                </p>
              ) : null}
              <SimpleLineChart
                data={methaneData}
                series={[
                  { key: 'actual_methane_kg_cow', label: 'Ist', color: chartSeriesColor(0) },
                  { key: 'target_methane_kg_cow', label: 'Soll (aktive Ration)', color: CHART_TARGET, dashed: true },
                ]}
                height={220}
                valueFormatter={(value) => formatNumber(value, 2)}
              />
            </section>
          </div>

          <section className="rounded-lg border bg-card p-4" aria-label="Gruppen-Benchmark">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <h3 className="font-semibold">Gruppen-Benchmark (Ø im Zeitraum)</h3>
              <div className="grid gap-1.5">
                <Label htmlFor="benchmark-kpi" className="sr-only">Kennzahl</Label>
                <select
                  id="benchmark-kpi"
                  className="h-9 rounded-md border bg-background px-3 text-sm"
                  value={benchmarkKpi}
                  onChange={(event) => setBenchmarkKpi(event.target.value as NumericKey)}
                >
                  {BENCHMARK_KPIS.map((kpi) => <option key={kpi.key} value={kpi.key}>{kpi.label} ({kpi.unit})</option>)}
                </select>
              </div>
            </div>
            {benchmark.length === 0 ? (
              <p className="text-sm text-muted-foreground" role="status">
                Für diese Kennzahl liegen im Zeitraum keine Istwerte vor.
              </p>
            ) : (
              <SimpleComparisonBars
                data={benchmark}
                valueFormatter={(value) => `${formatNumber(value, benchmarkMeta.digits)} ${benchmarkMeta.unit}`}
              />
            )}
            <p className="mt-3 text-xs text-muted-foreground">
              Vergleich der eigenen Fütterungsgruppen. Ein anonymisierter Betriebsvergleich ist bewusst
              späterer Ausbau.
            </p>
          </section>
        </>
      )}
    </section>
  )
}
