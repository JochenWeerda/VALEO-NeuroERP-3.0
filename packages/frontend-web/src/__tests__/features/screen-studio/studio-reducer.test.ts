import { describe, expect, it } from 'vitest'
import { emptyStudioDraft } from '@/features/screen-studio/studio-defaults'
import { mockRowsFor, studioReducer } from '@/features/screen-studio/studio-reducer'

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
