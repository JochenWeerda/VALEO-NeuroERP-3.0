import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'

/**
 * ScreenDefinition-Fragment fuer den Launcher. Nicht in der Backend-Registry.
 * Lead kann es spaeter als Worklist registrieren; bis dahin bleibt es ein Widget.
 */
export const ADAPTIVE_WORKSPACE_INBOX_SCREEN: ScreenDefinition = {
  schemaVersion: 1,
  id: 'workspace/inbox',
  domain: 'platform',
  mode: 'list',
  title: 'Beleg-Inbox',
  subtitle: 'Eingang pruefen und in die bestehende Belegmaske ueberfuehren',
  permissions: ['dms.inbox.write'],
  layout: {
    floorplan: 'worklist',
    density: 'compact',
    contextRail: 'workflow',
    tableProfile: 'audit',
  },
  dataSources: [
    {
      key: 'queue',
      endpoint: '/api/mcp/documents/inbox/queue',
      staleTimeMs: 15_000,
      pageSize: 50,
    },
  ],
  tables: [
    {
      key: 'queue',
      label: 'Eingang',
      dataSourceKey: 'queue',
      columns: [
        { key: 'proposal.label', label: 'Vorschlag', width: 220, priority: 'primary' },
        { key: 'confidence', label: 'Konfidenz', width: 100, numeric: true, priority: 'primary' },
        { key: 'source', label: 'Quelle', width: 160, priority: 'secondary' },
        { key: 'match_values.supplierName', label: 'Partner', width: 180, priority: 'secondary' },
        { key: 'status', label: 'Status', width: 110, renderKind: 'status', priority: 'tertiary' },
      ],
      rowActions: [
        { key: 'open_mask', label: 'Beleg öffnen' },
        { key: 'prepare', label: 'Vorschlag pruefen' },
      ],
    },
  ],
  actions: [
    {
      key: 'open_mask',
      label: 'Beleg öffnen',
      kind: 'primary',
      localEffect: 'navigation',
      dangerLevel: 'safe',
    },
    {
      key: 'prepare',
      label: 'Vorschlag pruefen',
      kind: 'secondary',
      commandEndpoint: '/api/mcp/documents/inbox/{id}/prepare',
      method: 'POST',
      dangerLevel: 'safe',
    },
  ],
  noWorkflowReason: 'Die Inbox ist ein Launcher auf die Belegmaske, kein eigener Belegstatus.',
  agentContract: {
    screenId: 'workspace/inbox',
    domain: 'platform',
    schemaVersion: 1,
    contractVersion: 1,
    businessPurpose: 'Eingangsbelege mit Konfidenz und Vorschlag in die vorhandene Belegmaske fuehren.',
    primaryEntity: 'dms_inbox',
    readableFields: ['id', 'confidence', 'proposal', 'match_values', 'blockers'],
    editableFields: [],
    sensitiveFields: ['ocr_excerpt'],
    availableActions: [
      {
        key: 'open_mask',
        label: 'Beleg öffnen',
        dangerLevel: 'safe',
        requiresHumanApproval: false,
        requiresConfirmation: false,
      },
      {
        key: 'prepare',
        label: 'Vorschlag pruefen',
        dangerLevel: 'safe',
        requiresHumanApproval: false,
        requiresConfirmation: false,
      },
    ],
    validationRules: [],
    workflowRules: [],
    auditRequirements: [],
    recommendedAgentTasks: [
      'Vorschlag mit Quelle und Konfidenz vorbereiten',
      'Prefill nach valeo.inbox.prefill schreiben',
      'Bestehende Belegmaske oeffnen',
    ],
    forbiddenAgentTasks: ['Beleg buchen', 'Beleg stornieren', 'Zahlung erzeugen', 'create_from_inbox als Buchung behandeln'],
    testSelectors: { root: 'adaptive-workspace-inbox' },
    examplePrompts: ['Welche Eingangsrechnungen liegen mit niedriger Konfidenz in der Inbox?'],
  },
}

export function inboxScreenIssues(): string[] {
  return validateScreenDefinition(ADAPTIVE_WORKSPACE_INBOX_SCREEN)
}
