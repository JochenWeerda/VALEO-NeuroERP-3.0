import { expect, test } from '@playwright/test'

type Individualpreis = {
  id: string
  preis_typ: 'VK' | 'EK'
  artikel_nr: string
  partner_nr: string | null
  gueltig_von: string
  gueltig_bis: string | null
  preis_eur: number
  mengeneinheit: string | null
  staffel_menge: number
  waehrung: string
  notiz: string | null
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
}

test.describe('Fachliche Vertiefung Gate: Individualpreise (Wave 19)', () => {
  test('VK-Individualpreis anlegen und sehen', async ({ page }) => {
    const preise: Individualpreis[] = [
      {
        id: 'pri-1',
        preis_typ: 'VK',
        artikel_nr: 'ART001',
        partner_nr: 'KD001',
        gueltig_von: '2026-01-01',
        gueltig_bis: '2026-12-31',
        preis_eur: 12.5,
        mengeneinheit: 'KG',
        staffel_menge: 0,
        waehrung: 'EUR',
        notiz: null,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) =>
        url.pathname === '/api/v1/preise/individualpreise' ||
        url.pathname.startsWith('/api/v1/preise/individualpreise'),
      async (route) => {
        if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            headers: corsHeaders,
            body: JSON.stringify(preise),
          })
        } else if (route.request().method() === 'POST') {
          const body = JSON.parse(route.request().postData() ?? '{}')
          const newPreis: Individualpreis = {
            id: 'pri-2',
            preis_typ: body.preis_typ ?? 'VK',
            artikel_nr: body.artikel_nr,
            partner_nr: body.partner_nr ?? null,
            gueltig_von: body.gueltig_von,
            gueltig_bis: body.gueltig_bis ?? null,
            preis_eur: body.preis_eur,
            mengeneinheit: body.mengeneinheit ?? null,
            staffel_menge: body.staffel_menge ?? 0,
            waehrung: body.waehrung ?? 'EUR',
            notiz: body.notiz ?? null,
            created_at: createdAt,
          }
          preise.push(newPreis)
          await route.fulfill({
            status: 201,
            headers: corsHeaders,
            body: JSON.stringify(newPreis),
          })
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/preise/individualpreise')
    await page.waitForLoadState('networkidle')

    await expect(page.getByRole('heading', { name: /Individualpreise/i }).first()).toBeVisible()
    await expect(page.getByText('ART001')).toBeVisible()
    await expect(page.getByText('KD001')).toBeVisible()

    await page.getByLabel('Artikel-Nr *').fill('ART002')
    await page.getByLabel('Preis (EUR) *').fill('25.00')
    await page.getByLabel('Gültig von *').fill('2026-06-01')
    await page.getByRole('button', { name: /Anlegen/i }).first().click()

    await expect(page.getByText('ART002')).toBeVisible()
  })

  test('EK-Tab anzeigen', async ({ page }) => {
    const ekPreise: Individualpreis[] = [
      {
        id: 'prie-1',
        preis_typ: 'EK',
        artikel_nr: 'ART010',
        partner_nr: 'LF001',
        gueltig_von: '2026-01-01',
        gueltig_bis: null,
        preis_eur: 8.0,
        mengeneinheit: 'T',
        staffel_menge: 100,
        waehrung: 'EUR',
        notiz: 'Jahreskontrakt',
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) =>
        url.pathname === '/api/v1/preise/individualpreise' ||
        url.pathname.startsWith('/api/v1/preise/individualpreise'),
      async (route) => {
        if (route.request().method() === 'GET') {
          const params = new URL(route.request().url()).searchParams
          const typ = params.get('preis_typ')
          if (typ === 'EK') {
            await route.fulfill({
              status: 200,
              headers: corsHeaders,
              body: JSON.stringify(ekPreise),
            })
          } else {
            await route.fulfill({ status: 200, headers: corsHeaders, body: JSON.stringify([]) })
          }
        } else {
          await route.continue()
        }
      },
    )

    await page.goto('/preise/individualpreise')
    await page.waitForLoadState('networkidle')

    await page.getByRole('tab', { name: /EK-Preise/i }).click()

    await expect(page.getByText('ART010')).toBeVisible()
    await expect(page.getByText('LF001')).toBeVisible()
  })
})
