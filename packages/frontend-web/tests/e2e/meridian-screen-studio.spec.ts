/**
 * MERIDIAN-SCREEN-STUDIO-E2E: Fach-Admin baut Lieferanten-Bewertung,
 * gibt Vier-Augen frei und oeffnet die published_temp-Maske.
 *
 * Gegen ein aktuelles Backend laeuft der Weg echt. Fehlt `/studio` am
 * laufenden Prozess, wird der Browserlauf gegen den Vertrag gemockt.
 */
import { expect, test, type APIRequestContext, type Page } from '@playwright/test'
import { prepareE2EAuth } from './helpers/auth-from-env'

const TENANT = '00000000-0000-0000-0000-000000000001'
const TOKEN = process.env.E2E_API_DEV_TOKEN ?? process.env.API_DEV_TOKEN ?? 'dev-token'
const HEADERS = {
  Authorization: `Bearer ${TOKEN}`,
  'X-Tenant-ID': TENANT,
}

const definition = {
  schemaVersion: 1,
  id: 'tenant/lieferanten-bewertung',
  domain: 'einkauf',
  mode: 'list',
  title: 'Lieferanten-Bewertung',
  adapter: { type: 'native', sourceId: 'tenant/lieferanten-bewertung', temporary: true },
  layout: { floorplan: 'worklist', columnNavigation: 'listDetail', density: 'compact', contextRail: 'none' },
  tables: [{
    key: 'list',
    label: 'Lieferanten',
    columns: [
      { key: 'lieferanten_nr', label: 'Nr' },
      { key: 'name', label: 'Name' },
      { key: 'score', label: 'Bewertung', numeric: true },
    ],
  }],
  actions: [{ key: 'create_activity', dangerLevel: 'safe' }],
}

async function studioApiAvailable(request: APIRequestContext): Promise<boolean> {
  const catalog = await request.get('/api/v1/studio/catalog', { headers: HEADERS })
  return catalog.status() === 200
}

async function retireExisting(request: APIRequestContext) {
  const listed = await request.get('/api/v1/studio/drafts', { headers: HEADERS })
  if (listed.status() !== 200) return
  const drafts = (await listed.json()).drafts ?? []
  for (const draft of drafts) {
    if (draft.screen_id !== 'tenant/lieferanten-bewertung') continue
    if (draft.status === 'published_temp') {
      await request.post(`/api/v1/studio/drafts/${draft.id}/retire`, {
        headers: { ...HEADERS, 'X-Actor-ID': 'studio-janitor' },
      })
    }
  }
}

async function mockStudioApi(page: Page) {
  await page.route('**/api/v1/studio/catalog', async (route) => {
    await route.fulfill({
      json: {
        floorplans: ['worklist'],
        fieldTypes: ['text'],
        columnNavigation: ['single', 'listDetail'],
        dataSources: [],
        actions: [],
      },
    })
  })
  await page.route('**/api/v1/studio/validate', async (route) => {
    await route.fulfill({ json: { violations: [], canPublish: true, readiness: { errors: [] }, definition } })
  })
  await page.route('**/api/v1/studio/drafts', async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        json: { id: 'draft-1', status: 'draft', violations: [], canPublish: true, readiness: { errors: [] }, definition },
      })
      return
    }
    await route.continue()
  })
  await page.route('**/api/v1/studio/drafts/draft-1/submit-review', async (route) => {
    await route.fulfill({ json: { id: 'draft-1', status: 'review' } })
  })
  await page.route('**/api/v1/studio/drafts/draft-1/publish', async (route) => {
    await route.fulfill({
      json: {
        id: 'draft-1',
        status: 'published_temp',
        route: '/studio/run/tenant__lieferanten-bewertung',
        violations: [],
        canPublish: true,
        readiness: { errors: [] },
        definition,
      },
    })
  })
  await page.route('**/api/v1/masks/tenant__lieferanten-bewertung/screen-definition', async (route) => {
    await route.fulfill({ json: definition })
  })
}

test.describe('Masken-Studio Abnahme', () => {
  test('Lieferanten-Bewertung erzeugen, freigeben und oeffnen', async ({ page, request }) => {
    const live = await studioApiAvailable(request)
    if (live) await retireExisting(request)
    else await mockStudioApi(page)
    await prepareE2EAuth(page)

    await page.goto('/admin/screen-studio')
    await expect(page.getByTestId('screen-studio')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Masken-Studio' })).toBeVisible()
    await expect(page.getByTestId('studio-preview')).toBeVisible()
    await expect(page.getByTestId('studio-gates')).toContainText('Publish möglich')
    await expect(page.getByRole('button', { name: 'Freigeben' })).toBeDisabled()

    const add = page.getByTestId('studio-add-column')
    await add.click()
    await add.click()
    await add.click()
    await expect(page.getByTestId('studio-column-count')).toHaveText('6 Felder')

    await page.getByRole('button', { name: 'Speichern' }).click()
    await expect(page.getByRole('status')).toContainText('Gespeichert')
    await page.getByRole('button', { name: 'Prüfung' }).click()
    await expect(page.getByRole('status')).toContainText('Zur Prüfung gegeben')
    await page.getByRole('button', { name: 'Freigeben' }).click()
    await expect(page.getByRole('status')).toContainText('published_temp')

    const link = page.getByTestId('studio-run-link')
    await expect(link).toBeVisible()
    await link.click()
    await expect(page.getByTestId('studio-run')).toBeVisible()
    await expect(page.getByTestId('studio-run')).toHaveAttribute('data-screen-id', 'tenant/lieferanten-bewertung')

    if (live) {
      const catalog = await request.get('/api/v1/ui/mask-registry/omnibox-catalog', { headers: HEADERS })
      expect(catalog.status()).toBe(200)
      const entry = (await catalog.json()).find((item: { screen_id: string }) => item.screen_id === 'tenant/lieferanten-bewertung')
      expect(entry?.route).toBe('/studio/run/tenant__lieferanten-bewertung')
    }
  })

  test('critical ohne Confirmation wird serverseitig abgelehnt', async ({ request }) => {
    test.skip(!(await studioApiAvailable(request)), 'Studio-API nicht erreichbar')
    const response = await request.post('/api/v1/studio/validate', {
      headers: HEADERS,
      data: {
        definition: {
          schemaVersion: 1,
          id: 'tenant/boese-storno',
          domain: 'einkauf',
          mode: 'list',
          title: 'Boese Storno',
          adapter: { type: 'native', sourceId: 'tenant/boese-storno', temporary: true },
          actions: [{ key: 'stornieren', dangerLevel: 'critical', forbiddenForAgents: true }],
        },
      },
    })
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(body.violations.join(' ')).toContain('action_confirmation_fehlt')
    expect(body.canPublish).toBe(false)
  })
})
