import { useEffect, useRef, useState } from 'react'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { StopCoordinate } from './load-timeline'

/**
 * Dieselbe Rasterquelle wie MilchviehKartePage in
 * `pages/agrar/milchvieh-karte-legacy.tsx`. Kein neuer Tile-Server, kein Key.
 */
export const DISPOSITION_MAP_TILES = ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'] as const

export const DISPOSITION_MAP_STYLE = {
  version: 8 as const,
  sources: {
    osm: {
      type: 'raster' as const,
      tiles: [...DISPOSITION_MAP_TILES],
      tileSize: 256,
      attribution: '© OpenStreetMap',
    },
  },
  layers: [{ id: 'osm', type: 'raster' as const, source: 'osm' }],
}

type MapLike = {
  on: (ev: string, cb: () => void) => void
  remove: () => void
  fitBounds: (bounds: [[number, number], [number, number]], opts: unknown) => void
}

type MarkerLike = {
  setLngLat: (coordinates: [number, number]) => MarkerLike
  addTo: (map: MapLike) => MarkerLike
  remove: () => void
}

function boundsOf(stops: StopCoordinate[]): [[number, number], [number, number]] {
  let minLng = Infinity
  let minLat = Infinity
  let maxLng = -Infinity
  let maxLat = -Infinity
  for (const stop of stops) {
    minLng = Math.min(minLng, stop.lng)
    minLat = Math.min(minLat, stop.lat)
    maxLng = Math.max(maxLng, stop.lng)
    maxLat = Math.max(maxLat, stop.lat)
  }
  return [[minLng, minLat], [maxLng, maxLat]]
}

/** Punktmarker nur für Stopps, deren lat/lng der Tour-GET geliefert hat. */
export function DispositionStopMap({ stops }: { stops: StopCoordinate[] }): JSX.Element | null {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (stops.length === 0) return
    const points = stops
    const container = containerRef.current
    if (!container) return

    let cancelled = false
    let map: MapLike | null = null
    const markers: MarkerLike[] = []

    void import('maplibre-gl')
      .then((ml) => {
        if (cancelled || !containerRef.current) return
        const ML = ml as unknown as {
          Map: new (opts: unknown) => MapLike
          Marker: new (opts: { element: HTMLElement }) => MarkerLike
        }
        map = new ML.Map({
          container,
          style: DISPOSITION_MAP_STYLE,
          center: [points[0].lng, points[0].lat],
          zoom: points.length === 1 ? 12 : 8,
        })
        map.on('load', () => {
          if (cancelled || !map) return
          for (const stop of points) {
            const element = document.createElement('div')
            element.dataset.testid = `dispo-map-marker-${stop.stopId}`
            element.dataset.lat = String(stop.lat)
            element.dataset.lng = String(stop.lng)
            element.title = stop.label
            element.className = 'h-3 w-3 rounded-full border border-background bg-foreground'
            markers.push(new ML.Marker({ element }).setLngLat([stop.lng, stop.lat]).addTo(map))
          }
          if (points.length > 1 && map) {
            map.fitBounds(boundsOf(points), { padding: 40, maxZoom: 12 })
          }
        })
      })
      .catch(() => {
        if (!cancelled) setError('Kartenbibliothek konnte nicht geladen werden.')
      })

    return () => {
      cancelled = true
      for (const marker of markers) marker.remove()
      map?.remove()
    }
  }, [stops])

  if (stops.length === 0) return null

  return (
    <div
      ref={containerRef}
      className="relative mt-2 h-48 overflow-hidden rounded-md border"
      data-testid="dispo-stop-map"
      aria-label="Stopp-Karte"
    >
      {error ? <p className="p-2 text-sm text-status-error" role="alert">{error}</p> : null}
    </div>
  )
}
