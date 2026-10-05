import { chartSeriesColor } from '@/components/charts/chart-palette'

type CategoryPoint = { name: string; sent: number; opened: number; clicked: number; converted: number }

export default function CampaignComparisonBarChart({
  data,
  labels,
}: {
  data: CategoryPoint[]
  labels: { sent: string; opened: string; clicked: string; converted: string }
}): JSX.Element {
  const maxValue = Math.max(
    ...data.flatMap((item) => [item.sent, item.opened, item.clicked, item.converted]),
    1,
  )
  const metrics = [
    { key: 'sent', label: labels.sent, color: chartSeriesColor(0) },
    { key: 'opened', label: labels.opened, color: chartSeriesColor(1) },
    { key: 'clicked', label: labels.clicked, color: chartSeriesColor(2) },
    { key: 'converted', label: labels.converted, color: chartSeriesColor(3) },
  ] as const

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-4 text-sm">
        {metrics.map((metric) => (
          <div key={metric.key} className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full" style={{ backgroundColor: metric.color }} aria-hidden />
            <span className="text-muted-foreground">{metric.label}</span>
          </div>
        ))}
      </div>
      <div className="space-y-4">
        {data.map((item) => (
          <div key={item.name} className="rounded-lg border p-3">
            <p className="mb-3 text-sm font-medium text-foreground">{item.name}</p>
            <div className="grid gap-3 md:grid-cols-2">
              {metrics.map((metric) => {
                const value = item[metric.key]
                return (
                  <div key={metric.key} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{metric.label}</span>
                      <span className="font-medium tabular-nums text-foreground">{value.toLocaleString('de-DE')}</span>
                    </div>
                    <div className="h-2.5 rounded-full bg-muted">
                      <div
                        className="h-2.5 rounded-full"
                        style={{
                          width: `${Math.max((value / maxValue) * 100, value > 0 ? 5 : 0)}%`,
                          backgroundColor: metric.color,
                        }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
