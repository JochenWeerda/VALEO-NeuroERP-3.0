import { expect, test } from '@playwright/test'

type Betriebsstaette = {
  id: string
  filial_nr: string
  bezeichnung: string
  ist_zentrale: boolean
  zentrale_filial_nr: string | null
  ident_untergrenze: number | null
  ident_obergrenze: number | null
  strasse: string | null
  plz: string | null
  ort: string | null
  land: string | null
  telefon: string | null
  email: string | null
  aktiv: boolean
  created_at: string
  untergeordnete: string[]
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Betriebsstätten & Filialen (Wave 14)', () => {
  test('zeigt Betriebsstätten-Liste mit Zentrale und Filiale', async ({ page }) => {
    const betriebsstaetten: Betriebsstaette[] = [
      {
        id: 'bs-1',
        filial_nr: '001',
        bezeichnung: 'Hauptstelle Musterstadt',
        ist_zentrale: true,
        zentrale_filial_nr: null,
        ident_untergrenze: 1000,
        ident_obergrenze: 9999,
        strasse: 'Musterstraße 1',
        plz: '12345',
        ort: 'Musterstadt',
        land: 'DE',
        telefon: null,
        email: null,
        aktiv: true,
        created_at: createdAt,
        untergeordnete: ['002'],
      },
      {
        id: 'bs-2',
        filial_nr: '002',
        bezeichnung: 'Filiale Nord',
        ist_zentrale: false,
        zentrale_filial_nr: '001',
        ident_untergrenze: null,
        ident_obergrenze: null,
        strasse: null,
        plz: '12346',
        ort: 'Nordstadt',
        land: 'DE',
        telefon: null,
        email: null,
        aktiv: true,
        created_at: createdAt,
        untergeordnete: [],
      },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/stammdaten/betriebsstaetten',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(betriebsstaetten) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newBs: Betriebsstaette = {
            id: 'bs-3',
            filial_nr: body.filial_nr,
            bezeichnung: body.bezeichnung,
            ist_zentrale: body.ist_zentrale ?? false,
            zentrale_filial_nr: body.zentrale_filial_nr ?? null,
            ident_untergrenze: null,
            ident_obergrenze: null,
            strasse: null,
            plz: null,
            ort: null,
            land: body.land ?? 'DE',
            telefon: null,
            email: null,
            aktiv: true,
            created_at: createdAt,
            untergeordnete: [],
          }
          betriebsstaetten.push(newBs)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newBs) })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/stammdaten/betriebsstaetten')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Betriebsstätten/i }).first()).toBeVisible()

    await expect(page.getByText('001')).toBeVisible()
    await expect(page.getByText('Hauptstelle Musterstadt')).toBeVisible()
    await expect(page.getByText('002').first()).toBeVisible()
    await expect(page.getByText('Filiale Nord')).toBeVisible()

    await expect(page.getByText('Zentrale').first()).toBeVisible()
    await expect(page.getByText('Filiale').first()).toBeVisible()

    await expect(page.getByText('12345 Musterstadt')).toBeVisible()
    await expect(page.getByText('1000 – 9999')).toBeVisible()
  })

  test('legt neue Betriebsstätte an', async ({ page }) => {
    const betriebsstaetten: Betriebsstaette[] = []

    await page.route(
      (url) => url.pathname === '/api/v1/stammdaten/betriebsstaetten',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(betriebsstaetten) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newBs: Betriebsstaette = {
            id: 'bs-new',
            filial_nr: body.filial_nr,
            bezeichnung: body.bezeichnung,
            ist_zentrale: body.ist_zentrale ?? false,
            zentrale_filial_nr: null,
            ident_untergrenze: null,
            ident_obergrenze: null,
            strasse: null,
            plz: null,
            ort: body.ort ?? null,
            land: 'DE',
            telefon: null,
            email: null,
            aktiv: true,
            created_at: createdAt,
            untergeordnete: [],
          }
          betriebsstaetten.push(newBs)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newBs) })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/stammdaten/betriebsstaetten')
    await page.waitForLoadState('networkidle')

    await page.getByRole('button', { name: /Neue Betriebsstätte/i }).click()

    await page.getByLabel('Filialnummer').fill('003')
    await page.getByLabel('Bezeichnung').fill('Zweigstelle Ost')

    await page.getByRole('button', { name: /Speichern/i }).click()

    await expect(page.getByText('003')).toBeVisible()
    await expect(page.getByText('Zweigstelle Ost')).toBeVisible()
  })
})
