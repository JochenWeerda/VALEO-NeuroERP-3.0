import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Zinsabrechnung = {
  id: string
  kontrakt_nr: string
  lieferant_nr: string
  lieferant_name: string | null
  zinssatz_prozent: number
  basisbetrag_eur: number
  von_datum: string
  bis_datum: string
  tage: number
  zinsbetrag_eur: number
  mwst_satz: number
  mwst_betrag_eur: number
  status: 'berechnet' | 'gebucht' | 'storniert'
  beleg_nr: string | null
  buchungs_periode: string | null
  created_at: string
}

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const createdAt = '2026-05-26T08:00:00'
const isCollection = (url: URL) => url.pathname === '/api/v1/zinsabrechnung'
const isItem = (url: URL) => /^\/api\/v1\/zinsabrechnung\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Zinsabrechnung (Wave 21)', () => {
  test('Zinsabrechnung anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let abrechnungen: Zinsabrechnung[] = [
      {
        id: 'za-1',
        kontrakt_nr: 'KONT-2026-001',
        lieferant_nr: 'LF-100',
        lieferant_name: 'Müller Agrar GmbH',
        zinssatz_prozent: 3.5,
        basisbetrag_eur: 10000,
        von_datum: '2026-01-01',
        bis_datum: '2026-03-31',
        tage: 90,
        zinsbetrag_eur: 86.30,
        mwst_satz: 19,
        mwst_betrag_eur: 16.40,
        status: 'berechnet',
        beleg_nr: null,
        buchungs_periode: '2026-03',
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isCollection(new URL(url)),
      async (route) => {
        const request = route.request()
        const pathname = new URL(request.url()).pathname
        requests.push(`${request.method()} ${pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (request.method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(abrechnungen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Partial<Zinsabrechnung>
          const basisbetrag = payload.basisbetrag_eur ?? 0
          const zinssatz = payload.zinssatz_prozent ?? 0
          const created: Zinsabrechnung = {
            id: `za-${Date.now()}`,
            kontrakt_nr: payload.kontrakt_nr ?? '',
            lieferant_nr: payload.lieferant_nr ?? '',
            lieferant_name: payload.lieferant_name ?? null,
            zinssatz_prozent: zinssatz,
            basisbetrag_eur: basisbetrag,
            von_datum: payload.von_datum ?? '',
            bis_datum: payload.bis_datum ?? '',
            tage: 30,
            zinsbetrag_eur: (basisbetrag * zinssatz / 100) * (30 / 365),
            mwst_satz: payload.mwst_satz ?? 19,
            mwst_betrag_eur: 0,
            status: 'berechnet',
            beleg_nr: null,
            buchungs_periode: payload.buchungs_periode ?? null,
            created_at: createdAt,
          }
          abrechnungen = [...abrechnungen, created]
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(created),
          })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.route(
      (url) => isItem(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(abrechnungen[0]) })
      }
    )

    await page.goto('/agrar/zinsabrechnung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.locator('h1').filter({ hasText: 'Zinsabrechnung' })).toBeVisible()
    await expect(page.getByText('Müller Agrar GmbH')).toBeVisible()

    await page.locator('#za_kontrakt_nr').fill('KONT-2026-002')
    await page.locator('#za_lieferant_nr').fill('LF-200')
    await page.locator('#za_zinssatz').fill('4.5')
    await page.locator('#za_basis').fill('20000')
    await page.locator('#za_von').fill('2026-04-01')
    await page.locator('#za_bis').fill('2026-04-30')

    await page.getByRole('button', { name: 'Anlegen' }).first().click()

    expect(requests.some((r) => r.startsWith('GET /api/v1/zinsabrechnung'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/zinsabrechnung'))).toBe(true)
  })
})
