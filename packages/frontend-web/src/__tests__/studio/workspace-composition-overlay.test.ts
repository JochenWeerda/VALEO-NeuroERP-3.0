import { describe, expect, it } from 'vitest'

import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  EMPTY_COMPOSITION_OVERLAY,
  applyCompositionPersonalization,
  compositionOverlayStorageKey,
  parseCompositionOverlay,
  pinCompositionView,
  serializeCompositionOverlay,
  setFixedStartView,
  unpinCompositionView,
} from '@/studio/workspace-composition-overlay'

const keys = WORKSPACE_COMPOSITION_FIXTURE.personalization

describe('workspace-composition-overlay', () => {
  it('scoped Storage-Key mit Mandant und sub', () => {
    expect(compositionOverlayStorageKey(keys.pinStorageKey)).toBe(
      'valeo.workspace.composition.overlay',
    )
    expect(compositionOverlayStorageKey(keys.pinStorageKey, 'user-1')).toBe(
      'valeo.workspace.composition.overlay.user-1',
    )
    expect(compositionOverlayStorageKey(keys.pinStorageKey, 'user-1', '0051')).toBe(
      'valeo.workspace.composition.overlay.0051.user-1',
    )
  })

  it('parst und serialisiert unter den Composition-Key-Namen', () => {
    const overlay = setFixedStartView(
      pinCompositionView(EMPTY_COMPOSITION_OVERLAY, 'beleg-inbox-host'),
      'beleg-inbox-host',
    )
    const raw = JSON.parse(serializeCompositionOverlay(overlay, keys)) as Record<string, unknown>
    expect(raw.pinnedViewIds).toEqual(['beleg-inbox-host'])
    expect(raw.fixedStartViewId).toBe('beleg-inbox-host')
    expect(parseCompositionOverlay(raw, keys)).toEqual(overlay)
  })

  it('reiht gepinnte und fixierte Views vor dem Katalog und zieht Slots nach', () => {
    const overlay = setFixedStartView(
      pinCompositionView(EMPTY_COMPOSITION_OVERLAY, 'beleg-inbox-host'),
      'beleg-inbox-host',
    )
    const next = applyCompositionPersonalization(WORKSPACE_COMPOSITION_FIXTURE, overlay)

    expect(next.views.map((view) => view.id)).toEqual(['beleg-inbox-host', 'dispo-cockpit'])
    expect(next.defaultViewId).toBe('beleg-inbox-host')
    expect(next.specializedComponents.map((slot) => slot.kind)).toEqual([
      'inbox',
      'disposition_board',
    ])
    // Katalog-Composition unveraendert
    expect(WORKSPACE_COMPOSITION_FIXTURE.views[0]?.id).toBe('dispo-cockpit')
  })

  it('ignoriert unbekannte View-IDs und loescht Fix beim Unpin', () => {
    const withGhost = parseCompositionOverlay(
      { pinnedViewIds: ['ghost', 'beleg-inbox-host'], fixedStartViewId: 'ghost' },
      keys,
    )
    const applied = applyCompositionPersonalization(WORKSPACE_COMPOSITION_FIXTURE, withGhost)
    expect(applied.views[0]?.id).toBe('beleg-inbox-host')
    expect(applied.defaultViewId).toBe('dispo-cockpit')

    const cleared = unpinCompositionView(
      setFixedStartView(EMPTY_COMPOSITION_OVERLAY, 'beleg-inbox-host'),
      'beleg-inbox-host',
    )
    expect(cleared.pinnedViewIds).toEqual([])
    expect(cleared.fixedStartViewId).toBeNull()
  })

  it('laesst ohne Overlay die Katalogordnung stehen', () => {
    const next = applyCompositionPersonalization(
      WORKSPACE_COMPOSITION_FIXTURE,
      EMPTY_COMPOSITION_OVERLAY,
    )
    expect(next.views.map((view) => view.id)).toEqual(['dispo-cockpit', 'beleg-inbox-host'])
    expect(next.specializedComponents.map((slot) => slot.kind)).toEqual([
      'disposition_board',
      'inbox',
    ])
  })
})
