import { describe, expect, it } from 'vitest'

import { applyRationPatch } from '@/pages/futtermittel/rationsoptimierung'

type WizardState = Parameters<typeof applyRationPatch>[0]

function state(): WizardState {
  return {
    selectedFeedIds: new Set(['mais', 'gras']),
    feedMinFm: { mais: 10 },
    feedMaxFm: { mais: 30, gras: 20 },
  } as WizardState
}

describe('Rations-Workbench Zeilen-CRUD', () => {
  it('fixiert eine Menge als identische Min-/Max-Grenze', () => {
    const result = applyRationPatch(state(), { fix_feed_fm: { mais: 17.5 } })

    expect(result.feedMinFm?.mais).toBe(17.5)
    expect(result.feedMaxFm.mais).toBe(17.5)
  })

  it('löst Fixierungen, ohne das Futtermittel aus dem Korb zu entfernen', () => {
    const result = applyRationPatch(state(), { unfix_feed_ids: ['mais'] })

    expect(result.selectedFeedIds.has('mais')).toBe(true)
    expect(result.feedMinFm?.mais).toBeUndefined()
    expect(result.feedMaxFm.mais).toBeUndefined()
  })

  it('entfernt Futtermittel samt Grenzen und kann neue hinzufügen', () => {
    const result = applyRationPatch(state(), {
      remove_feed_ids: ['mais'],
      add_feed_ids: ['raps'],
    })

    expect([...result.selectedFeedIds]).toEqual(['gras', 'raps'])
    expect(result.feedMinFm?.mais).toBeUndefined()
    expect(result.feedMaxFm.mais).toBeUndefined()
  })
})
