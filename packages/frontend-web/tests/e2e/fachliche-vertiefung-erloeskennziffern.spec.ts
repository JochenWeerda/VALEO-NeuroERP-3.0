import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Erloeskennziffer = {
  id: string
  ekz_nr: string
  bezeichnung: string
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-23T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Erlöskennziffern CRUD', () => {
  test('nutzt FIBU-API und bedient Create/Update/Delete sichtbar', async ({ page }) => {
    const requests: string[] = []
    let rows: Erloeskennziffer[] = [
      {
        id: 'ekz-1',
        ekz_nr: 'EKZ01',
        bezeichnung: 'Warenverkauf Inland',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/fibu/erloeskennziffern', async (route) => {
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
        const payload = request.postDataJSON() as Pick<Erloeskennziffer, 'ekz_nr' | 'bezeichnung'>
        const created: Erloeskennziffer = {
          id: `ekz-${payload.ekz_nr.toLowerCase()}`,
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

    await page.route('**/api/v1/fibu/erloeskennziffern/*', async (route) => {
      const request = route.request()
      const ekzNr = decodeURIComponent(new URL(request.url()).pathname.split('/').pop() ?? '')
      requests.push(`${request.method()} ${new URL(request.url()).pathname}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'PUT') {
        const payload = request.postDataJSON() as Pick<Erloeskennziffer, 'ekz_nr' | 'bezeichnung'>
        rows = rows.map((row) => (row.ekz_nr === ekzNr ? { ...row, ...payload } : row))
        const updated = rows.find((row) => row.ekz_nr === ekzNr)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(updated),
        })
        return
      }

      if (request.method() === 'DELETE') {
        rows = rows.filter((row) => row.ekz_nr !== ekzNr)
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

    await page.goto('/fibu/erloeskennziffern', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page).toHaveURL(/\/fibu\/erloeskennziffern($|\?)/)
    await expect(page.getByRole('heading', { name: /^Erlöskennziffern$/ })).toBeVisible()
    await expect(page.getByText('Warenverkauf Inland')).toBeVisible()

    await page.getByLabel('EKZ-Nummer').fill('EKZ02')
    await page.getByLabel('Bezeichnung', { exact: true }).fill('Dienstleistung')
    await page.getByRole('button', { name: 'Erlöskennziffer speichern' }).click()
    await expect(page.getByText('Dienstleistung')).toBeVisible()

    await page.getByRole('button', { name: 'EKZ01 bearbeiten' }).first().click()
    await page.getByLabel('Bezeichnung', { exact: true }).fill('Warenverkauf Inland A')
    await page.getByRole('button', { name: 'Erlöskennziffer speichern' }).click()
    await expect(page.getByText('Warenverkauf Inland A')).toBeVisible()

    await page.getByRole('button', { name: 'EKZ02 deaktivieren' }).click()
    await expect(page.getByText('Dienstleistung')).toHaveCount(0)

    expect(requests).toContain('GET /api/v1/fibu/erloeskennziffern')
    expect(requests).toContain('POST /api/v1/fibu/erloeskennziffern')
    expect(requests).toContain('PUT /api/v1/fibu/erloeskennziffern/EKZ01')
    expect(requests).toContain('DELETE /api/v1/fibu/erloeskennziffern/EKZ02')
  })
})
