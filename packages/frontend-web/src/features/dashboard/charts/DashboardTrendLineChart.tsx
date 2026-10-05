import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
import { chartSeriesColor } from '@/components/charts/chart-palette'
import type { ReactElement } from 'react'

interface TrendPoint {
  date: string
  contract_long_tons: number
  contract_short_tons: number
}

interface DashboardTrendLineChartProps {
  trend: TrendPoint[]
  dateFormatter: Intl.DateTimeFormat
}

export default function DashboardTrendLineChart({ trend, dateFormatter }: DashboardTrendLineChartProps): ReactElement {
  return (
    <SimpleLineChart
      data={trend.map((item) => ({
        label: dateFormatter.format(new Date(item.date)),
        long: item.contract_long_tons,
        short: item.contract_short_tons,
      }))}
      series={[
        { key: 'long', color: chartSeriesColor(0), label: 'Long' },
        { key: 'short', color: chartSeriesColor(1), label: 'Short' },
      ]}
      height={300}
    />
  )
}
