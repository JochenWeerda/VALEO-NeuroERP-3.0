import { Suspense, lazy } from 'react'
import { Card } from '@/components/ui/card'
import { useMcpQuery } from '@/lib/mcp'
import { useMcpRealtime } from '@/lib/useMcpRealtime'
import { useToast } from '@/components/ui/toast-provider'
import { Toolbar } from '@/components/ui/toolbar'
import { CopilotInsights } from '@/features/copilot/CopilotInsights'
import { useForecast } from '@/features/analytics/useForecast'
import { useKpiAlerts } from '@/features/alerts/useKpiAlerts'
import { KpiHeatmap } from '@/features/alerts/KpiHeatmap'
import { AlertBanner, AlertList } from '@/features/alerts/AlertBanner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'

const AnalyticsDashboardCharts = lazy(() =>
  import('@/pages/analytics/AnalyticsDashboardCharts').then((module) => ({ default: module.default })),
)

const CHART_HEIGHT = 250
const DECIMAL_PLACES = 1

type KPI = {
  id: string
  label: string
  value: number
  delta: number
  unit?: string
}

type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

type KPIResponse = {
  data: KPI[]
}

type TrendResponse = {
  data: TrendPoint[]
}

export default function AnalyticsDashboard(): JSX.Element {
  const { data: kpiData } = useMcpQuery<KPIResponse>('analytics', 'kpis', [])
  const { data: trendData } = useMcpQuery<TrendResponse>('analytics', 'trends', [])
  const { push } = useToast()
  const { result: forecast, loading: loadingForecast } = useForecast()
  const { cells, alerts } = useKpiAlerts()

  useMcpRealtime('analytics', (evt) => {
    if (evt.type === 'updated') push('Analytics aktualisiert')
    if (evt.type === 'forecast-updated') push('Prognose aktualisiert')
  })

  const emptyKpiFallback: KPI[] = [
    { id: 'kpi-1', label: 'Umsatz', value: 0, delta: 0, unit: 'EUR' },
    { id: 'kpi-2', label: 'Marge', value: 0, delta: 0, unit: 'EUR' },
    { id: 'kpi-3', label: 'Auftraege', value: 0, delta: 0, unit: 'EUR' },
    { id: 'kpi-4', label: 'Lagerbestand', value: 0, delta: 0, unit: 'EUR' },
  ]
  const rawKpis = kpiData?.ok === false ? [] : kpiData?.data?.data ?? []
  const rawTrends = trendData?.ok === false ? [] : trendData?.data?.data ?? []
  const kpis = rawKpis.length === 0 ? emptyKpiFallback : rawKpis
  const trends = rawTrends
  const showEmptyState = rawKpis.length === 0 && rawTrends.length === 0

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <Toolbar onSearch={() => undefined} onCopilot={() => push('KI-Analyse aktualisiert')} />

      {showEmptyState && (
        <Alert variant="default" className="border-amber-200 bg-amber-50 text-amber-800">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Aktuell liegen keine Analytics-Daten vor. Die Uebersicht bleibt betriebsbereit und fuellt sich, sobald
            Kennzahlen oder Trends aus den Quellsystemen eintreffen.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {kpis.map((k, idx): JSX.Element => {
          const label = k.label?.trim() || `Kennzahl ${idx + 1}`
          const valueText = `${k.value.toLocaleString('de-DE')} ${k.unit ?? ''}`.trim()
          const deltaText = `${k.delta >= 0 ? '?' : '?'} ${Math.abs(k.delta).toFixed(DECIMAL_PLACES)} %`
          return (
            <div key={k.id} className="animate-in fade-in-0 slide-in-from-bottom-1 duration-200">
              <Card className="bg-linear-to-br from-emerald-50 to-white p-4 shadow-md">
                <div className="text-sm opacity-70">{label}</div>
                <div className="text-2xl font-bold">{valueText}</div>
                <div className={k.delta >= 0 ? 'text-sm text-green-600' : 'text-sm text-red-600'}>{deltaText}</div>
              </Card>
            </div>
          )
        })}
      </div>

      <Suspense fallback={<div className="grid grid-cols-1 gap-4 md:grid-cols-2"><Card className="h-[282px] animate-pulse" /><Card className="h-[282px] animate-pulse" /></div>}>
        <AnalyticsDashboardCharts trends={trends} chartHeight={CHART_HEIGHT} />
      </Suspense>

      <Card className="p-4">
        <h4 className="mb-2 font-semibold">KPI Heatmap</h4>
        <KpiHeatmap cells={cells} />
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <AlertBanner items={alerts} />
        <Card className="p-4 md:col-span-2">
          <h4 className="mb-2 font-semibold">Alerts</h4>
          <AlertList items={alerts} />
        </Card>
      </div>

      <CopilotInsights />

      {loadingForecast && <p className="text-sm opacity-70">Berechne Prognose ...</p>}
      {forecast?.forecast != null && (
        <div
          className={`${forecast?.forecast?.anomaly === true ? 'border-red-300 bg-red-50' : 'border-emerald-300 bg-emerald-50'} animate-in fade-in-0 rounded-xl border p-4 shadow duration-200`}
        >
          <div className="flex items-center gap-2 font-semibold">
            <span>Prognose</span>
            {forecast?.forecast?.anomaly === true && <span className="text-xs text-red-600">ANOMALIE</span>}
          </div>
          <p className="mt-1 text-sm">{forecast?.summary ?? 'Keine Prognosedaten verfuegbar.'}</p>
          {(forecast?.factors?.length ?? 0) > 0 && (
            <ul className="mt-2 list-inside list-disc text-sm">
              {(forecast?.factors ?? []).map((factor, index): JSX.Element => <li key={index}>{factor}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
