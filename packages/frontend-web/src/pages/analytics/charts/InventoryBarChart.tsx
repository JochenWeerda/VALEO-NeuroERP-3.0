import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'

type TrendPoint = { date: string; inventory: number }

export default function InventoryBarChart({ trends }: { trends: TrendPoint[] }): JSX.Element {
  return (
    <SimpleVerticalBars
      data={trends.map((item) => ({ label: item.date, value: item.inventory }))}
      height={250}
    />
  )
}
