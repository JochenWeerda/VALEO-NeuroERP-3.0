import { Card } from '@/components/ui/card'
import { SimpleComparisonBars } from '@/components/charts/SimpleComparisonBars'
import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
import type { ReportDashboardData } from '@/pages/reports/report-chart-types'

const CHART_HEIGHT = 300
const formatCurrencyLabel = (value: number | string): [string, string] => [`${Number(value).toLocaleString('de-DE')} EUR`, 'Wert']

export default function CustomerAnalyticsCharts({ data }: { data: ReportDashboardData }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Top Kunden nach Umsatz</h4>
        <SimpleComparisonBars
          data={(data?.topCustomers ?? []).slice(0, 5).map(item => ({
            name: String(item.customerId),
            value: Number(item.totalRevenue ?? 0),
          }))}
          valueFormatter={(value) => formatCurrencyLabel(value)[0]}
        />
      </Card>
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Kundenakquise-Trends</h4>
        <SimpleLineChart
          data={Object.entries(data?.customerAcquisitionTrends ?? {}).map(([month, count]) => ({ label: month, count: Number(count) }))}
          series={[{ key: 'count', label: 'Anzahl' }]}
          height={CHART_HEIGHT}
          showLegend={false}
        />
      </Card>
    </div>
  )
}
