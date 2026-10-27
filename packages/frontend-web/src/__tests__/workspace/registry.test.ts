import { describe, expect, it } from 'vitest'
import type { LaunchpadSpace } from '@/app/navigation/launchpad-spaces'
import { EMPTY_LAUNCHPAD_OVERLAY, pinTile } from '@/app/navigation/launchpad-personalization'
import {
  SPECIALIST_COMPONENT_IDS,
  WORKSPACE_FACHAKTIONEN,
  getFachaktion,
  getFachaktionByCatalogId,
  getWorkspaceCatalog,
  modulesFromLaunchpadSpaces,
  userContextFromPersonalization,
} from '@/workspace'

const spaces: LaunchpadSpace[] = [
  {
    id: 'logistik',
    label: 'Lager & Logistik',
    pages: [
      {
        id: 'disposition',
        label: 'Tagesdisposition',
        origin: 'catalog',
        locked: false,
        tiles: [
          { id: 'tourenplanung', label: 'Tourenplanung', path: '/logistik/tourenplanung' },
        ],
      },
    ],
  },
]

describe('workspace registry', () => {
  it('leitet Module und Views aus Launchpad-Spaces ab und haengt Spezialkomponenten-IDs an', () => {
    const catalog = getWorkspaceCatalog(spaces)
    expect(modulesFromLaunchpadSpaces(spaces).map((module) => module.id)).toEqual(['logistik'])
    expect(catalog.views.some((view) => view.id === 'logistik:disposition')).toBe(true)
    expect(catalog.views.find((view) => view.id === 'view.inbox')?.specialistComponentId).toBe(
      SPECIALIST_COMPONENT_IDS.documentInbox,
    )
    expect(catalog.views.find((view) => view.id === 'view.dispo-board')?.specialistComponentId).toBe(
      SPECIALIST_COMPONENT_IDS.dispoBoard,
    )
    expect(catalog.views.find((view) => view.id === 'view.inbox')?.specializedKind).toBe('inbox')
    expect(catalog.views.find((view) => view.id === 'view.dispo-board')).toMatchObject({
      specializedKind: 'disposition_board',
      specializedId: 'lkw-disposition-board',
      route: '/disposition/touren-disposition',
    })
  })

  it('enthaelt die Referenz-Fachaktionen mit Zielroute statt freiem API-Call', () => {
    const ids = WORKSPACE_FACHAKTIONEN.map((action) => action.id)
    expect(ids).toEqual(
      expect.arrayContaining([
        'logistics.undispatched-truck-orders',
        'agrar.overdue-contracts',
        'sales.offer-for-customer',
        'procurement.goods-receipt-qty-variance',
        'finance.invoices-awaiting-my-approval',
      ]),
    )
    const quotes = getFachaktion('sales.customer-quotes-list')
    expect(quotes?.kind).toBe('open-worklist')
    expect(quotes?.target.route).toBe('/sales/angebote-liste')
    expect(quotes?.requiredScopes).toEqual(['sales:read'])
    expect(quotes?.catalogId).toBe('sales.customer_quote.list')
    expect(getFachaktionByCatalogId('sales.customer_quote.list')?.id).toBe(
      'sales.customer-quotes-list',
    )
    const offer = getFachaktion('sales.offer-for-customer')
    expect(offer?.kind).toBe('prepare-command')
    expect(offer?.target.route).toBe('/sales/angebot/neu')
    expect(offer?.target.actionKey).toBe('anlegen')
    expect(offer?.catalogId).toBe('sales.customer_quote.create')
    expect(getFachaktion('logistics.undispatched-truck-orders')?.catalogId).toBe(
      'logistik.undispatched_vehicles.list',
    )
    expect(getFachaktion('procurement.goods-receipt-qty-variance')).toMatchObject({
      requiredScopes: ['einkauf:read'],
      target: { route: '/einkauf/anlieferavis' },
    })
    expect(getFachaktion('finance.invoices-awaiting-my-approval')).toMatchObject({
      requiredScopes: ['finance:read'],
      target: { route: '/workflows/approval' },
    })
    expect(getFachaktion('harvest.intake-queue')?.catalogId).toBe('harvest.intake-queue')
    expect(getFachaktionByCatalogId('workspace.document-inbox')?.id).toBe('workspace.document-inbox')
    const quality = getFachaktion('agrar.qualitaets-handlungsbedarf')
    expect(quality?.catalogId).toBe('agrar.qualitaets-handlungsbedarf')
    expect(quality?.kind).toBe('open-worklist')
    expect(quality?.requiredScopes).toEqual(['agrar:read'])
    expect(quality?.target.route).toBe('/annahme/qualitaets-check')
    expect(quality?.target.screenId).toBe('annahme/qualitaets-check')
    expect(quality?.target.actionKey).toBeUndefined()
    expect(getFachaktionByCatalogId('agrar.qualitaets-handlungsbedarf')?.id).toBe(
      'agrar.qualitaets-handlungsbedarf',
    )
    expect(getFachaktionByCatalogId('sales.credit_note.list')?.id).toBe('sales.credit-notes-list')
    expect(getFachaktionByCatalogId('einkauf.gutschrift.list')?.target.route).toBe(
      '/einkauf/gutschriften-belastungen',
    )
    expect(getFachaktionByCatalogId('weighing.tickets.list')?.target.route).toBe('/weighing')
    expect(getFachaktionByCatalogId('einkauf.lieferschein.list')?.target.route).toBe(
      '/einkauf/lieferschein-erfassung',
    )
    for (const action of WORKSPACE_FACHAKTIONEN) {
      expect(action.catalogId).toBeTruthy()
      expect(action.target.route.startsWith('/')).toBe(true)
      expect(action.target.route.includes('/api/')).toBe(false)
    }
  })

  it('liest Pin und Fixieren aus dem Launchpad-Overlay, nicht aus Kachel-Rechten', () => {
    const overlay = pinTile(
      { ...EMPTY_LAUNCHPAD_OVERLAY, surfaceLocked: true, tileLabels: { kunden: 'Stamm' } },
      'kunden',
    )
    const context = userContextFromPersonalization({
      overlay,
      roles: ['buchhalter'],
      scopes: ['finance:approve'],
    })
    expect(context.pinned).toEqual(['kunden'])
    expect(context.favorites).toContain('kunden')
    expect(context.surfaceLocked).toBe(true)
    expect(context.roles).toEqual(['buchhalter'])
    expect(context.scopes).toEqual(['finance:approve'])
  })
})
