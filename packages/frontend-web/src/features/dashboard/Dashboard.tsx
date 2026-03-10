import { Suspense, lazy, type ReactElement } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/axios'

const KPI_KEYS = [
  'contract_long_tons',
  'contract_short_tons',
  'weighing_today_tons',
  'inventory_lots_blocked',
] as const

const TREND_HISTORY_LIMIT = 14
const DashboardCharts = lazy(() => import('@/features/dashboard/DashboardCharts'))

type KpiResult = {
  contract_long_tons: number
  contract_short_tons: number
  weighing_today_tons: number
  inventory_lots_blocked: number
  updated_at?: string
}

type TrendPoint = {
  date: string
  contract_long_tons: number
  contract_short_tons: number
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' ? (value as Record<string, unknown>) : null

const asArray = (value: unknown): unknown[] => (Array.isArray(value) ? value : [])
const asString = (value: unknown, fallback = ''): string => (typeof value === 'string' && value.length > 0 ? value : fallback)
const asNumber = (value: unknown): number => (typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : 0)

const tonsFormatter = new Intl.NumberFormat('de-DE', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

const integerFormatter = new Intl.NumberFormat('de-DE')
const dateFormatter = new Intl.DateTimeFormat('de-DE')

const normalizeKpis = (value: unknown): KpiResult => {
  const record = asRecord(value)
  if (!record) {
    return {
      contract_long_tons: 0,
      contract_short_tons: 0,
      weighing_today_tons: 0,
      inventory_lots_blocked: 0,
      updated_at: undefined,
    }
  }

  return {
    contract_long_tons: asNumber(record.contract_long_tons),
    contract_short_tons: asNumber(record.contract_short_tons),
    weighing_today_tons: asNumber(record.weighing_today_tons),
    inventory_lots_blocked: asNumber(record.inventory_lots_blocked),
    updated_at: asString(record.updated_at) || undefined,
  }
}

const normalizeTrendPoint = (value: unknown): TrendPoint | null => {
  const record = asRecord(value)
  if (!record) {
    return null
  }

  const date = asString(record.date)
  if (!date) {
    return null
  }

  return {
    date,
    contract_long_tons: asNumber(record.contract_long_tons),
    contract_short_tons: asNumber(record.contract_short_tons),
  }
}

const extractTrendList = (value: unknown): unknown[] => {
  if (Array.isArray(value)) {
    return value
  }

  const record = asRecord(value)
  if (!record) {
    return []
  }

  return asArray(record.data)
}

const fetchKpis = async (): Promise<KpiResult> => {
  const payload = await apiClient.get<unknown>('/api/v1/analytics/kpis')
  return normalizeKpis(payload.data)
}

const fetchTrend = async (): Promise<TrendPoint[]> => {
  const payload = await apiClient.get<unknown>('/api/v1/analytics/cubes/contract-positions')
  return extractTrendList(payload.data)
    .map(normalizeTrendPoint)
    .filter((value): value is TrendPoint => value !== null)
    .slice(-TREND_HISTORY_LIMIT)
}

const KPI_TITLES: Record<(typeof KPI_KEYS)[number], string> = {
  contract_long_tons: 'Contract Long',
  contract_short_tons: 'Contract Short',
  weighing_today_tons: 'Wiegen heute',
  inventory_lots_blocked: 'Blockierte Lose',
}

const KPI_DESCRIPTIONS: Record<(typeof KPI_KEYS)[number], string> = {
  contract_long_tons: 'Offene Long-Positionen',
  contract_short_tons: 'Offene Short-Positionen',
  weighing_today_tons: 'Gewogene Menge seit Mitternacht',
  inventory_lots_blocked: 'Qualitaetsbedingte Sperren',
}

const renderKpiValue = (key: (typeof KPI_KEYS)[number], value: number): string => {
  if (key === 'inventory_lots_blocked') {
    return integerFormatter.format(value)
  }
  return `${tonsFormatter.format(value)} t`
}

export default function Dashboard(): ReactElement {
  const {
    data: kpis,
    isPending: isKpiLoading,
    isError: isKpiError,
    refetch: refetchKpis,
  } = useQuery({
    queryKey: queryKeys.analytics.kpis,
    queryFn: fetchKpis,
  })

  const {
    data: trend = [],
    isPending: isTrendLoading,
    isError: isTrendError,
    refetch: refetchTrend,
  } = useQuery({
    queryKey: queryKeys.analytics.cubes('contract-positions'),
    queryFn: fetchTrend,
  })

  if (isKpiError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <Button variant="outline" onClick={() => void refetchKpis()}>
            Erneut laden
          </Button>
        </div>
        <Alert variant="destructive">
          <AlertTitle>Daten konnten nicht geladen werden</AlertTitle>
          <AlertDescription>Bitte Verbindung pruefen und erneut versuchen.</AlertDescription>
        </Alert>
      </div>
    )
  }

  const lastUpdatedLabel = kpis?.updated_at !== undefined ? dateFormatter.format(new Date(kpis.updated_at)) : 'unbekannt'

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500">Valero NeuroERP - Echtzeit Kennzahlen</p>
        </div>
        <p className="text-xs text-slate-400">Aktualisiert am {lastUpdatedLabel}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {KPI_KEYS.map((key) => (
          <Card key={key} className="rounded-2xl shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">{KPI_TITLES[key]}</CardTitle>
              <CardDescription>{KPI_DESCRIPTIONS[key]}</CardDescription>
            </CardHeader>
            <CardContent>
              {isKpiLoading || kpis === undefined ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <p className="text-2xl font-semibold text-slate-900">
                  {renderKpiValue(key, kpis[key])}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {isTrendLoading ? (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <Skeleton className="h-[300px] w-full" />
          <Skeleton className="h-[300px] w-full" />
        </div>
      ) : (
        <Suspense
          fallback={
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
              <Skeleton className="h-[300px] w-full" />
              <Skeleton className="h-[300px] w-full" />
            </div>
          }
        >
          <DashboardCharts
            trend={trend}
            isTrendError={isTrendError}
            refetchTrend={refetchTrend}
            dateFormatter={dateFormatter}
          />
        </Suspense>
      )}
    </div>
  )
}
