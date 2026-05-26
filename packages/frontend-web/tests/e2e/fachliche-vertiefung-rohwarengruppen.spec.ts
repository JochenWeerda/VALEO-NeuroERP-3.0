import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type RohwarengruppeOut = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  artikel_nr: string | null
  ek_aktiv: boolean
  vk_aktiv: boolean
  waehrung: string
  mengeneinheit: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-26T10:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Rohwarengruppen', () => {
  test('Rohwarengruppe anlegen und sehen', async ({ page }) => {
    const requests: string[] = []
    let rows: RohwarengruppeOut[] = [
      {
        id: 'rwg-1',
        gruppe_nr: 'RWG01',
        bezeichnung: 'Brotweizen',
        artikel_nr: null,
        ek_aktiv: true,
        vk_aktiv: false,
        waehrung: 'EUR',
        mengeneinheit: 't',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route('**/api/v1/rohware/gruppen', async (route) => {
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
        const payload = request.postDataJSON() as Pick<
          RohwarengruppeOut,
          'gruppe_nr' | 'bezeichnung' | 'ek_aktiv' | 'vk_aktiv' | 'waehrung'
        >
        const created: RohwarengruppeOut = {
          id: `rwg-${payload.gruppe_nr.toLowerCase()}`,
          ...payload,
          artikel_nr: null,
          mengeneinheit: null,
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
        body: '{"detail":"method not allowed"}',
      })
    })

    await page.route('**/api/v1/rohware/gruppen/*', async (route) => {
      const request = route.request()
      requests.push(`${request.method()} ${new URL(request.url()).pathname}`)

      if (request.method() === 'OPTIONS') {
        await route.fulfill({ status: 204, headers: corsHeaders })
        return
      }

      if (request.method() === 'DELETE') {
        const gruppeNr = decodeURIComponent(new URL(request.url()).pathname.split('/').pop() ?? '')
        rows = rows.filter((r) => r.gruppe_nr !== gruppeNr)
        await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
        return
      }

      await route.fulfill({
        status: 405,
        contentType: 'application/json',
        headers: corsHeaders,
        body: '{"detail":"method not allowed"}',
      })
    })

    await page.goto('/agrar/rohwarengruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page).toHaveURL(/\/agrar\/rohwarengruppen($|\?)/)
    await expect(page.getByRole('heading', { name: 'Rohwarengruppen [RWG]', exact: true })).toBeVisible()
    await expect(page.getByText('Brotweizen')).toBeVisible()

    await page.getByPlaceholder('Gruppe-Nr *').fill('RWG02')
    await page.getByPlaceholder('Bezeichnung *').fill('Futtergerste')
    await page.getByRole('button', { name: /Gruppe speichern/ }).click()
    await expect(page.getByText('Futtergerste')).toBeVisible()

    await page.getByRole('button', { name: 'RWG02 löschen' }).click()
    await expect(page.getByText('Futtergerste')).toHaveCount(0)

    expect(requests).toContain('GET /api/v1/rohware/gruppen')
    expect(requests).toContain('POST /api/v1/rohware/gruppen')
    expect(requests).toContain('DELETE /api/v1/rohware/gruppen/RWG02')
  })
})
