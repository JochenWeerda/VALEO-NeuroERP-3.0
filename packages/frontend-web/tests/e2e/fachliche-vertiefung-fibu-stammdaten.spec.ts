import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Zahlungsformular = {
  id: string
  formular_nr: string
  bezeichnung: string
  formularklasse: 'eingang' | 'ausgang'
  bank_blz: string | null
  bank_iban: string | null
  formulareinrichtung: string | null
  aktiv: boolean
  created_at: string
}

type Zinsgruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  zinssatz: number
  zinsmethode: string
  schwellwert_tage: number
  konto_zinsen: string | null
  konto_zinsabschlagsteuer: string | null
  aktiv: boolean
  created_at: string
}

type LeergutArt = {
  id: string
  art_nr: string
  bezeichnung: string
  leergut_typ: string
  pfandwert: number | null
  konto_leergut: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isZahlungsformulareCollection = (url: URL) =>
  url.pathname === '/api/v1/fibu/stammdaten/zahlungsformulare'
const isZahlungsformulareItem = (url: URL) =>
  /^\/api\/v1\/fibu\/stammdaten\/zahlungsformulare\/[^/]+$/.test(url.pathname)
const isZinsgruppenCollection = (url: URL) =>
  url.pathname === '/api/v1/fibu/stammdaten/zinsgruppen'
const isZinsgruppenItem = (url: URL) =>
  /^\/api\/v1\/fibu\/stammdaten\/zinsgruppen\/[^/]+$/.test(url.pathname)
const isLeergutartenCollection = (url: URL) =>
  url.pathname === '/api/v1/fibu/stammdaten/leergutarten'
const isLeergutartenItem = (url: URL) =>
  /^\/api\/v1\/fibu\/stammdaten\/leergutarten\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: FIBU Stammdaten (Wave 13)', () => {
  test('Zahlungsformulare anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let formulare: Zahlungsformular[] = [
      {
        id: 'zf-1',
        formular_nr: 'FIZAF-001',
        bezeichnung: 'SEPA Überweisung',
        formularklasse: 'ausgang',
        bank_blz: '37040044',
        bank_iban: 'DE89370400440532013000',
        formulareinrichtung: null,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isZahlungsformulareCollection(new URL(url)),
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
            body: JSON.stringify(formulare),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            Zahlungsformular,
            'formular_nr' | 'bezeichnung' | 'formularklasse'
          >
          const created: Zahlungsformular = {
            id: `zf-${Date.now()}`,
            formular_nr: payload.formular_nr,
            bezeichnung: payload.bezeichnung,
            formularklasse: payload.formularklasse,
            bank_blz: null,
            bank_iban: null,
            formulareinrichtung: null,
            aktiv: true,
            created_at: createdAt,
          }
          formulare = [...formulare, created]
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
      (url) => isZahlungsformulareItem(new URL(url)),
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

    await page.route(
      (url) => isZinsgruppenCollection(new URL(url)),
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
      (url) => isLeergutartenCollection(new URL(url)),
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

    await page.goto('/fibu/stammdaten', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(
      page.getByRole('heading', { name: /FIBU Zusatzstammdaten/, exact: false })
    ).toBeVisible()
    await expect(page.getByText('SEPA Überweisung')).toBeVisible()

    await page.locator('#zf_nr').fill('FIZAF-002')
    await page.locator('#zf_bez').fill('Lastschrift SEPA')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Lastschrift SEPA')).toBeVisible()

    expect(
      requests.some((r) => r.startsWith('GET /api/v1/fibu/stammdaten/zahlungsformulare'))
    ).toBe(true)
    expect(
      requests.some((r) => r.startsWith('POST /api/v1/fibu/stammdaten/zahlungsformulare'))
    ).toBe(true)
  })

  test('Zinsgruppen anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let zinsgruppen: Zinsgruppe[] = [
      {
        id: 'zg-1',
        gruppe_nr: 'ZINS-STD',
        bezeichnung: 'Standard-Zinssatz',
        zinssatz: 8.5,
        zinsmethode: 'act_360',
        schwellwert_tage: 30,
        konto_zinsen: '7665',
        konto_zinsabschlagsteuer: null,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isZahlungsformulareCollection(new URL(url)),
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
      (url) => isZinsgruppenCollection(new URL(url)),
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
            body: JSON.stringify(zinsgruppen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            Zinsgruppe,
            'gruppe_nr' | 'bezeichnung' | 'zinssatz' | 'zinsmethode'
          >
          const created: Zinsgruppe = {
            id: `zg-${Date.now()}`,
            gruppe_nr: payload.gruppe_nr,
            bezeichnung: payload.bezeichnung,
            zinssatz: payload.zinssatz,
            zinsmethode: payload.zinsmethode,
            schwellwert_tage: 0,
            konto_zinsen: null,
            konto_zinsabschlagsteuer: null,
            aktiv: true,
            created_at: createdAt,
          }
          zinsgruppen = [...zinsgruppen, created]
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
      (url) => isZinsgruppenItem(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
      }
    )

    await page.route(
      (url) => isLeergutartenCollection(new URL(url)),
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

    await page.goto('/fibu/stammdaten', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('tab', { name: 'Zinsgruppen', exact: true }).click()

    await expect(page.getByText('Standard-Zinssatz')).toBeVisible()

    await page.locator('#zg_nr').fill('ZINS-HOC')
    await page.locator('#zg_bez').fill('Hochzinssatz')
    await page.locator('#zg_satz').fill('12.5')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Hochzinssatz')).toBeVisible()

    expect(
      requests.some((r) => r.startsWith('GET /api/v1/fibu/stammdaten/zinsgruppen'))
    ).toBe(true)
    expect(
      requests.some((r) => r.startsWith('POST /api/v1/fibu/stammdaten/zinsgruppen'))
    ).toBe(true)
  })

  test('Leergutarten anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let leergutarten: LeergutArt[] = [
      {
        id: 'lg-1',
        art_nr: 'PAL-EUR',
        bezeichnung: 'Euro-Palette',
        leergut_typ: 'palette',
        pfandwert: 7.5,
        konto_leergut: '0480',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isZahlungsformulareCollection(new URL(url)),
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
      (url) => isZinsgruppenCollection(new URL(url)),
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
      (url) => isLeergutartenCollection(new URL(url)),
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
            body: JSON.stringify(leergutarten),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            LeergutArt,
            'art_nr' | 'bezeichnung' | 'leergut_typ'
          >
          const created: LeergutArt = {
            id: `lg-${Date.now()}`,
            art_nr: payload.art_nr,
            bezeichnung: payload.bezeichnung,
            leergut_typ: payload.leergut_typ,
            pfandwert: null,
            konto_leergut: null,
            aktiv: true,
            created_at: createdAt,
          }
          leergutarten = [...leergutarten, created]
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
      (url) => isLeergutartenItem(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
      }
    )

    await page.goto('/fibu/stammdaten', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('tab', { name: 'Leergutarten', exact: true }).click()

    await expect(page.getByText('Euro-Palette')).toBeVisible()

    await page.locator('#lg_nr').fill('BB-1000')
    await page.locator('#lg_bez').fill('Big-Bag 1000 kg')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Big-Bag 1000 kg')).toBeVisible()

    expect(
      requests.some((r) => r.startsWith('GET /api/v1/fibu/stammdaten/leergutarten'))
    ).toBe(true)
    expect(
      requests.some((r) => r.startsWith('POST /api/v1/fibu/stammdaten/leergutarten'))
    ).toBe(true)
  })
})
