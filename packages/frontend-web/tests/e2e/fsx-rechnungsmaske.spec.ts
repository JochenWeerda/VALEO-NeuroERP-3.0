/**
 * FSX-RECHNUNGSMASKE-MERIDIAN — Browser-Abnahme der beiden Rechnungsmasken.
 *
 * Geprueft wird, was pytest nicht sehen kann: dass der Renderer die **Form**
 * dieser Definitionen auch darstellt — die Worklist mit ihren Spalten, die
 * Objektseite mit den zwei Registern und dem Deckungsstand an der Position.
 *
 * Die Endpunkte sind gemockt (wie im UIX-056-Smoke), damit der Lauf ohne
 * Backend reproduzierbar bleibt. Die Definitionen selbst sind in
 * `tests/test_meridian_column_navigation_inventory.py` und
 * `tests/test_omnibox_catalog.py` abgesichert; hier geht es um die Darstellung.
 */
import { expect, test, type Page } from '@playwright/test'

const RECHNUNG_ID = 'smoke-invoice'

/** Spiegelt `build_sales_invoices_worklist_screen_definition()`. */
function worklistDefinition() {
  return {
    schemaVersion: 1,
    id: 'sales/invoices',
    domain: 'sales',
    mode: 'list',
    title: 'Ausgangsrechnungen',
    subtitle: 'Faktura / Forderungen',
    adapter: { type: 'native', sourceId: 'sales/invoices', temporary: false },
    permissions: ['*'],
    dataSources: [{ key: 'list', endpoint: '/api/v1/sales/invoices', pageSize: 50 }],
    tabs: [
      {
        key: 'rechnungen',
        label: 'Rechnungen',
        lazy: false,
        keepAlive: true,
        tables: [
          {
            key: 'list',
            label: 'Ausgangsrechnungen',
            dataSourceKey: 'list',
            serverPagination: true,
            pageSize: 50,
            virtualized: true,
            rowHeight: 52,
            rowRouteTemplate: '/verkauf/rechnung/{id}',
            columns: [
              { key: 'invoice_number', label: 'Rechnungsnr.', sortable: true, filterable: true, width: 150 },
              { key: 'customer_id', label: 'Kunde', sortable: true, filterable: true, width: 160 },
              { key: 'invoice_date', label: 'Rechnungsdatum', renderKind: 'date', sortable: true, width: 140 },
              { key: 'due_date', label: 'Faellig', renderKind: 'date', sortable: true, width: 120 },
              { key: 'line_count', label: 'Positionen', numeric: true, width: 100 },
              { key: 'net_amount', label: 'Netto', numeric: true, sortable: true, renderKind: 'currency' },
              { key: 'gross_amount', label: 'Brutto', numeric: true, sortable: true, renderKind: 'currency' },
              { key: 'status', label: 'Status', renderKind: 'status', filterable: true, width: 120 },
            ],
          },
        ],
      },
    ],
    actions: [
      { key: 'export', label: 'Liste exportieren', kind: 'secondary', dangerLevel: 'safe', zone: 'footer' },
    ],
    layout: {
      floorplan: 'worklist',
      columnNavigation: 'listDetail',
      density: 'expertDense',
      contextRail: 'none',
      tableProfile: 'financial',
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
    },
    performance: { initialPayloadBudgetKb: 40, requiresLazyTabs: false, requiresVirtualTables: true, lookupMinChars: 2 },
  }
}

/** Spiegelt `build_sales_invoice_screen_definition()`. */
function belegDefinition() {
  const basis = `/api/v1/sales/invoices/{entity_id}`
  return {
    schemaVersion: 1,
    id: 'sales/invoice',
    domain: 'sales',
    mode: 'detail',
    title: 'Ausgangsrechnung',
    subtitle: 'Verkauf / Faktura',
    adapter: { type: 'native', sourceId: 'sales/invoice', temporary: false },
    permissions: ['*'],
    summaryEndpoint: `${basis}/screen-summary`,
    dataSources: [
      { key: 'entity', endpoint: basis },
      { key: 'positionen', endpoint: `${basis}/tabs/positionen`, pageSize: 50 },
      { key: 'herkunft', endpoint: `${basis}/tabs/herkunft`, pageSize: 50 },
    ],
    tabs: [
      {
        key: 'kopf',
        label: 'Rechnungskopf',
        lazy: false,
        keepAlive: true,
        dataSourceKey: 'entity',
        fields: [
          { key: 'invoice_number', label: 'Rechnungsnr.', type: 'text', readOnly: true },
          { key: 'customer_id', label: 'Kunde', type: 'text', readOnly: true },
          { key: 'status', label: 'Status', type: 'text', readOnly: true },
        ],
      },
      {
        key: 'positionen',
        label: 'Positionen',
        lazy: true,
        keepAlive: false,
        tables: [
          {
            key: 'positionen',
            label: 'Positionen',
            dataSourceKey: 'positionen',
            serverPagination: true,
            pageSize: 50,
            virtualized: true,
            rowHeight: 52,
            columns: [
              { key: 'line_no', label: 'Pos.', width: 60, sortable: true },
              { key: 'description', label: 'Bezeichnung', width: 220, filterable: true },
              { key: 'quantity', label: 'Menge', numeric: true, renderKind: 'number' },
              { key: 'unit', label: 'Einheit', width: 70 },
              { key: 'herkunft', label: 'Herkunft', width: 170, filterable: true },
            ],
          },
        ],
      },
      {
        key: 'herkunft',
        label: 'Herkunft',
        lazy: true,
        keepAlive: false,
        tables: [
          {
            key: 'herkunft',
            label: 'Zuordnungen',
            dataSourceKey: 'herkunft',
            serverPagination: true,
            pageSize: 50,
            virtualized: true,
            rowHeight: 52,
            columns: [
              { key: 'line_no', label: 'Pos.', width: 60, sortable: true },
              { key: 'source_type', label: 'Belegart', width: 120, filterable: true },
              { key: 'source_document_id', label: 'Beleg', width: 220, filterable: true },
              { key: 'source_line_id', label: 'Quellposition', width: 110 },
              { key: 'quantity', label: 'Menge', numeric: true, renderKind: 'number' },
              { key: 'unit', label: 'Einheit', width: 70 },
            ],
          },
        ],
      },
    ],
    actions: [],
    layout: {
      floorplan: 'objectPage',
      columnNavigation: 'single',
      density: 'expertDense',
      contextRail: 'combined',
      tableProfile: 'financial',
      summaryPlacement: 'header',
      stickyHeader: true,
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
    },
    performance: { initialPayloadBudgetKb: 48, requiresLazyTabs: true, requiresVirtualTables: true, lookupMinChars: 2 },
  }
}

async function json(page: Page, muster: RegExp, koerper: unknown): Promise<void> {
  await page.route(muster, async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(koerper) })
  })
}

test.describe('FSX Rechnungsmasken', () => {
  test('Worklist zeigt die Faktura-Spalten samt Positionszahl', async ({ page }) => {
    await json(page, /\/api\/v1\/masks\/sales__invoices\/screen-definition$/, worklistDefinition())
    await json(page, /\/api\/v1\/sales\/invoices(\?|$)/, {
      items: [
        {
          id: RECHNUNG_ID,
          invoice_number: 'RE-0001',
          customer_id: 'K-100',
          invoice_date: '2026-09-15',
          due_date: null,
          line_count: 2,
          net_amount: '2500',
          gross_amount: '2675',
          status: 'entwurf',
        },
      ],
      total: 1,
      limit: 50,
      offset: 0,
      page: 1,
    })

    await page.goto('/verkauf/rechnungen', { waitUntil: 'domcontentloaded' })

    const wurzel = page.getByTestId('sales-invoices-worklist')
    await expect(wurzel).toBeVisible({ timeout: 30_000 })

    const maske = page.getByTestId('screen-sales/invoices')
    await expect(maske).toHaveAttribute('data-floorplan', 'worklist')
    await expect(maske).toHaveAttribute('data-column-navigation', 'listDetail')

    await expect(page.getByText('RE-0001').first()).toBeVisible({ timeout: 30_000 })
    // Die Positionszahl gehoert in die Liste: "sieht der Beleg leer aus?"
    await expect(page.getByText('Positionen').first()).toBeVisible()
  })

  test('Beleg zeigt zwei Register und den Deckungsstand an der Position', async ({ page }) => {
    await json(page, /\/api\/v1\/masks\/sales__invoice\/screen-definition$/, belegDefinition())
    await json(page, new RegExp(`/api/v1/sales/invoices/${RECHNUNG_ID}$`), {
      id: RECHNUNG_ID,
      invoice_number: 'RE-0001',
      customer_id: 'K-100',
      status: 'entwurf',
    })
    await json(page, new RegExp(`/api/v1/sales/invoices/${RECHNUNG_ID}/screen-summary$`), {
      schema_version: 1,
      screen_id: 'sales/invoice',
      invoice_id: RECHNUNG_ID,
      title: 'RE-0001',
      subtitle: 'K-100',
      summary: { status: 'entwurf', positionen: 1, ungedeckte_positionen: '1' },
      available_tabs: ['kopf', 'positionen', 'herkunft'],
      tab_endpoints: {},
      actions: [],
      performance: { initial_payload_budget_kb: 48, tabs_lazy: true },
    })
    await json(page, new RegExp(`/api/v1/sales/invoices/${RECHNUNG_ID}/tabs/positionen`), {
      tab_key: 'positionen',
      table_key: 'invoice_lines',
      items: [
        {
          line_no: '1',
          description: 'Weizen A',
          quantity: 100,
          unit: 'dt',
          herkunft: '40 dt ohne Zuordnung',
          herkunft_art: 'teilweise',
        },
      ],
      page: 1,
      limit: 50,
      total: 1,
    })
    await json(page, new RegExp(`/api/v1/sales/invoices/${RECHNUNG_ID}/tabs/herkunft`), {
      tab_key: 'herkunft',
      table_key: 'invoice_origins',
      items: [
        {
          line_no: '1',
          source_type: 'Lieferschein',
          source_document_id: 'LS-7',
          source_line_id: '1',
          quantity: 60,
          unit: 'dt',
        },
      ],
      page: 1,
      limit: 50,
      total: 1,
    })

    await page.goto(`/verkauf/rechnung/${RECHNUNG_ID}`, { waitUntil: 'domcontentloaded' })

    const wurzel = page.getByTestId('sales-invoice')
    await expect(wurzel).toBeVisible({ timeout: 30_000 })
    const maske = page.getByTestId('screen-sales/invoice')
    await expect(maske).toHaveAttribute('data-floorplan', 'objectPage')

    await expect(page.getByRole('tab', { name: /positionen/i })).toBeVisible({ timeout: 30_000 })
    await expect(page.getByRole('tab', { name: /herkunft/i })).toBeVisible()

    // Der Deckungsstand steht an der Position — die Luecke als Zahl.
    await page.getByRole('tab', { name: /positionen/i }).click()
    await expect(page.getByText('40 dt ohne Zuordnung').first()).toBeVisible({ timeout: 30_000 })

    // Und die Zuordnungen liegen als eigene Tabelle daneben.
    await page.getByRole('tab', { name: /herkunft/i }).click()
    await expect(page.getByText('LS-7').first()).toBeVisible({ timeout: 30_000 })
  })
})
