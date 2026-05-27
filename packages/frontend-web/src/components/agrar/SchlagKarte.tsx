/**
 * SchlagKarte — MapLibre-GL Karte mit GeoJSON-Polygonen der Ackerschläge.
 *
 * Lädt alle Schlag-Polygone aus GET /api/v1/agrar/feldbuch/schlaege/geojson/all
 * und rendert sie als farbige Flächen auf einer OpenStreetMap-Basiskarte.
 *
 * Anforderungen: maplibre-gl (npm install maplibre-gl)
 */
import { useEffect, useRef, useState } from 'react'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useSchlagGeojsonAll } from '@/lib/api/agrar'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Map } from 'lucide-react'

const GERMANY_CENTER: [number, number] = [10.4515, 51.1657]
const DEFAULT_ZOOM = 6

interface SchlagKarteProps {
  height?: string
  className?: string
}

export function SchlagKarte({ height = '480px', className = '' }: SchlagKarteProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<unknown>(null)
  const [mapReady, setMapReady] = useState(false)
  const [mapError, setMapError] = useState<string | null>(null)

  const { data: featureCollection, isLoading } = useSchlagGeojsonAll()

  // Init map once container is mounted
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return

    let map: {
      on: (ev: string, cb: () => void) => void
      addSource: (id: string, opts: unknown) => void
      addLayer: (opts: unknown) => void
      getSource: (id: string) => { setData: (d: unknown) => void } | undefined
      remove: () => void
      fitBounds: (bounds: [[number, number], [number, number]], opts: unknown) => void
      flyTo: (opts: unknown) => void
    } | null = null

    import('maplibre-gl')
      .then((ml) => {
        const MapLibreGL = (ml.default ?? ml) as unknown as { Map: new (opts: unknown) => NonNullable<typeof map> }
        if (!mapContainer.current) return
        map = new MapLibreGL.Map({
          container: mapContainer.current,
          style: {
            version: 8,
            sources: {
              osm: {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors',
              },
            },
            layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
          },
          center: GERMANY_CENTER,
          zoom: DEFAULT_ZOOM,
        })

        mapRef.current = map

        map.on('load', () => {
          // Non-null assertion is safe: map is assigned and not null at this point
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          map!.addSource('schlaege', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: [] },
          })
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          map!.addLayer({
            id: 'schlaege-fill',
            type: 'fill',
            source: 'schlaege',
            paint: {
              'fill-color': '#22c55e',
              'fill-opacity': 0.35,
            },
          })
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          map!.addLayer({
            id: 'schlaege-outline',
            type: 'line',
            source: 'schlaege',
            paint: {
              'line-color': '#16a34a',
              'line-width': 2,
            },
          })
          setMapReady(true)
        })
      })
      .catch((err) => {
        console.error('MapLibre load error', err)
        setMapError('Kartenbibliothek konnte nicht geladen werden.')
      })

    return () => {
      if (map) map.remove()
      mapRef.current = null
    }
  }, [])

  // Update GeoJSON data when featureCollection changes
  useEffect(() => {
    if (!mapReady || !mapRef.current || !featureCollection) return
    const m = mapRef.current as { getSource: (id: string) => { setData: (d: unknown) => void } | undefined; fitBounds: (bounds: [[number, number], [number, number]], opts: unknown) => void }
    const src = m.getSource('schlaege')
    if (src) {
      src.setData(featureCollection)
      // Auto-fit bounds if there are features
      const features = (featureCollection as { features?: { geometry?: { coordinates?: number[][][] } }[] }).features ?? []
      if (features.length > 0) {
        let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity
        for (const feat of features) {
          const coords = feat.geometry?.coordinates?.[0] ?? []
          for (const [lng, lat] of coords) {
            if (lng < minLng) minLng = lng
            if (lat < minLat) minLat = lat
            if (lng > maxLng) maxLng = lng
            if (lat > maxLat) maxLat = lat
          }
        }
        if (isFinite(minLng)) {
          m.fitBounds([[minLng, minLat], [maxLng, maxLat]], { padding: 60, maxZoom: 15 })
        }
      }
    }
  }, [mapReady, featureCollection])

  if (mapError) {
    return (
      <Alert>
        <Map className="h-4 w-4" />
        <AlertDescription>{mapError}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className={`relative rounded-lg overflow-hidden border ${className}`} style={{ height }}>
      {isLoading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/80">
          <Skeleton className="h-full w-full" />
        </div>
      )}
      <div ref={mapContainer} className="h-full w-full" />
      {!mapReady && !mapError && (
        <div className="absolute inset-0 flex items-center justify-center bg-green-50 dark:bg-green-950/30">
          <div className="text-center space-y-2">
            <Map className="h-10 w-10 mx-auto text-green-600 animate-pulse" />
            <p className="text-sm text-muted-foreground">Karte wird geladen…</p>
          </div>
        </div>
      )}
    </div>
  )
}
