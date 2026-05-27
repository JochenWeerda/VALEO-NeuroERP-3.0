/**
 * E2E: Settings / Admin — Nummernkreise, Benutzer, Rollen, Integrationen
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Settings & Admin', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Nummernkreise lädt', async ({ page }) => {
    await page.goto('/admin/nummernkreise')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Benutzerverwaltung lädt', async ({ page }) => {
    await page.goto('/admin/benutzer-liste')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Rollenverwaltung lädt', async ({ page }) => {
    await page.goto('/admin/rollen-verwaltung')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Integrationen / DMS lädt', async ({ page }) => {
    await page.goto('/admin/setup/dms-integration')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Admin Tenants', async ({ request }) => {
    const resp = await request.get('/api/v1/admin/tenants')
    expect([200, 401, 403, 404]).toContain(resp.status())
  })
})
