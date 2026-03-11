import { Suspense, lazy } from 'react'
import { Card } from '@/components/ui/card'

const SalesTrendLineChart = lazy(() => import('@/pages/analytics/charts/SalesTrendLineChart'))
const InventoryBarChart = lazy(() => import('@/pages/analytics/charts/InventoryBarChart'))

type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

type AnalyticsDashboardChartsProps = {
  trends: TrendPoint[]
  chartHeight: number
}

function ChartFallback({ height }: { height: number }): JSX.Element {
  return <div className="animate-pulse rounded bg-muted/30" style={{ height }} />
}

export default function AnalyticsDashboardCharts({ trends, chartHeight }: AnalyticsDashboardChartsProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Umsatztrend</h4>
        <Suspense fallback={<ChartFallback height={chartHeight} />}>
          <div style={{ height: chartHeight }}>
            <SalesTrendLineChart trends={trends} />
          </div>
        </Suspense>
      </Card>

      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Lagerbestand</h4>
        <Suspense fallback={<ChartFallback height={chartHeight} />}>
          <div style={{ height: chartHeight }}>
            <InventoryBarChart trends={trends} />
          </div>
        </Suspense>
      </Card>
    </div>
  )
}
