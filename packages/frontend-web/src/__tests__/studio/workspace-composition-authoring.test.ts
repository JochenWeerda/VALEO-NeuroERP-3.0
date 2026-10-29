import { describe, expect, it } from 'vitest'

import {
  patchWorkspaceCompositionMeta,
  setSpecializedHostView,
  upsertReleasedScreenView,
} from '@/studio/workspace-composition-authoring'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  isWorkspaceCompositionValid,
  validateWorkspaceComposition,
} from '@/studio/workspace-composition'

describe('WorkspaceComposition Authoring Mutationen', () => {
  it('patcht Titel und Beschreibung ohne Vertrag zu brechen', () => {
    const next = patchWorkspaceCompositionMeta(WORKSPACE_COMPOSITION_FIXTURE, {
      title: 'Neuer Arbeitsraum',
      description: 'Kurzbeschreibung',
    })
    expect(next.title).toBe('Neuer Arbeitsraum')
    expect(next.description).toBe('Kurzbeschreibung')
    expect(isWorkspaceCompositionValid(next)).toBe(true)
  })

  it('entfernt description und defaultViewId bei null', () => {
    const next = patchWorkspaceCompositionMeta(WORKSPACE_COMPOSITION_FIXTURE, {
      description: null,
      defaultViewId: null,
    })
    expect(next.description).toBeUndefined()
    expect(next.defaultViewId).toBeUndefined()
    expect(isWorkspaceCompositionValid(next)).toBe(true)
  })

  it('setzt Host-View fuer Inbox-Slot', () => {
    const next = setSpecializedHostView(
      WORKSPACE_COMPOSITION_FIXTURE,
      'inbox',
      'dispo-cockpit',
    )
    const inbox = next.specializedComponents.find((slot) => slot.kind === 'inbox')
    expect(inbox?.hostViewId).toBe('dispo-cockpit')
    expect(isWorkspaceCompositionValid(next)).toBe(true)
  })

  it('nimmt freigegebene ScreenDefinition als View auf', () => {
    const next = upsertReleasedScreenView(WORKSPACE_COMPOSITION_FIXTURE, {
      screenId: 'sales/angebot-detail',
      label: 'Angebot Detail',
      routePath: '/sales/angebot/neu',
      moduleId: 'sales',
      moduleLabel: 'Verkauf',
      domain: 'sales',
      asDefault: true,
    })
    const view = next.views.find((item) => item.screenId === 'sales/angebot-detail')
    expect(view).toBeDefined()
    expect(view?.label).toBe('Angebot Detail')
    expect(view?.routePath).toBe('/sales/angebot/neu')
    expect(next.modules.some((mod) => mod.id === 'sales')).toBe(true)
    expect(next.defaultViewId).toBe(view?.id)
    expect(isWorkspaceCompositionValid(next)).toBe(true)
  })

  it('aktualisiert bestehende View bei gleichem screenId', () => {
    const once = upsertReleasedScreenView(WORKSPACE_COMPOSITION_FIXTURE, {
      screenId: 'workspace/document-inbox',
      label: 'Inbox neu',
      routePath: '/workspace/inbox-v2',
    })
    const viewsWithScreen = once.views.filter((v) => v.screenId === 'workspace/document-inbox')
    expect(viewsWithScreen).toHaveLength(1)
    expect(viewsWithScreen[0]?.label).toBe('Inbox neu')
    expect(viewsWithScreen[0]?.routePath).toBe('/workspace/inbox-v2')
    expect(isWorkspaceCompositionValid(once)).toBe(true)
  })

  it('meldet ungueltigen defaultViewId', () => {
    const broken = patchWorkspaceCompositionMeta(WORKSPACE_COMPOSITION_FIXTURE, {
      defaultViewId: 'gibt-es-nicht',
    })
    const issues = validateWorkspaceComposition(broken)
    expect(issues.some((issue) => issue.code === 'default_view')).toBe(true)
  })
})
