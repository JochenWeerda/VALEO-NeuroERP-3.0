import { useEffect, useRef, useState } from 'react'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { useMilchviehMap, type CrossSellFilter, type GeoJSONFeatureCollection } from '@/lib/api/milchvieh-crosssell'

/**
 * CRM-Karte Milchvieh-Betriebe: POIs nach Hygiene-Bedarf eingefärbt, Größe nach
 * Herde; Hover („Fly-over") zeigt die Betriebskennzahlen. MapLibre + OSM-Tiles.
 */

type MapMouseEvent = {
  features?: Array<{ geometry: { coordinates: [number, number] }; properties: Record<string, unknown> }>
}
type MapLike = {
  on: (ev: string, layerOrCb: string | (() => void), cb?: (e: MapMouseEvent) => void) => void
  addSource: (id: string, opts: unknown) => void
  addLayer: (opts: unknown) => void
  getSource: (id: string) => { setData: (d: unknown) => void } | undefined
  getCanvas: () => HTMLCanvasElement
  remove: () => void
  fitBounds: (b: [[number, number], [number, number]], o: unknown) => void
}
type PopupLike = {
  setLngLat: (c: [number, number]) => PopupLike
  setHTML: (h: string) => PopupLike
  addTo: (m: MapLike) => PopupLike
  remove: () => void
}

const nf = (n: unknown): string =>
  typeof n === 'number' ? n.toLocaleString('de-DE', { maximumFractionDigits: 0 }) : '–'

const BEDARF_COLOR: Record<string, string> = { hoch: '#dc2626', mittel: '#eab308', niedrig: '#16a34a' }

function popupHtml(p: Record<string, unknown>): string {
  const zz = p.zellzahl_quelle === 'dev_synthetik' ? `${nf(p.zellzahl_tsd_ml)}~` : nf(p.zellzahl_tsd_ml)
  return `
    <div style="font:12px system-ui;min-width:200px">
      <div style="font-weight:600;margin-bottom:2px">${String(p.name ?? p.kunden_nr)}</div>
      <div style="color:#64748b;margin-bottom:6px">${String(p.plz ?? '')} ${String(p.ort ?? '')}</div>
      <table style="border-collapse:collapse">
        <tr><td style="color:#64748b;padding-right:8px">Kühe</td><td style="text-align:right">${nf(p.herd_size_kuehe)}</td></tr>
        <tr><td style="color:#64748b;padding-right:8px">Milch l/J</td><td style="text-align:right">${nf(p.milchmenge_l_jahr)}</td></tr>
        <tr><td style="color:#64748b;padding-right:8px">ECM kg</td><td style="text-align:right">${nf(p.ecm_kg)}</td></tr>
        <tr><td style="color:#64748b;padding-right:8px">Zellzahl</td><td style="text-align:right">${zz}</td></tr>
        <tr><td style="color:#64748b;padding-right:8px">Hygiene</td><td style="text-align:right;font-weight:600;color:${BEDARF_COLOR[String(p.hygiene_bedarf)] ?? '#334155'}">${String(p.hygiene_bedarf)}</td></tr>
        <tr><td style="color:#64748b;padding-right:8px">Kraftfutter t/J</td><td style="text-align:right">${nf(p.kraftfutter_t_jahr_min)}–${nf(p.kraftfutter_t_jahr_max)}</td></tr>
        <tr><td style="color:#64748b;padding-right:8px">Cross-Sell €</td><td style="text-align:right;font-weight:600">${nf(p.crosssell_ziel_eur)}</td></tr>
      </table>
    </div>`
}

function bbox(fc: GeoJSONFeatureCollection): [[number, number], [number, number]] | null {
  let minLng = Infinity, minLat = Infinity, maxLng = -Infinity, maxLat = -Infinity
  for (const f of fc.features) {
    const [lng, lat] = f.geometry.coordinates
    minLng = Math.min(minLng, lng); minLat = Math.min(minLat, lat)
    maxLng = Math.max(maxLng, lng); maxLat = Math.max(maxLat, lat)
  }
  return isFinite(minLng) ? [[minLng, minLat], [maxLng, maxLat]] : null
}

export default function MilchviehKartePage(): JSX.Element {
  const [filter, setFilter] = useState<CrossSellFilter>({})
  const mapData = useMilchviehMap(filter)
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLike | null>(null)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return
    let map: MapLike | null = null
    void import('maplibre-gl')
      .then((ml) => {
        const ML = (ml.default ?? ml) as unknown as {
          Map: new (o: unknown) => MapLike
          Popup: new (o: unknown) => PopupLike
        }
        if (!mapContainer.current) return
        map = new ML.Map({
          container: mapContainer.current,
          style: {
            version: 8,
            sources: { osm: { type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, attribution: '© OpenStreetMap' } },
            layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
          },
          center: [7.6, 53.5],
          zoom: 8,
        })
        mapRef.current = map
        const popup = new ML.Popup({ closeButton: false, closeOnClick: false })
        map.on('load', () => {
          const m = mapRef.current as MapLike
          m.addSource('farms', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
          m.addLayer({
            id: 'farms',
            type: 'circle',
            source: 'farms',
            paint: {
              'circle-color': ['match', ['get', 'hygiene_bedarf'], 'hoch', '#dc2626', 'mittel', '#eab308', 'niedrig', '#16a34a', '#94a3b8'],
              'circle-radius': ['interpolate', ['linear'], ['get', 'herd_size_kuehe'], 30, 5, 300, 15],
              'circle-stroke-width': 1,
              'circle-stroke-color': '#ffffff',
              'circle-opacity': 0.85,
            },
          })
          m.on('mousemove', 'farms', (e: MapMouseEvent) => {
            const f = e.features?.[0]
            if (!f) return
            m.getCanvas().style.cursor = 'pointer'
            popup.setLngLat(f.geometry.coordinates).setHTML(popupHtml(f.properties)).addTo(m)
          })
          m.on('mouseleave', 'farms', () => {
            m.getCanvas().style.cursor = ''
            popup.remove()
          })
          setReady(true)
        })
      })
      .catch(() => setError('Kartenbibliothek konnte nicht geladen werden.'))
    return () => {
      if (map) map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!ready || !mapRef.current || !mapData.data) return
    const src = mapRef.current.getSource('farms')
    if (src) {
      src.setData(mapData.data)
      const b = bbox(mapData.data)
      if (b) mapRef.current.fitBounds(b, { padding: 50, maxZoom: 12 })
    }
  }, [ready, mapData.data])

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col p-4">
      <div className="mb-3">
        <h1 className="text-2xl font-semibold">Milchvieh-Betriebe (Karte)</h1>
        <p className="text-sm text-muted-foreground">
          POIs nach Hygiene-Bedarf eingefärbt, Größe nach Herde. Mauszeiger über einen Betrieb zeigt die Kennzahlen.
        </p>
      </div>

      <Card className="mb-3">
        <CardContent className="flex flex-wrap items-end gap-3 p-3">
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Hygiene-Bedarf</span>
            <NativeSelect value={filter.hygiene_bedarf ?? ''} onValueChange={(v) => setFilter((f) => ({ ...f, hygiene_bedarf: v || undefined }))} className="w-40">
              <option value="">Alle</option>
              <option value="hoch">hoch</option>
              <option value="mittel">mittel</option>
              <option value="niedrig">niedrig</option>
            </NativeSelect>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Mindest-Herde</span>
            <Input type="number" min={0} className="w-32" value={filter.min_kuehe ?? ''}
              onChange={(e) => setFilter((f) => ({ ...f, min_kuehe: e.target.value ? Number(e.target.value) : undefined }))} />
          </label>
          <div className="ml-auto flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#16a34a' }} /> niedrig</span>
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#eab308' }} /> mittel</span>
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#dc2626' }} /> hoch</span>
            <span className="text-muted-foreground">{mapData.data ? `${mapData.data.features.length} Betriebe` : ''}</span>
          </div>
        </CardContent>
      </Card>

      {error ? (
        <div className="flex flex-1 items-center justify-center rounded-md border text-sm text-destructive">{error}</div>
      ) : (
        <div ref={mapContainer} className="min-h-[50vh] flex-1 overflow-hidden rounded-md border" />
      )}
    </div>
  )
}
