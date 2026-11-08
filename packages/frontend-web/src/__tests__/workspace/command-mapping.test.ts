import { describe, expect, it } from 'vitest'
import { buildPaletteCommands } from '@/components/navigation/command-palette-model'
import {
  WORKSPACE_FACHAKTIONEN,
  authorizeFachaktionen,
  mapAuthorizedFachaktionen,
  mapFachaktionToCommand,
} from '@/workspace'

describe('command center mapping', () => {
  it('mappt Worklisten auf Route plus Query und prepare-command auf omniboxAction', () => {
    const trucks = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'logistics.undispatched-truck-orders')!,
    )
    expect(trucks.id).toBe('fachaktion:logistics.undispatched-truck-orders')
    expect(trucks.actionParams.path).toBe('/disposition/touren-disposition')
    expect(String(trucks.actionParams.path)).not.toContain('status=undispatched')
    expect(
      mapFachaktionToCommand(
        WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'agrar.overdue-contracts')!,
      ).actionParams.path,
    ).toBe('/agrar/kontrakt-erfuellung?overdue=1')
    expect(trucks.actionParams.kind).toBe('open-worklist')
    expect(trucks.actionParams.catalogId).toBe('logistik.undispatched_vehicles.list')
    expect(
      mapFachaktionToCommand(WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'harvest.intake-queue')!)
        .actionParams.catalogId,
    ).toBe('harvest.intake-queue')
    expect(
      mapFachaktionToCommand(WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'workspace.document-inbox')!)
        .actionParams.catalogId,
    ).toBe('workspace.document-inbox')
    expect(trucks.mcp.intent).toBe('open-undispatched-truck-orders')
    expect(trucks.category).toBe('Handlungsbedarf')

    const quotes = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'sales.customer-quotes-list')!,
    )
    expect(quotes.actionParams.path).toBe('/sales/angebote-liste')
    expect(quotes.actionParams.kind).toBe('open-worklist')
    expect(quotes.actionParams.catalogId).toBe('sales.customer_quote.list')
    expect(quotes.mcp.requiredScopes).toEqual(['sales:read'])

    const offer = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'sales.offer-for-customer')!,
    )
    expect(offer.actionParams.path).toBe('/sales/angebot/neu?omniboxAction=anlegen')
    expect(offer.actionParams.actionKey).toBe('anlegen')
    expect(offer.hint).toBe('vorbereiten')
    expect(offer.mcp.requiredScopes).toEqual(['sales:write'])

    const variance = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'procurement.goods-receipt-qty-variance')!,
    )
    expect(variance.actionParams.path).toBe('/einkauf/anlieferavis?variance=qty')
    expect(variance.mcp.requiredScopes).toEqual(['einkauf:read'])

    const approval = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'finance.invoices-awaiting-my-approval')!,
    )
    expect(approval.actionParams.path).toContain('/workflows/approval')
    expect(approval.mcp.requiredScopes).toEqual(['finance:read'])
  })

  it('laesst ohne Session-Scopes alle Aktionen und filtert sonst streng', () => {
    expect(authorizeFachaktionen(WORKSPACE_FACHAKTIONEN, undefined)).toHaveLength(
      WORKSPACE_FACHAKTIONEN.length,
    )
    const writeOnly = mapAuthorizedFachaktionen(WORKSPACE_FACHAKTIONEN, { scopes: ['sales:write'] })
    expect(writeOnly.map((entry) => entry.id)).toEqual(['fachaktion:sales.offer-for-customer'])
    const readOnly = mapAuthorizedFachaktionen(WORKSPACE_FACHAKTIONEN, { scopes: ['sales:read'] })
    expect(readOnly.map((entry) => entry.id)).toEqual(
      expect.arrayContaining(['fachaktion:sales.customer-quotes-list']),
    )
    expect(readOnly.every((entry) => entry.id.startsWith('fachaktion:sales.'))).toBe(true)
    expect(readOnly.some((entry) => entry.id === 'fachaktion:sales.offer-for-customer')).toBe(false)
    const admin = authorizeFachaktionen(WORKSPACE_FACHAKTIONEN, ['admin:all'])
    expect(admin).toHaveLength(WORKSPACE_FACHAKTIONEN.length)
  })

  it('haengt YAML-Aliase als Suchphrasen an den Command-Center-Eintrag', () => {
    const trucks = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'logistics.undispatched-truck-orders')!,
    )
    expect(trucks.keywords).toEqual(
      expect.arrayContaining([
        'nicht disponierte lkw',
        'nicht disponierte lastwagen',
        'lkw nicht disponiert',
        'logistik.undispatched_vehicles.list',
      ]),
    )
    const inbox = mapFachaktionToCommand(
      WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'workspace.document-inbox')!,
    )
    expect(inbox.keywords).toEqual(expect.arrayContaining(['dokumenteneingang', 'beleg inbox']))
  })

  it('haengt Fachaktionen in die bestehende Palette und respektiert Agrar-Flag plus Scopes', () => {
    const withAgrar = buildPaletteCommands({
      agrarEnabled: true,
      navigationShortcuts: [],
      userScopes: ['agrar:read', 'logistics:read'],
    })
    expect(withAgrar.some((command) => command.id === 'fachaktion:agrar.overdue-contracts')).toBe(true)
    expect(withAgrar.some((command) => command.id === 'fachaktion:logistics.undispatched-truck-orders')).toBe(true)
    expect(withAgrar.some((command) => command.id === 'fachaktion:sales.offer-for-customer')).toBe(false)

    const withoutAgrar = buildPaletteCommands({
      agrarEnabled: false,
      navigationShortcuts: [],
      userScopes: ['agrar:read', 'logistics:read'],
    })
    expect(withoutAgrar.some((command) => command.id === 'fachaktion:agrar.overdue-contracts')).toBe(false)
    expect(withoutAgrar.some((command) => command.id === 'fachaktion:logistics.undispatched-truck-orders')).toBe(true)
  })
})
