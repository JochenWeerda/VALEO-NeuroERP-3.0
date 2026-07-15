import { CHART_AXIS_TEXT, CHART_GRID, CHART_SERIES } from './chart-palette'

interface BarDatum {
  label: string
  value: number
  /** Ohne Angabe: Slot 1 der Chart-Palette (eine Serie = eine Farbe). */
  color?: string
}

interface SimpleVerticalBarsProps {
  data: BarDatum[]
  height?: number
  valueFormatter?: (value: number) => string
}

export function SimpleVerticalBars({ data, height = 300, valueFormatter = (value) => value.toLocaleString('de-DE') }: SimpleVerticalBarsProps): JSX.Element {
  const width = 640
  const padding = { top: 16, right: 16, bottom: 28, left: 24 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  const maxValue = Math.max(...data.map((item) => item.value), 1)
  const barGap = 12
  const barWidth = Math.max((chartWidth - barGap * (data.length - 1)) / Math.max(data.length, 1), 24)

  return (
    <div className="space-y-3">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full rounded-lg bg-muted/30" role="img">
        <line x1={padding.left} y1={padding.top + chartHeight} x2={width - padding.right} y2={padding.top + chartHeight} style={{ stroke: CHART_GRID }} />
        {data.map((item, index) => {
          const x = padding.left + index * (barWidth + barGap)
          const barHeight = (item.value / maxValue) * chartHeight
          const y = padding.top + chartHeight - barHeight
          return (
            <g key={item.label}>
              <rect x={x} y={y} width={barWidth} height={barHeight} rx="4" style={{ fill: item.color ?? CHART_SERIES[0] }}>
                <title>{`${item.label}: ${valueFormatter(item.value)}`}</title>
              </rect>
              <text x={x + barWidth / 2} y={y - 6} textAnchor="middle" className="text-xs" style={{ fill: CHART_AXIS_TEXT }}>{valueFormatter(item.value)}</text>
              <text x={x + barWidth / 2} y={height - 6} textAnchor="middle" className="text-xs" style={{ fill: CHART_AXIS_TEXT }}>{item.label}</text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
