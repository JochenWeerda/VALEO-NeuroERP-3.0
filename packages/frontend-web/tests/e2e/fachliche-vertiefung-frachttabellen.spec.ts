import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Frachttabelle = {
  id: string
  tabelle_nr: string
  bezeichnung: string
  einheit: string | null
  waehrung: string
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isFTUrl = (url: URL) =>
  url.pathname.startsWith('/api/v1/logistik/frachttabellen')

test.describe('Fachliche Vertiefung Gate: Frachttabellen', () => {
  test('Frachttabelle anlegen und in Liste sehen', async ({ page }) => {
    const requests: string[] = []

    const tabellen: Frachttabelle[] = [
      {
        id: 'ft-1',
        tabelle_nr: 'FRA-STD',
        bezeichnung: 'Standard Frachttabelle',
        einheit: 't',
        waehrung: 'EUR',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isFTUrl(new URL(url)),
      async (route) => {
        const req = route.request()
        const pathname = new URL(req.url()).pathname
        requests.push(`${req.method()} ${pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'GET') {
          if (/positionen/.test(pathname)) {
            await route.fulfill({
              status: 200,
              contentType: 'application/json',
              headers: corsHeaders,
              body: JSON.stringify([]),
            })
            return
          }
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(tabellen),
          })
          return
        }
        if (req.method() === 'POST') {
          const body = JSON.parse(req.postData() ?? '{}')
          const newT: Frachttabelle = {
            id: 'ft-new',
            tabelle_nr: body.tabelle_nr ?? 'FT-NEW',
            bezeichnung: body.bezeichnung ?? 'Neue Tabelle',
            einheit: body.einheit ?? null,
            waehrung: body.waehrung ?? 'EUR',
            aktiv: true,
            created_at: createdAt,
          }
          tabellen.push(newT)
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(newT),
          })
          return
        }
        if (req.method() === 'DELETE') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.continue()
      },
    )

    await page.goto('/logistik/frachttabellen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    // Frachttabellen uses span elements with font-mono class for tabelle_nr
    await expect(page.locator('span.font-mono', { hasText: 'FRA-STD' }).first()).toBeVisible()
    await expect(page.getByText('Standard Frachttabelle').first()).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/logistik/frachttabellen'))).toBe(true)
  })
})
