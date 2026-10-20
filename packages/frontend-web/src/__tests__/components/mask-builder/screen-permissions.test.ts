import { describe, expect, it } from 'vitest'
import { getScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { User } from '@/lib/auth'

const user = (scopes: string[] = [], roles: string[] = []): User => ({
  sub: 'test', name: 'Test', email: 'test@example.invalid', exp: 9999999999, scopes, roles,
})
const screen: ScreenDefinition = {
  schemaVersion: 1, id: 'logistik/test', domain: 'logistics', mode: 'list', title: 'Test',
  permissions: ['logistics:write'], // A schema cannot grant itself access.
  actions: [
    { key: 'read', label: 'Read', permission: 'logistics:read' },
    { key: 'write', label: 'Write', permission: 'logistics:write' },
  ],
}
describe('authenticated mask permission projection', () => {
  it('denies anonymous users and ignores schema grants', () => {
    expect(getScreenPermissions(screen, null)).toEqual([])
    expect(getScreenPermissions(screen, user())).toEqual([])
  })
  it('keeps read and write distinct', () => {
    expect(getScreenPermissions(screen, user(['logistics:read']))).toEqual(['logistics:read'])
    expect(getScreenPermissions(screen, user(['logistics:write']))).toEqual(['logistics:read', 'logistics:write'])
  })
  it('projects declared permissions for admin only', () => {
    expect(getScreenPermissions(screen, user(['admin:all']))).toEqual(['logistics:read', 'logistics:write'])
    expect(getScreenPermissions(screen, user([], ['admin']))).toEqual(['logistics:read', 'logistics:write'])
  })
  it('matches the canonical lead write roles including creation', () => {
    const lead: ScreenDefinition = { ...screen, id: 'crm/lead', domain: 'crm', actions: [],
      creation: { endpoint: '/api/v1/crm/leads', permission: 'crm.lead.create', detailRoute: '/crm/lead/{entity_id}' } }
    expect(getScreenPermissions(lead, user([], ['CRM_LESEN']))).toEqual([])
    expect(getScreenPermissions(lead, user([], ['CRM_BEARBEITEN']))).toEqual(['crm.lead.create'])
  })
})


describe('platform capacity remains explicit', () => {
  const administration: ScreenDefinition = { ...screen, id: 'admin/identity-budgets', domain: 'platform',
    actions: [
      { key: 'root', label: 'Mandantenbudget', permission: 'platform:quota:manage' },
      { key: 'read', label: 'Eigene Kontingente', permission: 'identity:quota:read' },
      { key: 'allocate', label: 'Vergeben', permission: 'identity:quota:allocate' },
    ] }
  it('does not project platform capacity from tenant admin or admin:all', () => {
    expect(getScreenPermissions(administration, user(['admin:all'], ['admin'])))
      .toEqual(['identity:quota:read', 'identity:quota:allocate'])
    expect(getScreenPermissions(administration, user(['platform:quota:manage'])))
      .toEqual(['platform:quota:manage', 'identity:quota:read'])
  })
  it('keeps own quota navigation available without granting allocation rights', () => {
    expect(getScreenPermissions(administration, user())).toEqual(['identity:quota:read'])
    expect(getScreenPermissions(administration, null)).toEqual([])
  })
})


describe('canonical document permission projection', () => {
  const documentScreen = (id: string): ScreenDefinition => ({ ...screen, id, domain: 'einkauf',
    actions: ['lesen', 'preise', 'bearbeiten', 'ausstellen', 'buchen', 'stornieren'].map(right => ({
      key: right, label: right, permission: `belege.${right}`,
    })) })
  it('keeps purchase and sales rights separate for the existing buyer role', () => {
    expect(getScreenPermissions(documentScreen('beleg/purchase-invoice'), user([], ['EINKAUF_BEARBEITEN'])))
      .toEqual(['belege.lesen', 'belege.preise', 'belege.bearbeiten', 'belege.ausstellen', 'belege.buchen'])
    expect(getScreenPermissions(documentScreen('beleg/sales-invoice'), user([], ['EINKAUF_BEARBEITEN'])))
      .toEqual([])
  })
  it('lets warehouse readers read without prices or mutations', () => {
    expect(getScreenPermissions(documentScreen('beleg/goods-receipt'), user(['belege:read'], ['LAGER_LESEN'])))
      .toEqual(['belege.lesen'])
  })
  it('keeps finance reversal distinct from buyer editing and manager access', () => {
    expect(getScreenPermissions(documentScreen('beleg/purchase-invoice'), user([], ['FINANCE_BEARBEITEN'])))
      .toEqual(['belege.lesen', 'belege.preise', 'belege.buchen', 'belege.stornieren'])
    expect(getScreenPermissions(documentScreen('beleg/purchase-invoice'), user([], ['manager'])))
      .not.toContain('belege.stornieren')
  })
  it('does not grant document actions from transport scopes or schema declarations', () => {
    expect(getScreenPermissions(documentScreen('beleg/purchase-invoice'), user(['belege:write', 'admin:all'])))
      .toEqual([])
    expect(getScreenPermissions(documentScreen('beleg/unknown'), user([], ['admin']))).toEqual([])
  })
})


describe('controller supervises document exceptions without posting rights', () => {
  const controlledScreen: ScreenDefinition = { ...screen, id: 'beleg/purchase-invoice', domain: 'einkauf',
    actions: ['lesen', 'preise', 'bearbeiten', 'ausstellen', 'buchen', 'stornieren', 'freigeben', 'freigeben_erhoeht']
      .map(right => ({ key: right, label: right, permission: `belege.${right}` })) }
  it.each(['controller', 'CONTROLLING'])('projects approval only for %s', role => {
    expect(getScreenPermissions(controlledScreen, user([], [role])))
      .toEqual(['belege.freigeben', 'belege.freigeben_erhoeht'])
    expect(getScreenPermissions(controlledScreen, user(['belege:write', 'admin:all'], [role])))
      .toEqual(['belege.freigeben', 'belege.freigeben_erhoeht'])
  })
  it.each(['controller', 'CONTROLLING'])('combines %s with finance reading without granting posting', role => {
    expect(getScreenPermissions(controlledScreen, user([], [role, 'FINANCE_LESEN'])))
      .toEqual(['belege.lesen', 'belege.preise', 'belege.freigeben', 'belege.freigeben_erhoeht'])
  })
})


describe('action permissions follow the command route roles', () => {
  const order: ScreenDefinition = { ...screen, id: 'sales/sales-order', domain: 'sales',
    actions: [{ key: 'bearbeiten', label: 'Bearbeiten', permission: 'sales.order.update' }] }
  const contract: ScreenDefinition = { ...screen, id: 'agrar/kontrakte', domain: 'agrar',
    actions: [{ key: 'bearbeiten', label: 'Bearbeiten', permission: 'kontrakt.update' }] }
  it('grants the edit action to the area role without a scope attribute', () => {
    expect(getScreenPermissions(order, user([], ['SALES_BEARBEITEN']))).toEqual(['sales.order.update'])
    expect(getScreenPermissions(order, user([], ['SALES_LESEN']))).toEqual([])
  })
  it('a scope attribute cannot outvote the server roles', () => {
    expect(getScreenPermissions(order, user(['sales.order.update'], ['CRM_BEARBEITEN']))).toEqual([])
    // Kontraktaenderung verlangt die Kontraktrolle selbst; admin allein reicht dort auch serverseitig nicht.
    expect(getScreenPermissions(contract, user(['admin:all'], ['admin']))).toEqual([])
    expect(getScreenPermissions(contract, user([], ['KONTRAKT_BEARBEITEN']))).toEqual(['kontrakt.update'])
  })
})
