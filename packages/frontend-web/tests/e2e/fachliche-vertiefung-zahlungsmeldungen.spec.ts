import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Zahlungsmeldung = {
  id: string
  meldungs_nr: string
  kunden_nr: string
  rechnungs_nr: string | null
  zahlungsdatum: string
  zahlungsbetrag_eur: number
  skonto_betrag_eur: number
  skonto_erlaubt: boolean
  teilzahlung: boolean
  aus_fibu: boolean
  status: 'eingegangen' | 'verarbeitet' | 'abgewiesen'
  verarbeitet_am: string | null
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const isZMCollection = (url: URL) =>
  url.pathname === '/api/v1/fibu/zahlungsmeldungen'
const isZMItem = (url: URL) =>
  /^\/api\/v1\/fibu\/zahlungsmeldungen\/[^/]+$/.test(url.pathname)
const isZMVerarbeiten = (url: URL) =>
  /^\/api\/v1\/fibu\/zahlungsmeldungen\/[^/]+\/verarbeiten$/.test(url.pathname)

test.describe('Fachliche Vertiefung Gate: Zahlungsmeldungen (Wave 18)', () => {
  test('Zahlungsmeldung anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let meldungen: Zahlungsmeldung[] = [
      {
        id: 'zm-1',
        meldungs_nr: 'ZM-2025-001',
        kunden_nr: 'KD-001',
        rechnungs_nr: 'RE-2025-001',
        zahlungsdatum: '2025-03-15',
        zahlungsbetrag_eur: 1500.0,
        skonto_betrag_eur: 30.0,
        skonto_erlaubt: true,
        teilzahlung: false,
        aus_fibu: false,
        status: 'eingegangen',
        verarbeitet_am: null,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isZMCollection(new URL(url)),
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
            body: JSON.stringify(meldungen),
          })
          return
        }
        if (request.method() === 'POST') {
          const payload = request.postDataJSON() as Pick<
            Zahlungsmeldung,
            'kunden_nr' | 'zahlungsdatum' | 'zahlungsbetrag_eur'
          >
          const created: Zahlungsmeldung = {
            id: `zm-${Date.now()}`,
            meldungs_nr: `ZM-2025-00${meldungen.length + 1}`,
            kunden_nr: payload.kunden_nr,
            rechnungs_nr: null,
            zahlungsdatum: payload.zahlungsdatum,
            zahlungsbetrag_eur: payload.zahlungsbetrag_eur,
            skonto_betrag_eur: 0,
            skonto_erlaubt: false,
            teilzahlung: false,
            aus_fibu: false,
            status: 'eingegangen',
            verarbeitet_am: null,
            created_at: createdAt,
          }
          meldungen = [...meldungen, created]
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
      (url) => isZMItem(new URL(url)) && !isZMVerarbeiten(new URL(url)),
      async (route) => {
        const request = route.request()
        const pathname = new URL(request.url()).pathname
        requests.push(`${request.method()} ${pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (request.method() === 'DELETE') {
          const id = pathname.split('/').pop() ?? ''
          meldungen = meldungen.filter((m) => m.id !== id)
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.goto('/fibu/zahlungsmeldungen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(
      page.getByRole('heading', { name: /Zahlungsmeldungen/, exact: false }).first()
    ).toBeVisible()
    await expect(page.getByText('ZM-2025-001')).toBeVisible()
    await expect(page.getByText('KD-001')).toBeVisible()

    await page.locator('#zm_kunden_nr').fill('KD-002')
    await page.locator('#zm_zahlungsdatum').fill('2025-04-01')
    await page.locator('#zm_betrag').fill('2500.00')
    await page.getByRole('button', { name: 'Anlegen' }).first().click()
    await expect(page.getByText('KD-002')).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/fibu/zahlungsmeldungen'))).toBe(true)
    expect(requests.some((r) => r.startsWith('POST /api/v1/fibu/zahlungsmeldungen'))).toBe(true)
  })

  test('Zahlungsmeldung verarbeiten', async ({ page }) => {
    const requests: string[] = []

    let meldungen: Zahlungsmeldung[] = [
      {
        id: 'zm-1',
        meldungs_nr: 'ZM-2025-001',
        kunden_nr: 'KD-001',
        rechnungs_nr: null,
        zahlungsdatum: '2025-03-15',
        zahlungsbetrag_eur: 1500.0,
        skonto_betrag_eur: 0,
        skonto_erlaubt: false,
        teilzahlung: false,
        aus_fibu: false,
        status: 'eingegangen',
        verarbeitet_am: null,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isZMCollection(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify(meldungen),
        })
      }
    )

    await page.route(
      (url) => isZMVerarbeiten(new URL(url)),
      async (route) => {
        const request = route.request()
        const pathname = new URL(request.url()).pathname
        requests.push(`${request.method()} ${pathname}`)
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (request.method() === 'POST') {
          const id = pathname.split('/').at(-2) ?? ''
          meldungen = meldungen.map((m) =>
            m.id === id ? { ...m, status: 'verarbeitet', verarbeitet_am: createdAt } : m
          )
          const updated = meldungen.find((m) => m.id === id)!
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(updated),
          })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.route(
      (url) => isZMItem(new URL(url)) && !isZMVerarbeiten(new URL(url)),
      async (route) => {
        const request = route.request()
        if (request.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
      }
    )

    await page.goto('/fibu/zahlungsmeldungen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByText('ZM-2025-001')).toBeVisible()

    await page.getByRole('button', { name: /Zahlungsmeldung ZM-2025-001 verarbeiten/ }).click()
    await expect(page.getByText('verarbeitet')).toBeVisible()

    expect(requests.some((r) => r.includes('/api/v1/fibu/zahlungsmeldungen/zm-1/verarbeiten'))).toBe(true)
  })
})
