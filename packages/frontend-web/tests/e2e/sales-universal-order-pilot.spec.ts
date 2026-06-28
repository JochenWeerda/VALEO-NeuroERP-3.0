import { expect, test } from '@playwright/test'

const PILOT_ENABLED = process.env.VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER === 'true'

test.describe('Sales Universal Order Pilot', () => {
  test.skip(!PILOT_ENABLED, 'Set VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER=true to run the pilot smoke.')

  test.beforeEach(async ({ page }) => {
    await page.route(/\/api\/v1\/sales\/orders\/e2e-order\/screen-summary$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          schema_version: 1,
          screen_id: 'sales/sales-order',
          order_id: 'e2e-order',
          tenant_id: 'tenant-1',
          title: 'E2E Auftrag',
          subtitle: 'SO-E2E-100',
          customer_name: 'E2E Kunde',
          summary: {
            total_amount: 2400,
            item_count: 1,
            status: 'open',
            delivery_date: '2026-07-15',
          },
          available_tabs: ['kopf', 'positionen', 'lieferung'],
          tab_endpoints: {
            positionen: '/api/v1/sales/orders/e2e-order/tabs/positionen',
          },
          actions: [{ key: 'edit', label: 'Bearbeiten', permission: 'sales.order.update' }],
          performance: {
            initial_payload_budget_kb: 56,
            tabs_lazy: true,
            lookup_min_chars: 2,
            default_table_limit: 25,
          },
        }),
      })
    })

    await page.route(/\/api\/v1\/sales\/orders\/e2e-order\/tabs\/positionen$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tab_key: 'positionen',
          table_key: 'order_items',
          items: [
            {
              line_number: 1,
              article_number: 'WEIZEN-01',
              description: 'Weizen Premium',
              quantity: 10,
              unit_price: 240,
              line_total: 2400,
            },
          ],
        }),
      })
    })

    await page.route(/\/api\/v1\/masks\/sales%2Fsales-order\/screen-definition$/, async (route) => {
      await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'mock fallback' }) })
    })

    await page.route(/\/api\/v1\/sales\/orders\/e2e-order$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'e2e-order',
          tenant_id: 'tenant-1',
          order_number: 'SO-E2E-100',
          subject: 'E2E Auftrag',
          total_amount: 2400,
          currency: 'EUR',
          status: 'open',
          items: [],
          version: 1,
        }),
      })
    })
  })

  test('renders summary-first shell for existing order', async ({ page }) => {
    await page.goto('/sales/order-editor/e2e-order', { waitUntil: 'domcontentloaded' })

    await expect(page.getByTestId('universal-sales-order-pilot')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'E2E Auftrag' })).toBeVisible()
    await expect(page.getByText('Auftragssumme')).toBeVisible()
  })

  test('loads positions after tab switch', async ({ page }) => {
    const tabResponse = page.waitForResponse(/\/api\/v1\/sales\/orders\/e2e-order\/tabs\/positionen$/)
    await page.goto('/sales/order-editor/e2e-order', { waitUntil: 'domcontentloaded' })

    await page.getByRole('tab', { name: /positionen/i }).click()
    await tabResponse
    await expect(page.getByRole('button', { name: /Weizen Premium/i })).toBeVisible()
  })
})
