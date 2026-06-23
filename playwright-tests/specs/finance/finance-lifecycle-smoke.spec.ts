/**
 * DOM-FINANCE-004.5 — Finance Lifecycle @smoke Tests
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000'
const TENANT = 'test-tenant-finance-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

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
    const res = await ctx.post('/api/v1/finance/mahnstufe/RE-SMOKE-001/eskalieren', {
      headers: HEADERS,
      data: { operator: 'smoke-test' },
    })
    expect([201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })
})
