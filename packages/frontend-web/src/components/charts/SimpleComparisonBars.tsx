import { CHART_SERIES } from './chart-palette'

interface ComparisonBarDatum {
  name: string
  value: number
  /** Ohne Angabe: Slot 1 der Chart-Palette (eine Kennzahl über Kategorien = eine Farbe). */
  color?: string
}

interface SimpleComparisonBarsProps {
  data: ComparisonBarDatum[]
  valueFormatter?: (value: number) => string
}

export function SimpleComparisonBars({ data, valueFormatter = (value) => value.toLocaleString('de-DE') }: SimpleComparisonBarsProps): JSX.Element {
  const maxValue = Math.max(...data.map((item) => item.value), 1)

  return (
    <div className="space-y-4">
      {data.map((item) => (
        <div key={item.name} className="space-y-1.5">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{item.name}</span>
            <span className="font-medium tabular-nums text-foreground">{valueFormatter(item.value)}</span>
          </div>
          <div className="h-3 rounded-full bg-muted">
            <div
              className="h-3 rounded-full transition-[width]"
              style={{ width: `${Math.max((item.value / maxValue) * 100, item.value > 0 ? 6 : 0)}%`, backgroundColor: item.color ?? CHART_SERIES[0] }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
