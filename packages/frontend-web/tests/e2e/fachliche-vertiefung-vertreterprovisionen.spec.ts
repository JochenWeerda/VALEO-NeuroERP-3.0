import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type ProvisionsGruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: 'ek' | 'vk'
  provisionstyp: 'fix' | 'staffel_optpreis' | 'staffel_preis_zuab'
  provisionssatz: number | null
  aktiv: boolean
  created_at: string
}

type ProvisionsStaffelZeile = {
  id: string
  staffel_id: string
  zeile_nr: number
  ab_wert: number
  provisionssatz: number
}

type ProvisionsStaffel = {
  id: string
  gruppe_id: string
  vertreterklasse: string | null
  zeilen: ProvisionsStaffelZeile[]
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isGruppenCollection = (url: URL) =>
  url.pathname === '/api/v1/crm/vertreter/provisionen/gruppen'
const isGruppenItem = (url: URL) =>
  /^\/api\/v1\/crm\/vertreter\/provisionen\/gruppen\/[^/]+$/.test(url.pathname)
const isStaffelnCollection = (url: URL) =>
  url.pathname === '/api/v1/crm/vertreter/provisionen/staffeln'

test.describe('Fachliche Vertiefung Gate: Vertreterprovisionen (Wave 12)', () => {
  test('Provisionsgruppe Fix anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let gruppen: ProvisionsGruppe[] = [
      {
        id: 'pvg-1',
        gruppe_nr: 'PVG-NORD',
        bezeichnung: 'Außendienst Nord',
        richtung: 'vk',
        provisionstyp: 'fix',
        provisionssatz: 2.5,
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
          const payload = request.postDataJSON() as Omit<ProvisionsGruppe, 'id' | 'aktiv' | 'created_at'>
          const created: ProvisionsGruppe = {
            id: `pvg-${Date.now()}`,
            gruppe_nr: payload.gruppe_nr,
            bezeichnung: payload.bezeichnung,
            richtung: payload.richtung,
            provisionstyp: payload.provisionstyp,
            provisionssatz: payload.provisionssatz ?? null,
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

    await page.goto('/crm/vertreterprovisionen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(
      page.getByRole('heading', { name: /Vertreterprovisionsgruppen/, exact: false })
    ).toBeVisible()
    await expect(page.getByText('Außendienst Nord')).toBeVisible()
    await expect(page.getByText('Fixprovision')).toBeVisible()

    await page.locator('#pg_nr').fill('PVG-SÜD')
    await page.locator('#pg_bez').fill('Außendienst Süd')
    await page.locator('#pg_satz').fill('3.0')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Außendienst Süd')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/crm/vertreter/provisionen/gruppen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/crm/vertreter/provisionen/gruppen'))).toBe(true)
  })

  test('Provisionsstaffel anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    const staffelGruppe: ProvisionsGruppe = {
      id: 'pvg-staffel',
      gruppe_nr: 'PVG-STF',
      bezeichnung: 'Staffelgruppe West',
      richtung: 'vk',
      provisionstyp: 'staffel_optpreis',
      provisionssatz: null,
      aktiv: true,
      created_at: createdAt,
    }

    let staffeln: ProvisionsStaffel[] = []

    await page.route(
      (url) => isGruppenCollection(new URL(url)),
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
          body: JSON.stringify([staffelGruppe]),
        })
      }
    )

    await page.route(
      (url) => isGruppenItem(new URL(url)),
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
      (url) => isStaffelnCollection(new URL(url)),
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
            body: JSON.stringify(staffeln),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as {
            gruppe_id: string
            vertreterklasse: string | null
            zeilen: { zeile_nr: number; ab_wert: number; provisionssatz: number }[]
          }
          const newStaffelId = `stf-${Date.now()}`
          const created: ProvisionsStaffel = {
            id: newStaffelId,
            gruppe_id: payload.gruppe_id,
            vertreterklasse: payload.vertreterklasse,
            zeilen: payload.zeilen.map((z, i) => ({
              id: `sz-${i}`,
              staffel_id: newStaffelId,
              zeile_nr: z.zeile_nr,
              ab_wert: z.ab_wert,
              provisionssatz: z.provisionssatz,
            })),
            created_at: createdAt,
          }
          staffeln = [...staffeln, created]
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

    await page.goto('/crm/vertreterprovisionen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByText('Staffelgruppe West')).toBeVisible()
    await expect(page.getByText('Staffel (OPT-Preis)')).toBeVisible()

    await page
      .getByRole('button', { name: /Staffeln für PVG-STF/, exact: false })
      .first()
      .click()

    await expect(page.getByText('Keine Staffeln vorhanden.')).toBeVisible()

    await page.locator('input[id^="zeile_nr_"]').first().fill('1')
    await page.locator('input[id^="ab_wert_"]').first().fill('10000')
    await page.locator('input[id^="ps_"]').first().fill('2.5')
    await page.getByRole('button', { name: 'Staffel anlegen' }).first().click()

    await expect(page.getByText('Staffel angelegt.')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/crm/vertreter/provisionen/gruppen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('GET /api/v1/crm/vertreter/provisionen/staffeln'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/crm/vertreter/provisionen/staffeln'))).toBe(true)
  })
})
