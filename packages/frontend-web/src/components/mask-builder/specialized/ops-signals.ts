import { isAxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'

export const WEIGHING_TICKETS_ENDPOINT = '/api/v1/weighing-tickets'
export const WAAGE_ALLOCATED_IST = 'agrar.weighing_ticket.allocated'
export const EINLAGERUNG_IST = 'lager.einlagerung.created'
export const GOODS_RECEIPT_IST = 'goods_receipt.created'
/** Ist-EventType aus app/domains/verladung/models.py — kein Soll-Rename. */
export const LOADING_STARTED_IST = 'LOADING_STARTED'
export const LOADING_FINISHED_IST = 'LOADING_FINISHED'
export const OPS_AUTH_ERROR = 'Betriebszustände nicht lesbar: Recht oder Anmeldung fehlt.'

export type OpsSignalLabel =
  | 'Waage belegt'
  | 'Einlagerung'
  | 'Verladung gestartet'
  | 'Verladung beendet'

export const OPS_IST_LABEL: Record<string, OpsSignalLabel> = {
  [WAAGE_ALLOCATED_IST]: 'Waage belegt',
  [EINLAGERUNG_IST]: 'Einlagerung',
  [GOODS_RECEIPT_IST]: 'Einlagerung',
  [LOADING_STARTED_IST]: 'Verladung gestartet',
  [LOADING_FINISHED_IST]: 'Verladung beendet',
}

export const OPS_IST_TYPES = Object.keys(OPS_IST_LABEL)

export type OpsSignal = {
  id: string
  kind: 'waage' | 'lager' | 'verladung'
  label: OpsSignalLabel
  at: string | null
  detail?: string
}

type TicketRow = {
  id?: string
  ticket_number?: string
  scale_id?: string | null
  vehicle_plate?: string | null
  status?: string
  first_weighing_at?: string | null
}

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

function asString(value: unknown): string | null {
  if (typeof value !== 'string' || value.trim() === '') return null
  return value
}

function asTime(value: unknown): string | null {
  const text = asString(value)
  if (!text) return null
  return Number.isNaN(Date.parse(text)) ? null : text
}

export function istTypeFromSse(raw: unknown, namedType?: string): string | null {
  if (namedType && OPS_IST_LABEL[namedType]) return namedType
  const envelope = asObject(raw)
  if (!envelope) return null
  const type = [envelope.ist_event_type, envelope.event_type, envelope.event, envelope.type]
    .find((value): value is string => typeof value === 'string' && value.length > 0)
  return type && OPS_IST_LABEL[type] ? type : null
}

function nestedPayload(envelope: Record<string, unknown>): Record<string, unknown> {
  const nested = asObject(envelope.payload)
  return nested ?? envelope
}

export function opsSignalFromSse(
  raw: unknown,
  namedType?: string,
  receivedAt?: string,
): OpsSignal | null {
  const type = istTypeFromSse(raw, namedType)
  if (!type) return null
  const envelope = asObject(raw) ?? {}
  const payload = nestedPayload(envelope)
  const label = OPS_IST_LABEL[type]
  const kind: OpsSignal['kind'] =
    label === 'Waage belegt'
      ? 'waage'
      : label === 'Verladung gestartet' || label === 'Verladung beendet'
        ? 'verladung'
        : 'lager'
  const entityId = asString(payload.ticket_id)
    ?? asString(payload.tour_id)
    ?? asString(payload.receiptId)
    ?? asString(payload.id)
    ?? asString(envelope.event_id)
  const at = asTime(payload.timestamp)
    ?? asTime(payload.created_at)
    ?? asTime(payload.receivedDate)
    ?? asTime(payload.first_weighing_at)
    ?? asTime(envelope.timestamp)
    ?? receivedAt
    ?? null
  const detail = asString(payload.vehicle_plate)
    ?? asString(payload.ticket_number)
    ?? asString(payload.ticket_id)
    ?? asString(payload.receiptId)
    ?? asString(payload.id)
    ?? undefined
  return {
    id: entityId ? `${kind}:${entityId}` : `sse:${type}:${at ?? 'now'}`,
    kind,
    label,
    at,
    detail,
  }
}

export function occupancyFromTickets(items: TicketRow[]): OpsSignal[] {
  return items
    .filter((item) => String(item.status ?? '').toLowerCase() === 'open' && Boolean(item.id))
    .map((item) => ({
      id: `waage:${item.id}`,
      kind: 'waage' as const,
      label: 'Waage belegt' as const,
      at: asTime(item.first_weighing_at),
      detail: item.vehicle_plate || item.ticket_number || item.scale_id || undefined,
    }))
}

function readOccupancyError(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status
    if (status === 401 || status === 403) return OPS_AUTH_ERROR
    if (status === 503) return 'Betriebszustände nicht lesbar: Dienst oder Schema nicht bereit.'
    if (status != null) return `Betriebszustände nicht lesbar (HTTP ${status}).`
  }
  return 'Betriebszustände nicht lesbar.'
}

export async function fetchOpenScaleOccupancy(): Promise<OpsSignal[]> {
  let payload: { items?: TicketRow[] } | TicketRow[]
  try {
    const response = await apiClient.get<{ items?: TicketRow[] } | TicketRow[]>(
      WEIGHING_TICKETS_ENDPOINT,
      { params: { limit: 100 } },
    )
    payload = response.data ?? { items: [] }
  } catch (error) {
    throw new Error(readOccupancyError(error))
  }
  const items = Array.isArray(payload) ? payload : (payload.items ?? [])
  return occupancyFromTickets(items)
}

export function mergeOpsSignals(occupancy: OpsSignal[], incoming: OpsSignal[]): OpsSignal[] {
  const seen = new Set<string>()
  const merged: OpsSignal[] = []
  for (const row of [...incoming, ...occupancy]) {
    if (seen.has(row.id)) continue
    seen.add(row.id)
    merged.push(row)
  }
  return merged
}
