import { useEffect, useRef, useState } from 'react'
import { auth } from '@/lib/auth'
import { appendSseAuthToken } from '@/lib/sse-client'
import {
  OPS_IST_TYPES,
  opsSignalFromSse,
  type OpsSignal,
} from './ops-signals'

/** Bestehender Workspace-Kanal. Kein zweiter Event-Bus. */
export const WORKSPACE_TOUR_SSE_URL = '/api/events?stream=workspace'
export const TOUR_CREATED_IST_EVENT = 'logistik.tour.created'
export const SSE_AUTH_ERROR =
  'Live-Aktualisierung nicht verbunden (Anmeldung fehlt oder Kanal abgelehnt). Die Tafel bleibt sichtbar.'

const IGNORED = new Set(['assignment_confirmed', 'connected', 'ping', 'keepalive'])

function asObject(raw: unknown): Record<string, unknown> | null {
  if (typeof raw === 'string') {
    try {
      return asObject(JSON.parse(raw) as unknown)
    } catch {
      return null
    }
  }
  if (!raw || typeof raw !== 'object') return null
  return raw as Record<string, unknown>
}

/** Nur Ist-Name `logistik.tour.created`. Soll-Rename `assignment_confirmed` ignorieren. */
export function isTourCreatedSsePayload(raw: unknown, namedType?: string): boolean {
  if (namedType === TOUR_CREATED_IST_EVENT) return true
  if (namedType && IGNORED.has(namedType)) return false
  const payload = asObject(raw)
  if (!payload) return false
  const type = [payload.ist_event_type, payload.event_type, payload.event, payload.type]
    .find((value): value is string => typeof value === 'string' && value.length > 0)
  if (!type || IGNORED.has(type)) return false
  return type === TOUR_CREATED_IST_EVENT
}

/** Verbindungs-URL inkl. `?token=` fuer EventSource (kein Authorization-Header moeglich). */
export function workspaceTourSseUrl(
  getToken: () => string | null = () => auth.getAccessToken(),
): string | null {
  return appendSseAuthToken(WORKSPACE_TOUR_SSE_URL, getToken())
}

export function useWorkspaceTourCreated(
  onTourCreated: () => void,
  enabled: boolean,
): { error: string | null; opsSignals: OpsSignal[] } {
  const callbackRef = useRef(onTourCreated)
  callbackRef.current = onTourCreated
  const [error, setError] = useState<string | null>(null)
  const [opsSignals, setOpsSignals] = useState<OpsSignal[]>([])

  useEffect(() => {
    if (!enabled || typeof EventSource === 'undefined') return
    const url = workspaceTourSseUrl()
    if (!url) {
      setError(SSE_AUTH_ERROR)
      return
    }
    let source: EventSource
    try {
      source = new EventSource(url)
    } catch {
      setError(SSE_AUTH_ERROR)
      return
    }
    setError(null)

    const ingest = (raw: unknown, namedType?: string) => {
      if (isTourCreatedSsePayload(raw, namedType)) {
        callbackRef.current()
        return
      }
      const signal = opsSignalFromSse(raw, namedType, new Date().toISOString())
      if (!signal) return
      setOpsSignals((current) => [signal, ...current.filter((row) => row.id !== signal.id)].slice(0, 20))
    }

    source.onmessage = (event) => {
      ingest(event.data)
    }
    source.addEventListener(TOUR_CREATED_IST_EVENT, (event: Event) => {
      const message = event as MessageEvent<string>
      ingest(message.data, TOUR_CREATED_IST_EVENT)
    })
    for (const type of OPS_IST_TYPES) {
      source.addEventListener(type, (event: Event) => {
        const message = event as MessageEvent<string>
        ingest(message.data, type)
      })
    }
    source.onerror = () => {
      source.close()
      setError(SSE_AUTH_ERROR)
    }
    return () => {
      source.close()
    }
  }, [enabled])

  return { error, opsSignals }
}
