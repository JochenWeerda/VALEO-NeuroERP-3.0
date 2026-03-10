import { Suspense, lazy, type ReactElement } from 'react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

interface TrendPoint {
  date: string
  contract_long_tons: number
  contract_short_tons: number
}

interface DashboardChartsProps {
  trend: TrendPoint[]
  isTrendError: boolean
  refetchTrend: () => Promise<unknown>
  dateFormatter: Intl.DateTimeFormat
}

const DashboardTrendLineChart = lazy(() => import('@/features/dashboard/charts/DashboardTrendLineChart'))
const DashboardWeighingBarChart = lazy(() => import('@/features/dashboard/charts/DashboardWeighingBarChart'))

function EmptyChartState({
  title,
  description,
}: {
  title: string
  description: string
}): ReactElement {
  return (
    <div className="flex h-[300px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50 text-center">
      <p className="text-sm font-semibold text-slate-700">{title}</p>
      <p className="text-xs text-slate-500">{description}</p>
    </div>
  )
}

function ErrorChartState({ message, onRetry }: { message: string; onRetry: () => void }): ReactElement {
  return (
    <div className="flex h-[300px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50">
      <p className="text-sm font-medium text-slate-700">{message}</p>
      <Button variant="outline" size="sm" onClick={onRetry}>
        Erneut laden
      </Button>
    </div>
  )
}

function ChartSkeleton(): ReactElement {
  return <div className="h-[300px] w-full animate-pulse rounded-xl bg-slate-100" />
}

export default function DashboardCharts({
  trend,
  isTrendError,
  refetchTrend,
  dateFormatter,
}: DashboardChartsProps): ReactElement {
  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
      <Card className="rounded-2xl shadow-sm">
        <CardHeader>
          <CardTitle>Contract Positionen Trend</CardTitle>
          <CardDescription>Entwicklung der Long- und Short-Mengen</CardDescription>
        </CardHeader>
        <CardContent>
          {isTrendError ? (
            <ErrorChartState message="Trenddaten nicht verfuegbar" onRetry={() => void refetchTrend()} />
          ) : trend.length > 0 ? (
            <Suspense fallback={<ChartSkeleton />}>
              <DashboardTrendLineChart trend={trend} dateFormatter={dateFormatter} />
            </Suspense>
          ) : (
            <EmptyChartState title="Keine Trenddaten verfuegbar" description="Sobald Bewegungen vorliegen, wird die Entwicklung angezeigt." />
          )}
        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow-sm">
        <CardHeader>
          <CardTitle>Wiege-Performance der letzten Tage</CardTitle>
          <CardDescription>Vergleich der gemessenen Netto-Tonnen</CardDescription>
        </CardHeader>
        <CardContent>
          {isTrendError ? (
            <ErrorChartState message="Wiegedaten nicht verfuegbar" onRetry={() => void refetchTrend()} />
          ) : trend.length > 0 ? (
            <Suspense fallback={<ChartSkeleton />}>
              <DashboardWeighingBarChart
                trend={trend}
                dateFormatter={dateFormatter}
              />
            </Suspense>
          ) : (
            <EmptyChartState title="Keine Wiegedaten verfuegbar" description="Sobald Tickets gebucht sind, werden Mengen dargestellt." />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
