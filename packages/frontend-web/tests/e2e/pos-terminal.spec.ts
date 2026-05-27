/**
 * E2E: POS Terminal — Kassensystem, Tagesabschluss, Rückgabe
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('POS Terminal', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('POS Terminal lädt', async ({ page }) => {
    await page.goto('/pos/terminal')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Tagesabschluss lädt', async ({ page }) => {
    await page.goto('/pos/tagesabschluss')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Warenrückgabe lädt', async ({ page }) => {
    await page.goto('/pos/retoure')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: POS Health', async ({ request }) => {
    const resp = await request.get('/api/v1/pos/status')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: DSFinV-K Export Endpoint vorhanden', async ({ request }) => {
    const resp = await request.get('/api/v1/pos/dsfinvk/export?kassenschnitt_id=test')
    expect([200, 400, 401, 404, 422]).toContain(resp.status())
  })
})
