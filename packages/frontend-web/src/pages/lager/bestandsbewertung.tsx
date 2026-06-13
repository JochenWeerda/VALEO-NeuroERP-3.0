import { useState, useMemo } from 'react'
import { useStockValuation } from '@/lib/api/warehouse-wms'

export default function BestandsbewertungPage() {
  const [warehouseId, setWarehouseId] = useState('')
  const { data: rows = [], isLoading, isError } = useStockValuation(warehouseId || undefined)

  const totalValue = useMemo(
    () => rows.reduce((sum, r) => sum + r.total_value_eur, 0),
    [rows],
  )
  const totalQty = useMemo(
    () => rows.reduce((sum, r) => sum + r.total_quantity_kg, 0),
    [rows],
  )

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Bestandsbewertung (Ø-Einstandspreis)</h1>
        <div className="flex gap-2 items-center">
          <label className="text-sm text-gray-500">Lager-ID (optional)</label>
          <input
            className="border rounded px-2 py-1 text-sm w-48"
            placeholder="alle Lager"
            value={warehouseId}
            onChange={(e) => setWarehouseId(e.target.value)}
          />
        </div>
      </div>

      {isLoading && <p className="text-sm text-gray-500">Lade Bestandswerte…</p>}
      {isError && (
        <p className="text-sm text-red-600">Fehler beim Laden der Bestandsbewertung.</p>
      )}

      {!isLoading && !isError && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <SummaryCard label="Artikel/Chargen" value={rows.length.toString()} />
            <SummaryCard label="Gesamt-Menge (kg)" value={totalQty.toLocaleString('de-DE', { maximumFractionDigits: 2 })} />
            <SummaryCard
              label="Gesamtwert (€)"
              value={totalValue.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
              highlight
            />
          </div>

          <div className="overflow-auto rounded border">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="px-3 py-2 font-medium">Artikel-ID</th>
                  <th className="px-3 py-2 font-medium">Charge</th>
                  <th className="px-3 py-2 font-medium text-right">Menge (kg)</th>
                  <th className="px-3 py-2 font-medium text-right">Ø-Einstandspreis (€/kg)</th>
                  <th className="px-3 py-2 font-medium text-right">Bestandswert (€)</th>
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-3 py-4 text-center text-gray-400">
                      Keine Bestandsdaten vorhanden.
                    </td>
                  </tr>
                )}
                {rows.map((row, i) => (
                  <tr key={i} className="border-t hover:bg-gray-50">
                    <td className="px-3 py-2 font-mono text-xs">{row.article_id}</td>
                    <td className="px-3 py-2 text-gray-600">{row.batch_number ?? '—'}</td>
                    <td className="px-3 py-2 text-right">
                      {row.total_quantity_kg.toLocaleString('de-DE', { maximumFractionDigits: 3 })}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {row.avg_cost_per_kg > 0
                        ? row.avg_cost_per_kg.toLocaleString('de-DE', {
                            style: 'currency',
                            currency: 'EUR',
                            minimumFractionDigits: 4,
                          })
                        : <span className="text-gray-400 text-xs">k. A.</span>}
                    </td>
                    <td className="px-3 py-2 text-right font-medium">
                      {row.total_value_eur > 0
                        ? row.total_value_eur.toLocaleString('de-DE', {
                            style: 'currency',
                            currency: 'EUR',
                          })
                        : <span className="text-gray-400 text-xs">—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
              {rows.length > 0 && (
                <tfoot className="bg-gray-50 font-semibold border-t-2">
                  <tr>
                    <td colSpan={2} className="px-3 py-2">Summe</td>
                    <td className="px-3 py-2 text-right">
                      {totalQty.toLocaleString('de-DE', { maximumFractionDigits: 2 })}
                    </td>
                    <td />
                    <td className="px-3 py-2 text-right">
                      {totalValue.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </>
      )}
    </div>
  )
}

function SummaryCard({
  label,
  value,
  highlight,
}: {
  label: string
  value: string
  highlight?: boolean
}) {
  return (
    <div className={`rounded border p-4 ${highlight ? 'bg-blue-50 border-blue-200' : 'bg-white'}`}>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-lg font-semibold ${highlight ? 'text-blue-700' : ''}`}>{value}</p>
    </div>
  )
}
