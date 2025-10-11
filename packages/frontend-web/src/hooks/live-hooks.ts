import { useEffect, useMemo, useState } from 'react'
import { useSSE } from '@/lib/sse'
import { useLive } from '@/state/live'

type LiveStatus = 'open' | 'closed' | 'error'

interface SalesDocMessage {
  type: 'doc'
  id: string
  number: string
  status: string
  total?: number
  updatedAt?: number
}

interface InventoryMessage {
  type: 'stock'
  sku: string
  delta: number
  qty: number
  ts?: number
}

interface PolicyAlertMessage {
  type: 'alert'
  id: string
  title: string
  message: string
  severity: 'warn' | 'crit'
  ts?: number
}

const MILLISECONDS_PER_SECOND = 1000
const SECONDS_PER_MINUTE = 60
const POLICY_TTL_MINUTES = 5
const POLICY_SWEEP_INTERVAL_SECONDS = 10
const POLICY_TTL_MS = POLICY_TTL_MINUTES * SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND
const POLICY_SWEEP_INTERVAL_MS = POLICY_SWEEP_INTERVAL_SECONDS * MILLISECONDS_PER_SECOND

const isSalesDocMessage = (payload: unknown): payload is SalesDocMessage => {
  if (payload == null || typeof payload !== 'object') {
    return false
  }
  const candidate = payload as Partial<SalesDocMessage>
  return candidate.type === 'doc' && typeof candidate.id === 'string' && typeof candidate.number === 'string'
}

const isInventoryMessage = (payload: unknown): payload is InventoryMessage => {
  if (payload == null || typeof payload !== 'object') {
    return false
  }
  const candidate = payload as Partial<InventoryMessage>
  return candidate.type === 'stock' && typeof candidate.sku === 'string' && typeof candidate.delta === 'number'
}

const isPolicyAlertMessage = (payload: unknown): payload is PolicyAlertMessage => {
  if (payload == null || typeof payload !== 'object') {
    return false
  }
  const candidate = payload as Partial<PolicyAlertMessage>
  return candidate.type === 'alert' && typeof candidate.id === 'string' && typeof candidate.title === 'string'
}

export function useLiveSales(): { status: LiveStatus } {
  const { setSalesDoc } = useLive()
  const [status, setStatus] = useState<LiveStatus>('closed')

  useSSE(
    'sales',
    (msg) => {
      if (isSalesDocMessage(msg)) {
        setSalesDoc({
          id: msg.id,
          number: msg.number,
          status: msg.status,
          total: msg.total,
          updatedAt: msg.updatedAt ?? Date.now(),
        })
      }
    },
    { onStatus: setStatus },
  )

  return { status }
}

export function useLiveInventory(): { status: LiveStatus } {
  const { setInventoryEvt } = useLive()
  const [status, setStatus] = useState<LiveStatus>('closed')

  useSSE(
    'inventory',
    (msg) => {
      if (isInventoryMessage(msg)) {
        setInventoryEvt({
          sku: msg.sku,
          delta: msg.delta,
          qty: msg.qty,
          ts: msg.ts ?? Date.now(),
        })
      }
    },
    { onStatus: setStatus },
  )

  return { status }
}

export function usePolicyAlerts(): { status: LiveStatus; policy: ReturnType<typeof useLive>['policy'] } {
  const { pushPolicy, sweepPolicy, policy } = useLive()
  const [status, setStatus] = useState<LiveStatus>('closed')

  useSSE(
    'policy',
    (msg) => {
      if (isPolicyAlertMessage(msg)) {
        pushPolicy({
          id: msg.id,
          title: msg.title,
          message: msg.message,
          severity: msg.severity,
          ts: msg.ts ?? Date.now(),
        })
      }
    },
    { onStatus: setStatus },
  )

  useEffect(() => {
    const intervalId = setInterval(() => sweepPolicy(POLICY_TTL_MS), POLICY_SWEEP_INTERVAL_MS)
    return () => clearInterval(intervalId)
  }, [sweepPolicy])

  return useMemo(() => ({ status, policy }), [policy, status])
}
