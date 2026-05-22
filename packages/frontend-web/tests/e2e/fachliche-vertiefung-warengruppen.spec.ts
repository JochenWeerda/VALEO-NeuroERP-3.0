import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Warengruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  ober_id: string
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-22T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Warengruppen CRUD', () => {
  test('nutzt Stammdaten-API und bedient Create/Update/Delete sichtbar', async ({ page }) => {
    const requests: string[] = []
    let rows: Warengruppe[] = [
      {
        id: 'wg-1',
        gruppe_nr: 'WG01',
        bezeichnung: 'Brotgetreide',
        ober_id: 'owg-1',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/stammdaten/warengruppen', async (route) => {
      const request = route.request()
      requests.push(`${request.method()} ${new URL(request.url()).pathname}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(rows),
        })
        return
      }

      if (request.method() === 'POST') {
        const payload = request.postDataJSON() as Pick<Warengruppe, 'gruppe_nr' | 'bezeichnung' | 'ober_id'>
        const created: Warengruppe = {
          id: `wg-${payload.gruppe_nr.toLowerCase()}`,
          ...payload,
          aktiv: true,
          created_at: createdAt,
        }
        rows = [...rows, created]
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

    await page.route('**/api/v1/stammdaten/warengruppen/*', async (route) => {
      const request = route.request()
      const gruppeNr = decodeURIComponent(new URL(request.url()).pathname.split('/').pop() ?? '')
      requests.push(`${request.method()} ${new URL(request.url()).pathname}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'PUT') {
        const payload = request.postDataJSON() as Pick<Warengruppe, 'gruppe_nr' | 'bezeichnung' | 'ober_id'>
        rows = rows.map((row) => (row.gruppe_nr === gruppeNr ? { ...row, ...payload } : row))
        const updated = rows.find((row) => row.gruppe_nr === gruppeNr)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(updated),
        })
        return
      }

      if (request.method() === 'DELETE') {
        rows = rows.filter((row) => row.gruppe_nr !== gruppeNr)
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
        return
      }

      await route.fulfill({
        status: 405,
        contentType: 'application/json',
        headers: corsHeaders,
        body: '{"detail":"method"}',
      })
    })

    await page.goto('/einkauf/warengruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page).toHaveURL(/\/einkauf\/warengruppen($|\?)/)
    await expect(page.getByRole('heading', { name: /^Warengruppen$/ })).toBeVisible()
    await expect(page.getByText('Stammdaten - 3-stufige Warengruppenhierarchie')).toBeVisible()
    await expect(page.getByText('Brotgetreide')).toBeVisible()
    await expect(page.getByText('Jahresumsatz')).toHaveCount(0)

    await page.getByPlaceholder('Nummer', { exact: true }).fill('WG02')
    await page.getByPlaceholder('Bezeichnung', { exact: true }).fill('Futtergetreide')
    await page.getByPlaceholder('Oberwarengruppe-ID').fill('owg-2')
    await page.getByRole('button', { name: 'Warengruppe speichern' }).click()
    await expect(page.getByText('Futtergetreide')).toBeVisible()

    await page.getByRole('button', { name: 'WG01 bearbeiten' }).click()
    await page.getByPlaceholder('Bezeichnung', { exact: true }).fill('Brotgetreide A')
    await page.getByRole('button', { name: 'Warengruppe speichern' }).click()
    await expect(page.getByText('Brotgetreide A')).toBeVisible()

    await page.getByRole('button', { name: 'WG02 deaktivieren' }).click()
    await expect(page.getByText('Futtergetreide')).toHaveCount(0)

    expect(requests).toContain('GET /api/v1/stammdaten/warengruppen')
    expect(requests).toContain('POST /api/v1/stammdaten/warengruppen')
    expect(requests).toContain('PUT /api/v1/stammdaten/warengruppen/WG01')
    expect(requests).toContain('DELETE /api/v1/stammdaten/warengruppen/WG02')
  })
})
