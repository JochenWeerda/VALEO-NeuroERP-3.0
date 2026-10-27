import { describe, expect, it } from 'vitest'

import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  DISPOSITION_BOARD_ROUTE,
  listMountedKinds,
  resolveWorkspaceCompositionMounts,
  WORKSPACE_COMPOSITION_PREVIEW_ROUTE,
} from '@/studio/workspace-composition-runtime'
import type { WorkspaceComposition } from '@/studio/workspace-composition'

describe('WorkspaceComposition Runtime', () => {
  it('mountet aus der Fixture genau inbox und disposition_board', () => {
    const plan = resolveWorkspaceCompositionMounts(WORKSPACE_COMPOSITION_FIXTURE)

    expect(plan.compositionId).toBe('workspace.disposition-und-inbox')
    expect(plan.title).toBe('Disposition und Beleg-Inbox')
    expect(listMountedKinds(plan).sort()).toEqual(['disposition_board', 'inbox'])

    const inbox = plan.slots.find((s) => s.kind === 'inbox')
    const board = plan.slots.find((s) => s.kind === 'disposition_board')

    expect(inbox).toMatchObject({
      id: 'slot-document-inbox',
      bindingId: 'documents.inbox.capture',
      hostViewId: 'beleg-inbox-host',
      kind: 'inbox',
    })
    expect(board).toMatchObject({
      id: 'slot-disposition-board',
      bindingId: 'disposition.board.default',
      hostViewId: 'dispo-cockpit',
      kind: 'disposition_board',
      href: DISPOSITION_BOARD_ROUTE,
    })
    expect(board && 'href' in board ? board.href : null).toBe('/disposition/touren-disposition')
  })

  it('sortiert Slots deterministisch nach order dann id', () => {
    const shuffled: WorkspaceComposition = {
      ...WORKSPACE_COMPOSITION_FIXTURE,
      specializedComponents: [
        { ...WORKSPACE_COMPOSITION_FIXTURE.specializedComponents[1], order: 20 },
        { ...WORKSPACE_COMPOSITION_FIXTURE.specializedComponents[0], order: 10 },
      ],
    }
    const plan = resolveWorkspaceCompositionMounts(shuffled)
    expect(plan.slots.map((s) => s.id)).toEqual([
      'slot-disposition-board',
      'slot-document-inbox',
    ])
  })

  it('leitet Inbox-Widget-Props nur aus skalaren Composition-Props ab', () => {
    const withCompact: WorkspaceComposition = {
      ...WORKSPACE_COMPOSITION_FIXTURE,
      specializedComponents: [
        {
          ...WORKSPACE_COMPOSITION_FIXTURE.specializedComponents[1],
          props: { compact: true, confidenceMin: 0.5, queue: 'capture' },
        },
      ],
    }
    const plan = resolveWorkspaceCompositionMounts(withCompact)
    const inbox = plan.slots[0]
    expect(inbox.kind).toBe('inbox')
    if (inbox.kind !== 'inbox') return
    expect(inbox.widget).toEqual({ compact: true, confidenceMin: 0.5 })
    expect(inbox.props.queue).toBe('capture')
  })

  it('exportiert Preview-Pfad ohne App-Routenbaum zu aendern', () => {
    expect(WORKSPACE_COMPOSITION_PREVIEW_ROUTE).toBe('/studio/workspace-composition-preview')
  })
})
