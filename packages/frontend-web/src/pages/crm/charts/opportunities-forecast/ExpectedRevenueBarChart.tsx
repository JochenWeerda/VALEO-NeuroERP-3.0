import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'
import { formatCurrency } from '@/components/mask-builder/utils/formatting'

type ChartPoint = { stage?: string; owner?: string; total_expected_revenue: number }

export default function ExpectedRevenueBarChart({ chartData, xAxisKey, label }: { chartData: ChartPoint[]; xAxisKey: string; label: string }): JSX.Element {
  return (
    <SimpleVerticalBars
      data={chartData.map((item) => ({
        label: String(item[xAxisKey as keyof ChartPoint] ?? ''),
        value: Number(item.total_expected_revenue ?? 0),
        color: '#0088FE',
      }))}
      height={300}
      valueFormatter={(value) => formatCurrency(value, 'EUR')}
    />
  )
}
