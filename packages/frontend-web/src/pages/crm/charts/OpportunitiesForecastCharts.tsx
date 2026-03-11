import { Suspense, lazy } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type ViewMode = 'period' | 'stage' | 'owner'
type ChartPoint = { period?: string; stage?: string; owner?: string; count: number; total_amount: number; total_expected_revenue: number }
type StageDistributionPoint = { name: string; value: number }

type OpportunitiesForecastChartsProps = {
  chartData: ChartPoint[]
  stageDistributionData: StageDistributionPoint[]
  viewMode: ViewMode
  colors: string[]
}

const ExpectedRevenueLineChart = lazy(() => import('@/pages/crm/charts/opportunities-forecast/ExpectedRevenueLineChart'))
const ExpectedRevenueBarChart = lazy(() => import('@/pages/crm/charts/opportunities-forecast/ExpectedRevenueBarChart'))
const TotalAmountLineChart = lazy(() => import('@/pages/crm/charts/opportunities-forecast/TotalAmountLineChart'))
const TotalAmountBarChart = lazy(() => import('@/pages/crm/charts/opportunities-forecast/TotalAmountBarChart'))
const StageDistributionDonut = lazy(() => import('@/pages/crm/charts/opportunities-forecast/StageDistributionDonut'))
const OpportunityCountBarChart = lazy(() => import('@/pages/crm/charts/opportunities-forecast/OpportunityCountBarChart'))

function ChartFallback(): JSX.Element {
  return <div className="h-[300px] animate-pulse rounded bg-muted/30" />
}

export default function OpportunitiesForecastCharts({ chartData, stageDistributionData, viewMode, colors }: OpportunitiesForecastChartsProps): JSX.Element {
  const { t } = useTranslation()
  const xAxisKey = viewMode === 'period' ? 'period' : viewMode === 'stage' ? 'stage' : 'owner'

  return (
    <>
      <Card>
        <CardHeader><CardTitle>{t('crud.forecast.expectedRevenueChart')}</CardTitle></CardHeader>
        <CardContent><Suspense fallback={<ChartFallback />}>{viewMode === 'period' ? <ExpectedRevenueLineChart chartData={chartData} label={t('crud.fields.expectedRevenue')} /> : <ExpectedRevenueBarChart chartData={chartData} xAxisKey={xAxisKey} label={t('crud.fields.expectedRevenue')} />}</Suspense></CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>{t('crud.forecast.totalAmountChart')}</CardTitle></CardHeader>
        <CardContent><Suspense fallback={<ChartFallback />}>{viewMode === 'period' ? <TotalAmountLineChart chartData={chartData} label={t('crud.fields.totalAmount')} /> : <TotalAmountBarChart chartData={chartData} xAxisKey={viewMode === 'stage' ? 'stage' : 'owner'} label={t('crud.fields.totalAmount')} />}</Suspense></CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>{t('crud.forecast.stageDistribution')}</CardTitle></CardHeader>
        <CardContent><Suspense fallback={<ChartFallback />}><StageDistributionDonut data={stageDistributionData} colors={colors} /></Suspense></CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>{t('crud.forecast.opportunityCountChart')}</CardTitle></CardHeader>
        <CardContent><Suspense fallback={<ChartFallback />}><OpportunityCountBarChart chartData={chartData} xAxisKey={xAxisKey} label={t('crud.forecast.opportunityCount')} /></Suspense></CardContent>
      </Card>
    </>
  )
}
