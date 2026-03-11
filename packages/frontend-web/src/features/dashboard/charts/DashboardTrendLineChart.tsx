import { SimpleLineChart } from '@/components/charts/SimpleLineChart'
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
        { key: 'long', color: '#2563eb' },
        { key: 'short', color: '#f97316' },
      ]}
      height={300}
    />
  )
}
