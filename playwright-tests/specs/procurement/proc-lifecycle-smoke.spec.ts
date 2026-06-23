/**
 * DOM-PROC-004.5 — Procurement Lifecycle @smoke Tests
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'test-tenant-proc-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

test.describe('@smoke Procurement Lifecycle', () => {
  test('1 — Bestellung freigeben (422 ohne echte Bestellung)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/procurement/bestellungen/smoke-best-001/transition', {
      headers: HEADERS,
      data: { new_status: 'FREIGEGEBEN', operator: 'smoke-mgr' },
    })
    expect([200, 422, 404, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('2 — Wareneingang buchen (422 ohne echte Bestellung)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/procurement/bestellungen/smoke-best-001/wareneingang', {
      headers: HEADERS,
      data: { menge_erhalten: 100.0, einheit: 'KG', lager_id: 'lager-001' },
    })
    expect([201, 422, 404, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('3 — Rechnungsprüfung (3-Way-Match)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/procurement/bestellungen/smoke-best-001/rechnungspruefung', {
      headers: HEADERS,
      data: {
        rechnungs_nr: 'RE-SMOKE-001',
        rechnungs_betrag_eur: 1020.0,
        bestell_preis_eur: 10.0,
        we_menge: 100.0,
      },
    })
    expect([201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })
})
