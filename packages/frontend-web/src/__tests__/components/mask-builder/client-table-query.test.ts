import { describe, expect, it } from 'vitest'
import { applyClientTableQuery } from '@/components/mask-builder/runtime/client-table-query'

const zeilen = Array.from({ length: 120 }, (_, i) => ({
  id: String(i + 1), nummer: `A-${String(i + 1).padStart(3, '0')}`, status: i % 3 === 0 ? 'OFFEN' : 'FREIGEGEBEN', menge: i,
}))

describe('Tabellen ohne Serverblaetterung', () => {
  it('blaettert ueber alle geladenen Zeilen statt nur die erste Seite zu zeigen', () => {
    const zweite = applyClientTableQuery(zeilen, { page: 2, pageSize: 50 })
    expect(zweite.total).toBe(120)
    expect(zweite.rows[0].nummer).toBe('A-051')
    expect(applyClientTableQuery(zeilen, { page: 3, pageSize: 50 }).rows).toHaveLength(20)
  })

  it('sucht, filtert und sortiert im Browser', () => {
    expect(applyClientTableQuery(zeilen, { page: 1, pageSize: 50, q: 'a-007' }).rows.map((z) => z.id)).toEqual(['7'])
    const offen = applyClientTableQuery(zeilen, { page: 1, pageSize: 50,
      filterPlan: { status: { op: 'contains', value: 'offen' } } })
    expect(offen.total).toBe(40)
    const absteigend = applyClientTableQuery(zeilen, { page: 1, pageSize: 5, sort: 'menge', sortDir: 'desc' })
    expect(absteigend.rows.map((z) => z.menge)).toEqual([119, 118, 117, 116, 115])
  })
})
