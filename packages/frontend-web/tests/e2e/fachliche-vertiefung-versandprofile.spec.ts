import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type Versandprofil = {
  id: string
  profil_nr: string
  bezeichnung: string
  versandart: 'email' | 'fax' | 'edi' | 'post' | 'api'
  smtp_server: string | null
  absender_email: string | null
  absender_name: string | null
  archiv_kennzeichen: boolean
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const BASE_PROFILE = '/api/v1/logistik/versand/profile'
const BASE_AVISE = '/api/v1/logistik/versand/avise'

const isProfileUrl = (url: URL) =>
  url.pathname.startsWith(BASE_PROFILE)
const isAvisUrl = (url: URL) =>
  url.pathname.startsWith(BASE_AVISE)

test.describe('Fachliche Vertiefung Gate: Versandprofile & Lieferavise', () => {
  test('Versandprofil anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    const profile: Versandprofil[] = [
      {
        id: 'vp-1',
        profil_nr: 'EMAIL-STD',
        bezeichnung: 'Standard E-Mail-Versand',
        versandart: 'email',
        smtp_server: 'mail.valeo.de',
        absender_email: 'versand@valeo.de',
        absender_name: 'VALEO Versand',
        archiv_kennzeichen: true,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isProfileUrl(new URL(url)),
      async (route) => {
        const req = route.request()
        requests.push(`${req.method()} ${new URL(req.url()).pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(profile),
          })
          return
        }
        if (req.method() === 'POST') {
          const body = JSON.parse(req.postData() ?? '{}')
          const p: Versandprofil = {
            id: 'vp-new',
            profil_nr: body.profil_nr ?? 'NEW',
            bezeichnung: body.bezeichnung ?? 'Neu',
            versandart: body.versandart ?? 'email',
            smtp_server: null,
            absender_email: null,
            absender_name: null,
            archiv_kennzeichen: true,
            aktiv: true,
            created_at: createdAt,
          }
          profile.push(p)
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(p),
          })
          return
        }
        if (req.method() === 'DELETE') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.continue()
      },
    )

    await page.route(
      (url) => isAvisUrl(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify([]),
        })
      },
    )

    await page.goto('/logistik/versandprofile', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    // Page uses span elements, not table cells
    await expect(page.locator('span.font-mono', { hasText: 'EMAIL-STD' }).first()).toBeVisible()
    await expect(page.getByText('Standard E-Mail-Versand').first()).toBeVisible()

    expect(requests.some((r) => r.startsWith('GET /api/v1/logistik/versand/profile'))).toBe(true)
  })

  test('Versandprofil löschen', async ({ page }) => {
    const requests: string[] = []

    const profile: Versandprofil[] = [
      {
        id: 'vp-1',
        profil_nr: 'EMAIL-STD',
        bezeichnung: 'Standard E-Mail-Versand',
        versandart: 'email',
        smtp_server: null,
        absender_email: 'versand@valeo.de',
        absender_name: null,
        archiv_kennzeichen: true,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isProfileUrl(new URL(url)),
      async (route) => {
        const req = route.request()
        requests.push(`${req.method()} ${new URL(req.url()).pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: corsHeaders,
            body: JSON.stringify(profile),
          })
          return
        }
        if (req.method() === 'DELETE') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.continue()
      },
    )

    await page.route(
      (url) => isAvisUrl(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: corsHeaders,
          body: JSON.stringify([]),
        })
      },
    )

    await page.goto('/logistik/versandprofile', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    // aria-label is "{profil_nr} löschen"
    const deleteBtn = page.getByRole('button', { name: 'EMAIL-STD löschen' })
    await deleteBtn.click()

    await expect(async () => {
      expect(requests.some((r) => r.startsWith('DELETE'))).toBe(true)
    }).toPass({ timeout: 5000 })
  })
})
