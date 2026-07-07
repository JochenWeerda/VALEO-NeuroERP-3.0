/**
 * UIX-071: Nutzer-Overlays im UniversalMaskRuntime-Pfad.
 * Prueft Spaltenauswahl -> Overlay-Persistenz -> Reload -> Reset.
 */
import { expect, test, type Page } from '@playwright/test'

const screenId = 'crm/customer-360'
const encodedScreenId = screenId.replace(/\//g, '__')
const entityId = 'uix071-customer'

function screenDefinition() {
  return {
    schemaVersion: 1,
    id: screenId,
    domain: 'crm',
    mode: 'detail',
    title: 'UIX071 Kunde',
    adapter: { type: 'native', sourceId: screenId, temporary: false },
    fields: [{ key: 'name', label: 'Name', type: 'text' }],
    dataSources: [
      { key: 'entity', endpoint: `/api/v1/masks/${encodedScreenId}/entity/{entity_id}` },
      { key: 'op', endpoint: `/api/v1/masks/${encodedScreenId}/tables/op/{entity_id}` },
    ],
    tables: [
      {
        key: 'op',
        label: 'Offene Posten',
        dataSourceKey: 'op',
        serverPagination: true,
        columns: [
          { key: 'nr', label: 'Nr', sortable: true },
          { key: 'kunde', label: 'Kunde' },
          { key: 'betrag', label: 'Betrag', numeric: true, renderKind: 'currency' },
        ],
      },
    ],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
      floorplan: 'objectPage',
      density: 'compact',
      contextRail: 'combined',
      tableProfile: 'financial',
    },
    performance: {
      initialPayloadBudgetKb: 48,
      requiresLazyTabs: false,
      requiresVirtualTables: true,
      lookupMinChars: 2,
    },
  }
}

async function installMocks(page: Page): Promise<{ getOverlay: () => Record<string, unknown> }> {
  let overlay: Record<string, unknown> = {}

  await page.route(new RegExp(`/api/v1/masks/${encodedScreenId}/screen-definition$`), async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(screenDefinition()) })
  })

  await page.route(new RegExp(`/api/v1/masks/${encodedScreenId}/entity/${entityId}$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: entityId, name: 'UIX071 Kunde' }),
    })
  })

  await page.route(new RegExp(`/api/v1/masks/${encodedScreenId}/tables/op/${entityId}(\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [{ nr: 'OP-1', kunde: 'UIX071 Kunde', betrag: 42 }],
        total: 1,
      }),
    })
  })

  await page.route('**/api/v1/ux/overlays/crm/customer-360', async (route) => {
    const request = route.request()
    if (request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          screen_id: screenId,
          schema_version: 1,
          overlay,
          updated_at: null,
        }),
      })
      return
    }
    if (request.method() === 'PUT') {
      const payload = request.postDataJSON() as { overlay?: Record<string, unknown> }
      overlay = payload.overlay ?? {}
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          screen_id: screenId,
          schema_version: 1,
          overlay,
          updated_at: new Date().toISOString(),
        }),
      })
      return
    }
    if (request.method() === 'DELETE') {
      overlay = {}
      await route.fulfill({ status: 204 })
      return
    }
    await route.fallback()
  })

  return { getOverlay: () => overlay }
}

test('UIX-071 Spaltenauswahl persistiert ueber Reload und laesst sich resetten', async ({ page }) => {
  const mocks = await installMocks(page)
  await page.goto(`/crm/kunden/${entityId}`, { waitUntil: 'domcontentloaded' })

  const tableGrid = page.getByTestId('table-op').getByTestId('virtual-data-table')
  await expect(tableGrid.getByText('Betrag')).toBeVisible()

  await page.getByTestId('column-picker-toggle-op').click()
  const putRequest = page.waitForRequest(
    (request) => request.method() === 'PUT' && request.url().includes('/api/v1/ux/overlays/crm/customer-360'),
  )
  await page.getByTestId('column-toggle-op-betrag').click()
  await putRequest
  expect(mocks.getOverlay()).toEqual({ tables: { op: { visibleColumns: ['nr', 'kunde'] } } })
  await expect(tableGrid.getByText('Betrag')).toHaveCount(0)

  await page.reload({ waitUntil: 'domcontentloaded' })
  await expect(page.getByTestId('table-op').getByTestId('virtual-data-table').getByText('Betrag')).toHaveCount(0)

  const deleteRequest = page.waitForRequest(
    (request) => request.method() === 'DELETE' && request.url().includes('/api/v1/ux/overlays/crm/customer-360'),
  )
  await page.getByTestId('reset-overlay-op').click()
  await deleteRequest
  await page.reload({ waitUntil: 'domcontentloaded' })

  await expect(page.getByTestId('table-op').getByTestId('virtual-data-table').getByText('Betrag')).toBeVisible()
})
