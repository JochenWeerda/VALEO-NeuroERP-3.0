import React, { useEffect, useMemo, useState } from 'react'
import { inventoryService, type EpcisEvent } from '../../../lib/services/inventory-service'
import { Button } from '../../../components/ui/Button'

function formatDate(iso?: string | null) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleString('de-DE')
  } catch {
    return iso
  }
}

export default function EpcisEventsPage() {
  const [events, setEvents] = useState<EpcisEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [tenantId, setTenantId] = useState<string>('default')
  const [bizStep, setBizStep] = useState<string>('')
  const [sku, setSku] = useState<string>('')
  const [limit, setLimit] = useState<number>(200)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    inventoryService
      .listEpcisEvents({ limit }, tenantId)
      .then((res) => {
        if (mounted) setEvents(res.items || [])
      })
      .finally(() => mounted && setLoading(false))
    return () => {
      mounted = false
    }
  }, [tenantId, limit])

  const filtered = useMemo(() => {
    return events.filter((e) => {
      if (bizStep && (e.biz_step || '').toLowerCase() !== bizStep.toLowerCase()) return false
      if (sku && (e.sku || '').toLowerCase().indexOf(sku.toLowerCase()) === -1) return false
      return true
    })
  }, [events, bizStep, sku])

  const kpis = useMemo(() => {
    const total = filtered.length
    const byStep: Record<string, number> = {}
    filtered.forEach((e) => {
      const key = (e.biz_step || 'unbekannt').toLowerCase()
      byStep[key] = (byStep[key] || 0) + 1
    })
    const topSteps = Object.entries(byStep)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
    return { total, topSteps }
  }, [filtered])

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">EPCIS Events</h1>
        <div className="flex items-center gap-2">
          <input
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            placeholder="Tenant"
            className="border px-2 py-1 rounded"
          />
          <select
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value, 10))}
            className="border px-2 py-1 rounded"
          >
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
          </select>
          <Button onClick={() => window.location.reload()}>Reload</Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 border rounded">
          <div className="text-sm text-gray-500">Events gesamt</div>
          <div className="text-2xl font-semibold">{kpis.total}</div>
        </div>
        <div className="p-4 border rounded col-span-2">
          <div className="text-sm text-gray-500 mb-1">Top biz_steps</div>
          <div className="flex gap-3">
            {kpis.topSteps.map(([step, count]) => (
              <span key={step} className="px-2 py-1 rounded bg-gray-100 text-sm">
                {step}: {count}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <input
          value={bizStep}
          onChange={(e) => setBizStep(e.target.value)}
          placeholder="biz_step"
          className="border px-2 py-1 rounded"
        />
        <input
          value={sku}
          onChange={(e) => setSku(e.target.value)}
          placeholder="sku"
          className="border px-2 py-1 rounded"
        />
      </div>

      <div className="overflow-auto border rounded">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2">Zeit</th>
              <th className="text-left p-2">Typ</th>
              <th className="text-left p-2">biz_step</th>
              <th className="text-left p-2">sku</th>
              <th className="text-left p-2">qty</th>
              <th className="text-left p-2">read_point</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td className="p-2" colSpan={6}>
                  Lädt ...
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td className="p-2" colSpan={6}>
                  Keine Daten
                </td>
              </tr>
            ) : (
              filtered.map((e) => (
                <tr key={e.id} className="border-t">
                  <td className="p-2">{formatDate(e.event_time)}</td>
                  <td className="p-2">{e.event_type}</td>
                  <td className="p-2">{e.biz_step || ''}</td>
                  <td className="p-2">{e.sku || ''}</td>
                  <td className="p-2">{e.quantity ?? ''}</td>
                  <td className="p-2">{e.read_point || ''}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}


