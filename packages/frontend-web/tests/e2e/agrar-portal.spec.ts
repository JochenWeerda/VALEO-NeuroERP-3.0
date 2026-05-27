/**
 * E2E: Agrar Portal — Annahme, Qualitätscheck, Erntekampagne
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Agrar Portal', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Annahme-Übersicht lädt', async ({ page }) => {
    await page.goto('/annahme')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Qualitäts-Check lädt', async ({ page }) => {
    await page.goto('/annahme/qualitaets-check')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Erntekampagnen-Übersicht lädt', async ({ page }) => {
    await page.goto('/agrar/erntekampagnen')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Schlagkartei lädt', async ({ page }) => {
    await page.goto('/agrar/feldbuch/schlagkartei')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Agrar Schläge abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/agrar/schlaege?limit=5')
    expect([200, 401, 404]).toContain(resp.status())
  })
})
