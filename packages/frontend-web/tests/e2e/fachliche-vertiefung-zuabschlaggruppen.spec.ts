import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type ZuAbschlaggruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: 'ek' | 'vk'
  aktiv: boolean
  created_at: string
}

type ZuAbschlagklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: 'ek' | 'vk'
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isGruppenCollection = (url: URL) =>
  url.pathname === '/api/v1/preise/zu-abschlaege/gruppen'
const isGruppenItem = (url: URL) =>
  /^\/api\/v1\/preise\/zu-abschlaege\/gruppen\/[^/]+$/.test(url.pathname)
const isKlassenCollection = (url: URL) =>
  url.pathname === '/api/v1/preise/zu-abschlaege/klassen'
const isKlassenItem = (url: URL) =>
  /^\/api\/v1\/preise\/zu-abschlaege\/klassen\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Zu-/Abschlaggruppen (Wave 12)', () => {
  test('Zu-/Abschlaggruppen anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let gruppen: ZuAbschlaggruppe[] = [
      {
        id: 'zag-1',
        gruppe_nr: 'ZAG-QUAL',
        bezeichnung: 'Qualitätszuschlag',
        richtung: 'vk',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isGruppenCollection(new URL(url)),
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
            body: JSON.stringify(gruppen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            ZuAbschlaggruppe,
            'gruppe_nr' | 'bezeichnung' | 'richtung'
          >
          const created: ZuAbschlaggruppe = {
            id: `zag-${Date.now()}`,
            gruppe_nr: payload.gruppe_nr,
            bezeichnung: payload.bezeichnung,
            richtung: payload.richtung,
            aktiv: true,
            created_at: createdAt,
          }
          gruppen = [...gruppen, created]
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
      (url) => isGruppenItem(new URL(url)),
      async (route) => {
        const request = route.request()
        const pathname = new URL(request.url()).pathname
        const nr = decodeURIComponent(pathname.split('/').pop() ?? '')
        requests.push(`${request.method()} ${pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (request.method() === 'DELETE') {
          gruppen = gruppen.filter((g) => g.gruppe_nr !== nr)
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.route(
      (url) => isKlassenCollection(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify([]),
        })
      }
    )

    await page.route(
      (url) => isKlassenItem(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
      }
    )

    await page.goto('/preise/zu-abschlaggruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(
      page.getByRole('heading', { name: /Zu-\/Abschlaggruppen/, exact: false })
    ).toBeVisible()
    await expect(page.getByText('Qualitätszuschlag')).toBeVisible()

    await page.locator('#gruppe_nr').fill('ZAG-FEUCHT')
    await page.locator('#bezeichnung_gr').fill('Feuchtezuschlag')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Feuchtezuschlag')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/preise/zu-abschlaege/gruppen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/preise/zu-abschlaege/gruppen'))).toBe(true)
  })

  test('Zu-/Abschlagklassen anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let klassen: ZuAbschlagklasse[] = [
      {
        id: 'zak-1',
        klasse_nr: 'ZAK-GROSS',
        bezeichnung: 'Großkunde Stufe 1',
        richtung: 'vk',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isGruppenCollection(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify([]),
        })
      }
    )

    await page.route(
      (url) => isKlassenCollection(new URL(url)),
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
            body: JSON.stringify(klassen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            ZuAbschlagklasse,
            'klasse_nr' | 'bezeichnung' | 'richtung'
          >
          const created: ZuAbschlagklasse = {
            id: `zak-${Date.now()}`,
            klasse_nr: payload.klasse_nr,
            bezeichnung: payload.bezeichnung,
            richtung: payload.richtung,
            aktiv: true,
            created_at: createdAt,
          }
          klassen = [...klassen, created]
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
      (url) => isKlassenItem(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
      }
    )

    await page.goto('/preise/zu-abschlaggruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('tab', { name: 'Klassen [ZAKL]', exact: true }).click()

    await expect(page.getByText('Großkunde Stufe 1')).toBeVisible()

    await page.locator('#klasse_nr').fill('ZAK-MITTEL')
    await page.locator('#bezeichnung_kl').fill('Mittelkunde Stufe 2')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Mittelkunde Stufe 2')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/preise/zu-abschlaege/klassen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/preise/zu-abschlaege/klassen'))).toBe(true)
  })
})
