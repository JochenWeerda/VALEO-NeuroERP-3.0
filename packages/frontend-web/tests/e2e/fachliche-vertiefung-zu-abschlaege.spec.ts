import { expect, test } from '@playwright/test'
import { waitForDashboardShell } from './helpers/wait-dashboard-shell'

type ZuAbschlaggruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: 'ek' | 'vk'
  aktiv: boolean
  created_at: string
}

type ZuAbschlagklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: 'ek' | 'vk'
  aktiv: boolean
  created_at: string
}

type ZuAbschlagKondition = {
  id: string
  gruppe_id: string
  klasse_id: string
  kondition_typ: 'betrag' | 'prozent'
  wert: number
  gueltig_ab: string
  gueltig_bis: string | null
  beschreibung: string | null
  aktiv: boolean
  created_at: string
}

const createdAt = '2026-05-26T08:00:00'
const corsHeaders = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type,x-tenant-id',
  'access-control-allow-methods': 'GET,POST,PUT,DELETE,OPTIONS',
}

const BASE = '/api/v1/preise/zu-abschlaege'

const isGruppen = (url: URL) => url.pathname === `${BASE}/gruppen`
const isGruppeItem = (url: URL) => new RegExp(`^${BASE}/gruppen/[^/]+$`).test(url.pathname)
const isKlassen = (url: URL) => url.pathname === `${BASE}/klassen`
const isKlasseItem = (url: URL) => new RegExp(`^${BASE}/klassen/[^/]+$`).test(url.pathname)
const isKonditionen = (url: URL) => url.pathname === `${BASE}/konditionen`

test.describe('Fachliche Vertiefung Gate: Zu-/Abschlaggruppen & Konditionen (Wave 17)', () => {
  test('Zu-/Abschlaggruppe anlegen und sehen', async ({ page }) => {
    const requests: string[] = []

    let gruppen: ZuAbschlaggruppe[] = [
      {
        id: 'zagr-1',
        gruppe_nr: 'ZAGR-NORD',
        bezeichnung: 'Frachtaufschlag Nord',
        richtung: 'vk',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isGruppen(new URL(url)),
      async (route) => {
        const req = route.request()
        requests.push(`${req.method()} ${new URL(req.url()).pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200, contentType: 'application/json',
            headers: corsHeaders, body: JSON.stringify(gruppen),
          })
          return
        }
        if (req.method() === 'POST') {
          const payload = req.postDataJSON() as Omit<ZuAbschlaggruppe, 'id' | 'aktiv' | 'created_at'>
          const created: ZuAbschlaggruppe = {
            id: `zagr-${gruppen.length + 1}`,
            gruppe_nr: payload.gruppe_nr,
            bezeichnung: payload.bezeichnung,
            richtung: payload.richtung,
            aktiv: true,
            created_at: createdAt,
          }
          gruppen = [...gruppen, created]
          await route.fulfill({
            status: 201, contentType: 'application/json',
            headers: corsHeaders, body: JSON.stringify(created),
          })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.route(
      (url) => isGruppeItem(new URL(url)),
      async (route) => {
        const req = route.request()
        const url = new URL(req.url())
        const gruppe_nr = decodeURIComponent(url.pathname.split('/').pop() ?? '')
        const richtung = url.searchParams.get('richtung') ?? 'vk'
        requests.push(`${req.method()} ${url.pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        if (req.method() === 'DELETE') {
          gruppen = gruppen.filter(
            (g) => !(g.gruppe_nr === gruppe_nr && g.richtung === richtung)
          )
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    // Intercept klassen + konditionen (leere Listen — Tabs nicht geöffnet)
    await page.route(
      (url) => isKlassen(new URL(url)) || isKonditionen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders })
          return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: '[]',
        })
      }
    )

    await page.goto('/preise/zu-abschlaggruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(
      page.getByRole('heading', { name: 'Zu-/Abschlaggruppen & -klassen', exact: true })
    ).toBeVisible()
    await expect(page.getByText('Frachtaufschlag Nord')).toBeVisible()
    await expect(page.getByText('ZAGR-NORD')).toBeVisible()

    // Neue Gruppe anlegen
    await page.locator('#zagr_nr').fill('ZAGR-SÜD')
    await page.locator('#zagr_bez').fill('Frachtaufschlag Süd')

    const postResponse = page.waitForResponse(
      (res) => res.request().method() === 'POST' && isGruppen(new URL(res.url())),
      { timeout: 15000 },
    )
    await page.locator('[aria-label="Zu-/Abschlaggruppe anlegen"]').click()
    await postResponse

    await expect(page.getByText('Frachtaufschlag Süd')).toBeVisible()

    expect(requests.some((r) => r.startsWith(`GET ${BASE}/gruppen`))).toBe(true)
    expect(requests.some((r) => r.startsWith(`POST ${BASE}/gruppen`))).toBe(true)
  })

  test('Zu-/Abschlaggruppe löschen', async ({ page }) => {
    const requests: string[] = []

    let gruppen: ZuAbschlaggruppe[] = [
      {
        id: 'zagr-del',
        gruppe_nr: 'ZAGR-DEL',
        bezeichnung: 'Zu löschen',
        richtung: 'vk',
        aktiv: true,
        created_at: createdAt,
      },
    ]

    await page.route(
      (url) => isGruppen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: JSON.stringify(gruppen),
        })
      }
    )
    await page.route(
      (url) => isGruppeItem(new URL(url)),
      async (route) => {
        const req = route.request()
        requests.push(`${req.method()} ${new URL(req.url()).pathname}`)
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        if (req.method() === 'DELETE') {
          gruppen = []
          await route.fulfill({ status: 204, headers: corsHeaders, body: '' })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )
    await page.route(
      (url) => isKlassen(new URL(url)) || isKonditionen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: '[]',
        })
      }
    )

    await page.goto('/preise/zu-abschlaggruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await expect(page.getByText('Zu löschen')).toBeVisible()

    const deleteResponse = page.waitForResponse(
      (res) => res.request().method() === 'DELETE' && isGruppeItem(new URL(res.url())),
      { timeout: 15000 },
    )
    await page.locator('[aria-label="Zu-/Abschlaggruppe ZAGR-DEL deaktivieren"]').click()
    await deleteResponse

    expect(requests.some((r) => r.startsWith(`DELETE ${BASE}/gruppen`))).toBe(true)
  })

  test('Zu-/Abschlagklasse anlegen', async ({ page }) => {
    let klassen: ZuAbschlagklasse[] = []

    await page.route(
      (url) => isGruppen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: '[]',
        })
      }
    )
    await page.route(
      (url) => isKlassen(new URL(url)),
      async (route) => {
        const req = route.request()
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200, contentType: 'application/json',
            headers: corsHeaders, body: JSON.stringify(klassen),
          })
          return
        }
        if (req.method() === 'POST') {
          const payload = req.postDataJSON() as Omit<ZuAbschlagklasse, 'id' | 'aktiv' | 'created_at'>
          const created: ZuAbschlagklasse = {
            id: 'zakl-new',
            klasse_nr: payload.klasse_nr,
            bezeichnung: payload.bezeichnung,
            richtung: payload.richtung,
            aktiv: true,
            created_at: createdAt,
          }
          klassen = [created]
          await route.fulfill({
            status: 201, contentType: 'application/json',
            headers: corsHeaders, body: JSON.stringify(created),
          })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )
    await page.route(
      (url) => isKlasseItem(new URL(url)) || isKonditionen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: '[]',
        })
      }
    )

    await page.goto('/preise/zu-abschlaggruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('tab', { name: 'Klassen [ZAKL]' }).click()

    await page.locator('#zakl_nr').fill('ZAKL-A')
    await page.locator('#zakl_bez').fill('Großhändler')

    const postResponse = page.waitForResponse(
      (res) => res.request().method() === 'POST' && isKlassen(new URL(res.url())),
      { timeout: 15000 },
    )
    await page.locator('[aria-label="Zu-/Abschlagklasse anlegen"]').click()
    await postResponse

    await expect(page.getByRole('cell').filter({ hasText: 'ZAKL-A' }).first()).toBeVisible()
  })

  test('Zu-/Abschlagkondition anlegen und in Tabelle sehen', async ({ page }) => {
    const gruppe: ZuAbschlaggruppe = {
      id: 'zagr-k1',
      gruppe_nr: 'ZAGR-KND',
      bezeichnung: 'Frachtaufschlag',
      richtung: 'vk',
      aktiv: true,
      created_at: createdAt,
    }
    const klasse: ZuAbschlagklasse = {
      id: 'zakl-k1',
      klasse_nr: 'ZAKL-KND',
      bezeichnung: 'Hauskunde',
      richtung: 'vk',
      aktiv: true,
      created_at: createdAt,
    }
    let konditionen: ZuAbschlagKondition[] = []

    await page.route(
      (url) => isGruppen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: JSON.stringify([gruppe]),
        })
      }
    )
    await page.route(
      (url) => isKlassen(new URL(url)),
      async (route) => {
        if (route.request().method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        await route.fulfill({
          status: 200, contentType: 'application/json',
          headers: corsHeaders, body: JSON.stringify([klasse]),
        })
      }
    )
    await page.route(
      (url) => isKonditionen(new URL(url)),
      async (route) => {
        const req = route.request()
        if (req.method() === 'OPTIONS') {
          await route.fulfill({ status: 204, headers: corsHeaders }); return
        }
        if (req.method() === 'GET') {
          await route.fulfill({
            status: 200, contentType: 'application/json',
            headers: corsHeaders, body: JSON.stringify(konditionen),
          })
          return
        }
        if (req.method() === 'POST') {
          const payload = req.postDataJSON() as ZuAbschlagKondition
          const created: ZuAbschlagKondition = {
            id: 'zak-new',
            gruppe_id: payload.gruppe_id,
            klasse_id: payload.klasse_id,
            kondition_typ: payload.kondition_typ,
            wert: payload.wert,
            gueltig_ab: payload.gueltig_ab,
            gueltig_bis: payload.gueltig_bis,
            beschreibung: payload.beschreibung,
            aktiv: true,
            created_at: createdAt,
          }
          konditionen = [created]
          await route.fulfill({
            status: 201, contentType: 'application/json',
            headers: corsHeaders, body: JSON.stringify(created),
          })
          return
        }
        await route.fulfill({ status: 405, headers: corsHeaders, body: '{"detail":"method"}' })
      }
    )

    await page.goto('/preise/zu-abschlaggruppen', { waitUntil: 'domcontentloaded' })
    await waitForDashboardShell(page)

    await page.getByRole('tab', { name: 'Konditionen [ZAK]' }).click()

    await page.locator('#zak_gruppe').selectOption('zagr-k1')
    await page.locator('#zak_klasse').selectOption('zakl-k1')
    await page.locator('#zak_wert').fill('2.50')
    await page.locator('#zak_ab').fill('2026-01-01')

    const postResponse = page.waitForResponse(
      (res) => res.request().method() === 'POST' && isKonditionen(new URL(res.url())),
      { timeout: 15000 },
    )
    await page.locator('[aria-label="Zu-/Abschlagkondition anlegen"]').click()
    await postResponse

    await expect(page.getByRole('cell').filter({ hasText: '+2.50' })).toBeVisible()
  })
})
