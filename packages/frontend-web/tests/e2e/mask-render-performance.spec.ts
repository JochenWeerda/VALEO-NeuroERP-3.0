import { expect, test } from '@playwright/test'

const CRM_PILOT_ENABLED = process.env.VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER === 'true'
const SALES_PILOT_ENABLED = process.env.VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER === 'true'

test.describe('Mask render performance smoke', () => {
  test.skip(!CRM_PILOT_ENABLED, 'Set VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true')

  test('CRM pilot loads shell before tab API', async ({ page }) => {
    const tabRequests: string[] = []
    page.on('request', (request) => {
      if (/\/api\/v1\/crm\/customers\/perf-customer\/tabs\//.test(request.url())) {
        tabRequests.push(request.url())
      }
    })

    await page.route(/\/api\/v1\/crm\/customers\/perf-customer\/screen-summary$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          schema_version: 1,
          customer_id: 'perf-customer',
          title: 'Perf Kunde',
          subtitle: 'K-100',
          summary: { sales_ytd: 0, open_items_total: 0, recent_activity_count: 0, credit_status: 'ok' },
          available_tabs: ['kontakte', 'auftraege'],
          tab_endpoints: {
            kontakte: '/api/v1/crm/customers/perf-customer/tabs/kontakte',
            auftraege: '/api/v1/crm/customers/perf-customer/tabs/auftraege',
          },
          actions: [],
          performance: { initial_payload_budget_kb: 48, tabs_lazy: true, lookup_min_chars: 2 },
        }),
      })
    })

    await page.route(/\/api\/v1\/crm\/customers\/perf-customer$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'perf-customer', name: 'Perf Kunde', kunden_nr: 'K-100' }),
      })
    })

    await page.route(/\/api\/v1\/masks\/(?:crm%2Fcustomer-360|crm__customer-360)\/screen-definition$/, async (route) => {
      await route.fulfill({ status: 404, body: JSON.stringify({ detail: 'mock' }) })
    })

    await page.goto('/crm/kunden-stamm-modern?id=perf-customer', { waitUntil: 'domcontentloaded' })
    await expect(page.getByTestId('universal-customer-mask-pilot')).toBeVisible()
    expect(tabRequests).toHaveLength(0)

    await page.getByRole('tab', { name: /ansprechpartner/i }).click()
    await expect.poll(() => tabRequests.length).toBeGreaterThan(0)
  })
})

test.describe('Sales mask render performance smoke', () => {
  test.skip(!SALES_PILOT_ENABLED, 'Set VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER=true')

  test('virtual table stays DOM-light after tab switch', async ({ page }) => {
    await page.route(/\/api\/v1\/sales\/orders\/perf-order\/screen-summary$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          schema_version: 1,
          screen_id: 'sales/sales-order',
          order_id: 'perf-order',
          title: 'Perf Order',
          subtitle: 'SO-100',
          summary: { total_amount: 100, item_count: 50, status: 'open', delivery_date: '2026-08-01' },
          available_tabs: ['positionen'],
          tab_endpoints: { positionen: '/api/v1/sales/orders/perf-order/tabs/positionen' },
          actions: [],
          performance: { initial_payload_budget_kb: 56, tabs_lazy: true, lookup_min_chars: 2 },
        }),
      })
    })

    const rows = Array.from({ length: 50 }, (_, index) => ({
      line_number: index + 1,
      article_number: `ART-${index}`,
      description: `Position ${index}`,
      quantity: 1,
      unit_price: 10,
      line_total: 10,
    }))

    await page.route(/\/api\/v1\/sales\/orders\/perf-order\/tabs\/positionen/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tab_key: 'positionen',
          table_key: 'order_items',
          items: rows,
          page: 1,
          limit: 25,
          total: 50,
        }),
      })
    })

    await page.route(/\/api\/v1\/sales\/orders\/perf-order$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'perf-order',
          tenant_id: 'tenant-1',
          order_number: 'SO-100',
          subject: 'Perf',
          total_amount: 100,
          currency: 'EUR',
          status: 'open',
          items: [],
          version: 1,
        }),
      })
    })

    await page.goto('/sales/order-editor/perf-order', { waitUntil: 'domcontentloaded' })
    await page.getByRole('tab', { name: /positionen/i }).click()
    await expect(page.getByRole('button', { name: /Position 0/i })).toBeVisible()

    const domRows = await page.locator('[data-testid="virtual-data-table"] button[type="button"]').count()
    expect(domRows).toBeLessThanOrEqual(60)
  })
})
