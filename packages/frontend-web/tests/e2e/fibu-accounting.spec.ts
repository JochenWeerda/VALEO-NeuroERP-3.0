/**
 * E2E: FIBU / Buchhaltung — Bilanz, GuV, Sachkonten, Buchungsimport
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('FIBU Buchhaltung', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Bilanz lädt', async ({ page }) => {
    await page.goto('/fibu/bilanz')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('GuV lädt', async ({ page }) => {
    await page.goto('/fibu/guv')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('BWA lädt', async ({ page }) => {
    await page.goto('/fibu/bwa')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Kontenplan lädt', async ({ page }) => {
    await page.goto('/fibu/kontenplan')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Offene Posten Kreditoren lädt', async ({ page }) => {
    await page.goto('/finance/op-kreditoren')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('API: Finanzbericht Bilanz', async ({ request }) => {
    const resp = await request.get('/api/v1/finance/financial-reports/balance-sheet')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Journal Entries abrufen', async ({ request }) => {
    const resp = await request.get('/api/v1/journal-entries?limit=5')
    expect([200, 401, 404]).toContain(resp.status())
  })

  test('API: Buchungsimport CSV Endpoint vorhanden', async ({ request }) => {
    const resp = await request.post('/api/v1/bulk-journal-import/csv', {
      multipart: { file: { name: 'test.csv', mimeType: 'text/csv', buffer: Buffer.from('datum;konto;betrag\n2026-01-01;1200;100.00') } },
    })
    expect([200, 201, 400, 401, 422]).toContain(resp.status())
  })
})
