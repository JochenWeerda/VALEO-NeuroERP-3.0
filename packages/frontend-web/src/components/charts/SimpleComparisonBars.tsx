interface ComparisonBarDatum {
  name: string
  value: number
  color?: string
}

interface SimpleComparisonBarsProps {
  data: ComparisonBarDatum[]
  valueFormatter?: (value: number) => string
}

const DEFAULT_BAR_COLOR = '#2563EB'

export function SimpleComparisonBars({ data, valueFormatter = (value) => value.toLocaleString('de-DE') }: SimpleComparisonBarsProps): JSX.Element {
  const maxValue = Math.max(...data.map((item) => item.value), 1)

  return (
    <div className="space-y-4">
      {data.map((item) => (
        <div key={item.name} className="space-y-1.5">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-700">{item.name}</span>
            <span className="font-medium text-slate-900">{valueFormatter(item.value)}</span>
          </div>
          <div className="h-3 rounded-full bg-slate-100">
            <div
              className="h-3 rounded-full transition-[width]"
              style={{ width: `${Math.max((item.value / maxValue) * 100, item.value > 0 ? 6 : 0)}%`, backgroundColor: item.color ?? DEFAULT_BAR_COLOR }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
