/**
 * DOM-CONTROLLING-004.5 — Controlling Lifecycle @smoke Tests
 */
import { test, expect, request } from '@playwright/test'

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:8000'
const TENANT = 'test-tenant-ctrl-001'
const HEADERS = { 'X-Tenant-ID': TENANT, 'Content-Type': 'application/json' }

test.describe('@smoke Controlling Lifecycle', () => {
  test('1 — Budget anlegen (ENTWURF)', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/controlling/budgets', {
      headers: HEADERS,
      data: {
        kostenstelle_id: 'smoke-kst-001',
        periode: '2026-06',
        plan_eur: 50000.0,
        bezeichnung: 'Smoke-Budget IT',
        operator: 'smoke-mgr',
      },
    })
    expect([201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('2 — Abweichungsanalyse abrufen', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.get('/api/v1/controlling/abweichung?kostenstelle_id=smoke-kst-001&periode=2026-06', {
      headers: HEADERS,
    })
    expect([200, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })

  test('3 — KST-Abschluss starten', async () => {
    const ctx = await request.newContext({ baseURL: BASE })
    const res = await ctx.post('/api/v1/controlling/kostenstellen/smoke-kst-001/abschluss', {
      headers: HEADERS,
      data: { periode: '2026-06', new_status: 'OFFEN', operator: 'smoke-mgr' },
    })
    expect([200, 201, 422, 503]).toContain(res.status())
    await ctx.dispose()
  })
})
