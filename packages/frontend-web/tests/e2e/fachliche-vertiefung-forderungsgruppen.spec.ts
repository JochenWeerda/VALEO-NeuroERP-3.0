import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Forderungsgruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  konto_forderungen: string | null
  konto_verbindlichkeiten: string | null
  konto_sammel_1: string | null
  konto_sammel_2: string | null
  konto_sammel_3: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Forderungsgruppen (Wave 11)', () => {
  test('nutzt FIBU-Forderungsgruppen-API sichtbar', async ({ page }) => {
    const requests: string[] = []
    let rows: Forderungsgruppe[] = [
      {
        id: 'forg-1',
        gruppe_nr: 'LAND',
        bezeichnung: 'Landwirte',
        konto_forderungen: '1200',
        konto_verbindlichkeiten: null,
        konto_sammel_1: null,
        konto_sammel_2: null,
        konto_sammel_3: null,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/fibu/forderungsgruppen', async (route) => {
      const request = route.request()
      requests.push(`${request.method()} ${new URL(request.url()).pathname}`)
      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }
      if (request.method() === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(rows) })
        return
      }
      if (request.method() === 'POST') {
        const payload = request.postDataJSON() as Pick<Forderungsgruppe, 'gruppe_nr' | 'bezeichnung' | 'konto_forderungen'>
        const created: Forderungsgruppe = {
          id: 'forg-2',
          gruppe_nr: payload.gruppe_nr,
          bezeichnung: payload.bezeichnung,
          konto_forderungen: payload.konto_forderungen ?? null,
          konto_verbindlichkeiten: null,
          konto_sammel_1: null,
          konto_sammel_2: null,
          konto_sammel_3: null,
          aktiv: true,
          created_at: createdAt,
        }
        rows = [...rows, created]
        await route.fulfill({ status: 201, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(created) })
        return
      }
      await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
    })

    await page.route('**/api/v1/fibu/forderungsgruppen/*', async (route) => {
      const request = route.request()
      const pathname = new URL(request.url()).pathname
      const nr = decodeURIComponent(pathname.split('/').pop() ?? '')
      requests.push(`${request.method()} ${pathname}`)
      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }
      if (request.method() === 'PUT') {
        const payload = request.postDataJSON() as Pick<Forderungsgruppe, 'bezeichnung'>
        rows = rows.map((r) => (r.gruppe_nr === nr ? { ...r, ...payload } : r))
        const updated = rows.find((r) => r.gruppe_nr === nr)
        await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(updated) })
        return
      }
      if (request.method() === 'DELETE') {
        rows = rows.filter((r) => r.gruppe_nr !== nr)
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
        return
      }
      await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
    })

    await page.goto('/fibu/forderungsgruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /^Forderungsgruppen$/ })).toBeVisible()
    await expect(page.getByText('Landwirte')).toBeVisible()

    await page.locator('#forg-nr').fill('GROSS')
    await page.locator('#forg-bez').fill('Grosskunden')
    await page.locator('#forg-kf').fill('1400')
    await page.getByRole('button', { name: 'Speichern' }).click()
    await expect(page.getByText('Grosskunden')).toBeVisible()

    await page.getByRole('button', { name: 'LAND bearbeiten' }).click()
    await page.locator('#forg-bez').fill('Landwirte A')
    await page.getByRole('button', { name: 'Speichern' }).click()
    await expect(page.getByText('Landwirte A')).toBeVisible()

    expect(requests).toContain('GET /api/v1/fibu/forderungsgruppen')
    expect(requests).toContain('POST /api/v1/fibu/forderungsgruppen')
    expect(requests).toContain('PUT /api/v1/fibu/forderungsgruppen/LAND')
  })
})
