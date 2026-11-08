import { isAxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'

export const TOUR_DETAIL_PATH = (tourId: string) => `/api/v1/logistik/tours/${encodeURIComponent(tourId)}`
export const TIMELINE_FIELD_MISSING = 'Zeitachse nicht belegbar, Feld planned_arrival fehlt.'

export type TimelineStop = {
  stopId: string
  resourceId: string
  plannedArrival: string
  label: string
  lat?: number
  lng?: number
}

export type StopCoordinate = {
  stopId: string
  label: string
  lat: number
  lng: number
}

export type TimelineLane = {
  resourceId: string
  resourceLabel: string
  stops: TimelineStop[]
  coordinates: StopCoordinate[]
}

type TourStopPayload = {
  id?: string
  stop_order?: number
  planned_arrival?: string | null
  delivery_note_ref?: string | null
  address?: string | null
  lat?: unknown
  lng?: unknown
}

type TourDetailPayload = {
  id?: string
  vehicle_id?: string | null
  stops?: TourStopPayload[]
}

/** Grad aus dem Tour-GET. Keine Geocodierung, keine Mikrogramm-Umrechnung. */
export function readStopLatLng(lat: unknown, lng: unknown): { lat: number; lng: number } | null {
  if (typeof lat !== 'number' || typeof lng !== 'number') return null
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
  if (Math.abs(lat) > 90 || Math.abs(lng) > 180) return null
  return { lat, lng }
}

export function formatStopLatLng(lat: number, lng: number): string {
  const fmt = new Intl.NumberFormat('de-DE', {
    minimumFractionDigits: 5,
    maximumFractionDigits: 5,
    useGrouping: false,
  })
  return `${fmt.format(lat)}, ${fmt.format(lng)}`
}

function stopLabel(stop: TourStopPayload): string {
  return String(stop.delivery_note_ref || stop.address || `Stopp ${stop.stop_order ?? ''}`).trim()
}

export function readPlannedArrival(raw: unknown): string | null {
  if (typeof raw !== 'string' || !raw.trim()) return null
  const ms = Date.parse(raw)
  return Number.isFinite(ms) ? raw : null
}

export function laneFromTourDetail(detail: TourDetailPayload, fallbackId: string): TimelineLane {
  const resourceId = String(detail.id ?? fallbackId)
  const stops = Array.isArray(detail.stops) ? detail.stops : []
  const markers: TimelineStop[] = []
  const coordinates: StopCoordinate[] = []
  for (const stop of stops) {
    if (!stop?.id) continue
    const label = stopLabel(stop)
    const point = readStopLatLng(stop.lat, stop.lng)
    if (point) {
      coordinates.push({ stopId: String(stop.id), label, lat: point.lat, lng: point.lng })
    }
    const plannedArrival = readPlannedArrival(stop.planned_arrival)
    if (!plannedArrival) continue
    markers.push({
      stopId: String(stop.id),
      resourceId,
      plannedArrival,
      label,
      ...(point ?? {}),
    })
  }
  return {
    resourceId,
    resourceLabel: String(detail.vehicle_id || resourceId),
    stops: markers,
    coordinates,
  }
}

export function axisFromLanes(lanes: TimelineLane[]): { startMs: number; endMs: number } | null {
  const times = lanes.flatMap((lane) => lane.stops.map((stop) => Date.parse(stop.plannedArrival))).filter(Number.isFinite)
  if (times.length === 0) return null
  const startMs = Math.min(...times)
  const endMs = Math.max(...times)
  return { startMs, endMs }
}

export function markerOffset(plannedArrival: string, axis: { startMs: number; endMs: number }): number {
  const ms = Date.parse(plannedArrival)
  if (!Number.isFinite(ms)) return 0
  if (axis.endMs <= axis.startMs) return 50
  return Math.min(100, Math.max(0, ((ms - axis.startMs) / (axis.endMs - axis.startMs)) * 100))
}

function readError(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      return 'Zeitachse nicht lesbar: Anmeldung fehlt. Die Tafel bleibt sichtbar.'
    }
  }
  return 'Zeitachse nicht lesbar.'
}

/** Nur GET auf die bestehende Tour-Detail-API. Kein Scheduling, keine erfundenen Zeiten. */
export async function fetchTimelineLanes(resourceIds: string[]): Promise<TimelineLane[]> {
  const lanes: TimelineLane[] = []
  let lastError: string | null = null
  for (const resourceId of resourceIds) {
    try {
      const response = await apiClient.get<TourDetailPayload>(TOUR_DETAIL_PATH(resourceId))
      const payload = response.data && !Array.isArray(response.data) ? response.data : { id: resourceId, stops: [] }
      lanes.push(laneFromTourDetail(payload, resourceId))
    } catch (error) {
      lastError = readError(error)
    }
  }
  if (lanes.length === 0 && lastError) throw new Error(lastError)
  return lanes
}
