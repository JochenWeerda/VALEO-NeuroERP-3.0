import { useEffect, useRef, useState } from 'react'
import 'maplibre-gl/dist/maplibre-gl.css'
import { Card, CardContent } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { useKundenKarte, type KundenGeoJSON } from '@/lib/api/kunden-karte'

/**
 * CRM-Kundenkarte: alle Kunden als POIs, eingefärbt nach Typ; Hover („Fly-over")
 * zeigt die Stammdaten. MapLibre + OSM-Tiles (kein API-Key).
 */

type MapMouseEvent = { features?: Array<{ geometry: { coordinates: [number, number] }; properties: Record<string, unknown> }> }
type MapLike = {
  on: (ev: string, layerOrCb: string | (() => void), cb?: (e: MapMouseEvent) => void) => void
  addSource: (id: string, opts: unknown) => void
  addLayer: (opts: unknown) => void
  getSource: (id: string) => { setData: (d: unknown) => void } | undefined
  getCanvas: () => HTMLCanvasElement
  remove: () => void
  fitBounds: (b: [[number, number], [number, number]], o: unknown) => void
}
type PopupLike = { setLngLat: (c: [number, number]) => PopupLike; setHTML: (h: string) => PopupLike; addTo: (m: MapLike) => PopupLike; remove: () => void }

const TYP_COLOR: Record<string, string> = { gap: '#16a34a', milchvieh: '#0ea5e9', lead: '#8b5cf6', stamm: '#64748b' }
const TYP_LABEL: Record<string, string> = { gap: 'Förderempfänger', milchvieh: 'Milchvieh', lead: 'konv. Lead', stamm: 'Stammkunde' }

function popupHtml(p: Record<string, unknown>): string {
  const typ = String(p.typ)
  return `
    <div style="font:12px system-ui;min-width:180px">
      <div style="font-weight:600">${String(p.name ?? p.kunden_nr)}</div>
      <div style="color:#64748b;margin-bottom:4px">${String(p.plz ?? '')} ${String(p.ort ?? '')}</div>
      <div><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${TYP_COLOR[typ] ?? '#64748b'};margin-right:5px"></span>${TYP_LABEL[typ] ?? typ}${p.verbrueckt ? ' · verbrückt' : ''}</div>
      <div style="color:#94a3b8;font-size:11px;margin-top:2px">${String(p.kunden_nr)}</div>
    </div>`
}

function bbox(fc: KundenGeoJSON): [[number, number], [number, number]] | null {
  let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity
  for (const f of fc.features) {
    const [lng, lat] = f.geometry.coordinates
    a = Math.min(a, lng); b = Math.min(b, lat); c = Math.max(c, lng); d = Math.max(d, lat)
  }
  return isFinite(a) ? [[a, b], [c, d]] : null
}

export default function KundenKartePage(): JSX.Element {
  const [typ, setTyp] = useState<string>('')
  const data = useKundenKarte(typ || undefined)
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLike | null>(null)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return
    let map: MapLike | null = null
    void import('maplibre-gl').then((ml) => {
      const ML = (ml.default ?? ml) as unknown as { Map: new (o: unknown) => MapLike; Popup: new (o: unknown) => PopupLike }
      if (!mapContainer.current) return
      map = new ML.Map({
        container: mapContainer.current,
        style: { version: 8, sources: { osm: { type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, attribution: '© OpenStreetMap' } }, layers: [{ id: 'osm', type: 'raster', source: 'osm' }] },
        center: [9.5, 51.5], zoom: 5.5,
      })
      mapRef.current = map
      const popup = new ML.Popup({ closeButton: false, closeOnClick: false })
      map.on('load', () => {
        const m = mapRef.current as MapLike
        if (m.getSource('kunden')) { setReady(true); return } // StrictMode-Doppel-Init abfangen
        m.addSource('kunden', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
        m.addLayer({
          id: 'kunden', type: 'circle', source: 'kunden',
          paint: {
            'circle-color': ['match', ['get', 'typ'], 'gap', '#16a34a', 'milchvieh', '#0ea5e9', 'lead', '#8b5cf6', '#64748b'],
            'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 3, 11, 8],
            'circle-stroke-width': 1, 'circle-stroke-color': '#ffffff', 'circle-opacity': 0.85,
          },
        })
        m.on('mousemove', 'kunden', (e: MapMouseEvent) => {
          const f = e.features?.[0]; if (!f) return
          m.getCanvas().style.cursor = 'pointer'
          popup.setLngLat(f.geometry.coordinates).setHTML(popupHtml(f.properties)).addTo(m)
        })
        m.on('mouseleave', 'kunden', () => { m.getCanvas().style.cursor = ''; popup.remove() })
        setReady(true)
      })
    }).catch(() => setError('Kartenbibliothek konnte nicht geladen werden.'))
    return () => { if (map) map.remove(); mapRef.current = null }
  }, [])

  useEffect(() => {
    if (!ready || !mapRef.current || !data.data) return
    const src = mapRef.current.getSource('kunden')
    if (src) {
      src.setData(data.data)
      const bb = bbox(data.data)
      if (bb) mapRef.current.fitBounds(bb, { padding: 50, maxZoom: 12 })
    }
  }, [ready, data.data])

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col p-4">
      <div className="mb-3">
        <h1 className="text-2xl font-semibold">Kundenkarte</h1>
        <p className="text-sm text-muted-foreground">Alle Kunden als POIs, eingefärbt nach Typ. Mauszeiger über einen Kunden zeigt die Stammdaten.</p>
      </div>
      <Card className="mb-3">
        <CardContent className="flex flex-wrap items-center gap-3 p-3">
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Typ</span>
            <NativeSelect value={typ} onValueChange={setTyp} className="w-48">
              <option value="">Alle</option>
              <option value="gap">Förderempfänger (GAP)</option>
              <option value="milchvieh">Milchvieh</option>
              <option value="lead">Konvertierte Leads</option>
              <option value="stamm">Stammkunden</option>
            </NativeSelect>
          </label>
          <div className="ml-auto flex flex-wrap items-center gap-4 text-xs">
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#16a34a' }} /> Förderempfänger</span>
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#0ea5e9' }} /> Milchvieh</span>
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#8b5cf6' }} /> konv. Lead</span>
            <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-full" style={{ background: '#64748b' }} /> Stammkunde</span>
            <span className="text-muted-foreground">{data.data ? `${data.data.features.length} Kunden` : ''}</span>
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
