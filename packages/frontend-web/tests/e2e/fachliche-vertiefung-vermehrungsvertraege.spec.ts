import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Vermehrungsvertrag = {
  id: string
  vertrag_nr: string
  erntejahr: number
  vermehrer_kunden_nr: string
  sorte_nr: string | null
  sorte_bezeichnung: string | null
  kategorie: string | null
  vertrags_menge_t: number | null
  anbauflaeche_ha: number | null
  lwk_anerkennungsstelle: string | null
  vmkz: string | null
  status: 'angelegt' | 'aktiv' | 'beendet' | 'storniert'
  created_at: string
}

const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PATCH,DELETE,OPTIONS',
}

const createdAt = '2026-05-26T08:00:00'
const isCollection = (url: URL) => url.pathname === '/api/v1/saatzucht/vermehrungsvertraege'
const isItem = (url: URL) => /^\/api\/v1\/saatzucht\/vermehrungsvertraege\/[^/]+$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Vermehrungsverträge (Wave 21)', () => {
  test('Vermehrungsvertrag anlegen', async ({ page }) => {
    const requests: string[] = []

    let vertraege: Vermehrungsvertrag[] = [
      {
        id: 'vv-1',
        vertrag_nr: 'VV-2026-001',
        erntejahr: 2026,
        vermehrer_kunden_nr: 'KD-BAUER',
        sorte_nr: 'SORT-01',
        sorte_bezeichnung: 'Leibniz GW 2300',
        kategorie: 'Z1',
        vertrags_menge_t: 50.0,
        anbauflaeche_ha: 10.5,
        lwk_anerkennungsstelle: 'LWK-NDS',
        vmkz: 'VMKZ-01',
        status: 'aktiv',
        created_at: createdAt,
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
            body: JSON.stringify(vertraege),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Partial<Vermehrungsvertrag>
          const created: Vermehrungsvertrag = {
            id: `vv-${Date.now()}`,
            vertrag_nr: payload.vertrag_nr ?? 'VV-NEW',
            erntejahr: payload.erntejahr ?? 2026,
            vermehrer_kunden_nr: payload.vermehrer_kunden_nr ?? '',
            sorte_nr: payload.sorte_nr ?? null,
            sorte_bezeichnung: payload.sorte_bezeichnung ?? null,
            kategorie: payload.kategorie ?? null,
            vertrags_menge_t: payload.vertrags_menge_t ?? null,
            anbauflaeche_ha: payload.anbauflaeche_ha ?? null,
            lwk_anerkennungsstelle: payload.lwk_anerkennungsstelle ?? null,
            vmkz: payload.vmkz ?? null,
            status: 'angelegt',
            created_at: createdAt,
          }
          vertraege = [...vertraege, created]
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

    await page.goto('/agrar/vermehrungsvertraege', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.locator('#vv_vertrag_nr')).toBeVisible({ timeout: 30000 })
    await expect(page.getByText('Leibniz GW 2300')).toBeVisible()

    await page.locator('#vv_vertrag_nr').fill('VV-2026-002')
    await page.locator('#vv_erntejahr').fill('2026')
    await page.locator('#vv_vermehrer').fill('KD-NEUER')
    await page.locator('#vv_sorte_bez').fill('Testsorte Bravo')

    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('Testsorte Bravo')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/saatzucht/vermehrungsvertraege'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/saatzucht/vermehrungsvertraege'))).toBe(true)
  })
})
