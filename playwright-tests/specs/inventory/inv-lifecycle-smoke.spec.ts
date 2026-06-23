/**
 * DOM-INV-004.5 — Inventory Lifecycle @smoke Tests
 *
 * Kritische Pfade: Lot anlegen → Lot auflisten → Lot verbrauchen.
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'test-tenant-inv-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

let lotId: string

test.describe('@smoke Inventory Lot Lifecycle', () => {
  test('1 — Inventory-Lot anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/lager/lots', {
      headers: HEADERS,
      data: {
        article_id: 'article-smoke-inv-001',
        warehouse_id: 'warehouse-smoke-001',
        lot_number: `SMOKE-LOT-${Date.now()}`,
        initial_qty: 1000.0,
        unit: 'kg',
        mhd: new Date(Date.now() + 30 * 86400_000).toISOString().split('T')[0],
      },
    })
    expect(res.status()).toBe(201)
    const body = await res.json()
    expect(body).toHaveProperty('id')
    expect(body.current_qty).toBe(1000)
    expect(body.status).toBe('AKTIV')
    lotId = body.id
    await ctx.dispose()
  })

  test('2 — Lot-Liste FEFO abfragen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/lager/lots?article_id=article-smoke-inv-001', {
      headers: HEADERS,
    })
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(Array.isArray(body)).toBe(true)
    await ctx.dispose()
  })

  test('3 — Lot verbrauchen (500 kg)', async () => {
    test.skip(!lotId, 'Lot-ID fehlt — Test 1 fehlgeschlagen')
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post(`/api/v1/lager/lots/${lotId}/consume`, {
      headers: HEADERS,
      data: { quantity: 500.0 },
    })
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(body.remaining_qty).toBe(500)
    expect(body.status).toBe('AKTIV')
    await ctx.dispose()
  })
})
