import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type ArtikelVerpackung = {
  id: string
  verpackungs_nr: string
  bezeichnung: string
  stufen: number
  stufe1_bezeichnung: string | null
  stufe1_menge: number | null
  stufe1_einheit: string | null
  stufe1_gewicht_kg: number | null
  stufe2_bezeichnung: string | null
  stufe2_menge: number | null
  stufe2_einheit: string | null
  stufe2_gewicht_kg: number | null
  stufe3_bezeichnung: string | null
  stufe3_menge: number | null
  stufe3_einheit: string | null
  stufe3_gewicht_kg: number | null
  aktiv: boolean
  created_at: string
}

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const createdAt = '2026-05-26T08:00:00'
const isCollection = (url: URL) => url.pathname === '/api/v1/artikel/verpackungen'
const isItem = (url: URL) => /^\/api\/v1\/artikel\/verpackungen\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Artikelverpackung (Wave 21)', () => {
  test('Verpackung anlegen', async ({ page }) => {
    const requests: string[] = []

    let verpackungen: ArtikelVerpackung[] = [
      {
        id: 'vp-1',
        verpackungs_nr: 'VPK-001',
        bezeichnung: 'Standard-Palette Weizen',
        stufen: 2,
        stufe1_bezeichnung: 'Palette',
        stufe1_menge: 1,
        stufe1_einheit: 'Stk',
        stufe1_gewicht_kg: 25,
        stufe2_bezeichnung: 'Sack',
        stufe2_menge: 40,
        stufe2_einheit: 'Stk',
        stufe2_gewicht_kg: 0.5,
        stufe3_bezeichnung: null,
        stufe3_menge: null,
        stufe3_einheit: null,
        stufe3_gewicht_kg: null,
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
            body: JSON.stringify(verpackungen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Partial<ArtikelVerpackung>
          const created: ArtikelVerpackung = {
            id: `vp-${Date.now()}`,
            verpackungs_nr: payload.verpackungs_nr ?? 'VPK-NEW',
            bezeichnung: payload.bezeichnung ?? '',
            stufen: payload.stufen ?? 1,
            stufe1_bezeichnung: payload.stufe1_bezeichnung ?? null,
            stufe1_menge: payload.stufe1_menge ?? null,
            stufe1_einheit: payload.stufe1_einheit ?? null,
            stufe1_gewicht_kg: payload.stufe1_gewicht_kg ?? null,
            stufe2_bezeichnung: payload.stufe2_bezeichnung ?? null,
            stufe2_menge: payload.stufe2_menge ?? null,
            stufe2_einheit: payload.stufe2_einheit ?? null,
            stufe2_gewicht_kg: payload.stufe2_gewicht_kg ?? null,
            stufe3_bezeichnung: null,
            stufe3_menge: null,
            stufe3_einheit: null,
            stufe3_gewicht_kg: null,
            aktiv: true,
            created_at: createdAt,
          }
          verpackungen = [...verpackungen, created]
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

    await page.goto('/stammdaten/artikelverpackung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /Artikelverpackung/, exact: false })).toBeVisible()
    await expect(page.getByText('Standard-Palette Weizen')).toBeVisible()

    await page.locator('#av_nr').fill('VPK-002')
    await page.locator('#av_bez').fill('Kleinpackung Gerste')

    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Kleinpackung Gerste')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/artikel/verpackungen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/artikel/verpackungen'))).toBe(true)
  })
})
