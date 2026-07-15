import { chartSeriesColor } from './chart-palette'

interface DonutDatum {
  name: string
  value: number
  /** Ohne Angabe: kategorialer Slot nach Position; ab dem 7. Segment neutraler Sonstige-Slot. */
  color?: string
}

interface SimpleDonutChartProps {
  data: DonutDatum[]
  size?: number
  strokeWidth?: number
  valueFormatter?: (value: number) => string
}

export function SimpleDonutChart({
  data,
  size = 220,
  strokeWidth = 28,
  valueFormatter = (value) => value.toLocaleString('de-DE'),
}: SimpleDonutChartProps): JSX.Element {
  const total = data.reduce((sum, item) => sum + item.value, 0)
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  let offset = 0

  const segmentColor = (item: DonutDatum, index: number): string => item.color ?? chartSeriesColor(index)

  return (
    <div className="flex flex-col items-center gap-4">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible" role="img">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
        />
        {data.map((item, index) => {
          const segment = total > 0 ? (item.value / total) * circumference : 0
          const dashArray = `${segment} ${circumference - segment}`
          const dashOffset = -offset
          offset += segment
          return (
            <circle
              key={item.name}
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              style={{ stroke: segmentColor(item, index) }}
              strokeWidth={strokeWidth}
              strokeDasharray={dashArray}
              strokeDashoffset={dashOffset}
              strokeLinecap="butt"
              transform={`rotate(-90 ${size / 2} ${size / 2})`}
            >
              <title>{`${item.name}: ${valueFormatter(item.value)}`}</title>
            </circle>
          )
        })}
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="fill-foreground text-2xl font-semibold">
          {total.toLocaleString('de-DE')}
        </text>
      </svg>
      <div className="grid w-full gap-2">
        {data.map((item, index) => (
          <div key={item.name} className="flex items-center justify-between gap-3 text-sm">
            <div className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: segmentColor(item, index) }} aria-hidden />
              <span className="text-muted-foreground">{item.name}</span>
            </div>
            <span className="font-medium tabular-nums text-foreground">{valueFormatter(item.value)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
