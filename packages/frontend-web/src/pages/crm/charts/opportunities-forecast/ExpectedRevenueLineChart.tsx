import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
import { formatCurrency } from '@/components/mask-builder/utils/formatting'

type ChartPoint = { period?: string; total_expected_revenue: number }

export default function ExpectedRevenueLineChart({ chartData, label }: { chartData: ChartPoint[]; label: string }): JSX.Element {
  return (
    <SimpleLineChart
      data={chartData.map((item) => ({ label: item.period ?? '', total_expected_revenue: item.total_expected_revenue }))}
      series={[{ key: 'total_expected_revenue', color: '#0088FE', label }]}
      height={300}
    />
  )
}
