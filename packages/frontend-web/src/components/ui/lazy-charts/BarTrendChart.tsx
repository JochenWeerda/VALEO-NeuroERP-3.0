import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'

type ChartDatum = { name: string; value: number }

interface BarTrendChartProps {
  data: ChartDatum[]
  dataKey: string
  fill: string
}

export default function BarTrendChart({ data, dataKey, fill }: BarTrendChartProps): JSX.Element {
  return (
    <SimpleVerticalBars
      data={data.map((item) => ({ label: item.name, value: item.value, color: fill }))}
      height={220}
    />
  )
}
