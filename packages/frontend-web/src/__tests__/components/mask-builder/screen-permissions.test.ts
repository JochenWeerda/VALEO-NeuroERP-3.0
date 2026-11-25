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
  it('matches CRM write roles for Kontakt creation', () => {
    const kontakt: ScreenDefinition = { ...screen, id: 'crm/kontakt', domain: 'crm', actions: [],
      creation: { endpoint: '/api/v1/crm/contacts/', permission: 'crm.contact.create', detailRoute: '/crm/kontakt/{entity_id}' } }
    expect(getScreenPermissions(kontakt, user([], ['FINANCE_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(kontakt, user([], ['CRM_BEARBEITEN']))).toEqual(['crm.contact.create'])
  })
  it('matches SCHREIBEN AGRAR roles for Saatgut/Duenger creation', () => {
    const saatgut: ScreenDefinition = { ...screen, id: 'agrar/saatgut', domain: 'agrar', actions: [],
      creation: { endpoint: '/api/v1/agrar/saatgut/', permission: 'agrar.saatgut.create', detailRoute: '/agrar/saatgut/{entity_id}' } }
    expect(getScreenPermissions(saatgut, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(saatgut, user([], ['AGRAR_BEARBEITEN']))).toEqual(['agrar.saatgut.create'])
    expect(getScreenPermissions(saatgut, user([], ['HARVEST_ADMIN']))).toEqual(['agrar.saatgut.create'])
  })
  it('matches FINANCE write roles for Bankkonto/Kreditor creation', () => {
    const bank: ScreenDefinition = { ...screen, id: 'finance/bankkonto', domain: 'finance', actions: [],
      creation: { endpoint: '/api/v1/banken/konten', permission: 'finance.bankkonto.create', detailRoute: '/finance/bankkonto/{entity_id}' } }
    expect(getScreenPermissions(bank, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(bank, user([], ['FINANCE_BEARBEITEN']))).toEqual(['finance.bankkonto.create'])
  })
  it('matches CRM/SALES write roles for Opportunity creation', () => {
    const opp: ScreenDefinition = { ...screen, id: 'crm/opportunity', domain: 'crm', actions: [],
      creation: { endpoint: '/api/v1/crm/opportunities/', permission: 'crm.opportunity.create', detailRoute: '/crm/opportunity/{entity_id}' } }
    expect(getScreenPermissions(opp, user([], ['FINANCE_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(opp, user([], ['CRM_BEARBEITEN']))).toEqual(['crm.opportunity.create'])
    expect(getScreenPermissions(opp, user([], ['SALES_ADMIN']))).toEqual(['crm.opportunity.create'])
  })
  it('matches EINKAUF write roles for Anfrage creation', () => {
    const anfrage: ScreenDefinition = { ...screen, id: 'einkauf/anfrage', domain: 'einkauf', actions: [],
      creation: { endpoint: '/api/v1/einkauf/anfragen', permission: 'einkauf.anfrage.create', detailRoute: '/einkauf/anfrage/{entity_id}' } }
    expect(getScreenPermissions(anfrage, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(anfrage, user([], ['EINKAUF_BEARBEITEN']))).toEqual(['einkauf.anfrage.create'])
  })
  it('matches EINKAUF write roles for Angebot and Anlieferavis creation', () => {
    const angebot: ScreenDefinition = { ...screen, id: 'einkauf/angebot', domain: 'einkauf', actions: [],
      creation: { endpoint: '/api/v1/einkauf/angebote', permission: 'einkauf.angebot.create', detailRoute: '/einkauf/angebot/{entity_id}' } }
    const avis: ScreenDefinition = { ...screen, id: 'einkauf/anlieferavis', domain: 'einkauf', actions: [],
      creation: { endpoint: '/api/v1/einkauf/anlieferavis', permission: 'einkauf.anlieferavis.create', detailRoute: '/einkauf/anlieferavis/{entity_id}' } }
    expect(getScreenPermissions(angebot, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(angebot, user([], ['EINKAUF_BEARBEITEN']))).toEqual(['einkauf.angebot.create'])
    expect(getScreenPermissions(avis, user([], ['EINKAUF_ADMIN']))).toEqual(['einkauf.anlieferavis.create'])
  })
  it('matches QUALITAET write roles for Reklamation creation', () => {
    const rek: ScreenDefinition = { ...screen, id: 'qualitaet/reklamation', domain: 'qualitaet', actions: [],
      creation: { endpoint: '/api/v1/reklamationen', permission: 'qualitaet.reklamation.create', detailRoute: '/qualitaet/reklamation/{entity_id}', responseIdKey: 'reklamation_id' } }
    expect(getScreenPermissions(rek, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(rek, user([], ['LAGER_BEARBEITEN']))).toEqual(['qualitaet.reklamation.create'])
    expect(getScreenPermissions(rek, user([], ['AGRAR_ADMIN']))).toEqual(['qualitaet.reklamation.create'])
  })
  it('matches AGRAR write roles for Labor creation', () => {
    const labor: ScreenDefinition = { ...screen, id: 'qualitaet/labor-detail', domain: 'qualitaet', actions: [],
      creation: { endpoint: '/api/v1/qualitaet/labor-auftraege', permission: 'qualitaet.labor.create', detailRoute: '/qualitaet/labor/{entity_id}' } }
    expect(getScreenPermissions(labor, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(labor, user([], ['AGRAR_BEARBEITEN']))).toEqual(['qualitaet.labor.create'])
  })
  it('matches STAMMDATEN write roles for Artikel-Stamm creation', () => {
    const stoff: ScreenDefinition = { ...screen, id: 'stammdaten/artikel-stoffstrom', domain: 'stammdaten', actions: [],
      creation: { endpoint: '/api/v1/artikel/stoffstrom', permission: 'stammdaten.stoffstrom.create', detailRoute: '/stammdaten/artikel-stoffstrom/{entity_id}' } }
    expect(getScreenPermissions(stoff, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(stoff, user([], ['EINKAUF_BEARBEITEN']))).toEqual(['stammdaten.stoffstrom.create'])
    expect(getScreenPermissions(stoff, user([], ['LAGER_ADMIN']))).toEqual(['stammdaten.stoffstrom.create'])
  })
  it('matches CRM/SALES write roles for Verkauf-Kunde creation', () => {
    const kunde: ScreenDefinition = { ...screen, id: 'verkauf/kunde-neu', domain: 'verkauf', actions: [],
      creation: { endpoint: '/api/v1/crm/customers/', permission: 'verkauf.kunde.create', detailRoute: '/crm/customer-360/{entity_id}' } }
    expect(getScreenPermissions(kunde, user([], ['EINKAUF_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(kunde, user([], ['SALES_BEARBEITEN']))).toEqual(['verkauf.kunde.create'])
    expect(getScreenPermissions(kunde, user([], ['CRM_ADMIN']))).toEqual(['verkauf.kunde.create'])
  })
  it('matches SALES write roles for Individualpreis creation', () => {
    const preis: ScreenDefinition = { ...screen, id: 'preise/individualpreise', domain: 'preise', actions: [],
      creation: { endpoint: '/api/v1/preise/individualpreise', permission: 'preise.individualpreis.create', detailRoute: '/preise/individualpreise/{entity_id}' } }
    expect(getScreenPermissions(preis, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(preis, user([], ['SALES_BEARBEITEN']))).toEqual(['preise.individualpreis.create'])
  })
  it('matches KONTRAKT write roles for Zu-/Abschlaggruppe creation', () => {
    const zagr: ScreenDefinition = { ...screen, id: 'preise/zu-abschlaggruppen', domain: 'preise', actions: [],
      creation: { endpoint: '/api/v1/kontrakte/zuabschlagsgruppen', permission: 'preise.zuabschlaggruppe.create', detailRoute: '/preise/zu-abschlaggruppen/{entity_id}' } }
    expect(getScreenPermissions(zagr, user([], ['SALES_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(zagr, user([], ['KONTRAKT_BEARBEITEN']))).toEqual(['preise.zuabschlaggruppe.create'])
  })
  it('matches PERSONAL write roles for Schulung creation', () => {
    const schulung: ScreenDefinition = { ...screen, id: 'personal/schulung-neu', domain: 'personal', actions: [],
      creation: { endpoint: '/api/v1/training/courses', permission: 'personal.schulung.create', detailRoute: '/personal/schulungen/{entity_id}', payloadEnvelope: 'data' } }
    expect(getScreenPermissions(schulung, user([], ['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(schulung, user([], ['PERSONAL_BEARBEITEN']))).toEqual(['personal.schulung.create'])
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
  const lead: ScreenDefinition = { ...screen, id: 'crm/lead', domain: 'crm',
    actions: [{ key: 'bearbeiten', label: 'Bearbeiten', permission: 'crm.lead.update' }] }
  const contract: ScreenDefinition = { ...screen, id: 'agrar/kontrakte', domain: 'agrar',
    actions: [{ key: 'bearbeiten', label: 'Bearbeiten', permission: 'kontrakt.update' }] }
  it('grants the edit action to the area role without a scope attribute', () => {
    expect(getScreenPermissions(lead, user([], ['CRM_BEARBEITEN']))).toEqual(['crm.lead.update'])
    expect(getScreenPermissions(lead, user([], ['CRM_LESEN']))).toEqual([])
  })
  it('a scope attribute cannot outvote the server roles', () => {
    expect(getScreenPermissions(lead, user(['crm.lead.update'], ['SALES_BEARBEITEN']))).toEqual([])
    // Kontraktaenderung verlangt die Kontraktrolle selbst; admin allein reicht dort auch serverseitig nicht.
    expect(getScreenPermissions(contract, user(['admin:all'], ['admin']))).toEqual([])
    expect(getScreenPermissions(contract, user([], ['KONTRAKT_BEARBEITEN']))).toEqual(['kontrakt.update'])
  })
})

it('requires the backend admin role for renaming a branch', () => {
  const branch = {
    id: 'admin/branches/detail',
    actions: [{ key: 'bearbeiten', label: 'Umbenennen', permission: 'admin:all' }],
  } as ScreenDefinition
  expect(getScreenPermissions(branch, user(['admin:all']))).toEqual([])
  expect(getScreenPermissions(branch, user([], ['admin']))).toEqual(['admin:all'])
})
