/**
 * Typed Spiegel der YAML-Fixture `config/studio_workspace_composition.fixture.yaml`.
 * Tests nutzen dieses Objekt (kein YAML-Dependency im Frontend-Paket).
 */

import type { WorkspaceComposition } from './workspace-composition'

export const WORKSPACE_COMPOSITION_FIXTURE: WorkspaceComposition = {
  schemaVersion: 1,
  id: 'workspace.disposition-und-inbox',
  studioVersion: '1.0.0',
  title: 'Disposition und Beleg-Inbox',
  description:
    'Beispiel-Arbeitsraum: Cockpit-Host mit Document-Inbox und Dispo-Tafel '
    + 'als spezialisierte Slots — kundenindividuelles Layout ohne Neuimplementierung.',
  modules: [
    { id: 'logistics', label: 'Logistik', domain: 'logistics', order: 10 },
    { id: 'documents', label: 'Belege', domain: 'platform', order: 20 },
  ],
  views: [
    {
      id: 'dispo-cockpit',
      moduleId: 'logistics',
      label: 'Dispositions-Cockpit',
      screenId: 'workspace/disposition-cockpit',
      routePath: '/workspace/disposition',
      order: 10,
    },
    {
      id: 'beleg-inbox-host',
      moduleId: 'documents',
      label: 'Beleg-Inbox',
      screenId: 'workspace/document-inbox',
      routePath: '/workspace/inbox',
      order: 20,
    },
  ],
  specializedComponents: [
    {
      id: 'slot-disposition-board',
      kind: 'disposition_board',
      label: 'Dispo-Tafel',
      hostViewId: 'dispo-cockpit',
      bindingId: 'disposition.board.default',
      screenId: 'workspace/disposition-cockpit',
      props: { density: 'expert', showUnassigned: true },
    },
    {
      id: 'slot-document-inbox',
      kind: 'inbox',
      label: 'Document-Inbox',
      hostViewId: 'beleg-inbox-host',
      bindingId: 'documents.inbox.capture',
      screenId: 'workspace/document-inbox',
      props: { queue: 'capture', pageSize: 50 },
    },
  ],
  fachaktionRefs: [
    {
      id: 'action-open-inbox-item',
      actionKey: 'documents.inbox.open',
      label: 'Beleg öffnen',
      scope: 'specialized',
      specializedComponentId: 'slot-document-inbox',
      permission: 'dms.inbox.read',
    },
    {
      id: 'action-assign-tour',
      actionKey: 'disposition.tour.assign',
      label: 'Tour zuweisen',
      scope: 'specialized',
      specializedComponentId: 'slot-disposition-board',
      permission: 'logistics.disposition.write',
    },
    {
      id: 'action-refresh-cockpit',
      actionKey: 'workspace.cockpit.refresh',
      label: 'Aktualisieren',
      scope: 'view',
      viewId: 'dispo-cockpit',
      permission: 'logistics.disposition.read',
    },
    {
      id: 'action-workspace-home',
      actionKey: 'workspace.navigate.home',
      label: 'Arbeitsraum-Start',
      scope: 'workspace',
    },
  ],
  personalization: {
    pinStorageKey: 'valeo.workspace.composition.overlay',
    pinnedViewsKey: 'pinnedViewIds',
    fixedStartViewKey: 'fixedStartViewId',
  },
  defaultViewId: 'dispo-cockpit',
}
