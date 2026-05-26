import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Geschaeftsjahr = {
  id: string
  jahr_nr: number
  bezeichnung: string
  datum_beginn: string
  datum_ende: string
  anzahl_perioden_ware: number
  anzahl_perioden_fibu: number
  journal_nummernkreis: string | null
  status: 'offen' | 'gesperrt' | 'abgeschlossen'
  created_at: string
}

type FibuPeriode = {
  id: string
  jahr_nr: number
  periode_nr: number
  bezeichnung: string
  datum_von: string
  datum_bis: string
  typ: string
  gesperrt: boolean
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isGJCollection = (url: URL) =>
  url.pathname === '/api/v1/fibu/geschaeftsjahre'
const isGJItem = (url: URL) =>
  /^\/api\/v1\/fibu\/geschaeftsjahre\/\d+$/.test(url.pathname)
const isPeriodenCollection = (url: URL) =>
  /^\/api\/v1\/fibu\/geschaeftsjahre\/\d+\/perioden$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Geschäftsjahre (Wave 18)', () => {
  test('Geschäftsjahr anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let jahre: Geschaeftsjahr[] = [
      {
        id: 'gj-1',
        jahr_nr: 2024,
        bezeichnung: 'Geschäftsjahr 2024',
        datum_beginn: '2024-01-01',
        datum_ende: '2024-12-31',
        anzahl_perioden_ware: 12,
        anzahl_perioden_fibu: 12,
        journal_nummernkreis: null,
        status: 'abgeschlossen',
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isGJCollection(new URL(url)),
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
            body: JSON.stringify(jahre),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            Geschaeftsjahr,
            'jahr_nr' | 'bezeichnung' | 'datum_beginn' | 'datum_ende'
          >
          const created: Geschaeftsjahr = {
            id: `gj-${Date.now()}`,
            jahr_nr: payload.jahr_nr,
            bezeichnung: payload.bezeichnung,
            datum_beginn: payload.datum_beginn,
            datum_ende: payload.datum_ende,
            anzahl_perioden_ware: 12,
            anzahl_perioden_fibu: 12,
            journal_nummernkreis: null,
            status: 'offen',
            created_at: createdAt,
          }
          jahre = [...jahre, created]
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
      (url) => isGJItem(new URL(url)),
      async (route) => {
        const request = route.request()
        const pathname = new URL(request.url()).pathname
        requests.push(`${request.method()} ${pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (request.method() === 'DELETE') {
          const nr = parseInt(pathname.split('/').pop() ?? '0', 10)
          jahre = jahre.map((j) =>
            j.jahr_nr === nr ? { ...j, status: 'gesperrt' } : j
          )
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.goto('/fibu/geschaeftsjahre', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(
      page.getByRole('heading', { name: /Geschäftsjahre/, exact: false }).first()
    ).toBeVisible()
    await expect(page.getByText('Geschäftsjahr 2024')).toBeVisible()

    await page.locator('#gj_jahr_nr').fill('2025')
    await page.locator('#gj_bezeichnung').fill('Geschäftsjahr 2025')
    await page.locator('#gj_datum_beginn').fill('2025-01-01')
    await page.locator('#gj_datum_ende').fill('2025-12-31')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Geschäftsjahr 2025')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/fibu/geschaeftsjahre'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/fibu/geschaeftsjahre'))).toBe(true)
  })

  test('Perioden eines Jahres anzeigen', async ({ page }) => {
    const requests: string[] = []

    const jahre: Geschaeftsjahr[] = [
      {
        id: 'gj-1',
        jahr_nr: 2025,
        bezeichnung: 'Geschäftsjahr 2025',
        datum_beginn: '2025-01-01',
        datum_ende: '2025-12-31',
        anzahl_perioden_ware: 12,
        anzahl_perioden_fibu: 12,
        journal_nummernkreis: null,
        status: 'offen',
        created_at: createdAt,
      },
    ]

    const perioden: FibuPeriode[] = [
      {
        id: 'per-1',
        jahr_nr: 2025,
        periode_nr: 1,
        bezeichnung: 'Januar 2025',
        datum_von: '2025-01-01',
        datum_bis: '2025-01-31',
        typ: 'normal',
        gesperrt: false,
        created_at: createdAt,
      },
      {
        id: 'per-2',
        jahr_nr: 2025,
        periode_nr: 2,
        bezeichnung: 'Februar 2025',
        datum_von: '2025-02-01',
        datum_bis: '2025-02-28',
        typ: 'normal',
        gesperrt: false,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isGJCollection(new URL(url)),
      async (route) => {
        const request = route.request()
        requests.push(`${request.method()} ${new URL(request.url()).pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(jahre),
        })
      }
    )

    await page.route(
      (url) => isPeriodenCollection(new URL(url)),
      async (route) => {
        const request = route.request()
        requests.push(`${request.method()} ${new URL(request.url()).pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(perioden),
        })
      }
    )

    await page.goto('/fibu/geschaeftsjahre', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('tab', { name: 'Perioden', exact: true }).click()

    await page.getByRole('combobox', { name: /Geschäftsjahr für Perioden/ }).click()
    await page.getByRole('option', { name: /2025 — Geschäftsjahr 2025/ }).click()

    await expect(page.getByText('Januar 2025')).toBeVisible()
    await expect(page.getByText('Februar 2025')).toBeVisible()

    expect(requests.some((r) => r.includes('/api/v1/fibu/geschaeftsjahre/2025/perioden'))).toBe(true)
  })
})
