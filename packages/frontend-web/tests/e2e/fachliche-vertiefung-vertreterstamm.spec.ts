import { test, expect } from '@playwright/test'
import type { Vertretergruppe, Vertreter } from '../../src/lib/api/vertreterstamm'

const corsHeaders = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
}

const createdAt = '2026-05-25T09:00:00Z'

test.describe('Fachliche Vertiefung Gate: Vertreterstamm (Wave 15)', () => {
  test('zeigt Vertretergruppen-Tab und legt eine neue an', async ({ page }) => {
    const gruppen: Vertretergruppe[] = [
      { id: 'vg-1', gruppe_nr: 'VG01', bezeichnung: 'Außendienst Nord', aktiv: true, created_at: createdAt },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter/gruppen',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(gruppen) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newGruppe: Vertretergruppe = {
            id: 'vg-2',
            gruppe_nr: body.gruppe_nr,
            bezeichnung: body.bezeichnung,
            aktiv: true,
            created_at: createdAt,
          }
          gruppen.push(newGruppe)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newGruppe) })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/crm/vertreterstamm')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Vertreterstamm/i }).first()).toBeVisible()
    await expect(page.getByText('VG01')).toBeVisible()
    await expect(page.getByText('Außendienst Nord')).toBeVisible()

    await page.getByLabel('Gruppen-Nr').fill('VG02')
    await page.getByLabel('Bezeichnung der Vertretergruppe').fill('Außendienst Süd')
    await page.getByRole('button', { name: /Vertretergruppe anlegen/i }).click()

    await expect(page.getByText('VG02')).toBeVisible()
  })

  test('zeigt Vertreter-Tab und legt einen neuen an', async ({ page }) => {
    const gruppen: Vertretergruppe[] = [
      { id: 'vg-1', gruppe_nr: 'VG01', bezeichnung: 'Außendienst Nord', aktiv: true, created_at: createdAt },
    ]
    const vertreter: Vertreter[] = [
      {
        id: 'vt-1',
        vertreter_nr: 'VT01',
        name: 'Mustermann',
        vorname: 'Max',
        kuerzel: 'MM',
        telefon: null,
        email: null,
        vertretergruppe_nr: 'VG01',
        provisionsgruppe_nr: null,
        gebiet: 'Nord',
        aktiv: true,
        created_at: createdAt,
        updated_at: createdAt,
      },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter/gruppen',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(gruppen) })
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/crm/vertreter' && !url.pathname.includes('/gruppen'),
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(vertreter) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newVt: Vertreter = {
            id: 'vt-2',
            vertreter_nr: body.vertreter_nr,
            name: body.name,
            vorname: body.vorname ?? null,
            kuerzel: body.kuerzel ?? null,
            telefon: null,
            email: null,
            vertretergruppe_nr: body.vertretergruppe_nr ?? null,
            provisionsgruppe_nr: null,
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

    await page.goto('/crm/vertreterstamm')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /Vertreter \[VERT\]/i }).click()

    await expect(page.getByText('VT01')).toBeVisible()
    await expect(page.getByText('Mustermann')).toBeVisible()

    await page.getByLabel('Vertreter-Nr').fill('VT02')
    await page.getByLabel('Name des Vertreters').fill('Schmidt')
    await page.getByLabel('Vorname').fill('Anna')
    await page.getByRole('button', { name: /Vertreter anlegen/i }).click()

    await expect(page.getByText('VT02')).toBeVisible()
  })
})
