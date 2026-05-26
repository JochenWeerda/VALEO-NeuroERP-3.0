import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Massebilanz = {
  id: string
  periode: string
  artikel_nr: string | null
  lager_nr: string | null
  anfangsbestand_kg: number
  zugaenge_kg: number
  abgaenge_kg: number
  endbestand_kg: number
  differenz_kg: number
  status: 'offen' | 'festgeschrieben'
  festgeschrieben_am: string | null
  created_at: string
}

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const createdAt = '2026-05-26T08:00:00'
const isCollection = (url: URL) => url.pathname === '/api/v1/massebilanz'
const isItem = (url: URL) => /^\/api\/v1\/massebilanz\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Massebilanz (Wave 21)', () => {
  test('Massebilanz anlegen', async ({ page }) => {
    const requests: string[] = []

    let bilanzen: Massebilanz[] = [
      {
        id: 'mb-1',
        periode: '2026-04',
        artikel_nr: 'WEIZEN',
        lager_nr: 'LAG-01',
        anfangsbestand_kg: 10000,
        zugaenge_kg: 5000,
        abgaenge_kg: 3000,
        endbestand_kg: 12000,
        differenz_kg: 0,
        status: 'offen',
        festgeschrieben_am: null,
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
            body: JSON.stringify(bilanzen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as { periode: string; artikel_nr?: string; lager_nr?: string }
          const created: Massebilanz = {
            id: `mb-${Date.now()}`,
            periode: payload.periode,
            artikel_nr: payload.artikel_nr ?? null,
            lager_nr: payload.lager_nr ?? null,
            anfangsbestand_kg: 0,
            zugaenge_kg: 0,
            abgaenge_kg: 0,
            endbestand_kg: 0,
            differenz_kg: 0,
            status: 'offen',
            festgeschrieben_am: null,
            created_at: createdAt,
          }
          bilanzen = [...bilanzen, created]
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
        await route.fulfill({ status: 404, headers: corsHeaders, body: '{"detail":"not found"}' })
      }
    )

    await page.goto('/lager/massebilanz', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.locator('h1').filter({ hasText: 'Massebilanz' })).toBeVisible()
    await expect(page.getByText('2026-04')).toBeVisible()

    await page.locator('#mb_periode').fill('2026-05')
    await page.locator('#mb_artikel_nr').fill('GERSTE')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()

    await expect(page.getByText('2026-05')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/massebilanz'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/massebilanz'))).toBe(true)
  })
})
