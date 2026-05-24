import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Erloeskennziffer = {
  id: string
  ekz_nr: string
  bezeichnung: string
  aktiv: boolean
  created_at: string
}

type Erloeskontenzuordnung = {
  id: string
  ekz_id: string
  gueltig_ab: string
  steuerschluessel: string | null
  erlösklasse: string | null
  steuergruppe: string | null
  buchungsklasse: string | null
  konto_erloese: string | null
  konto_aufwand: string | null
  konto_umsatzsteuer: string | null
  konto_vorsteuer: string | null
  created_at: string
}

const createdAt = '2026-05-23T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Erlöskontenzuordnung (EKZZ)', () => {
  test('nutzt Zuordnungen- und Lookup-API sichtbar', async ({ page }) => {
    const requests: string[] = []

    const ekzRows: Erloeskennziffer[] = [
      {
        id: 'ekz-1',
        ekz_nr: 'EKZ01',
        bezeichnung: 'Warenverkauf Inland',
        aktiv: true,
        created_at: createdAt,
      },
      {
        id: 'ekz-2',
        ekz_nr: 'EKZ02',
        bezeichnung: 'Dienstleistung',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    let zuordnungen: Erloeskontenzuordnung[] = [
      {
        id: 'ekzz-1',
        ekz_id: 'ekz-1',
        gueltig_ab: '2026-01-01',
        steuerschluessel: '19',
        erlösklasse: 'INLAND',
        steuergruppe: null,
        buchungsklasse: null,
        konto_erloese: '8400',
        konto_aufwand: '3400',
        konto_umsatzsteuer: '1776',
        konto_vorsteuer: null,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/fibu/erloeskennziffern/zuordnungen**', async (route) => {
      const request = route.request()
      requests.push(`${request.method()} ${new URL(request.url()).pathname}${new URL(request.url()).search}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'GET') {
        const url = new URL(request.url())
        const ekzFilter = url.searchParams.get('ekz_id')
        const skFilter = url.searchParams.get('steuerschluessel')
        let filtered = zuordnungen
        if (ekzFilter) filtered = filtered.filter((row) => row.ekz_id === ekzFilter)
        if (skFilter) filtered = filtered.filter((row) => row.steuerschluessel === skFilter)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(filtered),
        })
        return
      }

      if (request.method() === 'POST') {
        const payload = request.postDataJSON() as Omit<Erloeskontenzuordnung, 'id' | 'created_at'>
        const existing = zuordnungen.find(
          (row) =>
            row.ekz_id === payload.ekz_id &&
            row.gueltig_ab === payload.gueltig_ab &&
            row.steuerschluessel === (payload.steuerschluessel ?? null),
        )
        if (existing) {
          const updated = { ...existing, ...payload }
          zuordnungen = zuordnungen.map((row) => (row.id === existing.id ? updated : row))
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(updated),
          })
          return
        }
        const created: Erloeskontenzuordnung = {
          id: `ekzz-${zuordnungen.length + 1}`,
          ...payload,
          created_at: createdAt,
        }
        zuordnungen = [...zuordnungen, created]
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(created),
        })
        return
      }

      await route.fulfill({
        status: 405,
        contentType: 'application/json',
        headers: corsHeaders,
        body: '{"detail":"method"}',
      })
    })

    await page.route('**/api/v1/fibu/erloeskennziffern/lookup**', async (route) => {
      const request = route.request()
      requests.push(`${request.method()} ${new URL(request.url()).pathname}${new URL(request.url()).search}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'GET') {
        const url = new URL(request.url())
        const ekzNr = url.searchParams.get('ekz_nr')
        const match = zuordnungen.find((row) => {
          const ekz = ekzRows.find((e) => e.id === row.ekz_id)
          return ekz?.ekz_nr === ekzNr
        })
        if (!match) {
          await route.fulfill({
            status: 404,
            contentType: 'application/json',
            headers: corsHeaders,
            body: '{"detail":"not found"}',
          })
          return
        }
        const ekz = ekzRows.find((e) => e.id === match.ekz_id)!
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify({
            ekz_nr: ekz.ekz_nr,
            gueltig_ab: match.gueltig_ab,
            konto_erloese: match.konto_erloese,
            konto_aufwand: match.konto_aufwand,
            konto_umsatzsteuer: match.konto_umsatzsteuer,
            konto_vorsteuer: match.konto_vorsteuer,
          }),
        })
        return
      }

      await route.fulfill({
        status: 405,
        contentType: 'application/json',
        headers: corsHeaders,
        body: '{"detail":"method"}',
      })
    })

    await page.route('**/api/v1/fibu/erloeskennziffern', async (route) => {
      const request = route.request()
      const pathname = new URL(request.url()).pathname
      if (pathname !== '/api/v1/fibu/erloeskennziffern') {
        await route.continue()
        return
      }
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
          body: JSON.stringify(ekzRows),
        })
        return
      }

      await route.fulfill({
        status: 405,
        contentType: 'application/json',
        headers: corsHeaders,
        body: '{"detail":"method"}',
      })
    })

    await page.goto('/fibu/erloeskontenzuordnung', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page).toHaveURL(/\/fibu\/erloeskontenzuordnung($|\?)/)
    await expect(page.getByRole('heading', { name: /^Erlöskontenzuordnung$/ })).toBeVisible()
    await expect(page.getByText('8400')).toBeVisible()

    await page.locator('#ekz-id').selectOption('ekz-2')
    await page.getByLabel('Gueltig ab').fill('2026-06-01')
    await page.locator('#steuerschluessel').fill('7')
    await page.locator('#konto-erloese').fill('8500')
    await page.getByRole('button', { name: 'Zuordnung speichern' }).click()
    await expect(page.getByText('8500')).toBeVisible()

    await page.getByRole('button', { name: 'Zuordnung ekzz-1 bearbeiten' }).click()
    await page.locator('#konto-erloese').fill('8410')
    await page.getByRole('button', { name: 'Zuordnung speichern' }).click()
    await expect(page.getByText('8410')).toBeVisible()

    await page.getByLabel('Steuerschluessel filtern').fill('19')
    await expect(page.getByText('8410')).toBeVisible()
    await expect(page.getByText('8500')).toHaveCount(0)

    await page.locator('#lookup-ekz').selectOption('EKZ01')
    await page.getByRole('button', { name: 'Kontenlookup ausfuehren' }).click()
    await expect(page.getByText('Erloeskonto:').locator('..')).toContainText('8410')

    expect(requests.some((entry) => entry.startsWith('GET /api/v1/fibu/erloeskennziffern/zuordnungen'))).toBe(true)
    expect(requests.some((entry) => entry.startsWith('POST /api/v1/fibu/erloeskennziffern/zuordnungen'))).toBe(true)
    expect(requests.some((entry) => entry.startsWith('GET /api/v1/fibu/erloeskennziffern/lookup'))).toBe(true)
    expect(requests).toContain('GET /api/v1/fibu/erloeskennziffern')
  })
})
