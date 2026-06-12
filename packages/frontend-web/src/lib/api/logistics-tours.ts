/**
 * Logistik Touren + Lieferschein-Read-Spine (LOG-SPINE-001 / LOG-SPINE-RAND-001)
 */
import { apiClient } from '../api-client'

export type DeliveryNoteHint = {
  id: string
  delivery_note_number?: string | null
  status?: string | null
  delivery_date?: string | null
  customer_id?: string | null
  sales_order_id?: string | null
}

export type TourStopRow = Record<string, unknown> & {
  id?: string
  delivery_note_ref?: string | null
  delivery_note_hint?: DeliveryNoteHint | null
}

export type LogisticsTourDetail = Record<string, unknown> & {
  id: string
  stops?: TourStopRow[]
  events?: unknown[]
}

export async function fetchTourWithDeliveryHints(tourId: string): Promise<LogisticsTourDetail> {
  const res = await apiClient.get<LogisticsTourDetail>(
    `/api/v1/logistik/tours/${encodeURIComponent(tourId)}`,
    { params: { include_delivery_hints: 'true' } },
  )
  return res.data as LogisticsTourDetail
}

export async function resolveSalesDeliveryNoteByRef(ref: string): Promise<DeliveryNoteHint> {
  const res = await apiClient.get<DeliveryNoteHint>('/api/v1/logistik/sales-delivery-note-by-ref', {
    params: { ref },
  })
  return res.data as DeliveryNoteHint
}

/** Fail-closed: nur GEPLANT, keine gelieferten Stopps (sonst 409). */
export async function cancelLogisticsTour(tourId: string, body?: { grund?: string }): Promise<void> {
  await apiClient.post(
    `/api/v1/logistik/tours/${encodeURIComponent(tourId)}/cancel`,
    body ?? {},
  )
}

/** Fail-closed: Stopp nur GEPLANT/ANGEFAHREN (sonst 409). */
export async function cancelLogisticsTourStop(
  tourId: string,
  stopId: string,
  body?: { grund?: string },
): Promise<void> {
  await apiClient.post(
    `/api/v1/logistik/tours/${encodeURIComponent(tourId)}/stops/${encodeURIComponent(stopId)}/cancel`,
    body ?? {},
  )
}
