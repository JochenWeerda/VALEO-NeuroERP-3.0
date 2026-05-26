import { expect, test } from '@playwright/test'

type Mengeneinheit = {
  id: string
  einheit_kuerzel: string
  bezeichnung: string
  basis_einheit: string | null
  umrechnungsfaktor: number | null
  dezimalstellen: number
  aktiv: boolean
  created_at: string
}

type Mengeneinheitengruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  bestand_einheit: string
  ek_einheit: string | null
  vk_einheit: string | null
  preis_einheit: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Mengeneinheiten & Gruppen (Wave 19)', () => {
  test('Mengeneinheit anlegen und sehen', async ({ page }) => {
    const einheiten: Mengeneinheit[] = [
      {
        id: 'me-1',
        einheit_kuerzel: 'KG',
        bezeichnung: 'Kilogramm',
        basis_einheit: null,
        umrechnungsfaktor: null,
        dezimalstellen: 3,
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/artikel/mengeneinheiten/stamm',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            headers: corsHeaders,
            body: JSON.stringify(einheiten),
          })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newEinheit: Mengeneinheit = {
            id: 'me-2',
            einheit_kuerzel: body.einheit_kuerzel,
            bezeichnung: body.bezeichnung,
            basis_einheit: body.basis_einheit ?? null,
            umrechnungsfaktor: body.umrechnungsfaktor ?? null,
            dezimalstellen: body.dezimalstellen ?? 3,
            aktiv: true,
            created_at: createdAt,
          }
          einheiten.push(newEinheit)
          await route.fulfill({
            status: 201,
            headers: corsHeaders,
            body: JSON.stringify(newEinheit),
          })
        } else {
          await route.continue()
        }
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/artikel/mengeneinheiten/gruppen',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify([]) })
      },
    )

    await page.goto('/stammdaten/mengeneinheiten')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Mengeneinheiten/i }).first()).toBeVisible()
    await expect(page.getByText('KG')).toBeVisible()
    await expect(page.getByText('Kilogramm')).toBeVisible()

    await page.getByLabel('Kürzel *').fill('T')
    await page.getByLabel('Bezeichnung *').fill('Tonne')
    await page.getByRole('button', { name: /Anlegen/i }).first().click()

    await expect(page.getByText('Tonne')).toBeVisible()
  })

  test('Einheitengruppe anlegen', async ({ page }) => {
    const gruppen: Mengeneinheitengruppe[] = [
      {
        id: 'eg-1',
        gruppe_nr: 'EG01',
        bezeichnung: 'Getreide Standard',
        bestand_einheit: 'KG',
        ek_einheit: 'T',
        vk_einheit: 'T',
        preis_einheit: 'T',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/artikel/mengeneinheiten/stamm',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify([]) })
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/artikel/mengeneinheiten/gruppen',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            headers: corsHeaders,
            body: JSON.stringify(gruppen),
          })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newGruppe: Mengeneinheitengruppe = {
            id: 'eg-2',
            gruppe_nr: body.gruppe_nr,
            bezeichnung: body.bezeichnung,
            bestand_einheit: body.bestand_einheit,
            ek_einheit: body.ek_einheit ?? null,
            vk_einheit: body.vk_einheit ?? null,
            preis_einheit: body.preis_einheit ?? null,
            aktiv: true,
            created_at: createdAt,
          }
          gruppen.push(newGruppe)
          await route.fulfill({
            status: 201,
            headers: corsHeaders,
            body: JSON.stringify(newGruppe),
          })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/stammdaten/mengeneinheiten')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /Einheitengruppen/i }).click()

    await expect(page.getByText('EG01')).toBeVisible()
    await expect(page.getByText('Getreide Standard')).toBeVisible()

    await page.getByLabel('Gruppen-Nr *').fill('EG02')
    await page.getByLabel('Bezeichnung *').fill('Ölsaaten Standard')
    await page.getByLabel('Bestand-Einheit *').fill('KG')
    await page.getByRole('button', { name: /Anlegen/i }).first().click()

    await expect(page.getByText('Ölsaaten Standard')).toBeVisible()
  })
})
