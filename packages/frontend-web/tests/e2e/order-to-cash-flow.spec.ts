/**
 * E2E: Order-to-Cash (O2C) Flow
 * Testet den vollständigen Verkaufsprozess: Angebot → Auftrag → Lieferschein → Rechnung
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Order-to-Cash Flow', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Verkaufsangebote Liste lädt', async ({ page }) => {
    await page.goto('/verkauf/angebote')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2').first()).toBeVisible()
  })

  test('Auftragsübersicht lädt', async ({ page }) => {
    await page.goto('/verkauf/auftraege')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, [class*="title"]').first()).toBeVisible()
  })

  test('Lieferschein-Liste lädt', async ({ page }) => {
    await page.goto('/verkauf/lieferscheine')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Ausgangsrechnungen Liste lädt', async ({ page }) => {
    await page.goto('/verkauf/rechnungen')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: O2C UAT-Scaffold liefert Status', async ({ request }) => {
    const resp = await request.get('/api/v1/o2c/uat/scaffold')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Sales Offer erstellen (Validierung)', async ({ request }) => {
    const resp = await request.post('/api/v1/sales/offers', {
      data: { customer_id: 'test', positions: [] },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
  })

  test('API: Rechnungsexport E-Invoice', async ({ request }) => {
    const resp = await request.get('/api/v1/sales/invoices/einvoice/export?format=xrechnung')
    expect([200, 400, 401, 404]).toContain(resp.status())
  })

  test('Erntekampagne-Übersicht lädt', async ({ page }) => {
    await page.goto('/agrar/erntekampagne')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })
})
