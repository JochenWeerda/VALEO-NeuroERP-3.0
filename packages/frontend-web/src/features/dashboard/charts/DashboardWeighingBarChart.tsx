import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'
import type { ReactElement } from 'react'

interface TrendPoint {
  date: string
  contract_long_tons: number
}

interface DashboardWeighingBarChartProps {
  trend: TrendPoint[]
  dateFormatter: Intl.DateTimeFormat
}

export default function DashboardWeighingBarChart({ trend, dateFormatter }: DashboardWeighingBarChartProps): ReactElement {
  return (
    <SimpleVerticalBars
      data={trend.map((item) => ({
        label: dateFormatter.format(new Date(item.date)),
        value: item.contract_long_tons,
      }))}
      height={300}
      valueFormatter={(value) => `${value.toLocaleString('de-DE')} t`}
    />
  )
}
