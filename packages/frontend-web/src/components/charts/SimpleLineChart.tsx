import { useMemo, useRef, useState } from 'react'
import { CHART_AXIS_TEXT, CHART_GRID, chartSeriesColor } from './chart-palette'

interface LineSeries {
  key: string
  /** Ohne Angabe: kategorialer Slot nach Serienposition (chart-palette). */
  color?: string
  label?: string
  /** Rezessive Soll-/Referenzlinie: gestrichelt und dünner. */
  dashed?: boolean
}

interface PointData {
  label: string
  [key: string]: string | number | null | undefined
}

interface SimpleLineChartProps {
  data: PointData[]
  series: LineSeries[]
  height?: number
  showLegend?: boolean
  valueFormatter?: (value: number) => string
}

/** null/undefined/'' sind fachlich unbekannt und werden als Lücke gezeichnet, nie als 0. */
function numericOrGap(raw: string | number | null | undefined): number | null {
  if (raw === null || raw === undefined || raw === '') return null
  const value = Number(raw)
  return Number.isFinite(value) ? value : null
}

export function SimpleLineChart({ data, series, height = 300, showLegend = true, valueFormatter = (value) => value.toLocaleString('de-DE') }: SimpleLineChartProps): JSX.Element {
  const width = 640
  const padding = { top: 16, right: 16, bottom: 28, left: 48 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  const containerRef = useRef<HTMLDivElement>(null)
  const [hoverIndex, setHoverIndex] = useState<number | null>(null)

  const allValues = data.flatMap((item) => series.map((entry) => numericOrGap(item[entry.key])).filter((value): value is number => value !== null))
  const maxValue = Math.max(...allValues, 1)

  const xFor = (index: number): number => padding.left + (data.length > 1 ? (index / (data.length - 1)) * chartWidth : chartWidth / 2)
  const yFor = (value: number): number => padding.top + chartHeight - (value / maxValue) * chartHeight

  const seriesColor = (entry: LineSeries, index: number): string => entry.color ?? chartSeriesColor(index)

  /** Lücken (null) zerschneiden die Linie in Segmente statt auf 0 zu fallen. */
  const segmentsForSeries = (seriesKey: string): string[] => {
    const segments: string[] = []
    let current: string[] = []
    data.forEach((item, index) => {
      const value = numericOrGap(item[seriesKey])
      if (value === null) {
        if (current.length > 0) segments.push(current.join(' '))
        current = []
        return
      }
      current.push(`${xFor(index)},${yFor(value)}`)
    })
    if (current.length > 0) segments.push(current.join(' '))
    return segments
  }

  const yTicks = useMemo(() => [0, maxValue / 2, maxValue], [maxValue])

  const labelStep = Math.max(1, Math.ceil(data.length / 8))

  function handleMouseMove(event: React.MouseEvent<HTMLDivElement>): void {
    if (data.length === 0) return
    const rect = containerRef.current?.getBoundingClientRect()
    if (!rect || rect.width === 0) return
    const svgX = ((event.clientX - rect.left) / rect.width) * width
    const relative = (svgX - padding.left) / Math.max(chartWidth, 1)
    const index = Math.round(relative * (data.length - 1))
    setHoverIndex(Math.min(Math.max(index, 0), data.length - 1))
  }

  const hovered = hoverIndex !== null ? data[hoverIndex] : null

  return (
    <div className="space-y-3">
      <div ref={containerRef} className="relative" onMouseMove={handleMouseMove} onMouseLeave={() => setHoverIndex(null)}>
        <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full overflow-visible rounded-lg bg-muted/30" role="img">
          {yTicks.map((tick) => (
            <g key={tick}>
              <line x1={padding.left} y1={yFor(tick)} x2={width - padding.right} y2={yFor(tick)} style={{ stroke: CHART_GRID }} strokeWidth={1} />
              <text x={padding.left - 6} y={yFor(tick) + 3} textAnchor="end" className="text-2xs" style={{ fill: CHART_AXIS_TEXT }}>{valueFormatter(tick)}</text>
            </g>
          ))}
          {hoverIndex !== null ? (
            <line x1={xFor(hoverIndex)} y1={padding.top} x2={xFor(hoverIndex)} y2={padding.top + chartHeight} style={{ stroke: CHART_AXIS_TEXT }} strokeWidth={1} strokeDasharray="3 3" aria-hidden />
          ) : null}
          {series.map((entry, seriesIndex) =>
            segmentsForSeries(entry.key).map((points, segmentIndex) => (
              <polyline key={`${entry.key}-${segmentIndex}`} fill="none" style={{ stroke: seriesColor(entry, seriesIndex) }} strokeWidth={entry.dashed ? 1.5 : 2} strokeDasharray={entry.dashed ? '6 4' : undefined} points={points} strokeLinejoin="round" strokeLinecap="round" />
            )),
          )}
          {hoverIndex !== null
            ? series.map((entry, seriesIndex) => {
                const value = numericOrGap(data[hoverIndex][entry.key])
                if (value === null) return null
                return <circle key={entry.key} cx={xFor(hoverIndex)} cy={yFor(value)} r={4} style={{ fill: seriesColor(entry, seriesIndex) }} stroke="hsl(var(--background))" strokeWidth={2} aria-hidden />
              })
            : null}
          {data.map((item, index) =>
            index % labelStep === 0 ? (
              <text key={`${String(item.label)}-${index}`} x={xFor(index)} y={height - 6} textAnchor="middle" className="text-xs" style={{ fill: CHART_AXIS_TEXT }}>{String(item.label)}</text>
            ) : null,
          )}
        </svg>
        {hovered ? (
          <div className="pointer-events-none absolute top-2 z-10 min-w-36 rounded-md border bg-popover px-3 py-2 text-xs shadow-md" style={{ left: `${(xFor(hoverIndex ?? 0) / width) * 100}%`, transform: (hoverIndex ?? 0) > data.length / 2 ? 'translateX(calc(-100% - 8px))' : 'translateX(8px)' }} role="status">
            <p className="font-medium text-popover-foreground">{String(hovered.label)}</p>
            {series.map((entry, seriesIndex) => {
              const value = numericOrGap(hovered[entry.key])
              return (
                <p key={entry.key} className="flex items-center justify-between gap-3 text-muted-foreground">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: seriesColor(entry, seriesIndex) }} aria-hidden />
                    {entry.label ?? entry.key}
                  </span>
                  <span className="font-mono tabular-nums text-popover-foreground">{value === null ? '–' : valueFormatter(value)}</span>
                </p>
              )
            })}
          </div>
        ) : null}
      </div>
      {showLegend && series.length > 1 ? (
        <div className="flex flex-wrap gap-4 text-sm">
          {series.map((entry, seriesIndex) => (
            <div key={entry.key} className="flex items-center gap-2">
              <span className={entry.dashed ? 'h-0.5 w-4' : 'h-3 w-3 rounded-full'} style={{ backgroundColor: seriesColor(entry, seriesIndex) }} aria-hidden />
              <span className="text-muted-foreground">{entry.label ?? entry.key}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  )
}
