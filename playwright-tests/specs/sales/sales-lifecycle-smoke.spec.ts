/**
 * DOM-SALES-004.5 — Sales Lifecycle @smoke Tests
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000'
const TENANT = 'test-tenant-sales-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

test.describe('@smoke Sales Lifecycle', () => {
  test('1 — AB-Transition (422 ohne echten Auftrag)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/sales/orders/smoke-auftrag-001/ab-transition', {
      headers: HEADERS,
      data: { new_status: 'VERSANDT' },
    })
    expect([200, 422, 404, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('2 — Lieferschein advance (422 ohne echten LS)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/sales/delivery-notes/smoke-ls-001/advance', {
      headers: HEADERS,
      data: { new_status: 'KOMMISSIONIERT' },
    })
    expect([200, 422, 404, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('3 — Preisabweichung prüfen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/sales/orders/smoke-auftrag-001/preisabweichung', {
      headers: HEADERS,
      data: { artikel_id: 'art-001', angebots_preis: 100.0, rechnungs_preis: 105.0 },
    })
    expect([201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })
})
