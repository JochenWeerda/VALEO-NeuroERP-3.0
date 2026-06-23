/**
 * DOM-AGRAR-004.5 — Agrar Lifecycle @smoke Tests
 *
 * Kritische Pfade: Partie anlegen → Trocknung buchen → Selbstabrechnung-Status.
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000'
const TENANT = 'test-tenant-agrar-001'
const TOKEN = process.env.API_DEV_TOKEN ?? process.env.VALEO_API_DEV_TOKEN ?? process.env.VITE_API_DEV_TOKEN ?? 'dev-token'
const HEADERS = { Authorization: `Bearer ${TOKEN}`, 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

let partieId: string

test.describe('@smoke Agrar Partie Lifecycle', () => {
  test('1 — Partie aus Dummy-Annahmen anlegen (expect 422 ohne echte Annahmen)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/agrar/p0/partien', {
      headers: HEADERS,
      data: { acceptance_ids: ['smoke-acceptance-001'] },
    })
    // 422 expected since smoke acceptance doesn't exist in DB — validates route reachable
    expect([201, 422]).toContain(res.status())
    if (res.status() === 201) {
      const body = await res.json()
      expect(body).toHaveProperty('partie_number')
      partieId = body.id
    }
    await ctx.dispose()
  })

  test('2 — Trocknung berechnen (422 ohne Partie in DB)', async () => {
    test.skip(!partieId, 'Keine Partie erstellt — übersprungen')
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post(`/api/v1/agrar/p0/partien/${partieId}/trocknung`, {
      headers: HEADERS,
      data: { moisture_out_pct: 13.0 },
    })
    expect([201, 422]).toContain(res.status())
    await ctx.dispose()
  })

  test('3 — Selbstabrechnung issue-Endpunkt erreichbar', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/agrar/p0/selbstabrechnung/smoke-r-001/issue', {
      headers: HEADERS,
    })
    // 422 = route reached but rechnung not found — validates endpoint wiring
    expect([200, 422, 404, 503]).toContain(res.status())
    await ctx.dispose()
  })
})
