import type { JSX } from 'react'
import { SimpleDonutChart } from '@/components/charts/SimpleDonutChart'

interface BalanceShare {
  name: string
  value: number
}

interface AnalyticsBalanceShareChartProps {
  balanceShares: BalanceShare[]
  donutColors: string[]
  currencyFormatter: Intl.NumberFormat
}

export default function AnalyticsBalanceShareChart({ balanceShares, donutColors, currencyFormatter }: AnalyticsBalanceShareChartProps): JSX.Element {
  return (
    <div className="flex h-full items-center justify-center">
      <SimpleDonutChart
        data={balanceShares.map((item, index) => ({
          ...item,
          color: donutColors[index % donutColors.length],
        }))}
        valueFormatter={(value) => currencyFormatter.format(value)}
      />
    </div>
  )
}
