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
    <div className="h-full rounded-lg border bg-card p-3">
      <SimpleLineChart
        data={data.map((item) => ({ label: item.name, [dataKey]: item.value }))}
        series={[{ key: dataKey, color: stroke, label: dataKey }]}
        height={220}
        showLegend={false}
      />
      <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: fill }} aria-hidden />
        <span>{dataKey}</span>
      </div>
    </div>
  )
}
