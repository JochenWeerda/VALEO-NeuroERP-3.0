import { useEffect, useState } from 'react'
import { useSSE } from '@/lib/sse'
import { useLive } from '@/state/live'

export function useLiveSales() {
  const { setSalesDoc } = useLive()
  const [status, setStatus] = useState<'open' | 'closed' | 'error'>('closed')
  useSSE('sales', (msg) => {
    // erwartet: { type:'doc', id, number, status, total, updatedAt }
    if (msg && typeof msg === 'object' && (msg as any).type === 'doc') {
      const d = msg as any
      setSalesDoc({ id: d.id, number: d.number, status: d.status, total: d.total, updatedAt: d.updatedAt ?? Date.now() })
    }
  }, { onStatus: setStatus })
  return { status }
}

export function useLiveInventory() {
  const { setInventoryEvt } = useLive()
  const [status, setStatus] = useState<'open' | 'closed' | 'error'>('closed')
  useSSE('inventory', (msg) => {
    // erwartet: { type:'stock', sku, delta, qty, ts }
    if (msg && typeof msg === 'object' && (msg as any).type === 'stock') {
      const e = msg as any
      setInventoryEvt({ sku: e.sku, delta: e.delta, qty: e.qty, ts: e.ts ?? Date.now() })
    }
  }, { onStatus: setStatus })
  return { status }
}

export function usePolicyAlerts() {
  const { pushPolicy, sweepPolicy, policy } = useLive()
  const [status, setStatus] = useState<'open' | 'closed' | 'error'>('closed')
  useSSE('policy', (msg) => {
    // erwartet: { type:'alert', id, title, message, severity, ts }
    if (msg && typeof msg === 'object' && (msg as any).type === 'alert') {
      const a = msg as any
      pushPolicy({ id: a.id, title: a.title, message: a.message, severity: a.severity, ts: a.ts ?? Date.now() })
    }
  }, { onStatus: setStatus })

  useEffect(() => {
    const t = setInterval(() => sweepPolicy(5 * 60 * 1000), 10 * 1000)
    return () => clearInterval(t)
  }, [sweepPolicy])

  return { status, policy }
}