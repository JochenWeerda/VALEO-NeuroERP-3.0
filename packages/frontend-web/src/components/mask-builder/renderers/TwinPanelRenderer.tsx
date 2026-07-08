import { memo, useMemo } from 'react'
import {
  cellStyle,
  keyboardOrder,
  shapeToPath,
  type TwinMetricDef,
  type TwinPlan,
} from './twin-geometry'

/**
 * TwinPanelRenderer (UIX-081): interaktive 2D-Belegungsansicht als EIN SVG.
 * Zellen sind Pfade aus der Plan-Geometrie; Metriken faerben Fuellung/Kontur/
 * Schraffur. Jede Zelle hat Klick-Durchstich (onCellActivate) und ist per
 * Tastatur erreichbar (Tab + Enter) — Twin ist Werkzeug, nicht Deko.
 * Bis 300 Zellen ohne Virtualisierung (keine per-Zelle-Components).
 */
export const TwinPanelRenderer = memo(function TwinPanelRenderer({
  plan,
  metrics,
  cellData,
  onCellActivate,
  updatedLabel,
}: {
  plan: TwinPlan
  metrics: TwinMetricDef[]
  /** cell_id → Metrikwerte */
  cellData: Record<string, Record<string, unknown>>
  onCellActivate: (_cellId: string) => void
  updatedLabel?: string
}): JSX.Element {
  const order = useMemo(() => keyboardOrder(plan.cells), [plan.cells])
  const orderIndex = useMemo(() => new Map(order.map((id, i) => [id, i])), [order])

  return (
    <div data-testid="twin-panel" className="relative w-full">
      {updatedLabel && (
        <div className="mb-1 text-xs text-muted-foreground" data-testid="twin-updated">
          Stand {updatedLabel}
        </div>
      )}
      <svg
        viewBox={`0 0 ${plan.canvas.width} ${plan.canvas.height}`}
        className="h-auto w-full rounded border border-border bg-background"
        role="group"
        aria-label={`Belegungsplan ${plan.plan_id}`}
      >
        <defs>
          <pattern id="twin-lock-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="6" stroke="#64748b" strokeWidth="1.5" />
          </pattern>
        </defs>
        {plan.cells.map((cell) => {
          const values = cellData[cell.id] ?? {}
          const style = cellStyle(metrics, values)
          const tooltip = [cell.label ?? cell.id, ...metrics.map((m) => `${m.label}: ${formatValue(values[m.key])}`)].join('\n')
          return (
            <g key={cell.id}>
              <path
                d={shapeToPath(cell.shape)}
                fill={style.fill}
                stroke={style.stroke}
                strokeWidth={style.strokeWidth}
                data-testid={`twin-cell-${cell.id}`}
                data-cell-id={cell.id}
                data-hatched={style.hatched}
                tabIndex={0}
                role="button"
                aria-label={tooltip.replace(/\n/g, ', ')}
                style={{ cursor: 'pointer', outline: 'none' }}
                onClick={() => onCellActivate(cell.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    onCellActivate(cell.id)
                  }
                }}
              >
                <title>{tooltip}</title>
              </path>
              {style.hatched && (
                <path d={shapeToPath(cell.shape)} fill="url(#twin-lock-hatch)" pointerEvents="none" />
              )}
            </g>
          )
        })}
      </svg>
      <span className="sr-only" data-testid="twin-cell-count">
        {orderIndex.size} Zellen
      </span>
    </div>
  )
})

function formatValue(value: unknown): string {
  if (value === true) return 'ja'
  if (value === false) return 'nein'
  if (value === null || value === undefined) return '–'
  return String(value)
}
