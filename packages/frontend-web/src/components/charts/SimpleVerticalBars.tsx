interface BarDatum {
  label: string
  value: number
  color?: string
}

interface SimpleVerticalBarsProps {
  data: BarDatum[]
  height?: number
  valueFormatter?: (value: number) => string
}

const DEFAULT_BAR_COLOR = '#2563EB'

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
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full rounded-lg bg-slate-50">
        <line x1={padding.left} y1={padding.top + chartHeight} x2={width - padding.right} y2={padding.top + chartHeight} stroke="#CBD5E1" />
        {data.map((item, index) => {
          const x = padding.left + index * (barWidth + barGap)
          const barHeight = (item.value / maxValue) * chartHeight
          const y = padding.top + chartHeight - barHeight
          return (
            <g key={item.label}>
              <rect x={x} y={y} width={barWidth} height={barHeight} rx="8" fill={item.color ?? DEFAULT_BAR_COLOR} />
              <text x={x + barWidth / 2} y={y - 6} textAnchor="middle" className="fill-slate-700 text-[11px]">{valueFormatter(item.value)}</text>
              <text x={x + barWidth / 2} y={height - 6} textAnchor="middle" className="fill-slate-500 text-[11px]">{item.label}</text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
