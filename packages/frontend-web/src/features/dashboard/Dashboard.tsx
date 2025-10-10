import type { ReactElement } from 'react'
import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'
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
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const KPI_KEYS = [
  'contract_long_tons',
  'contract_short_tons',
  'weighing_today_tons',
  'inventory_lots_blocked',
] as const

const TREND_HISTORY_LIMIT = 14
const BAR_CORNER_RADIUS = 8

const kpiSchema = z.object({
  contract_long_tons: z.number().nonnegative().default(0),
  contract_short_tons: z.number().nonnegative().default(0),
  weighing_today_tons: z.number().nonnegative().default(0),
  inventory_lots_blocked: z.number().nonnegative().default(0),
  updated_at: z.string().datetime({ offset: true }).optional(),
})

const trendPointSchema = z.object({
  date: z.string().min(1),
  contract_long_tons: z.number().nonnegative().default(0),
  contract_short_tons: z.number().nonnegative().default(0),
})

const trendResponseSchema = z
  .array(trendPointSchema)
  .or(z.object({ data: z.array(trendPointSchema) }).transform((payload) => payload.data))

const tonsFormatter = new Intl.NumberFormat('de-DE', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

const integerFormatter = new Intl.NumberFormat('de-DE')
const dateFormatter = new Intl.DateTimeFormat('de-DE')

const fetchKpis = async (): Promise<KpiResult> => {
  const payload = await apiClient.get<unknown>('/analytics/api/v1/kpis')
  const parsed = kpiSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data
  }

  const empty: KpiResult = {
    contract_long_tons: 0,
    contract_short_tons: 0,
    weighing_today_tons: 0,
    inventory_lots_blocked: 0,
    updated_at: undefined,
  }
  return empty
}

const fetchTrend = async (): Promise<TrendPoint[]> => {
  const payload = await apiClient.get<unknown>('/analytics/api/v1/cubes/contract-positions')
  const parsed = trendResponseSchema.safeParse(payload)
  if (parsed.success) {
    return parsed.data.slice(-TREND_HISTORY_LIMIT)
  }
  return []
}

type KpiResult = z.infer<typeof kpiSchema>
type TrendPoint = z.infer<typeof trendPointSchema>

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
          <p className="text-sm text-slate-500">Valero NeuroERP · Echtzeit Kennzahlen</p>
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

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Card className="rounded-2xl shadow-sm">
          <CardHeader>
            <CardTitle>Contract Positionen Trend</CardTitle>
            <CardDescription>Entwicklung der Long- und Short-Mengen</CardDescription>
          </CardHeader>
          <CardContent>
            {isTrendLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : isTrendError ? (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50">
                <p className="text-sm font-medium text-slate-700">Trenddaten nicht verfuegbar</p>
                <Button variant="outline" size="sm" onClick={() => void refetchTrend()}>
                  Erneut laden
                </Button>
              </div>
            ) : trend.length > 0 ? (
              <ResponsiveContainer height={300} width="100%">
                <LineChart data={trend}>
                  <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    stroke="#94a3b8"
                    tickFormatter={(value) => dateFormatter.format(new Date(value))}
                  />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    labelFormatter={(value) => dateFormatter.format(new Date(value))}
                    formatter={(value: number, name: string) => [
                      `${tonsFormatter.format(value)} t`,
                      name === 'contract_long_tons' ? 'Long' : 'Short',
                    ]}
                  />
                  <Line type="monotone" dataKey="contract_long_tons" stroke="#2563eb" strokeWidth={2} dot={false} name="Long" />
                  <Line type="monotone" dataKey="contract_short_tons" stroke="#f97316" strokeWidth={2} dot={false} name="Short" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50 text-center">
                <p className="text-sm font-semibold text-slate-700">Keine Trenddaten verfuegbar</p>
                <p className="text-xs text-slate-500">Sobald Bewegungen vorliegen, wird die Entwicklung angezeigt.</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-sm">
          <CardHeader>
            <CardTitle>Wiege-Performance der letzten Tage</CardTitle>
            <CardDescription>Vergleich der gemessenen Netto-Tonnen</CardDescription>
          </CardHeader>
          <CardContent>
            {isTrendLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : isTrendError ? (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50">
                <p className="text-sm font-medium text-slate-700">Wiegedaten nicht verfuegbar</p>
                <Button variant="outline" size="sm" onClick={() => void refetchTrend()}>
                  Erneut laden
                </Button>
              </div>
            ) : trend.length > 0 ? (
              <ResponsiveContainer height={300} width="100%">
                <BarChart data={trend}>
                  <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    stroke="#94a3b8"
                    tickFormatter={(value) => dateFormatter.format(new Date(value))}
                  />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    labelFormatter={(value) => dateFormatter.format(new Date(value))}
                    formatter={(value: number) => [`${tonsFormatter.format(value)} t`, 'Netto']}
                  />
                  <Bar dataKey="contract_long_tons" fill="#2563eb" radius={[BAR_CORNER_RADIUS, BAR_CORNER_RADIUS, 0, 0]} name="Netto" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50 text-center">
                <p className="text-sm font-semibold text-slate-700">Keine Wiegedaten verfuegbar</p>
                <p className="text-xs text-slate-500">Sobald Tickets gebucht sind, werden Mengen dargestellt.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}






