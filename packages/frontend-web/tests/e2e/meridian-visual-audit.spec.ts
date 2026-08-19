/**
 * Meridian Visual-Audit fuer repraesentative native Masken.
 *
 * Nutzt dieselben Render-/QC-Helfer wie die Benutzerhandbuch-Screenshots,
 * bleibt aber fokussiert auf den Single Mask Builder und drei Desktop-Viewports.
 */
import { expect, test, type Page, type TestInfo } from '@playwright/test'

import { waitUntilRenderable } from './handbuch-page-readiness'
import { assessContentQuality, resolveCaptureLocator } from './handbuch-screenshot-qc'

type ViewportCase = {
  name: string
  width: number
  height: number
}

type MeridianCase = {
  label: string
  slug: string
  path: string
  screenId: string
  testId: string
  title: string
  entityId: string
  domain: 'finance' | 'crm' | 'lager' | 'sales'
  floorplan: 'objectPage' | 'transaction' | 'cockpit'
  density: 'compact' | 'expertDense'
  contextRail: 'audit' | 'combined'
  tableProfile: 'financial' | 'inventory' | 'standard'
  tableKey: string
  tableLabel: string
  primaryActionLabel: string
  familiarWorkPattern?: boolean
  summaryPlacement?: 'header' | 'footer'
  rows: Record<string, unknown>[]
}

const VIEWPORTS: ViewportCase[] = [
  { name: '1366x768', width: 1366, height: 768 },
  { name: '1440x900', width: 1440, height: 900 },
  { name: '1920x1080', width: 1920, height: 1080 },
]

const CASES: MeridianCase[] = [
  {
    label: 'Finance Zahlungslauf',
    slug: 'finance-payment-run',
    path: '/finance/payment-run/visual-payment-run',
    screenId: 'finance/payment-run',
    testId: 'finance-payment-run',
    title: 'Visual Zahlungslauf',
    entityId: 'visual-payment-run',
    domain: 'finance',
    floorplan: 'transaction',
    density: 'expertDense',
    contextRail: 'audit',
    tableProfile: 'financial',
    tableKey: 'open_items',
    tableLabel: 'Offene Posten',
    primaryActionLabel: 'Zahlungslauf freigeben',
    rows: [
      { beleg: 'RE-240081', faellig: '2026-07-15', betrag: 4200.75, auditReason: 'Vier-Augen-Pruefung offen', status: 'pruefung' },
      { beleg: 'RE-240082', faellig: '2026-07-18', betrag: 815.2, auditReason: 'Skonto-Frist', status: 'bereit' },
    ],
  },
  {
    label: 'CRM Customer 360',
    slug: 'crm-customer-360',
    path: '/crm/kunden/visual-customer',
    screenId: 'crm/customer-360',
    testId: 'crm-customer-360',
    title: 'Visual Kunde 360',
    entityId: 'visual-customer',
    domain: 'crm',
    floorplan: 'cockpit',
    density: 'compact',
    contextRail: 'combined',
    tableProfile: 'standard',
    tableKey: 'activities',
    tableLabel: 'Aktivitaeten',
    primaryActionLabel: 'Naechste Aktion planen',
    familiarWorkPattern: true,
    rows: [
      { datum: '2026-07-04', typ: 'Anruf', status: 'offen', verantwortung: 'Innendienst' },
      { datum: '2026-07-03', typ: 'Angebot', status: 'gesendet', verantwortung: 'Vertrieb' },
    ],
  },
  {
    label: 'Lager Artikelbestand',
    slug: 'lager-article-stock',
    path: '/lager/article-stock/visual-article',
    screenId: 'lager/article-stock',
    testId: 'lager-article-stock',
    title: 'Visual Artikelbestand',
    entityId: 'visual-article',
    domain: 'lager',
    floorplan: 'objectPage',
    density: 'expertDense',
    contextRail: 'combined',
    tableProfile: 'inventory',
    tableKey: 'movements',
    tableLabel: 'Bestandsbewegungen',
    primaryActionLabel: 'Bestand pruefen',
    familiarWorkPattern: true,
    rows: [
      { artikel: 'A-1000', lagerort: 'Silo 3', bestand: 128.5, reserviert: 24, einheit: 't', status: 'frei' },
      { artikel: 'A-1000', lagerort: 'Halle 1', bestand: 48, reserviert: 12, einheit: 't', status: 'qs' },
    ],
  },
  {
    label: 'Verkauf Lieferschein',
    slug: 'sales-delivery-note',
    path: '/sales/delivery-note/visual-delivery',
    screenId: 'sales/delivery-note',
    testId: 'sales-delivery-note',
    title: 'Visual Lieferschein',
    entityId: 'visual-delivery',
    domain: 'sales',
    floorplan: 'transaction',
    density: 'expertDense',
    contextRail: 'combined',
    tableProfile: 'standard',
    tableKey: 'positionen',
    tableLabel: 'Positionen',
    primaryActionLabel: 'Lieferschein drucken',
    familiarWorkPattern: true,
    summaryPlacement: 'footer',
    rows: [
      { pos: 10, artikel: 'A-1000', bezeichnung: 'Testartikel', menge: 12.5, einheit: 't', status: 'bereit' },
      { pos: 20, artikel: 'A-2000', bezeichnung: 'Zweiter Artikel', menge: 4, einheit: 't', status: 'bereit' },
    ],
  },
]

function maskPath(screenId: string): string {
  return screenId.replace(/\//g, '__')
}

function tableColumns(c: MeridianCase) {
  if (c.tableProfile === 'financial') {
    return [
      { key: 'beleg', label: 'Beleg', width: 150, sortable: true, filterable: true },
      { key: 'faellig', label: 'Faellig', width: 130, renderKind: 'date' },
      { key: 'betrag', label: 'Betrag', width: 140, numeric: true, renderKind: 'currency' },
      { key: 'auditReason', label: 'AuditReason', width: 220 },
      { key: 'status', label: 'Status', width: 120, renderKind: 'status' },
    ]
  }
  if (c.tableProfile === 'inventory') {
    return [
      { key: 'artikel', label: 'Artikel', width: 130, sortable: true, filterable: true },
      { key: 'lagerort', label: 'Lagerort', width: 150 },
      { key: 'bestand', label: 'Bestand', width: 120, numeric: true, renderKind: 'number' },
      { key: 'reserviert', label: 'Reserviert', width: 120, numeric: true, renderKind: 'number' },
      { key: 'einheit', label: 'Einheit', width: 90 },
      { key: 'status', label: 'Status', width: 110, renderKind: 'status' },
    ]
  }
  if (c.domain === 'sales') {
    return [
      { key: 'pos', label: 'Pos.', width: 80, sortable: true },
      { key: 'artikel', label: 'Artikel-Nr.', width: 130, filterable: true },
      { key: 'bezeichnung', label: 'Bezeichnung', width: 220 },
      { key: 'menge', label: 'Menge', width: 120, numeric: true, renderKind: 'number' },
      { key: 'einheit', label: 'Einheit', width: 90 },
      { key: 'status', label: 'Status', width: 110, renderKind: 'status' },
    ]
  }
  return [
    { key: 'datum', label: 'Datum', width: 130, renderKind: 'date' },
    { key: 'typ', label: 'Typ', width: 150 },
    { key: 'status', label: 'Status', width: 120, renderKind: 'status' },
    { key: 'verantwortung', label: 'Verantwortung', width: 180 },
  ]
}

function screenDefinition(c: MeridianCase) {
  const encoded = maskPath(c.screenId)
  return {
    schemaVersion: 1,
    id: c.screenId,
    domain: c.domain,
    mode: 'detail',
    title: c.title,
    subtitle: 'Meridian Visual-Audit',
    adapter: { type: 'native', sourceId: c.screenId, temporary: false },
    fields: [
      { key: 'name', label: 'Name', type: 'text', readOnly: true },
      { key: 'status', label: 'Status', type: 'text', readOnly: true },
      { key: 'owner', label: 'Verantwortung', type: 'text', readOnly: true },
    ],
    dataSources: [
      { key: 'entity', endpoint: `/api/v1/masks/${encoded}/entity/{entity_id}` },
      { key: c.tableKey, endpoint: `/api/v1/masks/${encoded}/tables/${c.tableKey}/{entity_id}` },
    ],
    tables: [
      {
        key: c.tableKey,
        label: c.tableLabel,
        dataSourceKey: c.tableKey,
        pageSize: 10,
        virtualized: true,
        rowHeight: 44,
        serverPagination: true,
        columns: tableColumns(c),
      },
    ],
    tabs: [
      {
        key: 'uebersicht',
        label: 'Uebersicht',
        lazy: false,
        keepAlive: true,
        fields: [
          { key: 'name', label: 'Name', type: 'text', readOnly: true },
          { key: 'status', label: 'Status', type: 'text', readOnly: true },
        ],
      },
      {
        key: 'audit',
        label: c.contextRail === 'audit' ? 'Audit' : 'Kontext',
        lazy: true,
        keepAlive: true,
        fields: [
          { key: 'lastChange', label: 'Letzte Aenderung', type: 'text', readOnly: true },
          { key: 'nextAction', label: 'Naechste Aktion', type: 'text', readOnly: true },
        ],
      },
    ],
    summary: [
      { key: 'status', label: 'Status', value: 'in Pruefung', tone: 'warning' },
      { key: 'risk', label: 'Audit', value: c.contextRail === 'audit' ? 'Begruendung sichtbar' : 'Kontext aktiv', tone: 'info' },
      { key: 'density', label: 'Dichte', value: c.density, tone: 'neutral' },
    ],
    workflow: {
      processKey: `${c.slug}-workflow`,
      status: 'in_pruefung',
      nextActionKey: 'primary',
      auditRequired: c.contextRail === 'audit',
      evidenceRequired: c.tableProfile !== 'standard',
    },
    actions: [
      { key: 'primary', label: c.primaryActionLabel, kind: 'primary', zone: c.familiarWorkPattern ? 'commit' : 'header' },
      { key: 'secondary', label: 'Notiz erfassen', kind: 'secondary', zone: c.familiarWorkPattern ? 'footer' : 'header' },
      {
        key: 'critical',
        label: c.tableProfile === 'financial' ? 'Zahlungslauf stoppen' : 'Sperre setzen',
        kind: 'danger',
        dangerLevel: c.tableProfile === 'financial' ? 'critical' : 'high',
        requiresConfirmation: true,
        auditReasonRequired: true,
        zone: c.familiarWorkPattern ? 'footer' : 'header',
      },
    ],
    permissions: ['*'],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
      floorplan: c.floorplan,
      density: c.density,
      contextRail: c.contextRail,
      tableProfile: c.tableProfile,
      summaryPlacement: c.summaryPlacement ?? 'header',
      stickyHeader: c.familiarWorkPattern ?? false,
      stickyFooter: c.familiarWorkPattern ?? false,
    },
    interaction: { enterMovesFocus: c.familiarWorkPattern ?? false },
    performance: {
      initialPayloadBudgetKb: 64,
      requiresLazyTabs: true,
      requiresVirtualTables: true,
      lookupMinChars: 2,
    },
  }
}

async function installNativeMocks(page: Page, c: MeridianCase): Promise<void> {
  const encoded = maskPath(c.screenId)
  await page.route(new RegExp(`/api/v1/masks/${encoded}/screen-definition$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(screenDefinition(c)),
    })
  })
  await page.route(new RegExp(`/api/v1/masks/${encoded}/entity/${c.entityId}$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: c.entityId,
        name: c.title,
        status: 'in Pruefung',
        owner: 'Codex Visual Audit',
        lastChange: '2026-07-05 20:00',
        nextAction: c.primaryActionLabel,
      }),
    })
  })
  await page.route(new RegExp(`/api/v1/masks/${encoded}/tables/${c.tableKey}/${c.entityId}(\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: c.rows, total: c.rows.length }),
    })
  })
}

async function assertNoViewportOverflow(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => {
    const vw = window.innerWidth
    return Array.from(document.querySelectorAll('[data-runtime="native"] *'))
      .map((el) => {
        const rect = el.getBoundingClientRect()
        const style = getComputedStyle(el)
        if (style.display === 'none' || style.visibility === 'hidden') return null
        if (style.position === 'fixed' || style.position === 'absolute') return null
        if (rect.width <= 0 || rect.height <= 0) return null
        if (rect.left < -8 || rect.right > vw + 8) {
          return `${el.tagName.toLowerCase()} right=${Math.round(rect.right)} vw=${vw}`
        }
        return null
      })
      .filter(Boolean)
      .slice(0, 5)
  })
  expect(overflow).toEqual([])
}

async function captureAuditedSurface(page: Page, c: MeridianCase, viewport: ViewportCase, testInfo: TestInfo): Promise<void> {
  const qc = await assessContentQuality(page)
  expect(qc.approval, qc.issues.join('; ')).not.toBe('rejected')

  const { locator } = await resolveCaptureLocator(page)
  await locator.screenshot({
    path: testInfo.outputPath(`meridian-${c.slug}-${viewport.name}.png`),
    animations: 'disabled',
    timeout: 30_000,
  })
}

for (const viewport of VIEWPORTS) {
  test.describe(`Meridian Visual-Audit ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    for (const c of CASES) {
      test(`${c.label}`, async ({ page }, testInfo) => {
        await installNativeMocks(page, c)
        const response = await page.goto(c.path, { waitUntil: 'domcontentloaded' })
        expect(response?.status() ?? 200).toBeLessThan(400)

        const renderState = await waitUntilRenderable(page, 45_000)
        expect(renderState).toBe('ready')

        const shell = page.getByTestId(c.testId)
        await expect(shell).toBeVisible()
        await expect(shell).toHaveAttribute('data-runtime', 'native')

        const rendererRoot = page.getByTestId(`screen-${c.screenId}`)
        await expect(rendererRoot).toHaveAttribute('data-floorplan', c.floorplan)
        await expect(rendererRoot).toHaveAttribute('data-density', c.density)
        await expect(rendererRoot).toHaveAttribute('data-context-rail', c.contextRail)
        await expect(rendererRoot).toHaveAttribute('data-table-profile', c.tableProfile)

        await expect(page.getByRole('heading', { name: c.title })).toBeVisible()
        if (!c.familiarWorkPattern) {
          await expect(page.getByTestId('meridian-action-bar')).toBeVisible()
        }
        await expect(page.getByRole('button', { name: c.primaryActionLabel })).toBeVisible()
        if (c.familiarWorkPattern) {
          await expect(page.getByTestId('meridian-footer-actions')).toBeVisible()
          await expect(page.getByTestId('meridian-footer-actions')).toHaveAttribute('data-sticky', 'true')
          await expect(page.getByTestId('action-primary')).toHaveAttribute('data-action-zone', 'commit')
        }
        if (c.summaryPlacement === 'footer') {
          const summary = page.getByTestId('mask-summary')
          const footer = page.getByTestId('meridian-footer-actions')
          await expect(summary).toBeVisible()
          expect(await summary.evaluate((node, footerNode) => Boolean(node.compareDocumentPosition(footerNode as Node) & Node.DOCUMENT_POSITION_FOLLOWING), await footer.elementHandle())).toBe(true)
        }
        await expect(page.getByTestId('workflow-panel-placeholder')).toBeVisible()

        const table = page.getByTestId(`table-${c.tableKey}`)
        await expect(table).toBeVisible()
        await expect(table).toHaveAttribute('data-table-profile', c.tableProfile)
        await expect(table.getByText(`${c.tableProfile[0].toUpperCase()}${c.tableProfile.slice(1)} Table Profile`)).toBeVisible()

        await page.getByRole('tab', { name: c.contextRail === 'audit' ? 'Audit' : 'Kontext' }).click()
        await expect(page.getByText(c.primaryActionLabel).first()).toBeVisible()

        await assertNoViewportOverflow(page)
        await captureAuditedSurface(page, c, viewport, testInfo)
      })
    }
  })
}
