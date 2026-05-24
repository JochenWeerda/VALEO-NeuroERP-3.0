import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Zahlungsbedingung = {
  id: string
  zabd_nr: string
  bezeichnung: string
  zahlungsziel_tage: number
  skonto1_tage: number | null
  skonto1_prozent: number | null
  skonto2_tage: number | null
  skonto2_prozent: number | null
  netto_tage: number | null
  manuelles_datum: boolean
  zahlungsart: string
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-23T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Zahlungsbedingungen CRUD', () => {
  test('nutzt FIBU-API und bedient Create/Update/Delete sichtbar', async ({ page }) => {
    const requests: string[] = []
    let rows: Zahlungsbedingung[] = [
      {
        id: 'zabd-1',
        zabd_nr: 'Z30',
        bezeichnung: '30 Tage netto',
        zahlungsziel_tage: 30,
        skonto1_tage: null,
        skonto1_prozent: null,
        skonto2_tage: null,
        skonto2_prozent: null,
        netto_tage: 30,
        manuelles_datum: false,
        zahlungsart: 'ueberweisung',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/fibu/zahlungsbedingungen', async (route) => {
      const request = route.request()
      const pathname = new URL(request.url()).pathname
      if (pathname !== '/api/v1/fibu/zahlungsbedingungen') {
        await route.fallback()
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
          body: JSON.stringify(rows),
        })
        return
      }

      if (request.method() === 'POST') {
        const payload = request.postDataJSON() as Omit<Zahlungsbedingung, 'id' | 'aktiv' | 'created_at'>
        const created: Zahlungsbedingung = {
          id: `zabd-${payload.zabd_nr.toLowerCase()}`,
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

    await page.route('**/api/v1/fibu/zahlungsbedingungen/*', async (route) => {
      const request = route.request()
      const zabdNr = decodeURIComponent(new URL(request.url()).pathname.split('/').pop() ?? '')
      requests.push(`${request.method()} ${new URL(request.url()).pathname}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'PUT') {
        const payload = request.postDataJSON() as Omit<Zahlungsbedingung, 'id' | 'aktiv' | 'created_at'>
        rows = rows.map((row) => (row.zabd_nr === zabdNr ? { ...row, ...payload } : row))
        const updated = rows.find((row) => row.zabd_nr === zabdNr)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(updated),
        })
        return
      }

      if (request.method() === 'DELETE') {
        rows = rows.filter((row) => row.zabd_nr !== zabdNr)
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

    await page.goto('/einkauf/zahlungsbedingungen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page).toHaveURL(/\/einkauf\/zahlungsbedingungen($|\?)/)
    await expect(page.getByRole('heading', { name: /^Zahlungsbedingungen$/ })).toBeVisible()
    await expect(page.getByText('30 Tage netto')).toBeVisible()

    await page.getByLabel('ZABD-Nr.').fill('Z14')
    await page.getByLabel('Bezeichnung', { exact: true }).fill('14 Tage 2% Skonto')
    await page.getByLabel('Skonto 1 (Tage)').fill('14')
    await page.getByLabel('Skonto 1 (%)').fill('2')
    await page.getByRole('button', { name: 'Zahlungsbedingung speichern' }).click()
    await expect(page.getByText('14 Tage 2% Skonto')).toBeVisible()

    await page.getByRole('button', { name: 'Z30 bearbeiten' }).first().click()
    await page.getByLabel('Bezeichnung', { exact: true }).fill('30 Tage netto A')
    await page.getByRole('button', { name: 'Zahlungsbedingung speichern' }).click()
    await expect(page.getByText('30 Tage netto A')).toBeVisible()

    await page.getByRole('button', { name: 'Z14 deaktivieren' }).click()
    await expect(page.getByText('14 Tage 2% Skonto')).toHaveCount(0)

    expect(requests).toContain('GET /api/v1/fibu/zahlungsbedingungen')
    expect(requests).toContain('POST /api/v1/fibu/zahlungsbedingungen')
    expect(requests).toContain('PUT /api/v1/fibu/zahlungsbedingungen/Z30')
    expect(requests).toContain('DELETE /api/v1/fibu/zahlungsbedingungen/Z14')
  })
})
