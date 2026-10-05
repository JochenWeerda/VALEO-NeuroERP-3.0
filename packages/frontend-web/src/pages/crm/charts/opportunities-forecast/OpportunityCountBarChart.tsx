import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'
import { chartSeriesColor } from '@/components/charts/chart-palette'

type ChartPoint = { period?: string; stage?: string; owner?: string; count: number }

export default function OpportunityCountBarChart({ chartData, xAxisKey, label }: { chartData: ChartPoint[]; xAxisKey: string; label: string }): JSX.Element {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-muted-foreground">{label}</p>
      <SimpleVerticalBars
        data={chartData.map((item) => ({
          label: String(item[xAxisKey as keyof ChartPoint] ?? ''),
          value: Number(item.count ?? 0),
          color: chartSeriesColor(1),
        }))}
        height={280}
      />
    </div>
  )
}
