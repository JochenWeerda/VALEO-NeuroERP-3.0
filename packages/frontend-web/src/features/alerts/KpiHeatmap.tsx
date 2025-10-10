import * as React from "react"
import { heatColor, severityBorder, toSeverity } from "./color"
import type { HeatCell } from "./rules"

const GRID_FIRST_COLUMN_WIDTH = "160px"
const GRID_CELL_MIN_WIDTH = "80px"
const PERCENTAGE_MULTIPLIER = 100

type Props = {
  cells: HeatCell[]
}

/**
 * KPI-Heatmap Komponente
 * Zeigt Scores als farbcodierte Matrix an
 */
export function KpiHeatmap({ cells }: Props): JSX.Element {
  // Reihen/Spalten dynamisch aus Cells ableiten
  const rows = Array.from(new Set(cells.map((c) => c.row)))
  const cols = Array.from(new Set(cells.map((c) => c.col)))

  const gridTemplateColumns = `${GRID_FIRST_COLUMN_WIDTH} repeat(${cols.length}, minmax(${GRID_CELL_MIN_WIDTH}, 1fr))`

  return (
    <div className="w-full overflow-x-auto">
      <div className="min-w-[480px]">
        <div className="grid" style={{ gridTemplateColumns }}>
          {/* Header */}
          <div />
          {cols.map((colName): JSX.Element => (
            <div key={colName} className="text-sm font-semibold p-2">
              {colName}
            </div>
          ))}

          {/* Rows */}
          {rows.map((rowName): JSX.Element => (
            <React.Fragment key={rowName}>
              <div className="text-sm font-medium p-2">{rowName}</div>
              {cols.map((colName): JSX.Element => {
                const cell = cells.find(
                  (x) => x.row === rowName && x.col === colName
                )
                const score = cell?.score ?? 0
                const bg = heatColor(score)
                const severity = toSeverity(score)
                const border = severityBorder(severity)
                const displayValue =
                  cell !== undefined
                    ? score >= 0
                      ? `+${(score * PERCENTAGE_MULTIPLIER).toFixed(0)}%`
                      : `${(score * PERCENTAGE_MULTIPLIER).toFixed(0)}%`
                    : "–"

                return (
                  <div
                    key={`${rowName}-${colName}`}
                    className="p-2 text-sm rounded-md"
                    style={{ backgroundColor: bg, border: `1px solid ${border}` }}
                    title={cell?.tooltip}
                  >
                    {displayValue}
                  </div>
                )
              })}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  )
}
