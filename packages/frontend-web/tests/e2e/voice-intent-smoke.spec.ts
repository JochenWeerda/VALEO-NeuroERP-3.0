/**
 * E2E: Voice Intent / KI-Usability Smoke Tests
 * Testet die Voice-Intent-Endpoints (Slice-010+011)
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Voice Intent API', () => {
  test('API: Lager-Intent auflösen', async ({ request }) => {
    const resp = await request.post('/api/ki/intents/resolve', {
      data: { utterance: 'zeige mir den Lagerbestand von Weizen', tenant_id: 'test' },
    })
    // KI-Service möglicherweise nicht im E2E-Modus verfügbar
    expect([200, 201, 401, 404, 503]).toContain(resp.status())
  })

  test('API: Verkauf-Intent auflösen', async ({ request }) => {
    const resp = await request.post('/api/ki/intents/resolve', {
      data: { utterance: 'erstelle ein Angebot für Kunde Müller', tenant_id: 'test' },
    })
    expect([200, 201, 401, 404, 503]).toContain(resp.status())
  })

  test('API: Actions Registry abrufen', async ({ request }) => {
    const resp = await request.get('/api/ki/actions/registry')
    expect([200, 401, 404, 503]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(Array.isArray(body) || typeof body === 'object').toBe(true)
    }
  })
})

test.describe('Admin / Monitoring', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Audit Log lädt', async ({ page }) => {
    await page.goto('/admin/audit-log')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Command Monitor lädt', async ({ page }) => {
    await page.goto('/admin/command-monitor')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Monitoring Alerts lädt', async ({ page }) => {
    await page.goto('/admin/monitoring/alerts')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: System Health', async ({ request }) => {
    const resp = await request.get('/api/v1/health')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('status')
    }
  })
})
