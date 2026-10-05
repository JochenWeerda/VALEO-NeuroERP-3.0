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

export type LogisticsTourCreate = {
  date?: string
  vehicle_id?: string | null
  driver_id?: string | null
  notes?: string | null
  stops?: Array<{
    stop_order?: number
    address?: string | null
    lat?: number | null
    lng?: number | null
    customer_id?: string | null
    delivery_note_ref?: string | null
  }>
}

export type Zielort = { address: string | null; lat: number | null; lng: number | null }

/** Straße aus dem Kundenstamm, Koordinate nur aus der Kundenkarte. Kein Geocoding. */
export async function zielortFuerKunde(customerId: string): Promise<Zielort> {
  const leer: Zielort = { address: null, lat: null, lng: null }
  try {
    const { data } = await apiClient.get<Record<string, unknown>>(
      `/api/v1/crm/customers/${encodeURIComponent(customerId)}`,
    )
    const teile = [data.address, data.postal_code, data.city]
      .map((wert) => String(wert ?? '').trim())
      .filter(Boolean)
    const nr = String(data.customer_number ?? data.kunden_nr ?? '').trim()
    let lat: number | null = null
    let lng: number | null = null
    if (nr) {
      const karte = await apiClient.get<{
        features?: Array<{ properties?: { kunden_nr?: string }; geometry?: { coordinates?: number[] } }>
      }>('/api/v1/crm/kunden-karte/map')
      const coords = (karte.data.features ?? []).find((feature) => feature.properties?.kunden_nr === nr)
        ?.geometry?.coordinates
      if (coords && coords.length >= 2 && Number.isFinite(coords[0]) && Number.isFinite(coords[1])) {
        lng = coords[0]
        lat = coords[1]
      }
    }
    return { address: teile.length > 0 ? teile.join(', ') : null, lat, lng }
  } catch {
    // Zielort ist optional. Die Tour entsteht auch ohne Straße und Koordinate.
    return leer
  }
}

/** Tour aus einem Warenbeleg. Der Lieferschein bleibt die Referenz am Stopp. */
export async function createLogisticsTour(body: LogisticsTourCreate): Promise<{ id: string }> {
  const res = await apiClient.post<{ id: string }>('/api/v1/logistik/tours', body)
  return res.data
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
