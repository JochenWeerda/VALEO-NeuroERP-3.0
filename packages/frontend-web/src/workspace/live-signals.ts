import { useEffect, useMemo, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { auth } from '@/lib/auth'
import { appendSseAuthToken } from '@/lib/sse-client'
import { defaultHomeSignals } from './home-signals'
import { INBOX_SLOT } from './queue-contracts'
import type { WorkspaceLayer, WorkspaceSignal, SignalKind, SignalSeverity } from './types'

/** Bestehender SSE-Kanal. Originalnamen, keine Soll-Rename. */
export const WORKSPACE_SSE_URL = '/api/events?stream=workspace'

/** EventSource-URL mit `?token=` (kein Authorization-Header moeglich). */
export function workspaceLiveSseUrl(
  getToken: () => string | null = () => auth.getAccessToken(),
): string | null {
  return appendSseAuthToken(WORKSPACE_SSE_URL, getToken())
}

/** Freigabe-Worklist laut catalogId `finance.ap_invoice.approval.worklist`. */
export const APPROVAL_QUEUE_PATH = '/api/v1/workflows/approvals?assignee=me&status=pending'

const IGNORED_SOLL_NAMES = new Set([
  'assignment_confirmed',
  'document_proposed',
  'document_posted',
])

type IstSignalTarget = {
  relatedActionIds: string[]
  kind: SignalKind
  layer: Extract<WorkspaceLayer, 'situational' | 'proactive'>
  severity: SignalSeverity
  /** Zusätzliche Pruefcodes fuer die Handlungsbedarf-Liste (Anzeige; Score bleibt severity/count). */
  reasonCodes?: readonly string[]
}

/**
 * Ist-Typen auf dem Stream `/api/events?stream=workspace`.
 * Keine Soll-Namen, kein Sales-Angebot, keine Kontraktmahnung, kein NC-G3.
 */
export const IST_EVENT_ACTIONS: Record<string, IstSignalTarget> = {
  'logistik.tour.created': {
    relatedActionIds: ['logistics.undispatched-truck-orders'],
    kind: 'incident',
    layer: 'situational',
    severity: 3,
  },
  'lkw.registered': {
    relatedActionIds: ['logistics.undispatched-truck-orders'],
    kind: 'incident',
    layer: 'situational',
    severity: 3,
  },
  /** Ist EventType aus Verladung — Outbox in tours.py start/finish-loading. */
  LOADING_STARTED: {
    relatedActionIds: ['logistics.undispatched-truck-orders'],
    kind: 'incident',
    layer: 'situational',
    severity: 3,
    reasonCodes: ['ops:verladung', 'ist:LOADING_STARTED'],
  },
  LOADING_FINISHED: {
    relatedActionIds: ['logistics.undispatched-truck-orders'],
    kind: 'incident',
    layer: 'situational',
    severity: 3,
    reasonCodes: ['ops:verladung', 'ist:LOADING_FINISHED'],
  },
  'finance.ap_invoice.approval_requested': {
    relatedActionIds: ['finance.invoices-awaiting-my-approval'],
    kind: 'open-task',
    layer: 'proactive',
    severity: 4,
    reasonCodes: ['ops:freigabe', 'ist:approval_requested'],
  },
  'finance.ap_invoice.approval_granted': {
    relatedActionIds: ['finance.invoices-awaiting-my-approval'],
    kind: 'incident',
    layer: 'situational',
    severity: 3,
  },
  'finance.ap_invoice.approved': {
    relatedActionIds: ['finance.invoices-awaiting-my-approval'],
    kind: 'incident',
    layer: 'situational',
    severity: 3,
  },
  'finance.ap_invoice.posted': {
    relatedActionIds: ['finance.invoices-awaiting-my-approval', 'workspace.document-inbox'],
    kind: 'bottleneck',
    layer: 'situational',
    severity: 3,
  },
  'goods_receipt.created': {
    relatedActionIds: ['procurement.goods-receipt-qty-variance'],
    kind: 'bottleneck',
    layer: 'situational',
    severity: 3,
  },
  'lager.einlagerung.created': {
    relatedActionIds: ['procurement.goods-receipt-qty-variance'],
    kind: 'bottleneck',
    layer: 'situational',
    severity: 3,
  },
  'docflow.document.posted': {
    relatedActionIds: ['workspace.document-inbox'],
    kind: 'open-task',
    layer: 'situational',
    severity: 3,
  },
  'sales.invoice.proposed': {
    relatedActionIds: ['workspace.document-inbox'],
    kind: 'open-task',
    layer: 'proactive',
    severity: 4,
  },
  'sales.invoice.posted': {
    relatedActionIds: ['workspace.document-inbox'],
    kind: 'open-task',
    layer: 'situational',
    severity: 3,
  },
  'sales.gutschrift.proposed': {
    relatedActionIds: ['workspace.document-inbox'],
    kind: 'open-task',
    layer: 'proactive',
    severity: 4,
  },
  'agrar.weighing_ticket.allocated': {
    relatedActionIds: ['harvest.intake-queue'],
    kind: 'open-task',
    layer: 'situational',
    severity: 3,
  },
  /** Ist-Outbox aus quality_protocols finalize → stream=workspace (document_posted). */
  'agrar.quality_protocol.completed': {
    relatedActionIds: ['agrar.qualitaets-handlungsbedarf'],
    kind: 'open-task',
    layer: 'proactive',
    severity: 4,
  },
}

export type WorkspaceQueueCounts = {
  inbox?: number
  approval?: number
}

export function parseQueueCount(payload: unknown): number | undefined {
  if (typeof payload === 'number' && Number.isFinite(payload)) {
    return Math.max(0, Math.floor(payload))
  }
  if (Array.isArray(payload)) {
    return payload.length
  }
  if (!payload || typeof payload !== 'object') {
    return undefined
  }
  const value = payload as Record<string, unknown>
  if (typeof value.count === 'number' && Number.isFinite(value.count)) {
    return Math.max(0, Math.floor(value.count))
  }
  if (Array.isArray(value.items)) {
    return value.items.length
  }
  if (Array.isArray(value.results)) {
    return value.results.length
  }
  if ('data' in value) {
    return parseQueueCount(value.data)
  }
  return undefined
}

function parseObject(raw: unknown): Record<string, unknown> | null {
  if (typeof raw === 'string') {
    try {
      return parseObject(JSON.parse(raw) as unknown)
    } catch {
      return null
    }
  }
  if (!raw || typeof raw !== 'object') {
    return null
  }
  return raw as Record<string, unknown>
}

export function istTypeFromSsePayload(raw: unknown): string | null {
  const payload = parseObject(raw)
  if (!payload) {
    return null
  }
  const istType = [payload.ist_event_type, payload.eventType, payload.event, payload.type]
    .find((value): value is string => typeof value === 'string' && value.length > 0)
  if (!istType || istType === 'connected' || istType === 'ping' || istType === 'keepalive') {
    return null
  }
  if (IGNORED_SOLL_NAMES.has(istType) || !(istType in IST_EVENT_ACTIONS)) {
    return null
  }
  return istType
}

export function signalFromIstEvent(istType: string, count = 1): WorkspaceSignal | null {
  const target = IST_EVENT_ACTIONS[istType]
  if (!target) {
    return null
  }
  return {
    id: `sse:${istType}`,
    kind: target.kind,
    layer: target.layer,
    relatedActionIds: target.relatedActionIds,
    severity: target.severity,
    source: `sse:${istType}`,
    count,
    ...(target.reasonCodes && target.reasonCodes.length > 0
      ? { reasonCodes: target.reasonCodes }
      : {}),
  }
}

/** Bestehende Fachaktion `logistik.undispatched_vehicles.list`. Keine zweite Route. */
export const OPEN_ABRUF_ACTION_ID = 'logistics.undispatched-truck-orders'

/**
 * Ein Sammelsignal aus der Abruf-Liste der Dispo-Tafel.
 * Keine Zeile pro Auftrag. Eine leere Liste liefert nichts.
 */
export function signalFromOpenAbrufe(orders: readonly { id: string }[]): WorkspaceSignal | null {
  if (orders.length === 0) {
    return null
  }
  return {
    id: 'queue-open-abrufe',
    kind: 'open-task',
    layer: 'situational',
    relatedActionIds: [OPEN_ABRUF_ACTION_ID],
    severity: 3,
    source: 'disposition:open-abrufe',
    count: orders.length,
  }
}

export function signalsFromQueueCounts(counts: WorkspaceQueueCounts): WorkspaceSignal[] {
  const signals: WorkspaceSignal[] = []
  if (typeof counts.inbox === 'number' && counts.inbox > 0) {
    signals.push({
      id: 'queue-inbox',
      kind: 'open-task',
      layer: 'situational',
      relatedActionIds: ['workspace.document-inbox'],
      severity: 3,
      source: 'queue:inbox',
      count: counts.inbox,
    })
  }
  if (typeof counts.approval === 'number' && counts.approval > 0) {
    signals.push({
      id: 'queue-approval',
      kind: 'open-task',
      layer: 'proactive',
      relatedActionIds: ['finance.invoices-awaiting-my-approval'],
      severity: 4,
      source: 'queue:approval',
      count: counts.approval,
      reasonCodes: ['queue:approval', 'ops:freigabe'],
    })
  }
  return signals
}

export function mergeHomeSignals(
  calendar: WorkspaceSignal[],
  live: WorkspaceSignal[],
): WorkspaceSignal[] {
  if (live.length === 0) {
    return calendar
  }
  const byId = new Map(calendar.map((signal) => [signal.id, signal]))
  for (const signal of live) {
    byId.set(signal.id, signal)
  }
  return [...byId.values()]
}

/** Only successfully read queues can replace their previous, possibly stale, signals. */
export function reconcileQueueSignals(
  current: WorkspaceSignal[],
  counts: WorkspaceQueueCounts,
  discardOldSse = false,
): WorkspaceSignal[] {
  const refreshedActions = new Set<string>()
  if (counts.inbox !== undefined) refreshedActions.add('workspace.document-inbox')
  if (counts.approval !== undefined) refreshedActions.add('finance.invoices-awaiting-my-approval')
  const retained = current.filter((signal) => {
    if (counts.inbox !== undefined && signal.id === 'queue-inbox') return false
    if (counts.approval !== undefined && signal.id === 'queue-approval') return false
    return !discardOldSse || !signal.id.startsWith('sse:')
      || !signal.relatedActionIds.some((id) => refreshedActions.has(id))
  })
  return mergeHomeSignals(retained, signalsFromQueueCounts(counts))
}

async function readQueueCount(path: string): Promise<number | undefined> {
  try {
    const response = await apiClient.get<unknown>(path)
    return parseQueueCount(response.data) ?? parseQueueCount(response)
  } catch {
    return undefined
  }
}

export async function fetchWorkspaceQueueCounts(): Promise<WorkspaceQueueCounts | 'unavailable'> {
  const [inbox, approval] = await Promise.all([
    readQueueCount(INBOX_SLOT.queueEndpoint),
    readQueueCount(APPROVAL_QUEUE_PATH),
  ])
  if (inbox === undefined && approval === undefined) {
    return 'unavailable'
  }
  return { inbox, approval }
}

export function useWorkspaceLiveSignals(now: Date): WorkspaceSignal[] {
  const calendar = useMemo(() => defaultHomeSignals(now), [now])
  const [live, setLive] = useState<WorkspaceSignal[]>([])

  useEffect(() => {
    let cancelled = false
    let source: EventSource | null = null
    let retryTimer: ReturnType<typeof setTimeout> | null = null
    let queueTimer: ReturnType<typeof setTimeout> | null = null
    let retries = 0
    let queueRequest = 0
    let signalRevision = 0
    const maxRetries = 5
    const retryBaseMs = 1_000

    const reloadQueues = async (reconnected = false): Promise<void> => {
      const request = ++queueRequest
      const revision = signalRevision
      const counts = await fetchWorkspaceQueueCounts()
      if (cancelled || request !== queueRequest || counts === 'unavailable') return
      setLive((current) => reconcileQueueSignals(current, counts, reconnected && revision === signalRevision))
    }

    const ingest = (raw: unknown): void => {
      const istType = istTypeFromSsePayload(raw)
      if (!istType) return
      const payload = parseObject(raw)
      const nested = payload?.payload
      const count = parseQueueCount(nested) ?? parseQueueCount(payload?.count) ?? 1
      const signal = signalFromIstEvent(istType, count)
      if (!signal) return
      signalRevision += 1
      setLive((current) => mergeHomeSignals(current, [signal]))
      // Queue-facing SSE events are hints. A short, shared debounce lets the
      // authenticated read model confirm completions and clear old counts.
      if (signal.relatedActionIds.some((id) =>
        id === 'workspace.document-inbox' || id === 'finance.invoices-awaiting-my-approval')) {
        if (queueTimer) clearTimeout(queueTimer)
        queueTimer = setTimeout(() => {
          queueTimer = null
          void reloadQueues(true)
        }, 250)
      }
    }

    const scheduleReconnect = (): void => {
      if (cancelled || retryTimer || retries >= maxRetries) return
      const delay = Math.min(retryBaseMs * 2 ** retries, 16_000)
      retries += 1
      retryTimer = setTimeout(() => {
        retryTimer = null
        void connect()
      }, delay)
    }

    const connect = async (initialToken?: string): Promise<void> => {
      if (cancelled || source || typeof EventSource === 'undefined') return
      // Revalidate on every attempt: the URL must never reuse an expired token.
      let token: string | null
      try {
        token = initialToken ?? await auth.getFreshAccessToken()
      } catch {
        scheduleReconnect()
        return
      }
      if (cancelled || source || !token) return
      const url = workspaceLiveSseUrl(() => token)
      if (!url) return
      let next: EventSource
      try {
        next = new EventSource(url)
      } catch {
        scheduleReconnect()
        return
      }
      source = next
      next.onopen = () => {
        if (cancelled || source !== next) return
        // A socket can fail before its first open; the mount snapshot may now
        // be stale. Every successful open refreshes both queues.
        // A confirmed open starts a new five-attempt outage budget.
        retries = 0
        void reloadQueues(true)
      }
      next.onmessage = (event) => {
        if (!cancelled && source === next) ingest(event.data)
      }
      for (const istType of Object.keys(IST_EVENT_ACTIONS)) {
        next.addEventListener(istType, (event: Event) => {
          if (cancelled || source !== next) return
          const message = event as MessageEvent<string>
          ingest(message.data ? { type: istType, ...(parseObject(message.data) ?? {}) } : { type: istType })
        })
      }
      next.onerror = () => {
        if (cancelled || source !== next) return
        next.close()
        source = null
        scheduleReconnect()
      }
    }

    void (async () => {
      let token: string | null
      try {
        token = await auth.getFreshAccessToken()
      } catch {
        scheduleReconnect()
        return
      }
      if (cancelled || !token) return
      void reloadQueues()
      void connect(token)
    })()
    return () => {
      cancelled = true
      queueRequest += 1
      if (retryTimer) clearTimeout(retryTimer)
      if (queueTimer) clearTimeout(queueTimer)
      source?.close()
      source = null
    }
  }, [])


  return useMemo(() => mergeHomeSignals(calendar, live), [calendar, live])
}
