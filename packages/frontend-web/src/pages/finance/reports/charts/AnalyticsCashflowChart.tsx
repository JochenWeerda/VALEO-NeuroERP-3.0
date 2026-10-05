import type { JSX } from 'react'
import { CHART_NEGATIVE, CHART_POSITIVE, chartSeriesColor } from '@/components/charts/chart-palette'

interface CashflowPoint {
  period: string
  inflow: number
  outflow: number
  net: number
}

interface AnalyticsCashflowChartProps {
  cashflow: CashflowPoint[]
  currencyFormatter: Intl.NumberFormat
}

/* Zufluss/Abfluss tragen Polarität (gut/schlecht) → Statusfarben; Netto ist neutral → Slot 1. */
const FLOW_COLORS = { inflow: CHART_POSITIVE, outflow: CHART_NEGATIVE, net: chartSeriesColor(0) }

export default function AnalyticsCashflowChart({ cashflow, currencyFormatter }: AnalyticsCashflowChartProps): JSX.Element {
  const maxValue = Math.max(
    ...cashflow.flatMap((item) => [Math.abs(item.inflow), Math.abs(item.outflow), Math.abs(item.net)]),
    1,
  )

  return (
    <div className="grid h-full gap-4 overflow-auto pr-1">
      <div className="flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: FLOW_COLORS.inflow }} aria-hidden />
          <span className="text-muted-foreground">Zufluss</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: FLOW_COLORS.outflow }} aria-hidden />
          <span className="text-muted-foreground">Abfluss</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: FLOW_COLORS.net }} aria-hidden />
          <span className="text-muted-foreground">Netto</span>
        </div>
      </div>

      <div className="space-y-3">
        {cashflow.map((item) => (
          <div key={item.period} className="rounded-lg border bg-muted/30 p-3">
            <div className="mb-3 flex items-center justify-between gap-3">
              <span className="text-sm font-medium text-foreground">{item.period}</span>
              <span className={`text-sm font-semibold tabular-nums ${item.net >= 0 ? 'text-status-success' : 'text-status-error'}`}>
                {currencyFormatter.format(item.net)}
              </span>
            </div>
            <div className="space-y-2">
              {[
                { label: 'Zufluss', value: item.inflow, color: FLOW_COLORS.inflow },
                { label: 'Abfluss', value: item.outflow, color: FLOW_COLORS.outflow },
                { label: 'Netto', value: Math.abs(item.net), color: FLOW_COLORS.net },
              ].map((entry) => (
                <div key={entry.label} className="space-y-1">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{entry.label}</span>
                    <span className="tabular-nums">{currencyFormatter.format(entry.value)}</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-muted">
                    <div
                      className="h-2.5 rounded-full"
                      style={{
                        width: `${Math.max((entry.value / maxValue) * 100, entry.value > 0 ? 4 : 0)}%`,
                        backgroundColor: entry.color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
