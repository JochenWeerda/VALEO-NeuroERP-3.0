import type { ScreenDefinition } from '@/components/mask-builder/schema'

export function emptyStudioDraft(): ScreenDefinition {
  return {
    schemaVersion: 1,
    id: 'tenant/lieferanten-bewertung',
    domain: 'einkauf',
    mode: 'list',
    title: 'Lieferanten-Bewertung',
    subtitle: 'Studio-Entwurf',
    adapter: { type: 'native', sourceId: 'tenant/lieferanten-bewertung', temporary: true },
    dataSources: [{ key: 'suppliers', endpoint: '/api/v1/einkauf/lieferanten', pageSize: 50 }],
    layout: {
      floorplan: 'worklist',
      columnNavigation: 'listDetail',
      density: 'compact',
      contextRail: 'none',
      tableProfile: 'standard',
    },
    tables: [{
      key: 'list',
      label: 'Lieferanten',
      dataSourceKey: 'suppliers',
      serverPagination: true,
      pageSize: 25,
      virtualized: true,
      rowHeight: 44,
      columns: [
        { key: 'lieferanten_nr', label: 'Nr', sortable: true, filterable: true },
        { key: 'name', label: 'Name', sortable: true, filterable: true },
        { key: 'score', label: 'Bewertung', sortable: true, numeric: true },
      ],
    }],
    actions: [{
      key: 'create_activity',
      label: 'Aktivitaet anlegen',
      dangerLevel: 'safe',
      permission: 'studio.draft.execute',
    }],
    noWorkflowReason: 'Studio-Worklist priorisiert Auswahl; Statuswechsel bleiben auf der ObjectPage.',
    agentContract: {
      businessPurpose: 'Lieferanten bewerten und auswählen.',
      testSelectors: { screenRoot: "[data-testid='screen-tenant/lieferanten-bewertung']" },
    },
  }
}
