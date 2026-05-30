/**
 * E2E Gate Wave 23: Kundenbankverbindungen im Kundenstamm
 */
import { test, expect } from '@playwright/test'
import type { KundenBankverbindung } from '../../src/lib/api/kundenbanken'

const KUNDEN_NR = 'K001'
const corsHeaders = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
}

const createdAt = '2026-05-30T10:00:00Z'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('dev_bypass_auth', 'true')
  })
})

test.describe('Fachliche Vertiefung Gate: Kundenbanken (Wave 23)', () => {
  test('zeigt Bankverbindungen und legt neue an', async ({ page }) => {
    const bankverbindungen: KundenBankverbindung[] = [
      {
        id: 'bv-1',
        kunden_nr: KUNDEN_NR,
        bezeichnung: 'Hauptkonto',
        iban: 'DE89370400440532013000',
        iban_masked: 'DE89****3000',
        bic: 'COBADEFFXXX',
        bank_name: 'Sparkasse',
        kontoinhaber: 'Muster GmbH',
        sepa_mandat_ref: 'MAND-001',
        sepa_mandat_datum: '2026-01-15',
        standard: true,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/crm/contacts**', async (route) => {
      await route.fulfill({ json: { data: [] } })
    })

    await page.route('**/api/v1/crm/customers/**', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          json: {
            id: KUNDEN_NR,
            kunden_nr: KUNDEN_NR,
            firma: 'Muster GmbH',
            nachname: 'Muster',
            strasse: 'Hauptstr. 1',
            plz: '12345',
            ort: 'Musterstadt',
            land: 'DE',
            status: 'aktiv',
          },
        })
        return
      }
      await route.continue()
    })

    await page.route(`**/api/v1/kunden/${KUNDEN_NR}/bankverbindungen**`, async (route) => {
      const url = route.request().url()
      if (route.request().method() === 'GET' && !url.includes('/standard')) {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(bankverbindungen) })
        return
      }
      if (route.request().method() === 'POST') {
        const body = JSON.parse(route.request().postData() ?? '{}') as Record<string, unknown>
        const created: KundenBankverbindung = {
          id: 'bv-new',
          kunden_nr: KUNDEN_NR,
          bezeichnung: (body.bezeichnung as string) ?? null,
          iban: body.iban as string,
          iban_masked: 'DE89****3000',
          bic: (body.bic as string) ?? null,
          bank_name: (body.bank_name as string) ?? null,
          kontoinhaber: (body.kontoinhaber as string) ?? null,
          sepa_mandat_ref: (body.sepa_mandat_ref as string) ?? null,
          sepa_mandat_datum: (body.sepa_mandat_datum as string) ?? null,
          standard: Boolean(body.standard),
          aktiv: true,
          created_at: createdAt,
        }
        bankverbindungen.push(created)
        await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(created) })
        return
      }
      await route.continue()
    })

    await page.goto(`/crm/kunden/${KUNDEN_NR}`)
    await page.waitForLoadState('networkidle')

    const panel = page.getByTestId('kunden-bankverbindungen-panel')
    await panel.scrollIntoViewIfNeeded()
    await expect(panel).toBeVisible({ timeout: 15_000 })
    await expect(page.getByTestId('kunden-bv-iban').first()).toContainText('DE89****3000')
    await expect(page.getByText('Standard', { exact: true })).toBeVisible()

    await page.getByRole('button', { name: 'Neue Bankverbindung anlegen' }).click()
    await page.getByLabel('Bezeichnung').fill('Zweitkonto')
    await page.getByLabel('IBAN').fill('DE44200400600543010000')
    await page.getByTestId('kunden-bv-form').getByRole('button', { name: 'Speichern' }).click()

    await expect(page.getByText('Zweitkonto')).toBeVisible({ timeout: 10_000 })
  })
})
