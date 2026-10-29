import type { LaunchpadSpace } from '@/app/navigation/launchpad-spaces'
import {
  SPECIALIST_COMPONENT_IDS,
  type TypedFachaktion,
  type WorkspaceCatalog,
  type WorkspaceModule,
  type WorkspaceView,
} from './types'

function action(
  partial: TypedFachaktion,
): TypedFachaktion {
  return partial
}

/**
 * Referenz-Fachaktionen der vier Launcher-Ebenen.
 * Ziele sind bestehende Routen/Worklisten — keine freien API-Calls.
 */
export const WORKSPACE_FACHAKTIONEN: TypedFachaktion[] = [
  action({
    id: 'logistics.undispatched-truck-orders',
    label: 'Nicht disponierte LKW-Auftraege',
    kind: 'open-worklist',
    layer: 'proactive',
    keywords: ['lkw', 'disposition', 'nicht disponiert', 'tour', 'fracht', 'auftrag'],
    requiredScopes: ['logistics:read'],
    businessDomain: 'logistics',
    target: {
      // Die Tafel liest keinen status-Query. Sammelsignal bleibt auf der Route.
      route: '/disposition/touren-disposition',
      screenId: 'disposition/touren-disposition',
    },
    mcpIntent: 'open-undispatched-truck-orders',
    reasonTemplate: 'Offene Transporte ohne Tourenzuordnung',
    catalogId: 'logistik.undispatched_vehicles.list',
    launchpadTileId: 'tour-fracht-arbeitsraum',
  }),
  action({
    id: 'agrar.overdue-contracts',
    label: 'Ueberfaellige Kontrakte',
    kind: 'open-worklist',
    layer: 'proactive',
    keywords: ['kontrakt', 'ueberfaellig', 'vertrag', 'frist', 'agrar'],
    requiredScopes: ['agrar:read'],
    businessDomain: 'agrar',
    target: {
      route: '/agrar/kontrakt-erfuellung',
      screenId: 'agrar/kontrakt-erfuellung',
      worklistQuery: { overdue: '1' },
    },
    mcpIntent: 'open-overdue-contracts',
    reasonTemplate: 'Kontrakte mit ueberschrittener Erfuellungsfrist',
    catalogId: 'agrar.contract.overdue.list',
    launchpadTileId: 'kontrakt-erfuellung',
  }),
  action({
    id: 'agrar.qualitaets-handlungsbedarf',
    label: 'Qualitaets-Handlungsbedarf',
    kind: 'open-worklist',
    layer: 'proactive',
    keywords: ['qualitaet', 'protokoll', 'labor', 'annahme', 'handlungsbedarf'],
    requiredScopes: ['agrar:read'],
    businessDomain: 'agrar',
    target: {
      route: '/annahme/qualitaets-check',
      screenId: 'annahme/qualitaets-check',
    },
    mcpIntent: 'open-quality-queue',
    reasonTemplate: 'Abgeschlossene Qualitaetsprotokolle zur Pruefung',
    catalogId: 'agrar.qualitaets-handlungsbedarf',
    launchpadTileId: 'annahme-qualitaets-check',
  }),
  action({
    id: 'sales.customer-quotes-list',
    label: 'Angebote Kunde',
    kind: 'open-worklist',
    layer: 'dialog',
    keywords: ['angebot', 'kunde', 'angebote', 'offerte', 'quote', 'kundenangebot'],
    requiredScopes: ['sales:read'],
    businessDomain: 'sales',
    target: {
      route: '/sales/angebote-liste',
      screenId: 'sales/angebote-liste',
    },
    mcpIntent: 'open-customer-quotes',
    reasonTemplate: 'Kundenangebote lesen — Anlegen ist separate prepare-command',
    catalogId: 'sales.customer_quote.list',
    launchpadTileId: 'angebot',
  }),
  action({
    id: 'sales.offer-for-customer',
    label: 'Angebot fuer Kunden anlegen',
    kind: 'prepare-command',
    layer: 'dialog',
    keywords: ['angebot', 'kunde', 'offerte', 'mueller', 'quote'],
    requiredScopes: ['sales:write'],
    businessDomain: 'sales',
    target: {
      route: '/sales/angebot/neu',
      screenId: 'sales/angebote/neu',
      actionKey: 'anlegen',
    },
    mcpIntent: 'prepare-sales-offer',
    reasonTemplate: 'Angebot vorbereiten — Ausfuehrung nur in der Maske',
    catalogId: 'sales.customer_quote.create',
    launchpadTileId: 'angebot',
  }),
  action({
    id: 'procurement.goods-receipt-qty-variance',
    label: 'Wareneingang mit Mengenabweichung',
    kind: 'open-worklist',
    layer: 'situational',
    keywords: ['wareneingang', 'mengenabweichung', 'avis', 'differenz', 'eingang'],
    requiredScopes: ['einkauf:read'],
    businessDomain: 'procurement',
    target: {
      route: '/einkauf/anlieferavis',
      screenId: 'einkauf/anlieferavis',
      worklistQuery: { variance: 'qty' },
    },
    mcpIntent: 'open-goods-receipt-variance',
    reasonTemplate: 'Wareneingaenge mit Mengenabweichung zum Avis',
    catalogId: 'einkauf.goods_receipt.quantity_variance.list',
    launchpadTileId: 'wareneingang',
  }),
  action({
    id: 'finance.invoices-awaiting-my-approval',
    label: 'Rechnungen auf meine Freigabe',
    kind: 'open-worklist',
    layer: 'proactive',
    keywords: ['rechnung', 'freigabe', 'eingangsrechnung', 'approval', 'meine'],
    requiredScopes: ['finance:read'],
    businessDomain: 'finance',
    target: {
      route: '/workflows/approval',
      screenId: 'workflows/approval',
      worklistQuery: { assignee: 'me', status: 'pending' },
    },
    mcpIntent: 'open-my-invoice-approvals',
    reasonTemplate: 'Eingangsrechnungen, die auf die eigene Freigabe warten',
    catalogId: 'finance.ap_invoice.approval.worklist',
    launchpadTileId: 'freigaben',
  }),
  action({
    id: 'harvest.intake-queue',
    label: 'Annahme-Warteschlange',
    kind: 'navigate',
    layer: 'situational',
    keywords: ['warteschlange', 'waage', 'annahme', 'hof', 'ernte'],
    requiredScopes: ['logistics:read'],
    businessDomain: 'logistics',
    target: {
      route: '/annahme/warteschlange',
      screenId: 'annahme/warteschlange',
    },
    mcpIntent: 'navigate',
    reasonTemplate: 'Hof- und Waagenannahme',
    catalogId: 'harvest.intake-queue',
    launchpadTileId: 'warteschlange',
  }),
  action({
    id: 'workspace.document-inbox',
    label: 'Beleg-Inbox',
    kind: 'navigate',
    layer: 'personal',
    keywords: ['inbox', 'beleg', 'dokument', 'eingang', 'ocr'],
    requiredScopes: ['dms:read'],
    businessDomain: 'documents',
    target: {
      route: '/inbox',
      screenId: 'inbox',
    },
    mcpIntent: 'navigate',
    reasonTemplate: 'Eingehende Belege der bestehenden Document-Pipeline',
    catalogId: 'workspace.document-inbox',
    launchpadTileId: 'letzte-dokumente',
  }),
  action({
    id: 'sales.credit-notes-list',
    label: 'Gutschriften Verkauf',
    kind: 'open-worklist',
    layer: 'situational',
    keywords: ['gutschrift', 'gutschriften', 'credit note', 'verkauf', 'ausgehend'],
    requiredScopes: ['sales:read'],
    businessDomain: 'sales',
    target: {
      route: '/sales/credit-notes',
      screenId: 'sales/gutschrift',
    },
    mcpIntent: 'open-credit-notes',
    reasonTemplate: 'Verkaufs-Gutschriften-Uebersicht (outgoing), kein Einzelbeleg',
    catalogId: 'sales.credit_note.list',
    launchpadTileId: 'ausgehend-gutschrift',
  }),
  action({
    id: 'einkauf.gutschriften-list',
    label: 'Gutschriften Einkauf',
    kind: 'open-worklist',
    layer: 'situational',
    keywords: ['gutschrift', 'belastung', 'einkauf', 'eingehend'],
    requiredScopes: ['einkauf:read'],
    businessDomain: 'procurement',
    target: {
      route: '/einkauf/gutschriften-belastungen',
      screenId: 'einkauf/gutschriften-belastungen',
    },
    mcpIntent: 'open-purchase-credit-notes',
    reasonTemplate: 'Einkaufs-Gutschriften-Uebersicht (incoming), kein Einzelbeleg',
    catalogId: 'einkauf.gutschrift.list',
  }),
  action({
    id: 'weighing.tickets-list',
    label: 'Wiegescheine',
    kind: 'open-worklist',
    layer: 'situational',
    keywords: ['wiegeschein', 'wiegescheine', 'wiegung', 'waage', 'weighing'],
    requiredScopes: ['logistics:read'],
    businessDomain: 'logistics',
    target: {
      route: '/weighing',
      screenId: 'weighing',
    },
    mcpIntent: 'open-weighing-tickets',
    reasonTemplate: 'Wiegeschein-Uebersicht ohne Schein-ID',
    catalogId: 'weighing.tickets.list',
    launchpadTileId: 'wiegungen',
  }),
  action({
    id: 'einkauf.lieferschein-list',
    label: 'Lieferscheine Einkauf',
    kind: 'open-worklist',
    layer: 'situational',
    keywords: ['lieferschein', 'lieferscheine', 'einkauf', 'eingang'],
    requiredScopes: ['einkauf:read'],
    businessDomain: 'procurement',
    target: {
      route: '/einkauf/lieferschein-erfassung',
      screenId: 'einkauf/lieferschein-erfassung',
    },
    mcpIntent: 'open-purchase-delivery-notes',
    reasonTemplate: 'Einkaufs-Lieferschein-Uebersicht ohne Prefill, kein Einzelbeleg',
    catalogId: 'einkauf.lieferschein.list',
    launchpadTileId: 'einkauf-lieferschein-erfassung',
  }),
  action({
    id: 'einkauf.lieferant-create',
    label: 'Lieferant anlegen vorbereiten',
    kind: 'prepare-command',
    layer: 'dialog',
    keywords: ['lieferant', 'lieferanten', 'kreditor', 'stammdaten', 'anlegen'],
    requiredScopes: ['einkauf:write'],
    businessDomain: 'procurement',
    target: {
      route: '/einkauf/lieferanten',
      screenId: 'einkauf/lieferanten',
      actionKey: 'anlegen',
    },
    mcpIntent: 'prepare-supplier-create',
    reasonTemplate:
      'Lieferantenstamm vorbereiten — Ausfuehrung nur ueber POST /api/v1/einkauf/lieferanten in der Maske',
    catalogId: 'einkauf.lieferant.create',
    launchpadTileId: 'lieferanten',
  }),
  action({
    id: 'artikel.stamm-create',
    label: 'Artikel anlegen vorbereiten',
    kind: 'prepare-command',
    layer: 'dialog',
    keywords: ['artikel', 'artikelstamm', 'stammdaten', 'anlegen'],
    requiredScopes: ['stammdaten:write'],
    businessDomain: 'inventory',
    target: {
      route: '/artikel/neu',
      screenId: 'artikel/stamm',
      actionKey: 'anlegen',
    },
    mcpIntent: 'prepare-article-create',
    reasonTemplate:
      'Artikelstamm vorbereiten — Ausfuehrung nur ueber POST /api/v1/articles/ in der Maske',
    catalogId: 'artikel.stamm.create',
    launchpadTileId: 'artikel-neu',
  }),
]

export const WORKSPACE_VIEWS: WorkspaceView[] = [
  {
    id: 'view.inbox',
    moduleId: 'steuerung',
    label: 'Beleg-Inbox',
    route: '/inbox',
    specialistComponentId: SPECIALIST_COMPONENT_IDS.documentInbox,
    specializedKind: 'inbox',
  },
  {
    id: 'view.dispo-board',
    moduleId: 'logistik',
    label: 'Dispo-Tafel',
    route: '/disposition/touren-disposition',
    specialistComponentId: SPECIALIST_COMPONENT_IDS.dispoBoard,
    specializedKind: 'disposition_board',
    specializedId: 'lkw-disposition-board',
  },
]

export function modulesFromLaunchpadSpaces(spaces: LaunchpadSpace[]): WorkspaceModule[] {
  return spaces.map((space) => ({
    id: space.id,
    label: space.label,
    domain: space.id,
    viewIds: space.pages.map((page) => `${space.id}:${page.id}`),
  }))
}

export function viewsFromLaunchpadSpaces(spaces: LaunchpadSpace[]): WorkspaceView[] {
  const specialistByRoute = new Map(WORKSPACE_VIEWS.map((view) => [view.route, view.specialistComponentId]))
  return spaces.flatMap((space) =>
    space.pages.map((page) => {
      const route = page.tiles[0]?.path ?? `/${space.id}/${page.id}`
      return {
        id: `${space.id}:${page.id}`,
        moduleId: space.id,
        label: page.label,
        route,
        specialistComponentId: specialistByRoute.get(route),
      }
    }),
  )
}

export function getWorkspaceCatalog(spaces: LaunchpadSpace[] = []): WorkspaceCatalog {
  const spaceViews = viewsFromLaunchpadSpaces(spaces)
  const extraViews = WORKSPACE_VIEWS.filter(
    (view) => !spaceViews.some((entry) => entry.route === view.route),
  )
  return {
    modules: modulesFromLaunchpadSpaces(spaces),
    views: [...spaceViews, ...extraViews],
    actions: WORKSPACE_FACHAKTIONEN,
  }
}

export function getFachaktion(id: string): TypedFachaktion | undefined {
  return WORKSPACE_FACHAKTIONEN.find((action) => action.id === id)
}

/** YAML `action_id` ist catalogId — kein zweiter semantischer Katalog. */
export function getFachaktionByCatalogId(catalogId: string): TypedFachaktion | undefined {
  return WORKSPACE_FACHAKTIONEN.find((action) => action.catalogId === catalogId)
}
