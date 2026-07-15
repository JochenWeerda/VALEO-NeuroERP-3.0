import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
import { chartSeriesColor } from '@/components/charts/chart-palette'
import { formatCurrency } from '@/components/mask-builder/utils/formatting'

type ChartPoint = { period?: string; total_amount: number }

export default function TotalAmountLineChart({ chartData, label }: { chartData: ChartPoint[]; label: string }): JSX.Element {
  return (
    <SimpleLineChart
      data={chartData.map((item) => ({ label: item.period ?? '', total_amount: item.total_amount }))}
      series={[{ key: 'total_amount', color: chartSeriesColor(2), label }]}
      height={300}
    />
  )
}
