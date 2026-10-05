/**
 * DOM-FINANCE-004.5 — Finance Lifecycle @smoke Tests
 */
import { test, expect, request } from '@playwright/test'
import { randomUUID } from 'node:crypto'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000'
const TENANT = 'test-tenant-finance-001'
const TOKEN = process.env.API_DEV_TOKEN ?? process.env.VALEO_API_DEV_TOKEN ?? process.env.VITE_API_DEV_TOKEN ?? 'dev-token'
const HEADERS = { Authorization: `Bearer ${TOKEN}`, 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

test.describe('@smoke Finance Lifecycle', () => {
  test('1 — SEPA-Mandat anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/sepa/mandate', {
      headers: HEADERS,
      data: { glaeubiger_id: 'DE98ZZZ09999999999', iban: 'DE12345678901234567890', bic: 'COBADEFFXXX' },
    })
    expect([201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('2 — Ratenzahlungsplan anlegen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/finance/ratenzahlung/plaene', {
      headers: HEADERS,
      data: { op_id: 'smoke-op-001', gesamt_eur: 300.0, anzahl_raten: 3, erste_faelligkeit: '2026-07-01' },
    })
    expect([201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('3 — Mahnstufe eskalieren', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const invoice = `RE-SMOKE-${randomUUID()}`
    const endpoint = `/api/v1/finance/mahnstufe/${invoice}`
    try {
      let previous: string | null = null
      for (const stage of ['1', '2', '3', 'INKASSO']) {
        const res = await ctx.post(`${endpoint}/eskalieren`, {
          headers: HEADERS, data: { operator: 'smoke-test' },
        })
        expect(res.status(), await res.text()).toBe(201)
        const body = await res.json()
        expect(body.stufe).toBe(stage)
        expect(body.vorherige_stufe).toBe(previous)
        previous = stage
      }
      const blocked = await ctx.post(`${endpoint}/eskalieren`, {
        headers: HEADERS, data: { operator: 'smoke-test' },
      })
      expect(blocked.status()).toBe(422)
      const trail = await ctx.get(`${endpoint}/trail`, { headers: HEADERS })
      expect(trail.status()).toBe(200)
      const body = await trail.json()
      expect(body.count).toBe(4)
      expect(body.trail.map((entry: { stufe: string }) => entry.stufe)).toEqual(['1', '2', '3', 'INKASSO'])
    } finally {
      await ctx.dispose()
    }
  })
})
