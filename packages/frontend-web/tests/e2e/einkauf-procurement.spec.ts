/**
 * E2E: Einkauf / Procurement
 * Bestellvorschläge, Bestellungen, FinTS-Banking-Seiten
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Einkauf Bestellvorschlag', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Bestellvorschlag Lager lädt', async ({ page }) => {
    await page.goto('/einkauf/bestellvorschlag-lager')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Bestellvorschlag Rohware lädt', async ({ page }) => {
    await page.goto('/einkauf/bestellvorschlag-rohware')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Bestellvorschläge abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/einkauf/bestellvorschlaege?limit=10')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(Array.isArray(body) || body.items !== undefined).toBe(true)
    }
  })

  test('API: Bestellung erstellen (Validierung)', async ({ request }) => {
    const resp = await request.post('/api/v1/einkauf/bestellungen', {
      data: { lieferant_id: 'L-001', positionen: [], notiz: 'E2E-Test' },
    })
    expect([200, 201, 401, 422]).toContain(resp.status())
  })
})

test.describe('Banking FinTS', () => {
  test('Bankenseite lädt', async ({ page }) => {
    await prepareE2EAuth(page)
    await page.goto('/fibu/bankverbindungen')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: FinTS Konten Simulator', async ({ request }) => {
    const resp = await request.get('/api/v1/banken/fints/konten')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body.erfolg).toBe(true)
      expect(Array.isArray(body.konten)).toBe(true)
      // Simulator liefert 2 Konten
      expect(body.konten.length).toBeGreaterThan(0)
    }
  })

  test('API: FinTS Umsätze Simulator', async ({ request }) => {
    const resp = await request.get('/api/v1/banken/fints/umsaetze?iban=DE89370400440532013000&von=2026-05-01&bis=2026-05-31')
    expect([200, 401]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body.erfolg).toBe(true)
      expect(Array.isArray(body.buchungen)).toBe(true)
    }
  })
})
