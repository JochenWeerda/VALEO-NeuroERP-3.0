interface LineSeries {
  key: string
  color: string
  label?: string
}

interface PointData {
  label: string
  [key: string]: string | number
}

interface SimpleLineChartProps {
  data: PointData[]
  series: LineSeries[]
  height?: number
  showLegend?: boolean
}

export function SimpleLineChart({ data, series, height = 300, showLegend = true }: SimpleLineChartProps): JSX.Element {
  const width = 640
  const padding = { top: 16, right: 16, bottom: 28, left: 32 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  const allValues = data.flatMap((item) => series.map((entry) => Number(item[entry.key] ?? 0)))
  const maxValue = Math.max(...allValues, 1)

  const pointsForSeries = (seriesKey: string) =>
    data.map((item, index) => {
      const x = padding.left + (data.length > 1 ? (index / (data.length - 1)) * chartWidth : chartWidth / 2)
      const y = padding.top + chartHeight - (Number(item[seriesKey] ?? 0) / maxValue) * chartHeight
      return `${x},${y}`
    }).join(' ')

  return (
    <div className="space-y-3">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full overflow-visible rounded-lg bg-slate-50">
        <line x1={padding.left} y1={padding.top + chartHeight} x2={width - padding.right} y2={padding.top + chartHeight} stroke="#CBD5E1" />
        <line x1={padding.left} y1={padding.top} x2={padding.left} y2={padding.top + chartHeight} stroke="#CBD5E1" />
        {series.map((entry) => (
          <polyline key={entry.key} fill="none" stroke={entry.color} strokeWidth="3" points={pointsForSeries(entry.key)} strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {data.map((item, index) => {
          const x = padding.left + (data.length > 1 ? (index / (data.length - 1)) * chartWidth : chartWidth / 2)
          return <text key={String(item.label)} x={x} y={height - 6} textAnchor="middle" className="fill-slate-500 text-[11px]">{String(item.label)}</text>
        })}
      </svg>
      {showLegend ? (
        <div className="flex flex-wrap gap-4 text-sm">
          {series.map((entry) => (
            <div key={entry.key} className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-slate-700">{entry.label ?? entry.key}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}
