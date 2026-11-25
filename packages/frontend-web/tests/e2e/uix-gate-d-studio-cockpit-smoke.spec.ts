/**
 * Gate D (Browser) — Made-by-Studio Sichtnachweis fuer Studio-Cockpits
 * aus den Open-Routes-Hebungen (Batch 24–28).
 *
 * Mockt ScreenDefinition + flache Listen/Overview-APIs; prueft Routing,
 * native-cockpit Runtime-Shell und sichtbaren Titel (publizierte Route).
 */
import { expect, test, type Page } from '@playwright/test'
import { setzeUiTestsitzung } from './helpers/ui-testsitzung'

type CockpitCase = {
  label: string
  path: string
  screenId: string
  testId: string
  title: string
  listEndpoint?: string
  overviewEndpoint?: string
}

const COCKPIT_CASES: CockpitCase[] = [
  {
    label: 'admin/externe-gates',
    path: '/admin/externe-gates',
    screenId: 'admin/externe-gates',
    testId: 'screen-admin/externe-gates',
    title: 'Externe Gates',
    overviewEndpoint: '/api/v1/external-gates/overview',
    listEndpoint: '/api/v1/external-gates/items',
  },
  {
    label: 'admin/command-monitor',
    path: '/admin/command-monitor',
    screenId: 'admin/command-monitor',
    testId: 'screen-admin/command-monitor',
    title: 'Command-Monitor',
  },
  {
    label: 'agrar/milchvieh-crosssell',
    path: '/agrar/milchvieh-crosssell',
    screenId: 'agrar/milchvieh-crosssell',
    testId: 'screen-agrar/milchvieh-crosssell',
    title: 'Milchvieh Cross-Sell',
  },
  // Specialized workbenches (Batches 28–38): native-cockpit shell + specialized surface
  {
    label: 'lager/materialfluss',
    path: '/lager/materialfluss',
    screenId: 'lager/materialfluss',
    testId: 'screen-lager/materialfluss',
    title: 'Materialfluss',
  },
  {
    label: 'konditionen/konditionssystem',
    path: '/konditionen/konditionssystem',
    screenId: 'konditionen/konditionssystem',
    testId: 'screen-konditionen/konditionssystem',
    title: 'Konditionssystem',
  },
  {
    label: 'fuhrpark/fahrzeug-vertiefung',
    path: '/fuhrpark/fahrzeug-vertiefung',
    screenId: 'fuhrpark/fahrzeug-vertiefung',
    testId: 'screen-fuhrpark/fahrzeug-vertiefung',
    title: 'Fahrzeug-Vertiefung',
  },
  // Prefixe, die vor Batch 41 an page-module-loader scheiterten
  {
    label: 'dms/archiv-suche',
    path: '/dms/archiv-suche',
    screenId: 'dms/archiv-suche',
    testId: 'dms-archiv-suche',
    title: 'Archiv-Suche',
  },
  {
    label: 'betrieb/maschinen-stamm',
    path: '/betrieb/maschinen-stamm',
    screenId: 'betrieb/maschinen-stamm',
    testId: 'betrieb-maschinen-stamm',
    title: 'Maschinen-Stamm',
  },
]

function maskPath(screenId: string): string {
  return screenId.replace(/\//g, '__')
}

function minimalCockpitDefinition(c: CockpitCase) {
  return {
    schemaVersion: 1,
    id: c.screenId,
    domain: c.screenId.split('/')[0],
    mode: 'cockpit',
    title: c.title,
    adapter: { type: 'native', sourceId: c.screenId, temporary: false },
    fields: [
      { key: 'label', label: 'Name', type: 'text', readOnly: true },
      { key: 'status', label: 'Status', type: 'text', readOnly: true },
    ],
    dataSources: [
      ...(c.overviewEndpoint
        ? [{ key: 'entity', endpoint: c.overviewEndpoint }]
        : [{ key: 'entity', endpoint: `/api/v1/masks/${maskPath(c.screenId)}/overview` }]),
      ...(c.listEndpoint
        ? [{ key: 'items', endpoint: c.listEndpoint, pageSize: 50 }]
        : [{ key: 'items', endpoint: `/api/v1/masks/${maskPath(c.screenId)}/items`, pageSize: 50 }]),
    ],
    summary: [
      { key: 'gesamt', label: 'Gesamt', tone: 'neutral' },
    ],
    tables: [
      {
        key: 'items',
        label: 'Eintraege',
        dataSourceKey: 'items',
        pageSize: 50,
        columns: [
          { key: 'label', label: 'Name', priority: 'primary' },
          { key: 'status', label: 'Status', priority: 'primary' },
        ],
        rowActions: [],
      },
    ],
    actions: [
      {
        key: 'refresh',
        label: 'Aktualisieren',
        kind: 'secondary',
        zone: 'header',
        dangerLevel: 'safe',
        localEffect: 'refetch',
      },
    ],
    permissions: ['*'],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
      floorplan: 'cockpit',
      density: 'compact',
      contextRail: 'combined',
      tableProfile: 'audit',
    },
    performance: {
      initialPayloadBudgetKb: 48,
      requiresLazyTabs: false,
      requiresVirtualTables: true,
      lookupMinChars: 2,
    },
    noWorkflowReason: 'Gate-D-Smoke ohne Beleg-Lebenszyklus.',
  }
}

async function installCockpitMocks(page: Page, c: CockpitCase): Promise<void> {
  const encoded = maskPath(c.screenId)
  const sd = minimalCockpitDefinition(c)

  await page.route(new RegExp(`/api/v1/masks/${encoded}/screen-definition$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sd),
    })
  })

  const overviewPath = c.overviewEndpoint ?? `/api/v1/masks/${encoded}/overview`
  await page.route(`**${overviewPath}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ gesamt: 1, ok_count: 1, problem_count: 0 }),
    })
  })

  const listPath = c.listEndpoint ?? `/api/v1/masks/${encoded}/items`
  await page.route(`**${listPath}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 'smoke-1', label: c.title, status: 'ok' }]),
    })
  })
}

async function applyTheme(page: Page, theme: 'light' | 'dark'): Promise<void> {
  await page.addInitScript((mode) => {
    try {
      window.localStorage.setItem('theme', mode)
    } catch {
      /* storage may be blocked in locked-down browsers */
    }
    const root = document.documentElement
    root.classList.toggle('dark', mode === 'dark')
    root.classList.toggle('light', mode === 'light')
  }, theme)
}

test.describe('Gate D — Studio Cockpit Browser Smoke (Made-by-Studio)', () => {
  test.beforeEach(async ({ page }) => {
    // UI-Testsitzung: unsigniertes Token nur fuer Render/Routing (kein Live-SSO / keine API-Rechte).
    await setzeUiTestsitzung(page)
  })

  for (const c of COCKPIT_CASES) {
    for (const theme of ['light', 'dark'] as const) {
      test(`${c.label} — native-cockpit Runtime, Titel sichtbar (${theme})`, async ({ page }) => {
        await applyTheme(page, theme)
        await installCockpitMocks(page, c)
        const response = await page.goto(c.path, { waitUntil: 'domcontentloaded' })
        expect(response?.status() ?? 200).toBeLessThan(400)

        await expect(page.locator('html')).toHaveClass(
          theme === 'dark' ? /(?:^|\s)dark(?:\s|$)/ : /(?:^|\s)light(?:\s|$)/,
        )

        // Cockpit-Shell und Renderer teilen oft denselben testId — Runtime-Attribut ist eindeutig.
        const root = page.locator(`[data-testid="${c.testId}"][data-runtime="native-cockpit"]`)
        await expect(root).toBeVisible({ timeout: 30_000 })
        await expect(page.getByRole('heading', { name: c.title }).first()).toBeVisible({
          timeout: 30_000,
        })

        await page.screenshot({
          path: `test-results/gate-d-${c.screenId.replace(/\//g, '_')}-${theme}.png`,
          fullPage: true,
        })
      })
    }
  }
})
