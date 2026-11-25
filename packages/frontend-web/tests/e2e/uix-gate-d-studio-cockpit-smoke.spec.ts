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
  /** Specialized workbench contract — mounts Fach-Surface inside native-cockpit. */
  specializedType?:
    | 'pricing_workbench'
    | 'fleet_workbench'
    | 'lager_workbench'
    | 'agrar_workbench'
    | 'finance_workbench'
    | 'feed_workbench'
    | 'admin_workbench'
  specializedFields?: Array<{ key: string; label: string }>
  /** ARIA tablist name inside the specialized surface (Studio Tabs-Invariante). */
  specializedTablist?: string
  /** Accessible name / text proving the specialized surface mounted. */
  specializedLandmark?: string
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
    specializedType: 'lager_workbench',
    specializedFields: [
      { key: 'warehouse_id', label: 'Lager' },
      { key: 'node_count', label: 'Knoten' },
      { key: 'edge_count', label: 'Kanten' },
    ],
  },
  {
    label: 'konditionen/konditionssystem',
    path: '/konditionen/konditionssystem',
    screenId: 'konditionen/konditionssystem',
    testId: 'screen-konditionen/konditionssystem',
    title: 'Konditionssystem',
    specializedType: 'pricing_workbench',
    specializedFields: [
      { key: 'preisliste_count', label: 'Preislisten' },
      { key: 'rabattgruppe_count', label: 'Rabattgruppen' },
      { key: 'individualpreis_count', label: 'Individualpreise' },
    ],
    specializedTablist: 'Konditionssystem',
  },
  {
    label: 'fuhrpark/fahrzeug-vertiefung',
    path: '/fuhrpark/fahrzeug-vertiefung',
    screenId: 'fuhrpark/fahrzeug-vertiefung',
    testId: 'screen-fuhrpark/fahrzeug-vertiefung',
    title: 'Fahrzeug-Vertiefung',
    specializedType: 'fleet_workbench',
    specializedFields: [
      { key: 'fahrzeug_id', label: 'Fahrzeug' },
      { key: 'status', label: 'Status' },
      { key: 'schaden_offen', label: 'Offene Schäden' },
      { key: 'bussgeld_offen', label: 'Offene Bußgelder' },
    ],
    specializedTablist: 'Fahrzeug-Vertiefung',
  },
  {
    label: 'agrar/kunden-schlagkartei',
    path: '/agrar/kunden-schlagkartei',
    screenId: 'agrar/kunden-schlagkartei',
    testId: 'screen-agrar/kunden-schlagkartei',
    title: 'Kundenschlagkartei',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'kunden_nr', label: 'Kunde' },
      { key: 'schlag_count', label: 'Schläge' },
      { key: 'massnahme_count', label: 'Maßnahmen' },
      { key: 'gesamt_flaeche_ha', label: 'Fläche ha' },
    ],
    specializedTablist: 'Schlagkartei',
  },
  {
    label: 'agrar/ernte-annahme-erfassung',
    path: '/agrar/ernte-annahme-erfassung',
    screenId: 'agrar/ernte-annahme-erfassung',
    testId: 'screen-agrar/ernte-annahme-erfassung',
    title: 'Ernte-Annahme-Erfassung',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'acceptance_number', label: 'Annahmenummer' },
      { key: 'customer_id', label: 'Kunde' },
      { key: 'release_status', label: 'Freigabe' },
      { key: 'delivery_date', label: 'Lieferdatum' },
    ],
    // Ohne Annahme-ID erscheint oft die Listen-/Ansichts-Registerleiste zuerst.
    specializedTablist: 'Annahme-Ansichten',
  },
  {
    label: 'finance/bank-abgleich',
    path: '/finance/bank-abgleich',
    screenId: 'finance/bank-abgleich',
    testId: 'native-cockpit-finance-bank-abgleich',
    title: 'Bankabgleich',
    specializedType: 'finance_workbench',
    specializedFields: [
      { key: 'kontoId', label: 'Bankkonto' },
      { key: 'camtFile', label: 'Kontoauszug' },
      { key: 'statementId', label: 'Statement' },
      { key: 'startSaldo', label: 'Startsaldo' },
      { key: 'endSaldo', label: 'Endsaldo' },
      { key: 'gebuchteUmsaetze', label: 'Umsätze' },
      { key: 'zugeordnet', label: 'Zugeordnet' },
      { key: 'nichtZugeordnet', label: 'Nicht zugeordnet' },
      { key: 'abgleichsDifferenz', label: 'Differenz' },
      { key: 'accountingBalance', label: 'Hauptbuchsaldo' },
      { key: 'zuordnungData', label: 'Umsatzzeilen' },
      { key: 'importErrors', label: 'Importprotokoll' },
      { key: 'differences', label: 'Differenzen' },
      { key: 'comparisonState', label: 'Nachweisstatus' },
    ],
    specializedLandmark: 'Bankabgleich Arbeitsbereich',
  },
  {
    label: 'mahnwesen/mahnlauf',
    path: '/mahnwesen/mahnlauf',
    screenId: 'mahnwesen/mahnlauf',
    testId: 'native-cockpit-mahnwesen-mahnlauf',
    title: 'Mahnlauf',
    specializedType: 'finance_workbench',
    specializedFields: [
      { key: 'op_id', label: 'Posten' },
      { key: 'rechnungsnr', label: 'Rechnung' },
      { key: 'partner', label: 'Partner' },
      { key: 'tage_ueberfaellig', label: 'Überfällig' },
      { key: 'offen', label: 'Offen' },
      { key: 'aktuelle_stufe', label: 'Aktuelle Stufe' },
      { key: 'naechste_stufe', label: 'Nächste Stufe' },
      { key: 'dunning_fee', label: 'Gebühr' },
      { key: 'interest', label: 'Zinsen' },
      { key: 'total_amount', label: 'Gesamt' },
      { key: 'id', label: 'Mahnung' },
      { key: 'stufe', label: 'Stufe' },
      { key: 'gesamt', label: 'Gesamtbetrag' },
      { key: 'frist', label: 'Frist' },
      { key: 'datum', label: 'Datum' },
      { key: 'status', label: 'Status' },
      { key: 'versand_art', label: 'Versandart' },
      { key: 'empfaenger', label: 'Empfänger' },
      { key: 'auswahl', label: 'Auswahl' },
    ],
    specializedLandmark: 'Mahnlauf Arbeitsbereich',
  },
  {
    label: 'agrar/milchvieh-karte',
    path: '/agrar/milchvieh-karte',
    screenId: 'agrar/milchvieh-karte',
    testId: 'screen-agrar/milchvieh-karte',
    title: 'Milchvieh-Karte',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'feature_count', label: 'Betriebe' },
    ],
    specializedLandmark: 'Milchvieh-Karte Arbeitsbereich',
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
  const contractFields = (c.specializedFields ?? []).map((field) => ({
    key: field.key,
    label: field.label,
    type: 'number' as const,
    readOnly: true,
  }))
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
      ...contractFields,
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
    ...(c.specializedType
      ? {
          specialized: {
            type: c.specializedType,
            id: c.screenId,
          },
        }
      : {}),
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
  await page.route(new RegExp(`${overviewPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ gesamt: 1, ok_count: 1, problem_count: 0 }),
    })
  })

  const listPath = c.listEndpoint ?? `/api/v1/masks/${encoded}/items`
  await page.route(new RegExp(`${listPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 'smoke-1', label: c.title, status: 'ok' }]),
    })
  })

  // Overlay ohne Backend — leeres Overlay, kein Crash in der Runtime.
  await page.route(new RegExp(`/api/v1/ux/overlays/${c.screenId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`), async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: 'null' })
  })

  // Specialized-Surface-Fetches: Arrays (nicht {items}), sonst crasht z. B. Konditionen-Map.
  if (c.specializedType === 'pricing_workbench') {
    await page.route(/\/api\/v1\/price-lists\/?(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'lager_workbench') {
    await page.route(/\/api\/v1\/inventory\/warehouses(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
  }
  if (c.specializedType === 'finance_workbench') {
    await page.route(/\/api\/v1\/banken\/konten(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
    await page.route(/\/api\/v1\/finance\/bank-accounts(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      })
    })
    await page.route(/\/api\/v1\/finance\/mahnlauf\/candidates(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
    await page.route(/\/api\/v1\/finance\/mahnlauf\/notices(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
  }
  if (c.screenId === 'agrar/milchvieh-karte') {
    await page.route(/\/api\/v1\/agrar\/milchvieh-crosssell\/map(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ type: 'FeatureCollection', features: [] }),
      })
    })
  }
  if (c.screenId === 'agrar/kunden-schlagkartei') {
    // PortalKontoGate: ein Konto → Auto-Wahl → Tabs der Specialized-Surface.
    await page.route(/\/api\/v1\/portal\/kundenkonten(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            customer_id: 'smoke-kunde-1',
            customer_number: 'K-1',
            name: 'Smoke-Hof',
            rolle: 'betreiber',
            rechte: ['*'],
          },
        ]),
      })
    })
    await page.route(/\/(?:api\/v1\/)?innendienst\/kunden\/[^/]+\/schlaege(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ schlaege: [], count: 0 }),
      })
    })
    await page.route(/\/(?:api\/v1\/)?innendienst\/kunden\/[^/]+\/massnahmen(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ massnahmen: [], count: 0 }),
      })
    })
  }
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

        if (c.specializedTablist) {
          await expect(page.getByRole('tablist', { name: c.specializedTablist })).toBeVisible({
            timeout: 30_000,
          })
        } else if (c.specializedLandmark) {
          await expect(page.getByRole('region', { name: c.specializedLandmark })).toBeVisible({
            timeout: 30_000,
          })
        } else if (c.specializedType === 'lager_workbench') {
          await expect(page.getByText('Hinweis Prototyp')).toBeVisible({ timeout: 30_000 })
        }

        await page.screenshot({
          path: `test-results/gate-d-${c.screenId.replace(/\//g, '_')}-${theme}.png`,
          fullPage: true,
        })
      })
    }
  }
})
