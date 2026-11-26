import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import MilchviehKartePage from '@/pages/agrar/milchvieh-karte-legacy'

const mapApi = vi.hoisted(() => {
  const source = { setData: vi.fn() }
  const canvas = { style: { cursor: '' } }
  const handlers: Record<string, Array<(...args: unknown[]) => void>> = {}
  const map = {
    on: vi.fn((ev: string, layerOrCb: string | (() => void), cb?: (...args: unknown[]) => void) => {
      const key = typeof layerOrCb === 'string' ? `${ev}:${layerOrCb}` : ev
      const fn = typeof layerOrCb === 'function' ? layerOrCb : cb
      if (fn) {
        handlers[key] = handlers[key] ?? []
        handlers[key].push(fn)
      }
    }),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    getSource: vi.fn(() => source),
    getCanvas: vi.fn(() => canvas),
    remove: vi.fn(),
    fitBounds: vi.fn(),
  }
  return {
    handlers,
    source,
    canvas,
    map,
    Map: vi.fn(function Map() { return map }),
    Popup: vi.fn(function Popup() {
      return {
        setLngLat: vi.fn().mockReturnThis(),
        setHTML: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
      }
    }),
  }
})

vi.mock('maplibre-gl', () => ({
  default: { Map: mapApi.Map, Popup: mapApi.Popup },
  Map: mapApi.Map,
  Popup: mapApi.Popup,
}))

vi.mock('@/lib/api/milchvieh-crosssell', () => ({
  useMilchviehMap: () => ({
    data: {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [7.5, 53.4] },
        properties: {
          name: 'Hof Nord',
          kunden_nr: 'K-1',
          plz: '26789',
          ort: 'Leer',
          herd_size_kuehe: 120,
          milchmenge_l_jahr: 900000,
          ecm_kg: 8500,
          zellzahl_tsd_ml: 180,
          zellzahl_quelle: 'lab',
          hygiene_bedarf: 'hoch',
          kraftfutter_t_jahr_min: 10,
          kraftfutter_t_jahr_max: 20,
          crosssell_ziel_eur: 12000,
        },
      }],
    },
  }),
}))

describe('MilchviehKartePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    Object.keys(mapApi.handlers).forEach((k) => { delete mapApi.handlers[k] })
    Object.defineProperty(window, 'getComputedStyle', {
      configurable: true,
      value: () => ({ getPropertyValue: () => '0 70% 45%' }),
    })
  })
  afterEach(cleanup)

  it('lädt MapLibre, setzt Farm-Source und reagiert auf Filter', async () => {
    render(<MilchviehKartePage />)
    expect(screen.getByRole('heading', { name: 'Milchvieh-Betriebe (Karte)' })).toBeTruthy()

    await waitFor(() => expect(mapApi.Map).toHaveBeenCalled())
    const load = mapApi.handlers.load?.[0]
    expect(load).toBeTypeOf('function')
    load?.()

    await waitFor(() => expect(mapApi.map.addSource).toHaveBeenCalledWith('farms', expect.any(Object)))
    await waitFor(() => expect(mapApi.source.setData).toHaveBeenCalled())
    expect(mapApi.map.fitBounds).toHaveBeenCalled()

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'hoch' } })

    const move = mapApi.handlers['mousemove:farms']?.[0]
    move?.({
      features: [{
        geometry: { coordinates: [7.5, 53.4] },
        properties: {
          name: 'Hof Nord',
          hygiene_bedarf: 'hoch',
          herd_size_kuehe: 120,
          zellzahl_tsd_ml: 180,
          zellzahl_quelle: 'dev_synthetik',
        },
      }],
    })
    expect(mapApi.canvas.style.cursor).toBe('pointer')
    mapApi.handlers['mouseleave:farms']?.[0]?.()
    expect(mapApi.canvas.style.cursor).toBe('')
  })
})
