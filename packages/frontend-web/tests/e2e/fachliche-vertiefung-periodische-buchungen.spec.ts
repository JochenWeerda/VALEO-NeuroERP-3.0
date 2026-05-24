import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type PeriodischeBuchung = {
  id: string
  bezeichnung: string
  vorgangsklasse: string
  konto: string
  gegenkonto: string
  buchungstext: string | null
  betrag: string
  turnus: string
  gueltig_ab: string
  gueltig_bis: string | null
  gesperrt: boolean
  kostenstelle: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PATCH,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Periodische Buchungen (Wave 11)', () => {
  test('nutzt WZA-API inkl. Faellig sichtbar', async ({ page }) => {
    const requests: string[] = []
    let rows: PeriodischeBuchung[] = [
      {
        id: 'wza-1',
        bezeichnung: 'Miete Buero',
        vorgangsklasse: 'ZA',
        konto: '4210',
        gegenkonto: '1200',
        buchungstext: 'Monatsmiete',
        betrag: '1500.00',
        turnus: 'monatlich',
        gueltig_ab: '2026-01-01',
        gueltig_bis: null,
        gesperrt: false,
        kostenstelle: null,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(/\/api\/v1\/fibu\/periodische-buchungen/, async (route) => {
      const request = route.request()
      const url = new URL(request.url())
      const pathname = url.pathname
      requests.push(`${request.method()} ${pathname}${url.search}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (pathname === '/api/v1/fibu/periodische-buchungen/faellig') {
        if (request.method() === 'GET') {
          const faellig = rows.filter((r) => !r.gesperrt).map((r) => ({
            id: r.id,
            bezeichnung: r.bezeichnung,
            konto: r.konto,
            gegenkonto: r.gegenkonto,
            betrag: r.betrag,
            vorgangsklasse: r.vorgangsklasse,
            turnus: r.turnus,
            gueltig_ab: r.gueltig_ab,
          }))
          await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(faellig) })
          return
        }
      }

      if (pathname === '/api/v1/fibu/periodische-buchungen') {
        if (request.method() === 'GET') {
          await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(rows) })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as PeriodischeBuchung
          const created: PeriodischeBuchung = {
            id: 'wza-2',
            bezeichnung: payload.bezeichnung,
            vorgangsklasse: payload.vorgangsklasse ?? 'ZA',
            konto: payload.konto,
            gegenkonto: payload.gegenkonto,
            buchungstext: payload.buchungstext ?? null,
            betrag: String(payload.betrag),
            turnus: payload.turnus ?? 'monatlich',
            gueltig_ab: payload.gueltig_ab,
            gueltig_bis: payload.gueltig_bis ?? null,
            gesperrt: payload.gesperrt ?? false,
            kostenstelle: payload.kostenstelle ?? null,
            aktiv: true,
            created_at: createdAt,
          }
          rows = [...rows, created]
          await route.fulfill({ status: 201, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify(created) })
          return
        }
      }

      if (pathname.endsWith('/sperren')) {
        const id = pathname.split('/')[4]
        if (request.method() === 'PATCH') {
          const gesperrt = url.searchParams.get('gesperrt') === 'true'
          rows = rows.map((r) => (r.id === id ? { ...r, gesperrt } : r))
          await route.fulfill({ status: 200, contentType: 'application/json', headers: corsHeaders, body: JSON.stringify({ id, gesperrt }) })
          return
        }
      }

      const id = pathname.split('/')[4]
      if (id && request.method() === 'DELETE') {
        rows = rows.filter((r) => r.id !== id)
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
        return
      }

      await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
    })

    await page.goto('/fibu/periodische-buchungen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByRole('heading', { name: /^Periodische Buchungen$/ })).toBeVisible()
    await expect(page.getByText('Miete Buero').first()).toBeVisible()

    await page.locator('#wza-bez').fill('Versicherung')
    await page.locator('#wza-konto').fill('4360')
    await page.locator('#wza-gkonto').fill('1200')
    await page.locator('#wza-betrag').fill('250')
    await page.getByRole('button', { name: 'Speichern' }).click()
    await expect(page.getByText('Versicherung').first()).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/fibu/periodische-buchungen/faellig'))).toBe(true)
    expect(requests.some((r) => r.startsWith('GET /api/v1/fibu/periodische-buchungen') && !r.includes('faellig'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/fibu/periodische-buchungen'))).toBe(true)
  })
})
