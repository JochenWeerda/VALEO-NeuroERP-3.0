import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'
import type { IndivArtikelNr } from '../../src/lib/api/individuelleArtikelnummern'

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const createdAt = '2026-05-30T12:00:00'
const BASE = '/api/v1/artikel/individuelle-nummern'

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('dev_bypass_auth', 'true')
  })
})

test.describe('Fachliche Vertiefung Gate: Individuelle Artikelnummern (Wave 24)', () => {
  test('Zuordnung anlegen und Lookup', async ({ page }) => {
    const requests: string[] = []

    let nummern: IndivArtikelNr[] = [
      {
        id: 'ian-1',
        artikel_nr: '100234',
        partner_nr: 'K001',
        partner_typ: 'kunden',
        indiv_artikel_nr: 'K-MAIS-01',
        indiv_bezeichnung: 'Mais Premium Kunde',
        gueltig_von: '2026-01-01',
        gueltig_bis: null,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/artikel/individuelle-nummern**', async (route) => {
      const request = route.request()
      const url = new URL(request.url())
      const pathname = url.pathname
      requests.push(`${request.method()} ${pathname}${url.search}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'DELETE') {
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
        return
      }

      if (request.method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(nummern),
        })
        return
      }

      if (request.method() === 'POST') {
        const payload = request.postDataJSON() as Partial<IndivArtikelNr>
        const created: IndivArtikelNr = {
          id: `ian-${Date.now()}`,
          artikel_nr: payload.artikel_nr ?? '',
          partner_nr: payload.partner_nr ?? '',
          partner_typ: payload.partner_typ ?? 'kunden',
          indiv_artikel_nr: payload.indiv_artikel_nr ?? '',
          indiv_bezeichnung: payload.indiv_bezeichnung ?? null,
          gueltig_von: payload.gueltig_von ?? null,
          gueltig_bis: payload.gueltig_bis ?? null,
          aktiv: true,
          created_at: createdAt,
        }
        nummern = [...nummern, created]
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(created),
        })
        return
      }

      await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
    })

    await page.route('**/api/v1/artikel/individuelle-nummern/lookup**', async (route) => {
      const request = route.request()
      const url = new URL(request.url())
      requests.push(`${request.method()} ${url.pathname}${url.search}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      const indiv = url.searchParams.get('indiv_artikel_nr')
      if (indiv === 'K-NEU-99') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify({
            interne_artikel_nr: '100999',
            indiv_bezeichnung: 'Neu angelegt',
          }),
        })
        return
      }
      await route.fulfill({ status: 404, headers: corsHeaders, body: '{"detail":"not found"}' })
    })

    await page.goto('/stammdaten/individuelle-artikelnummern', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /Individuelle Artikelnummern/ })).toBeVisible()
    await expect(page.getByText('K-MAIS-01')).toBeVisible()

    await page.locator('#ian_artikel_nr').fill('100999')
    await page.locator('#ian_partner_nr').fill('K001')
    await page.locator('#ian_indiv_nr').fill('K-NEU-99')
    await page.locator('#ian_bezeichnung').fill('Neu angelegt')

    await page.locator('[data-testid="ian-form"]').getByRole('button', { name: 'Anlegen' }).click()
    await expect(page.getByText('K-NEU-99')).toBeVisible()

    await page.locator('#lookup_partner_nr').fill('K001')
    await page.locator('#lookup_indiv_nr').fill('K-NEU-99')
    await page.getByRole('button', { name: 'Interne Artikelnummer suchen' }).click()
    await expect(page.getByTestId('ian-lookup-result')).toContainText('100999', { timeout: 15_000 })

    expect(requests.some((r) => r.startsWith(`GET ${BASE}`))).toBe(true)
    expect(requests.some((r) => r.startsWith(`POST ${BASE}`))).toBe(true)
    expect(requests.some((r) => r.startsWith(`GET ${BASE}/lookup`))).toBe(true)
  })
})
