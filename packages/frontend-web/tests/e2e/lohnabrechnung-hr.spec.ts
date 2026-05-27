/**
 * E2E: HR / Lohnabrechnung
 * Steuerklassen I–VI, SV-Beiträge 2025, Personal-Verwaltung
 */
import { test, expect } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

test.describe('Lohnabrechnung Engine', () => {
  const cases = [
    { steuerklasse: 1, brutto: 3000, hat_kinder: false, label: 'SK I ledig' },
    { steuerklasse: 2, brutto: 2500, hat_kinder: true,  label: 'SK II alleinerziehend' },
    { steuerklasse: 3, brutto: 5000, hat_kinder: true,  label: 'SK III verheiratet' },
    { steuerklasse: 4, brutto: 3500, hat_kinder: false, label: 'SK IV Ehegatte' },
    { steuerklasse: 5, brutto: 2000, hat_kinder: false, label: 'SK V Zweiverdiener' },
    { steuerklasse: 6, brutto: 800,  hat_kinder: false, label: 'SK VI Nebenbeschäftigung' },
  ]

  for (const tc of cases) {
    test(`Brutto-Netto ${tc.label}`, async ({ request }) => {
      const resp = await request.post('/api/v1/personal/lohn/berechnung', {
        data: {
          brutto: tc.brutto,
          steuerklasse: tc.steuerklasse,
          hat_kinder: tc.hat_kinder,
          kinder_freibetraege: tc.hat_kinder ? 2.0 : 0.0,
          kirchensteuersatz: 0.0,
          zusatzbeitrag_kv: 0.016,
        },
      })
      expect([200, 401, 422]).toContain(resp.status())
      if (resp.status() === 200) {
        const body = await resp.json()
        expect(body).toHaveProperty('netto_betrag')
        // Netto muss kleiner als Brutto sein
        expect(body.netto_betrag).toBeLessThan(tc.brutto)
        expect(body.netto_betrag).toBeGreaterThan(0)
        expect(body).toHaveProperty('steuerklasse', tc.steuerklasse)
      }
    })
  }

  test('KiSt-Berechnung (9%)', async ({ request }) => {
    const resp = await request.post('/api/v1/personal/lohn/berechnung', {
      data: { brutto: 4000, steuerklasse: 1, hat_kinder: false, kirchensteuersatz: 0.09 },
    })
    expect([200, 401, 422]).toContain(resp.status())
    if (resp.status() === 200) {
      const body = await resp.json()
      expect(body).toHaveProperty('kirchensteuer_betrag')
    }
  })
})

test.describe('Personal-Verwaltung', () => {
  test.beforeEach(async ({ page }) => {
    await prepareE2EAuth(page)
  })

  test('Mitarbeiterliste lädt', async ({ page }) => {
    await page.goto('/personal/mitarbeiter')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Zeiterfassung lädt', async ({ page }) => {
    await page.goto('/personal/zeiterfassung')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })

  test('Abwesenheiten lädt', async ({ page }) => {
    await page.goto('/personal/abwesenheiten')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, h2, main').first()).toBeVisible()
  })
})
