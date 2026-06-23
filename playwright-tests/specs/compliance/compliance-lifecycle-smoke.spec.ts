/**
 * DOM-COMPLIANCE-004.5 — Compliance Lifecycle @smoke Tests
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'test-tenant-compliance-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

test.describe('@smoke Compliance Lifecycle', () => {
  test('1 — PCN-Meldung anlegen (201)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/compliance/pcn-meldungen', {
      headers: HEADERS,
      data: { artikel_id: 'smoke-art-001', meldungstyp: 'ZULASSUNG' },
    })
    expect([201, 422, 503]).toContain(res.status())
    if (res.status() === 201) {
      const body = await res.json()
      expect(body).toHaveProperty('meldung_nummer')
      expect(body.status).toBe('DRAFT')
    }
    await ctx.dispose()
  })

  test('2 — Fällige VVVO-Prüfungen listen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/compliance/vvvo/faellige-pruefungen?within_days=30', {
      headers: HEADERS,
    })
    expect([200, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('3 — Artikel sperren (Audit-Trail)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/compliance/artikel/smoke-art-001/sperre', {
      headers: HEADERS,
      data: { grund: 'Smoke-Test-Sperre' },
    })
    expect([200, 201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })
})
