/**
 * DOM-LOG-004.5 — Logistik Lifecycle @smoke Tests
 *
 * Kritische Pfade: Tour anlegen → Stopp-Status-Update → Disposition-Check.
 * Setzt ein laufendes Backend voraus (BASE_URL oder PLAYWRIGHT_BASE_URL).
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'test-tenant-log-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

let tourId: string
let stopId: string

test.describe('@smoke Logistik Lifecycle', () => {
  test('1 — Tour anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/logistik/tours', {
      headers: HEADERS,
      data: {
        date: new Date().toISOString(),
        vehicle_id: 'vehicle-smoke-001',
        driver_id: 'driver-smoke-001',
        status: 'GEPLANT',
        stops: [
          {
            address: 'Teststraße 1, 12345 Musterdorf',
            lat: 51.5,
            lng: 9.9,
            stop_order: 0,
            planned_arrival: new Date(Date.now() + 3600_000).toISOString(),
          },
        ],
      },
    })
    expect(res.status()).toBe(201)
    const body = await res.json()
    expect(body).toHaveProperty('id')
    tourId = body.id
    if (body.stops && body.stops.length > 0) {
      stopId = body.stops[0].id
    }
    await ctx.dispose()
  })

  test('2 — Stopp-Status auf GELIEFERT setzen', async () => {
    test.skip(!tourId, 'Tour-ID fehlt — Test 1 fehlgeschlagen')
    test.skip(!stopId, 'Stop-ID fehlt — kein Stopp in Tour')
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.patch(`/api/v1/logistik/tours/${tourId}/stops/${stopId}`, {
      headers: HEADERS,
      data: { status: 'GELIEFERT', actual_arrival: new Date().toISOString() },
    })
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(body.status).toBe('GELIEFERT')
    await ctx.dispose()
  })

  test('3 — Disposition-Check zurückgeben (NO_WEIGHT_DATA erlaubt)', async () => {
    test.skip(!tourId, 'Tour-ID fehlt — Test 1 fehlgeschlagen')
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post(`/api/v1/logistik/tours/${tourId}/disposition-check`, {
      headers: HEADERS,
      data: { capacity_kg: 20000 },
    })
    // 200 = OK or NO_WEIGHT_DATA; 422 = OVERLOADED
    expect([200, 422]).toContain(res.status())
    const body = await res.json()
    if (res.status() === 200) {
      expect(body).toHaveProperty('result')
      expect(['OK', 'NO_WEIGHT_DATA']).toContain(body.result)
    }
    await ctx.dispose()
  })
})
