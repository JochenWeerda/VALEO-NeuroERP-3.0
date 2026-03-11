import type { JSX } from 'react'

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

export default function AnalyticsCashflowChart({ cashflow, currencyFormatter }: AnalyticsCashflowChartProps): JSX.Element {
  const maxValue = Math.max(
    ...cashflow.flatMap((item) => [Math.abs(item.inflow), Math.abs(item.outflow), Math.abs(item.net)]),
    1,
  )

  return (
    <div className="grid h-full gap-4 overflow-auto pr-1">
      <div className="flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-[#0EA870]" />
          <span className="text-slate-700">Zufluss</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-[#D94A66]" />
          <span className="text-slate-700">Abfluss</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-[#005599]" />
          <span className="text-slate-700">Netto</span>
        </div>
      </div>

      <div className="space-y-3">
        {cashflow.map((item) => (
          <div key={item.period} className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
            <div className="mb-3 flex items-center justify-between gap-3">
              <span className="text-sm font-medium text-slate-900">{item.period}</span>
              <span className={`text-sm font-semibold ${item.net >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>
                {currencyFormatter.format(item.net)}
              </span>
            </div>
            <div className="space-y-2">
              {[
                { label: 'Zufluss', value: item.inflow, color: '#0EA870' },
                { label: 'Abfluss', value: item.outflow, color: '#D94A66' },
                { label: 'Netto', value: Math.abs(item.net), color: '#005599' },
              ].map((entry) => (
                <div key={entry.label} className="space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-600">
                    <span>{entry.label}</span>
                    <span>{currencyFormatter.format(entry.value)}</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-white">
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
