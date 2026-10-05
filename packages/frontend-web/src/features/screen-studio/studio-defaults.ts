import { generateAgentMaskContract } from '@/components/mask-builder/runtime/generateAgentMaskContract'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

export function emptyStudioDraft(): ScreenDefinition {
  const draft: ScreenDefinition = {
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
        { key: 'lieferantennummer', label: 'Nr', sortable: true, filterable: true },
        { key: 'firmenname', label: 'Name', sortable: true, filterable: true },
        { key: 'bewertung', label: 'Bewertung', sortable: true, numeric: true },
        { key: 'ort', label: 'Ort', sortable: true, filterable: true },
      ],
    }],
    actions: [{
      key: 'create_activity',
      label: 'Aktivitaet anlegen',
      dangerLevel: 'safe',
      permission: 'studio.draft.execute',
    }],
    noWorkflowReason: 'Studio-Worklist priorisiert Auswahl; Statuswechsel bleiben auf der ObjectPage.',
  }
  return {
    ...draft,
    agentContract: {
      ...generateAgentMaskContract(draft),
      businessPurpose: 'Lieferanten bewerten und auswählen.',
      testSelectors: {
        screenRoot: "[data-testid='screen-tenant/lieferanten-bewertung']",
        submitButton: '[data-testid="form-submit-btn"]',
        workflowPanel: '[data-testid="workflow-panel"]',
      },
      examplePrompts: ['Welche Lieferanten haben die beste Bewertung?'],
      recommendedAgentTasks: ['Lieferanten nach Bewertung sortieren'],
    },
  }
}
