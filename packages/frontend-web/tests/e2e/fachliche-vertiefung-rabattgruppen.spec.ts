import { expect, test } from '@playwright/test'

type Rabattgruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: 'EK' | 'VK'
  aktiv: boolean
  created_at: string
}

type Rabattklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: 'EK' | 'VK'
  aktiv: boolean
  created_at: string
}

type Rabattsatz = {
  id: string
  rabattgruppe_nr: string
  rabattklasse_nr: string
  richtung: 'EK' | 'VK'
  rabatt_prozent: number
  ab_menge: number | null
  gueltig_ab: string | null
  gueltig_bis: string | null
  created_at: string
}

const createdAt = '2026-05-24T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Rabattgruppen & -klassen (Wave 14)', () => {
  test('zeigt Rabattgruppen-Liste und legt eine neue an', async ({ page }) => {
    const gruppen: Rabattgruppe[] = [
      { id: 'rag-1', gruppe_nr: 'RAG01', bezeichnung: 'Standard VK', richtung: 'VK', aktiv: true, created_at: createdAt },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/preise/rabatte/gruppen',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(gruppen) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newGruppe: Rabattgruppe = {
            id: 'rag-2',
            gruppe_nr: body.gruppe_nr,
            bezeichnung: body.bezeichnung,
            richtung: body.richtung,
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

    await page.goto('/preise/rabattgruppen')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Rabattgruppen/i }).first()).toBeVisible()
    await expect(page.getByText('RAG01')).toBeVisible()
    await expect(page.getByText('Standard VK')).toBeVisible()

    await page.getByLabel('Gruppen-Nr').fill('RAG02')
    await page.getByLabel('Bezeichnung').fill('Stammkunden VK')
    await page.getByRole('button', { name: /Anlegen/i }).first().click()

    await expect(page.getByText('RAG02')).toBeVisible()
  })

  test('zeigt Rabattklassen-Tab und legt eine neue an', async ({ page }) => {
    const klassen: Rabattklasse[] = [
      { id: 'rak-1', klasse_nr: 'RAK01', bezeichnung: 'A-Kunden', richtung: 'VK', aktiv: true, created_at: createdAt },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/preise/rabatte/gruppen',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify([]) })
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/preise/rabatte/klassen',
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(klassen) })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newKlasse: Rabattklasse = {
            id: 'rak-2',
            klasse_nr: body.klasse_nr,
            bezeichnung: body.bezeichnung,
            richtung: body.richtung,
            aktiv: true,
            created_at: createdAt,
          }
          klassen.push(newKlasse)
          await route.fulfill({ status: 201, headers: corsHeaders, body: JSON.stringify(newKlasse) })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/preise/rabattgruppen')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /Rabattklassen/i }).click()

    await expect(page.getByText('RAK01')).toBeVisible()
    await expect(page.getByText('A-Kunden')).toBeVisible()

    await page.getByLabel('Klassen-Nr').fill('RAK02')
    await page.getByLabel('Bezeichnung').nth(0).fill('B-Kunden')
    await page.getByRole('button', { name: /Anlegen/i }).first().click()

    await expect(page.getByText('RAK02')).toBeVisible()
  })

  test('zeigt Rabattsätze-Tab', async ({ page }) => {
    const saetze: Rabattsatz[] = [
      {
        id: 'rs-1',
        rabattgruppe_nr: 'RAG01',
        rabattklasse_nr: 'RAK01',
        richtung: 'VK',
        rabatt_prozent: 5.0,
        ab_menge: null,
        gueltig_ab: null,
        gueltig_bis: null,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => url.pathname === '/api/v1/preise/rabatte/gruppen',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify([]) })
      },
    )

    await page.route(
      (url) => url.pathname === '/api/v1/preise/rabatte/saetze',
      async (route) => {
        await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify(saetze) })
      },
    )

    await page.goto('/preise/rabattgruppen')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /Rabattsätze/i }).click()

    await expect(page.getByText('RAG01').first()).toBeVisible()
    await expect(page.getByText('RAK01').first()).toBeVisible()
    await expect(page.getByText('5.00 %')).toBeVisible()
  })
})
