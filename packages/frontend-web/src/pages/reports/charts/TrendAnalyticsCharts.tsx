import { Card } from '@/components/ui/card'
import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
import type { ReportDashboardData } from '@/pages/reports/report-chart-types'

const CHART_HEIGHT = 300
const formatCurrencyLabel = (value: number | string): [string, string] => [`${Number(value).toLocaleString('de-DE')} EUR`, 'Wert']

export default function TrendAnalyticsCharts({ data }: { data: ReportDashboardData }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Umsatztrend</h4>
        <SimpleLineChart
          data={Object.entries(data?.revenueTrends ?? {}).map(([period, value]) => ({ label: period, value: Number(value) }))}
          series={[{ key: 'value', color: '#EF4444', label: 'Wert' }]}
          height={CHART_HEIGHT}
          showLegend={false}
        />
      </Card>
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Auftragsvolumen</h4>
        <SimpleLineChart
          data={Object.entries(data?.orderVolumeTrends ?? {}).map(([period, value]) => ({ label: period, value: Number(value) }))}
          series={[{ key: 'value', color: '#EF4444', label: 'Aufträge' }]}
          height={CHART_HEIGHT}
          showLegend={false}
        />
      </Card>
    </div>
  )
}
