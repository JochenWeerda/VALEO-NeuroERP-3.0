import { Suspense, lazy } from 'react'

type ReportType = 'sales-performance' | 'customer-analytics' | 'product-analytics' | 'financial-analytics' | 'trend-analytics'

type ReportChartsProps = {
  selectedReport: ReportType
  data: unknown
}

const chartModules: Record<ReportType, React.LazyExoticComponent<(props: { data: unknown }) => JSX.Element>> = {
  'sales-performance': lazy(() => import('@/pages/reports/charts/SalesPerformanceCharts')),
  'customer-analytics': lazy(() => import('@/pages/reports/charts/CustomerAnalyticsCharts')),
  'product-analytics': lazy(() => import('@/pages/reports/charts/ProductAnalyticsCharts')),
  'financial-analytics': lazy(() => import('@/pages/reports/charts/FinancialAnalyticsCharts')),
  'trend-analytics': lazy(() => import('@/pages/reports/charts/TrendAnalyticsCharts')),
}

export default function ReportsDashboardCharts({ selectedReport, data }: ReportChartsProps): JSX.Element | null {
  const SelectedChart = chartModules[selectedReport]
  if (!SelectedChart) return null
  return (
    <Suspense fallback={<div className="grid grid-cols-1 gap-4 md:grid-cols-2"><div className="h-[332px] animate-pulse rounded-lg bg-muted/30" /><div className="h-[332px] animate-pulse rounded-lg bg-muted/30" /></div>}>
      <SelectedChart data={data} />
    </Suspense>
  )
}
