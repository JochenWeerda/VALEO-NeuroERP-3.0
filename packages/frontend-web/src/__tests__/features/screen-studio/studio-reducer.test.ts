import { describe, expect, it } from 'vitest'
import { emptyStudioDraft } from '@/features/screen-studio/studio-defaults'
import { mockRowsFor, studioReducer, removeStudioActions } from '@/features/screen-studio/studio-reducer'

describe('studioReducer', () => {
  it('adds a table column without dropping the floorplan contract', () => {
    const next = studioReducer(emptyStudioDraft(), {
      type: 'addColumn',
      tableKey: 'list',
      column: { key: 'region', label: 'Region', sortable: true },
    })
    expect(next.layout?.floorplan).toBe('worklist')
    expect(next.layout?.columnNavigation).toBe('listDetail')
    expect(next.tables?.[0]?.columns.map((column) => column.key)).toContain('region')
  })

  it('builds mock rows for the live preview', () => {
    const rows = mockRowsFor(emptyStudioDraft())
    expect(rows.list).toHaveLength(3)
    expect(rows.list[0]).toMatchObject({ id: 'list-1' })
  })
})


it('removes nested and agent actions and keeps domain metadata consistent', () => {
  const draft = emptyStudioDraft()
  const cleared = removeStudioActions(draft)
  expect(cleared.actions).toEqual([])
  expect(cleared.agentContract?.availableActions).toEqual([])
  expect(cleared.agentContract?.editableFields).toEqual([])
  const agrar = studioReducer(cleared, { type: 'setDomain', domain: 'agrar' })
  expect(agrar.domain).toBe('agrar')
  expect(agrar.agentContract?.domain).toBe('agrar')
})
