import { Card } from '@/components/ui/card'
import { SimpleVerticalBars } from '@/components/charts/SimpleVerticalBars'

const CHART_HEIGHT = 300
const formatCurrencyLabel = (value: number | string): [string, string] => [`${Number(value).toLocaleString('de-DE')} EUR`, 'Wert']

export default function ProductAnalyticsCharts({ data }: { data: unknown }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Top Produkte nach Umsatz</h4>
        <SimpleVerticalBars
          data={(data?.topProductsByRevenue ?? []).slice(0, 5).map(item => ({
            label: String(item.article),
            value: Number(item.revenue ?? 0),
            color: '#8B5CF6',
          }))}
          height={CHART_HEIGHT}
          valueFormatter={(value) => formatCurrencyLabel(value)[0]}
        />
      </Card>
      <Card className="p-4">
        <h4 className="mb-2 font-semibold">Top Produkte nach Menge</h4>
        <SimpleVerticalBars
          data={(data?.topProductsByQuantity ?? []).slice(0, 5).map(item => ({
            label: String(item.article),
            value: Number(item.quantity ?? 0),
            color: '#8B5CF6',
          }))}
          height={CHART_HEIGHT}
          valueFormatter={(value) => `${Number(value).toLocaleString('de-DE')} kg`}
        />
      </Card>
    </div>
  )
}
