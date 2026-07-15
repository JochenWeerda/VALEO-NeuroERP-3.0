import { SimpleLineChart } from '@/components/charts/SimpleLineChart'

type TrendPoint = { date: string; sales: number }

export default function SalesTrendLineChart({ trends }: { trends: TrendPoint[] }): JSX.Element {
  return (
    <SimpleLineChart
      data={trends.map((item) => ({ label: item.date, sales: item.sales }))}
      series={[{ key: 'sales', label: 'Umsatz' }]}
      height={250}
    />
  )
}
