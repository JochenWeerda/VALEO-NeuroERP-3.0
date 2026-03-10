import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'

type ChartPoint = { period?: string; stage?: string; owner?: string; count: number }

export default function OpportunityCountBarChart({ chartData, xAxisKey, label }: { chartData: ChartPoint[]; xAxisKey: string; label: string }): JSX.Element {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-slate-700">{label}</p>
      <SimpleVerticalBars
        data={chartData.map((item) => ({
          label: String(item[xAxisKey as keyof ChartPoint] ?? ''),
          value: Number(item.count ?? 0),
          color: '#FFBB28',
        }))}
        height={280}
      />
    </div>
  )
}
