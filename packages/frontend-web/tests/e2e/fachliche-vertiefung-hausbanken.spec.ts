import { test, expect } from '@playwright/test'
import type { Hausbank } from '../../src/lib/api/hausbanken'

const corsHeaders = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
}

const createdAt = '2026-05-25T09:00:00Z'

test.describe('Fachliche Vertiefung Gate: Hausbankenstamm (Wave 15)', () => {
  test('zeigt Hausbankenliste mit Standard- und eRechnung-Badges', async ({ page }) => {
    const hausbanken: Hausbank[] = [
      {
        id: 'hb-1',
        bank_nr: 'HB01',
        bezeichnung: 'Hauptkonto Sparkasse',
        iban: 'DE89370400440532013000',
        bic: 'COBADEFFXXX',
        bank_name: 'Sparkasse Muster',
        kontonummer: '0532013000',
        blz: '37040044',
        waehrung: 'EUR',
        erechnung_aktiv: true,
        sepa_glaeubiger_id: 'DE98ZZZ09999999999',
        standard: true,
        aktiv: true,
        created_at: createdAt,
        updated_at: createdAt,
      },
      {
        id: 'hb-2',
        bank_nr: 'HB02',
        bezeichnung: 'Fremdwährungskonto',
        iban: 'DE44200400600543010000',
        bic: null,
        bank_name: null,
        kontonummer: null,
        blz: null,
        waehrung: 'USD',
        erechnung_aktiv: false,
        sepa_glaeubiger_id: null,
        standard: false,
        aktiv: true,
        created_at: createdAt,
        updated_at: createdAt,
      },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/stammdaten/hausbanken',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(hausbanken) })
      },
    )

    await page.goto('/stammdaten/hausbanken')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Hausbankenstamm/i }).first()).toBeVisible()
    await expect(page.getByText('HB01')).toBeVisible()
    await expect(page.getByText('Hauptkonto Sparkasse')).toBeVisible()
    await expect(page.getByText('DE89370400440532013000')).toBeVisible()

    await expect(page.getByText('Standard', { exact: true })).toBeVisible()
    await expect(page.getByText('eRechnung', { exact: true })).toBeVisible()
    await expect(page.getByText('SEPA', { exact: true })).toBeVisible()

    await expect(page.getByText('HB02')).toBeVisible()
    await expect(page.getByText('USD')).toBeVisible()
  })

  test('legt neue Hausbank an', async ({ page }) => {
    const hausbanken: Hausbank[] = []

    await page.route(
      (url) => url.pathname === '/api/v1/stammdaten/hausbanken',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(hausbanken) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newBank: Hausbank = {
            id: 'hb-new',
            bank_nr: body.bank_nr,
            bezeichnung: body.bezeichnung,
            iban: body.iban,
            bic: body.bic ?? null,
            bank_name: null,
            kontonummer: null,
            blz: null,
            waehrung: body.waehrung ?? 'EUR',
            erechnung_aktiv: body.erechnung_aktiv ?? false,
            sepa_glaeubiger_id: null,
            standard: body.standard ?? false,
            aktiv: true,
            created_at: createdAt,
            updated_at: createdAt,
          }
          hausbanken.push(newBank)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newBank) })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/stammdaten/hausbanken')
    await page.waitForLoadState('networkidle')

    await page.getByRole('button', { name: /Neue Hausbank anlegen/i }).click()

    await page.getByLabel('Bank-Nr').fill('HB03')
    await page.getByLabel('Bezeichnung').fill('Girokonto Volksbank')
    await page.getByLabel('IBAN').fill('DE27100777770209299700')

    await page.getByRole('button', { name: /Speichern/i }).click()

    await expect(page.getByText('HB03')).toBeVisible()
    await expect(page.getByText('Girokonto Volksbank')).toBeVisible()
  })
})
