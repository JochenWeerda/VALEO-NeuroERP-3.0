import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Partiegruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  aktiv: boolean
  created_at: string
}

type Partiestamm = {
  id: string
  partie_nr: string
  bezeichnung: string | null
  artikel_nr: string
  lager_nr: string | null
  partie_typ: string
  gruppe_id: string | null
  erntejahr: number | null
  herkunftsland: string | null
  status: string
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Partiestamm (Wave 11)', () => {
  test('nutzt Lager-Partien-API sichtbar', async ({ page }) => {
    const requests: string[] = []
    let gruppen: Partiegruppe[] = [
      { id: 'pgr-1', gruppe_nr: 'PG-GET', bezeichnung: 'Getreide', aktiv: true, created_at: createdAt },
    ]
    let partien: Partiestamm[] = [
      {
        id: 'par-1',
        partie_nr: 'PAR-000001',
        bezeichnung: 'Weizen 2024',
        artikel_nr: 'WEIZEN-A',
        lager_nr: null,
        partie_typ: 'artikelstamm',
        gruppe_id: 'pgr-1',
        erntejahr: 2024,
        herkunftsland: 'DE',
        status: 'aktiv',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(/\/api\/v1\/lager\/partien/, async (route) => {
      const request = route.request()
      const url = new URL(request.url())
      const pathname = url.pathname
      requests.push(`${request.method()} ${pathname}${url.search}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (pathname === '/api/v1/lager/partien/gruppen') {
        if (request.method() === 'GET') {
          await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(gruppen) })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<Partiegruppe, 'gruppe_nr' | 'bezeichnung'>
          const created = { id: 'pgr-2', ...payload, aktiv: true, created_at: createdAt }
          gruppen = [...gruppen, created]
          await route.fulfill({ status: 201, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(created) })
          return
        }
      }

      if (pathname.startsWith('/api/v1/lager/partien/gruppen/')) {
        const nr = decodeURIComponent(pathname.split('/').pop() ?? '')
        if (request.method() === 'DELETE') {
          gruppen = gruppen.filter((g) => g.gruppe_nr !== nr)
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
      }

      if (pathname === '/api/v1/lager/partien') {
        if (request.method() === 'GET') {
          await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(partien) })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Partiestamm
          const created: Partiestamm = {
            id: 'par-2',
            partie_nr: 'PAR-000002',
            bezeichnung: payload.bezeichnung ?? null,
            artikel_nr: payload.artikel_nr,
            lager_nr: payload.lager_nr ?? null,
            partie_typ: payload.partie_typ ?? 'artikelstamm',
            gruppe_id: payload.gruppe_id ?? null,
            erntejahr: payload.erntejahr ?? null,
            herkunftsland: payload.herkunftsland ?? null,
            status: 'aktiv',
            aktiv: true,
            created_at: createdAt,
          }
          partien = [...partien, created]
          await route.fulfill({ status: 201, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(created) })
          return
        }
      }

      if (pathname.startsWith('/api/v1/lager/partien/') && pathname.endsWith('/status')) {
        const nr = decodeURIComponent(pathname.split('/')[4] ?? '')
        if (request.method() === 'PATCH') {
          const status = url.searchParams.get('status') ?? 'gesperrt'
          partien = partien.map((p) => (p.partie_nr === nr ? { ...p, status } : p))
          await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify({ partie_nr: nr, status }) })
          return
        }
      }

      if (pathname.startsWith('/api/v1/lager/partien/') && !pathname.includes('/gruppen')) {
        const nr = decodeURIComponent(pathname.split('/').pop() ?? '')
        if (request.method() === 'DELETE') {
          partien = partien.filter((p) => p.partie_nr !== nr)
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
      }

      await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
    })

    await page.goto('/lager/partiestamm', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /^Partiestamm$/ })).toBeVisible()
    await expect(page.getByText('Weizen 2024')).toBeVisible()

    await page.locator('#par-artikel').fill('GERSTE-B')
    await page.locator('#par-bez').fill('Gerste Partie')
    await page.getByRole('button', { name: 'Partie speichern' }).click()
    await expect(page.getByText('Gerste Partie')).toBeVisible()

    await page.locator('#pgr-nr').fill('PG-NEU')
    await page.locator('#pgr-bez').fill('Neue Gruppe')
    await page.getByRole('button', { name: 'Gruppe anlegen' }).click()
    await expect(page.getByRole('cell', { name: 'PG-NEU', exact: true })).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/lager/partien') && !r.includes('gruppen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('GET /api/v1/lager/partien/gruppen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/lager/partien') && !r.includes('gruppen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/lager/partien/gruppen'))).toBe(true)
  })
})
