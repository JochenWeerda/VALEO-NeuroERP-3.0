import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'
import { formatCurrency } from '@/components/mask-builder/utils/formatting'

type ChartPoint = { stage?: string; owner?: string; total_amount: number }

export default function TotalAmountBarChart({ chartData, xAxisKey, label }: { chartData: ChartPoint[]; xAxisKey: string; label: string }): JSX.Element {
  return (
    <SimpleVerticalBars
      data={chartData.map((item) => ({
        label: String(item[xAxisKey as keyof ChartPoint] ?? ''),
        value: Number(item.total_amount ?? 0),
        color: '#00C49F',
      }))}
      height={300}
      valueFormatter={(value) => formatCurrency(value, 'EUR')}
    />
  )
}
