import type { Page } from '@playwright/test'

export const BENCH_ORDER_ID = 'bench-order'
export const BENCH_CONTRACT_ID = 'bench-contract'

const POSITION_ROWS = Array.from({ length: 50 }, (_, index) => ({
  line_number: index + 1,
  article_number: `ART-${String(index + 1).padStart(3, '0')}`,
  description: `Benchmark Position ${index + 1}`,
  quantity: 10,
  unit_price: 100,
  line_total: 1000,
}))

const CONTRACT_LINES = Array.from({ length: 50 }, (_, index) => ({
  line_id: `line-${index + 1}`,
  position_no: index + 1,
  article_id: `ART-${String(index + 1).padStart(3, '0')}`,
  description1: `Kontraktzeile ${index + 1}`,
  qty_contract: 100,
  qty_remaining: 40,
  unit_price: 220,
}))

export async function setupSalesOrderBenchmarkMocks(page: Page): Promise<void> {
  await page.route(/\/api\/v1\/sales\/orders\/?(\?.*)?$/, async (route) => {
    if (route.request().method() !== 'GET') {
      await route.continue()
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], total: 0, skip: 0, limit: 100 }),
    })
  })

  await page.route(/\/api\/v1\/sales\/orders\/bench-order\/screen-summary$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        schema_version: 1,
        screen_id: 'sales/sales-order',
        order_id: BENCH_ORDER_ID,
        tenant_id: 'tenant-1',
        title: 'Benchmark Auftrag',
        subtitle: 'SO-BENCH-100',
        customer_name: 'Benchmark Kunde AG',
        summary: {
          total_amount: 50000,
          item_count: POSITION_ROWS.length,
          status: 'open',
          delivery_date: '2026-08-01',
        },
        available_tabs: ['kopf', 'positionen'],
        tab_endpoints: {
          positionen: `/api/v1/sales/orders/${BENCH_ORDER_ID}/tabs/positionen`,
        },
        actions: [],
        performance: {
          initial_payload_budget_kb: 56,
          tabs_lazy: true,
          lookup_min_chars: 2,
          default_table_limit: 25,
        },
      }),
    })
  })

  await page.route(/\/api\/v1\/sales\/orders\/bench-order\/tabs\/positionen/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        tab_key: 'positionen',
        table_key: 'order_items',
        items: POSITION_ROWS.slice(0, 25),
        page: 1,
        limit: 25,
        total: POSITION_ROWS.length,
      }),
    })
  })

  await page.route(/\/api\/v1\/sales\/orders\/bench-order$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: BENCH_ORDER_ID,
        tenant_id: 'tenant-1',
        order_number: 'SO-BENCH-100',
        subject: 'Benchmark Auftrag',
        total_amount: 50000,
        currency: 'EUR',
        status: 'open',
        delivery_date: '2026-08-01',
        items: POSITION_ROWS,
        version: 1,
      }),
    })
  })

  await page.route(/\/api\/v1\/masks\/sales%2Fsales-order\/screen-definition$/, async (route) => {
    await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'mock' }) })
  })

  await page.route(/\/api\/v1\/crm\/customers\//, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'bench-customer',
        customer_number: 'K-BENCH',
        name: 'Benchmark Kunde AG',
        company_name: 'Benchmark Kunde AG',
      }),
    })
  })

  await page.route(/\/api\/v1\/sales\/eligibility\//, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ eligible: true, reasons: [] }),
    })
  })
}

export async function setupKontraktBenchmarkMocks(page: Page): Promise<void> {
  await page.route(/\/api\/v1\/kontrakte\/bench-contract\/screen-summary$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        schema_version: 1,
        screen_id: 'agrar/kontrakte',
        contract_id: BENCH_CONTRACT_ID,
        tenant_id: 'tenant-1',
        title: 'K-BENCH-100',
        subtitle: 'Benchmark Landwirt',
        party_name: 'Benchmark Landwirt',
        summary: {
          line_count: CONTRACT_LINES.length,
          rest_quantity: 1200,
          total_quantity: 5000,
          unit: 't',
          status: 'OFFEN',
          contract_type: 'VERKAUF',
          valid_to: '2026-12-31',
        },
        available_tabs: ['kopf', 'positionen', 'umsaetze'],
        tab_endpoints: {
          positionen: `/api/v1/kontrakte/${BENCH_CONTRACT_ID}/tabs/positionen`,
          umsaetze: `/api/v1/kontrakte/${BENCH_CONTRACT_ID}/tabs/umsaetze`,
        },
        actions: [],
        performance: {
          initial_payload_budget_kb: 52,
          tabs_lazy: true,
          lookup_min_chars: 2,
          default_table_limit: 25,
        },
      }),
    })
  })

  await page.route(/\/api\/v1\/kontrakte\/bench-contract\/tabs\/positionen/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        tab_key: 'positionen',
        table_key: 'contract_lines',
        items: CONTRACT_LINES.slice(0, 25),
        page: 1,
        limit: 25,
        total: CONTRACT_LINES.length,
      }),
    })
  })

  await page.route(/\/api\/v1\/kontrakte\/bench-contract\/tabs\/umsaetze/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        tab_key: 'umsaetze',
        table_key: 'contract_movements',
        items: [],
        page: 1,
        limit: 25,
        total: 0,
      }),
    })
  })

  await page.route(/\/api\/v1\/kontrakte\/bench-contract$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        contract_id: BENCH_CONTRACT_ID,
        contract_no: 'K-BENCH-100',
        contract_type: 'VERKAUF',
        party_id: 'party-bench',
        quantity_type: 'GESAMTKONTRAKT',
        total_quantity: 5000,
        rest_quantity: 1200,
        unit: 't',
        allow_overdelivery: false,
        status: 'OFFEN',
        valid_from: '2026-01-01',
        valid_to: '2026-12-31',
        lines: CONTRACT_LINES,
      }),
    })
  })

  await page.route(/\/api\/v1\/kontrakte\/positionen/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [] }),
    })
  })

  await page.route(/\/api\/v1\/masks\/agrar%2Fkontrakte\/screen-definition$/, async (route) => {
    await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'mock' }) })
  })
}
