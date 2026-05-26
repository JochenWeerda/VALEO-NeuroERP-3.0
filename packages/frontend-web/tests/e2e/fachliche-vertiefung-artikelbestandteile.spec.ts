import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type BestandteilDef = {
  id: string
  bestandteil_nr: string
  bezeichnung: string
  einheit: string | null
  grenzwert_min: number | null
  grenzwert_max: number | null
  nutzung: string | null
  typ_schad_naehr: string | null
  waage_qualitaet_nr: string | null
  aktiv: boolean
  created_at: string
}

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const createdAt = '2026-05-26T08:00:00'
const isCollection = (url: URL) => url.pathname === '/api/v1/artikel/bestandteile/stamm'
const isItem = (url: URL) => /^\/api\/v1\/artikel\/bestandteile\/stamm\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Artikel-Bestandteile (Wave 21)', () => {
  test('Bestandteil anlegen', async ({ page }) => {
    const requests: string[] = []

    let bestandteile: BestandteilDef[] = [
      {
        id: 'ab-1',
        bestandteil_nr: 'FEUCHTE',
        bezeichnung: 'Feuchtegehalt',
        einheit: '%',
        grenzwert_min: 0,
        grenzwert_max: 15,
        nutzung: 'Qualität',
        typ_schad_naehr: 'S',
        waage_qualitaet_nr: null,
        aktiv: true,
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
            body: JSON.stringify(bestandteile),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Partial<BestandteilDef>
          const created: BestandteilDef = {
            id: `ab-${Date.now()}`,
            bestandteil_nr: payload.bestandteil_nr ?? 'NEW',
            bezeichnung: payload.bezeichnung ?? '',
            einheit: payload.einheit ?? null,
            grenzwert_min: payload.grenzwert_min ?? null,
            grenzwert_max: payload.grenzwert_max ?? null,
            nutzung: payload.nutzung ?? null,
            typ_schad_naehr: payload.typ_schad_naehr ?? null,
            waage_qualitaet_nr: payload.waage_qualitaet_nr ?? null,
            aktiv: true,
            created_at: createdAt,
          }
          bestandteile = [...bestandteile, created]
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
        if (request.method() === 'DELETE') {
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.goto('/stammdaten/artikelbestandteile', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /Artikel-Bestandteile/, exact: false })).toBeVisible()
    await expect(page.getByText('Feuchtegehalt')).toBeVisible()

    await page.locator('#ab_nr').fill('PROTEIN')
    await page.locator('#ab_bezeichnung').fill('Proteingehalt')
    await page.locator('#ab_einheit').fill('%')

    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Proteingehalt')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/artikel/bestandteile/stamm'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/artikel/bestandteile/stamm'))).toBe(true)
  })
})
