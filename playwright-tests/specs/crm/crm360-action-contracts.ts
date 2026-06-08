export type Crm360ActionKind =
  | 'modal'
  | 'tab'
  | 'navigate'
  | 'create'
  | 'update'
  | 'complete'
  | 'external'
  | 'delegated'
  | 'local-only'

export type Crm360Workflow =
  | 'customer-master'
  | 'customer-communication'
  | 'offer-to-cash'
  | 'receivables'
  | 'document-management'
  | 'follow-up'
  | 'analytics'

export interface Crm360ActionContract {
  id: string
  label: string
  selector: string
  handler: string
  kind: Crm360ActionKind
  requiredContext: string[]
  expectedTarget: string
  crud: 'C' | 'R' | 'U' | 'D' | 'COMPLETE' | 'NONE'
  backTarget: string
  workflow: Crm360Workflow
  automated: boolean
  note?: string
}

export const CRM360_ACTION_CONTRACTS: readonly Crm360ActionContract[] = [
  {
    id: 'crm360.master.open',
    label: 'Öffnen',
    selector: '[data-action-id="crm360.master.open"]',
    handler: 'openMasterEdit',
    kind: 'update',
    requiredContext: ['customerId'],
    expectedTarget: 'Dialog Stammdaten & Kreditversicherung bearbeiten',
    crud: 'U',
    backTarget: '/crm',
    workflow: 'customer-master',
    automated: true,
  },
  {
    id: 'crm360.activity.create',
    label: 'Neu',
    selector: '[data-action-id="crm360.activity.create"]',
    handler: 'ContactHistoryTable öffnen',
    kind: 'create',
    requiredContext: ['customerId'],
    expectedTarget: '#add-history-vorgang-form',
    crud: 'C',
    backTarget: '/crm',
    workflow: 'customer-communication',
    automated: true,
  },
  {
    id: 'crm360.customer.info',
    label: 'Information',
    selector: '[data-action-id="crm360.customer.info"]',
    handler: 'setShowCustomerInfoModal',
    kind: 'modal',
    requiredContext: ['customerId'],
    expectedTarget: '[data-testid="crm360-customer-info-dialog"]',
    crud: 'R',
    backTarget: '/crm',
    workflow: 'customer-master',
    automated: true,
  },
  {
    id: 'crm360.presents.open',
    label: 'Präsente',
    selector: '[data-action-id="crm360.presents.open"]',
    handler: 'setShowPresentsModal',
    kind: 'modal',
    requiredContext: ['customerId'],
    expectedTarget: 'Präsente & Geschenke-PR Protokoll',
    crud: 'R',
    backTarget: '/crm',
    workflow: 'customer-communication',
    automated: true,
  },
  {
    id: 'crm360.call.create',
    label: 'Telefon',
    selector: '[data-action-id="crm360.call.create"]',
    handler: 'setShowCallLogModal',
    kind: 'create',
    requiredContext: ['customerId'],
    expectedTarget: 'Schnelles Telefonat protokollieren',
    crud: 'C',
    backTarget: '/crm',
    workflow: 'customer-communication',
    automated: true,
  },
  {
    id: 'crm360.email.open',
    label: 'E-Mail',
    selector: '[data-action-id="crm360.email.open"]',
    handler: 'mailto',
    kind: 'external',
    requiredContext: ['customerId', 'email'],
    expectedTarget: 'mailto:<customer.email>',
    crud: 'NONE',
    backTarget: '/crm',
    workflow: 'customer-communication',
    automated: false,
    note: 'OS-Mailclient ist extern; automatisiert wird nur der vorhandene Kundenkontext inventarisiert.',
  },
  {
    id: 'crm360.offer.create',
    label: 'Ang./Auf.',
    selector: '[data-action-id="crm360.offer.create"]',
    handler: 'navigate',
    kind: 'navigate',
    requiredContext: ['debtorNo', 'customerName'],
    expectedTarget: '/sales/angebot-erstellen?kunde=<debtorNo>&kundeName=<name>&entryMode=crm360',
    crud: 'C',
    backTarget: '/crm',
    workflow: 'offer-to-cash',
    automated: true,
  },
  {
    id: 'crm360.receivables.open',
    label: 'Faktur',
    selector: '[data-action-id="crm360.receivables.open"]',
    handler: 'navigate',
    kind: 'navigate',
    requiredContext: ['debtorNo'],
    expectedTarget: '/finance/op-debitoren?kunden_nr=<debtorNo>',
    crud: 'R',
    backTarget: '/crm',
    workflow: 'receivables',
    automated: true,
  },
  {
    id: 'crm360.filters.reset',
    label: 'Filter rstd.',
    selector: '[data-action-id="crm360.filters.reset"]',
    handler: 'reset workspace key and active tab',
    kind: 'tab',
    requiredContext: [],
    expectedTarget: '#sub-workspace-tab-allgemein',
    crud: 'NONE',
    backTarget: '/crm',
    workflow: 'customer-master',
    automated: true,
  },
  {
    id: 'crm360.ai.summary',
    label: 'NeuroAI',
    selector: '[data-action-id="crm360.ai.summary"]',
    handler: 'fetchNeuroSummary',
    kind: 'create',
    requiredContext: ['customerId'],
    expectedTarget: '#slide-ai-markdown',
    crud: 'NONE',
    backTarget: '/crm',
    workflow: 'analytics',
    automated: true,
  },
  ...[
    ['allgemein', 'Allgemein / Ansprechpartner', 'customer-master'],
    ['belege', 'Belegwesen', 'offer-to-cash'],
    ['kontrakte', 'Silokontrakte', 'offer-to-cash'],
    ['finanzen', 'Finanzwesen', 'receivables'],
    ['audit', 'Unterlagen', 'document-management'],
    ['tasks', 'Wiedervorlage', 'follow-up'],
    ['chef', 'Chef-Anweisungen', 'customer-master'],
    ['leads', 'Lead-Management', 'offer-to-cash'],
    ['geo', 'CRM-Geo / Karte', 'customer-master'],
  ].map(([key, label, workflow]) => ({
    id: `crm360.tab.${key}`,
    label,
    selector: `[data-action-id="crm360.tab.${key}"]`,
    handler: 'setActiveTab',
    kind: 'tab' as const,
    requiredContext: ['customerId'],
    expectedTarget: `CRM360 tab ${key}`,
    crud: 'R' as const,
    backTarget: '/crm',
    workflow: workflow as Crm360Workflow,
    automated: !['leads', 'geo'].includes(key),
  })),
  {
    id: 'crm360.documents.create.delegated',
    label: 'Warenbeleg erfassen',
    selector: '#btn-trigger-add-doc',
    handler: 'infoFachprozess',
    kind: 'delegated',
    requiredContext: ['customerId'],
    expectedTarget: 'Beleg-/Auftragserfassung',
    crud: 'C',
    backTarget: '/crm',
    workflow: 'offer-to-cash',
    automated: true,
    note: 'KIM ist laut Slice-Vertrag für Belege lesend.',
  },
  {
    id: 'crm360.open-items.create.delegated',
    label: 'Warenrechnung anlegen',
    selector: '#financial-ledger-table-block button',
    handler: 'infoFachprozess',
    kind: 'delegated',
    requiredContext: ['customerId'],
    expectedTarget: 'Faktura/Finanzbuchhaltung',
    crud: 'C',
    backTarget: '/crm',
    workflow: 'receivables',
    automated: true,
    note: 'KIM ist laut Slice-Vertrag für offene Posten lesend.',
  },
  {
    id: 'crm360.contract.create.delegated',
    label: 'Silokontrakt registrieren',
    selector: '#agrarian-contracts-widget > div:nth-child(2) button',
    handler: 'infoFachprozess',
    kind: 'delegated',
    requiredContext: ['customerId'],
    expectedTarget: 'Beleg-/Auftragserfassung',
    crud: 'C',
    backTarget: '/crm',
    workflow: 'offer-to-cash',
    automated: true,
    note: 'KIM zeigt Kontrakte, persistiert aber keinen Kontrakt.',
  },
  {
    id: 'crm360.archive.local',
    label: 'Unterlagen Upload/Vorschau/Download/Delete',
    selector: '#documents-panel-component',
    handler: 'local React state / alert',
    kind: 'local-only',
    requiredContext: ['customerId'],
    expectedTarget: 'Persistentes DMS',
    crud: 'NONE',
    backTarget: '/crm',
    workflow: 'document-management',
    automated: false,
    note: 'Aktuell kein Backend-CRUD und daher kein fachlicher Nachweis.',
  },
] as const

export const AUTOMATED_CRM360_ACTIONS = CRM360_ACTION_CONTRACTS.filter((action) => action.automated)
