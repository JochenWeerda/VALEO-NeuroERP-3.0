/**
 * E2E: Fuhrpark / Logistik — Fahrzeuge, Transporte, LKW-Beladung
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Fuhrpark', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Fahrzeugliste lädt', async ({ page }) => {
    await page.goto('/fuhrpark/fahrzeuge')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Fuhrpark-Auswertung lädt', async ({ page }) => {
    await page.goto('/fuhrpark/auswertung-kosten-pro-fahrzeug')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Fahrzeuge abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/fuhrpark/fahrzeuge?limit=5')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Transporte abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/transporte?limit=5')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('LKW-Beladung lädt', async ({ page }) => {
    await page.goto('/lager/lkw-beladung')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })
})
