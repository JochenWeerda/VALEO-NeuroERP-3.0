import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type RezepturGruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  tierart: string | null
  nutzungsrichtung: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isRezgCollection = (url: URL) =>
  url.pathname === '/api/v1/produktion/mischfutter/rezepturgruppen'
const isRezgItem = (url: URL) =>
  /^\/api\/v1\/produktion\/mischfutter\/rezepturgruppen\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Rezepturgruppen (Wave 22)', () => {
  test('Rezepturgruppe anlegen und in Liste sehen', async ({ page }) => {
    const requests: string[] = []

    let gruppen: RezepturGruppe[] = [
      {
        id: 'rezg-1',
        gruppe_nr: 'RIND-MILCH',
        bezeichnung: 'Rind Milchleistung',
        tierart: 'Rind',
        nutzungsrichtung: 'Milch',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isRezgCollection(new URL(url)) || isRezgItem(new URL(url)),
      async (route) => {
        const req = route.request()
        const pathname = new URL(req.url()).pathname
        requests.push(`${req.method()} ${pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(gruppen),
          })
          return
        }
        if (req.method() === 'POST') {
          const body = JSON.parse(req.postData() ?? '{}')
          const newGruppe: RezepturGruppe = {
            id: 'rezg-2',
            gruppe_nr: body.gruppe_nr ?? 'SCHWEIN-MAST',
            bezeichnung: body.bezeichnung ?? 'Schwein Masttier',
            tierart: body.tierart ?? 'Schwein',
            nutzungsrichtung: body.nutzungsrichtung ?? 'Mast',
            aktiv: true,
            created_at: createdAt,
          }
          gruppen = [...gruppen, newGruppe]
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(newGruppe),
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

    await page.goto('/produktion/rezepturgruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: 'Rezepturgruppen [REZG]', exact: true })).toBeVisible()
    await expect(page.getByRole('cell', { name: 'RIND-MILCH', exact: true })).toBeVisible()
    await expect(page.getByRole('cell', { name: 'Rind Milchleistung', exact: true })).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/produktion/mischfutter/rezepturgruppen'))).toBe(true)
  })

  test('Rezepturgruppe löschen', async ({ page }) => {
    const requests: string[] = []

    let gruppen: RezepturGruppe[] = [
      {
        id: 'rezg-1',
        gruppe_nr: 'RIND-MILCH',
        bezeichnung: 'Rind Milchleistung',
        tierart: 'Rind',
        nutzungsrichtung: 'Milch',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isRezgCollection(new URL(url)) || isRezgItem(new URL(url)),
      async (route) => {
        const req = route.request()
        const pathname = new URL(req.url()).pathname
        requests.push(`${req.method()} ${pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(gruppen),
          })
          return
        }
        if (req.method() === 'DELETE') {
          gruppen = gruppen.filter((g) => !pathname.includes(g.gruppe_nr))
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.continue()
      },
    )

    await page.goto('/produktion/rezepturgruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    const deleteBtn = page.getByRole('row').filter({ hasText: 'RIND-MILCH' }).getByRole('button').first()
    await deleteBtn.click()

    await expect(async () => {
      expect(requests.some((r) => r.startsWith('DELETE'))).toBe(true)
    }).toPass({ timeout: 5000 })
  })
})
