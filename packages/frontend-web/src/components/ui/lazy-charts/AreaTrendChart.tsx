import { SimpleLineChart } from '@/components/charts/SimpleLineChart'

type ChartDatum = { name: string; value: number }

interface AreaTrendChartProps {
  data: ChartDatum[]
  dataKey: string
  stroke: string
  fill: string
}

export default function AreaTrendChart({ data, dataKey, stroke, fill }: AreaTrendChartProps): JSX.Element {
  return (
    <div className="h-full rounded-lg border border-slate-100 bg-gradient-to-b from-white to-slate-50/80 p-3">
      <SimpleLineChart
        data={data.map((item) => ({ label: item.name, [dataKey]: item.value }))}
        series={[{ key: dataKey, color: stroke, label: dataKey }]}
        height={220}
        showLegend={false}
      />
      <div className="mt-2 flex items-center gap-2 text-xs text-slate-600">
        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: fill }} />
        <span>{dataKey}</span>
      </div>
    </div>
  )
}
