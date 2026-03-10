import { Suspense, lazy } from 'react'
import { useTranslation } from 'react-i18next'
import { BarChart3, Target } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

const CampaignPerformanceTrendChart = lazy(() => import('@/pages/crm/charts/campaign-performance/CampaignPerformanceTrendChart'))
const CampaignComparisonBarChart = lazy(() => import('@/pages/crm/charts/campaign-performance/CampaignComparisonBarChart'))
const CampaignTypeDistributionChart = lazy(() => import('@/pages/crm/charts/campaign-performance/CampaignTypeDistributionChart'))

type MetricPoint = { date: string; sent: number; opened: number; clicked: number; converted: number }
type CategoryPoint = { name: string; sent: number; opened: number; clicked: number; converted: number }
type DistributionPoint = { name: string; value: number }

type CampaignPerformanceChartsProps = {
  loading: boolean
  chartData: MetricPoint[]
  campaignChartData: CategoryPoint[]
  typeChartData: DistributionPoint[]
}

function EmptyChartState({ icon: Icon }: { icon: typeof BarChart3 | typeof Target }): JSX.Element {
  const { t } = useTranslation()
  return <div className="flex h-[300px] items-center justify-center rounded-lg border-2 border-dashed bg-muted/20"><div className="text-center text-muted-foreground"><Icon className="mx-auto mb-2 h-12 w-12 opacity-50" /><p>{t('crud.campaigns.chartPreview')}</p></div></div>
}

function ChartFallback(): JSX.Element {
  return <Skeleton className="h-[300px] w-full" />
}

export default function CampaignPerformanceCharts({ loading, chartData, campaignChartData, typeChartData }: CampaignPerformanceChartsProps): JSX.Element {
  const { t } = useTranslation()
  const labels = {
    sent: t('crud.fields.sentCount'),
    opened: t('crud.fields.openCount'),
    clicked: t('crud.fields.clickCount'),
    converted: t('crud.fields.conversionCount'),
  }

  return (
    <>
      <Card>
        <CardHeader><CardTitle>{t('crud.campaigns.performanceChart')}</CardTitle><CardDescription>{t('crud.campaigns.performanceChartDescription')}</CardDescription></CardHeader>
        <CardContent>{loading ? <Skeleton className="h-[300px] w-full" /> : chartData.length > 0 ? <Suspense fallback={<ChartFallback />}><CampaignPerformanceTrendChart chartData={chartData} labels={labels} /></Suspense> : <EmptyChartState icon={BarChart3} />}</CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>{t('crud.campaigns.campaignComparison')}</CardTitle><CardDescription>{t('crud.campaigns.campaignComparisonDescription')}</CardDescription></CardHeader>
        <CardContent>{loading ? <Skeleton className="h-[300px] w-full" /> : campaignChartData.length > 0 ? <Suspense fallback={<ChartFallback />}><CampaignComparisonBarChart data={campaignChartData} labels={labels} /></Suspense> : <EmptyChartState icon={BarChart3} />}</CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>{t('crud.campaigns.typeDistribution')}</CardTitle><CardDescription>{t('crud.campaigns.typeDistributionDescription')}</CardDescription></CardHeader>
        <CardContent>{loading ? <Skeleton className="h-[300px] w-full" /> : typeChartData.length > 0 ? <Suspense fallback={<ChartFallback />}><CampaignTypeDistributionChart data={typeChartData} /></Suspense> : <EmptyChartState icon={Target} />}</CardContent>
      </Card>
    </>
  )
}
