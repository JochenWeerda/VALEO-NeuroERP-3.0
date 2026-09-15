/**
 * UIX-091: Prozessband navigiert entlang zweier Ketten (Verkauf, Einkauf).
 * ScreenDefinition wird gemockt — der Test belegt Compiler+Renderer, nicht den Live-Katalog.
 */
import { expect, test, type Page } from '@playwright/test'

const VERKAUF_CHAIN = {
  k2_verkauf: {
    label: 'Verkauf',
    steps: [
      { key: 'auftrag', label: 'Auftrag', screenId: 'sales/sales-order', routePath: '/verkauf/auftraege' },
      { key: 'lieferschein', label: 'Lieferschein', screenId: 'sales/delivery-note', routePath: '/sales/delivery-note/smoke-ls' },
    ],
  },
}

const EINKAUF_CHAIN = {
  k3_einkauf: {
    label: 'Einkauf',
    steps: [
      { key: 'anfrage', label: 'Anfrage', screenId: 'einkauf/anfrage', routePath: '/einkauf/anfragen' },
      { key: 'bestellung', label: 'Bestellung', screenId: 'einkauf/purchase-order', routePath: '/einkauf/bestellung/smoke-po' },
    ],
  },
}

function screenDefinition(screenId: string, chainId: string, stepKey: string, catalog: Record<string, unknown>) {
  const encoded = screenId.replace(/\//g, '__')
  return {
    schemaVersion: 1,
    id: screenId,
    domain: screenId.split('/')[0],
    mode: 'detail',
    title: stepKey,
    adapter: { type: 'native', sourceId: screenId, temporary: false },
    processChain: { chainId, stepKey },
    processChains: catalog,
    fields: [{ key: 'name', label: 'Name', type: 'text' }],
    dataSources: [{ key: 'entity', endpoint: `/api/v1/masks/${encoded}/entity/{entity_id}` }],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      floorplan: 'objectPage',
      density: 'compact',
      contextRail: 'combined',
      tableProfile: 'standard',
    },
  }
}

async function mockScreen(page: Page, screenId: string, entityId: string, body: unknown): Promise<void> {
  const encoded = screenId.replace(/\//g, '__')
  await page.route(new RegExp(`/api/v1/masks/${encoded}/screen-definition$`), async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
  await page.route(new RegExp(`/api/v1/masks/${encoded}/entity/${entityId}$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: entityId, name: screenId }),
    })
  })
}

test('Verkaufskette: Lieferschein markiert current, Klick auf Auftrag navigiert', async ({ page }) => {
  await mockScreen(
    page,
    'sales/delivery-note',
    'smoke-ls',
    screenDefinition('sales/delivery-note', 'k2_verkauf', 'lieferschein', VERKAUF_CHAIN),
  )
  await page.goto('/sales/delivery-note/smoke-ls', { waitUntil: 'domcontentloaded' })
  await expect(page.getByTestId('process-ribbon')).toHaveAttribute('data-chain', 'k2_verkauf', { timeout: 30_000 })
  await expect(page.getByTestId('ribbon-step-lieferschein')).toHaveAttribute('data-state', 'current')
  await page.getByTestId('ribbon-step-auftrag').click()
  await expect(page).toHaveURL(/\/verkauf\/auftraege/)
})

test('Einkaufskette: Bestellung markiert current, Klick auf Anfrage navigiert', async ({ page }) => {
  await mockScreen(
    page,
    'einkauf/purchase-order',
    'smoke-po',
    screenDefinition('einkauf/purchase-order', 'k3_einkauf', 'bestellung', EINKAUF_CHAIN),
  )
  await page.goto('/einkauf/bestellung/smoke-po', { waitUntil: 'domcontentloaded' })
  await expect(page.getByTestId('process-ribbon')).toHaveAttribute('data-chain', 'k3_einkauf', { timeout: 30_000 })
  await expect(page.getByTestId('ribbon-step-bestellung')).toHaveAttribute('data-state', 'current')
  await page.getByTestId('ribbon-step-anfrage').click()
  await expect(page).toHaveURL(/\/einkauf\/anfragen/)
})
