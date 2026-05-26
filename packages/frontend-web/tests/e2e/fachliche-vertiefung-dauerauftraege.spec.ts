import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Dauerauftrag = {
  id: string
  da_nr: string
  kunden_nr: string
  bezeichnung: string | null
  da_anfang: string
  da_naechster: string
  da_ende: string | null
  perioden_typ: string
  perioden_wert: number
  aktiv: boolean
  letzter_lauf: string | null
  positionen: { id: string; pos_nr: number; artikel_nr: string; menge: number; mengeneinheit: string | null; preis_eur: number | null }[]
}

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const createdAt = '2026-05-26T08:00:00'

const isCollection = (url: URL) => url.pathname === '/api/v1/dauerauftraege'
const isItem = (url: URL) => /^\/api\/v1\/dauerauftraege\/[^/]+$/.test(url.pathname)
const isStarten = (url: URL) => /^\/api\/v1\/dauerauftraege\/[^/]+\/starten$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Daueraufträge (Wave 21)', () => {
  test('Dauerauftrag anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let dauerauftraege: Dauerauftrag[] = [
      {
        id: 'da-1',
        da_nr: 'DA-2026-001',
        kunden_nr: 'KD-100',
        bezeichnung: 'Monatliche Getreideleitung',
        da_anfang: '2026-01-01',
        da_naechster: '2026-06-01',
        da_ende: null,
        perioden_typ: 'monatlich',
        perioden_wert: 1,
        aktiv: true,
        letzter_lauf: null,
        positionen: [{ id: 'pos-1', pos_nr: 1, artikel_nr: 'WEIZEN', menge: 100, mengeneinheit: 'kg', preis_eur: null }],
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
            body: JSON.stringify(dauerauftraege),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Omit<Dauerauftrag, 'id' | 'aktiv' | 'letzter_lauf'>
          const created: Dauerauftrag = {
            id: `da-${Date.now()}`,
            da_nr: `DA-${Date.now()}`,
            kunden_nr: payload.kunden_nr,
            bezeichnung: payload.bezeichnung ?? null,
            da_anfang: payload.da_anfang,
            da_naechster: payload.da_naechster,
            da_ende: payload.da_ende ?? null,
            perioden_typ: payload.perioden_typ,
            perioden_wert: payload.perioden_wert,
            aktiv: true,
            letzter_lauf: null,
            positionen: [],
          }
          dauerauftraege = [...dauerauftraege, created]
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

    await page.route(
      (url) => isStarten(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (request.method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify({ rechnung_nr: `RE-${Date.now()}` }),
          })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.goto('/verkauf/dauerauftraege', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.locator('h1').filter({ hasText: /Dauerauftr/ })).toBeVisible()
    await expect(page.getByText('Monatliche Getreideleitung')).toBeVisible()

    await page.locator('#da_kunden_nr').fill('KD-200')
    await page.locator('#da_anfang').fill('2026-06-01')
    await page.locator('#da_naechster').fill('2026-07-01')

    const artikelInputs = page.locator('input[placeholder="z. B. ART-001"]')
    await artikelInputs.first().fill('GERSTE')
    const mengeInputs = page.locator('input[placeholder="10"]')
    await mengeInputs.first().fill('50')

    await page.getByRole('button', { name: 'Anlegen' }).first().click()

    expect(requests.some((r) => r.startsWith('GET /api/v1/dauerauftraege'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/dauerauftraege'))).toBe(true)
  })
})
