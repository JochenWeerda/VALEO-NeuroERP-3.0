/**
 * UIX-056: Browser-Smoke über repräsentative native /:id-Routen (nach UIX-051).
 * Mockt ScreenDefinition + Entity — prüft Routing, Runtime-Shell und Human-Gates.
 */
import { expect, test, type Page } from '@playwright/test'

type SmokeCase = {
  label: string
  path: string
  screenId: string
  testId: string
  title: string
  entityId: string
  actions?: Array<{
    key: string
    label: string
    dangerLevel?: string
    requiresConfirmation?: boolean
    humanApprovalRequired?: boolean
    stubReason?: string
  }>
}

const SMOKE_CASES: SmokeCase[] = [
  {
    label: 'crm/kunden/:id',
    path: '/crm/kunden/smoke-customer',
    screenId: 'crm/customer-360',
    testId: 'crm-customer-360',
    title: 'Smoke Kunde',
    entityId: 'smoke-customer',
  },
  {
    label: 'einkauf/lieferanten/:id',
    path: '/einkauf/lieferanten/smoke-supplier',
    screenId: 'einkauf/supplier',
    testId: 'einkauf-supplier',
    title: 'Smoke Lieferant',
    entityId: 'smoke-supplier',
  },
  {
    label: 'sales/sales-order/:id',
    path: '/sales/sales-order/smoke-order',
    screenId: 'sales/sales-order',
    testId: 'sales-sales-order',
    title: 'Smoke Auftrag',
    entityId: 'smoke-order',
  },
  {
    label: 'agrar/kontrakt/:id',
    path: '/agrar/kontrakt/smoke-contract',
    screenId: 'agrar/kontrakte',
    testId: 'agrar-kontrakt',
    title: 'Smoke Kontrakt',
    entityId: 'smoke-contract',
  },
  {
    label: 'finance/payment-run/:id',
    path: '/finance/payment-run/smoke-run',
    screenId: 'finance/payment-run',
    testId: 'finance-payment-run',
    title: 'Smoke Zahlungslauf',
    entityId: 'smoke-run',
    actions: [
      {
        key: 'freigeben',
        label: 'Zahlungslauf freigeben',
        dangerLevel: 'critical',
        requiresConfirmation: true,
        humanApprovalRequired: true,
        stubReason: 'Smoke: Freigabe nur nach 4-Augen-Prüfung',
      },
    ],
  },
]

function maskPath(screenId: string): string {
  return screenId.replace(/\//g, '__')
}

function minimalScreenDefinition(c: SmokeCase) {
  const encoded = maskPath(c.screenId)
  return {
    schemaVersion: 1,
    id: c.screenId,
    domain: c.screenId.split('/')[0],
    mode: 'detail',
    title: c.title,
    adapter: { type: 'native', sourceId: c.screenId, temporary: false },
    fields: [
      { key: 'name', label: 'Name', type: 'text' },
      { key: 'status', label: 'Status', type: 'text', readOnly: true },
    ],
    dataSources: [
      { key: 'entity', endpoint: `/api/v1/masks/${encoded}/entity/{entity_id}` },
    ],
    tabs: [
      {
        key: 'kopf',
        label: 'Kopf',
        lazy: false,
        keepAlive: true,
        dataSourceKey: 'entity',
        fields: [
          { key: 'name', label: 'Name', type: 'text' },
          { key: 'status', label: 'Status', type: 'text', readOnly: true },
        ],
      },
    ],
    actions: c.actions ?? [],
    permissions: ['*'],
    layout: { preferredMode: 'desktopDense', mobileMode: 'mobileStack', touchTargetPx: 44 },
    performance: {
      initialPayloadBudgetKb: 48,
      requiresLazyTabs: false,
      requiresVirtualTables: false,
      lookupMinChars: 2,
    },
  }
}

async function installNativeMocks(page: Page, c: SmokeCase): Promise<void> {
  const encoded = maskPath(c.screenId)
  const sd = minimalScreenDefinition(c)

  await page.route(new RegExp(`/api/v1/masks/${encoded}/screen-definition$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sd),
    })
  })

  await page.route(new RegExp(`/api/v1/masks/${encoded}/entity/${c.entityId}$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: c.entityId,
        name: c.title,
        status: 'open',
      }),
    })
  })
}

test.describe('UIX-056 Native route smoke', () => {
  for (const c of SMOKE_CASES) {
    test(`${c.label} — kein 404, native Runtime, Entity sichtbar`, async ({ page }) => {
      await installNativeMocks(page, c)
      const response = await page.goto(c.path, { waitUntil: 'domcontentloaded' })
      expect(response?.status() ?? 200).toBeLessThan(400)

      const root = page.getByTestId(c.testId)
      await expect(root).toBeVisible({ timeout: 30_000 })
      await expect(root).toHaveAttribute('data-runtime', 'native')
      await expect(page.getByRole('heading', { name: c.title })).toBeVisible({ timeout: 30_000 })
      await expect(page.getByRole('tab', { name: /kopf/i })).toBeVisible()
    })
  }

  test('finance/payment-run — Freigabe erfordert Bestätigung (Human Gate)', async ({ page }) => {
    const c = SMOKE_CASES.find((entry) => entry.screenId === 'finance/payment-run')
    if (!c) throw new Error('payment-run case missing')
    await installNativeMocks(page, c)
    await page.goto(c.path, { waitUntil: 'domcontentloaded' })

    const freigeben = page.getByRole('button', { name: /zahlungslauf freigeben/i })
    await expect(freigeben).toBeVisible({ timeout: 30_000 })
    await freigeben.click()

    await expect(page.getByRole('alertdialog')).toBeVisible()
    await expect(page.getByText(/bestätigen|sicher|freigeben/i).first()).toBeVisible()
    await page.getByRole('button', { name: /abbrechen|cancel/i }).click()
    await expect(page.getByRole('alertdialog')).toHaveCount(0)
  })
})
