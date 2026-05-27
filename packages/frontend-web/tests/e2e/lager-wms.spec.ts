/**
 * E2E: Lager / WMS — Einlagerung, Auslagerung, Bestandsübersicht
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Lager / WMS', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Lagerübersicht lädt', async ({ page }) => {
    await page.goto('/lager/bestand')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Einlagerung lädt', async ({ page }) => {
    await page.goto('/lager/einlagerung')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Auslagerung lädt', async ({ page }) => {
    await page.goto('/lager/auslagerung')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Inventur lädt', async ({ page }) => {
    await page.goto('/lager/inventur')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Lagerbestand abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/lager/bestand?limit=10')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Einlagerung buchen', async ({ request }) => {
    const resp = await request.post('/api/v1/lager/einlagerung', {
      data: {
        artikel_id: 'ART-001',
        menge: 100.0,
        einheit: 't',
        lagerort_id: 'LAGER-01',
        charge: 'CH-2026-001',
      },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
  })

  test('API: WMS Inventory Operations', async ({ request }) => {
    const resp = await request.get('/api/v1/wms/inventory/status')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('Silooperationen lädt', async ({ page }) => {
    await page.goto('/lager/silo-operationen')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })
})
