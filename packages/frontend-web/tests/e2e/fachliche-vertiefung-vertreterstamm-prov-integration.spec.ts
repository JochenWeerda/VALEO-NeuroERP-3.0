import { test, expect } from '@playwright/test'
import type { ProvisionsGruppe } from '../../src/lib/api/vertreterprovisionen'
import type { Vertretergruppe, Vertreter } from '../../src/lib/api/vertreterstamm'

const corsHeaders = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
}

const createdAt = '2026-05-25T10:00:00Z'

const provisionsgruppen: ProvisionsGruppe[] = [
  {
    id: 'pg-1',
    gruppe_nr: 'PVG-VK',
    bezeichnung: 'Außendienst VK-Provision',
    richtung: 'vk',
    provisionstyp: 'fix',
    provisionssatz: 2.5,
    aktiv: true,
    created_at: createdAt,
  },
  {
    id: 'pg-2',
    gruppe_nr: 'PVG-EK',
    bezeichnung: 'Einkauf-Provision',
    richtung: 'ek',
    provisionstyp: 'staffel_optpreis',
    provisionssatz: null,
    aktiv: true,
    created_at: createdAt,
  },
]

const vertretergruppen: Vertretergruppe[] = [
  { id: 'vg-1', gruppe_nr: 'VG01', bezeichnung: 'Nord', aktiv: true, created_at: createdAt },
]

const vertreter: Vertreter[] = []

test.describe('Fachliche Vertiefung Gate W16: Vertreterstamm-Provisionsgruppen-Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter/provisionen/gruppen',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(provisionsgruppen) })
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter/gruppen',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(vertretergruppen) })
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter' && !url.pathname.includes('/gruppen') && !url.pathname.includes('/provisionen'),
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(vertreter) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newVt: Vertreter = {
            id: `vt-${Date.now()}`,
            vertreter_nr: body.vertreter_nr,
            name: body.name,
            vorname: body.vorname ?? null,
            kuerzel: null,
            telefon: null,
            email: null,
            vertretergruppe_nr: body.vertretergruppe_nr ?? null,
            provisionsgruppe_nr: body.provisionsgruppe_nr ?? null,
            gebiet: null,
            aktiv: true,
            created_at: createdAt,
            updated_at: createdAt,
          }
          vertreter.push(newVt)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newVt) })
        } else {
          await route.continue()
        }
      },
    )
  })

  test('Provisionsgruppe-Select im Vertreter-Anlegen-Formular zeigt Provisionsgruppen', async ({ page }) => {
    await page.goto('/crm/vertreterstamm')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /Vertreter \[VERT\]/i }).click()

    const pgSelect = page.getByLabel('Provisionsgruppe des Vertreters')
    await expect(pgSelect).toBeVisible()

    const options = await pgSelect.locator('option').allTextContents()
    expect(options.some(o => o.includes('PVG-VK'))).toBe(true)
    expect(options.some(o => o.includes('PVG-EK'))).toBe(true)
  })

  test('Vertreter mit Provisionsgruppe anlegen — provisionsgruppe_nr wird korrekt übertragen', async ({ page }) => {
    let capturedPayload: Record<string, unknown> | null = null
    const localVertreter: Vertreter[] = []

    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter' && !url.pathname.includes('/gruppen') && !url.pathname.includes('/provisionen'),
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(localVertreter) })
        } else if (route.request().method() === 'POST') {
          capturedPayload = JSON.parse(route.request().postData() ?? '{}')
          const newVt: Vertreter = {
            id: 'vt-test',
            vertreter_nr: capturedPayload!.vertreter_nr as string,
            name: capturedPayload!.name as string,
            vorname: null,
            kuerzel: null,
            telefon: null,
            email: null,
            vertretergruppe_nr: null,
            provisionsgruppe_nr: capturedPayload!.provisionsgruppe_nr as string | null,
            gebiet: null,
            aktiv: true,
            created_at: createdAt,
            updated_at: createdAt,
          }
          localVertreter.push(newVt)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newVt) })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/crm/vertreterstamm')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /Vertreter \[VERT\]/i }).click()

    await page.getByLabel('Vertreter-Nr').fill('VT-W16')
    await page.getByLabel('Name des Vertreters').fill('Testvertreter')

    const pgSelect = page.getByLabel('Provisionsgruppe des Vertreters')
    await pgSelect.selectOption('PVG-VK')

    await page.getByRole('button', { name: /Vertreter anlegen/i }).click()

    await expect(page.getByText('VT-W16')).toBeVisible()
    expect(capturedPayload?.provisionsgruppe_nr).toBe('PVG-VK')
  })
})
