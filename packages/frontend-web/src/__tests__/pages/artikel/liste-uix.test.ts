import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/artikel/liste.tsx'),
  'utf8',
)

describe('Artikel-Liste UIX', () => {
  it('stellt Bezeichnung 44 px, Export wirkt, KPI nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('persistExport')
    expect(src).toContain('Suche Artikel')
    expect(src).not.toContain('text-blue-600')
  })
})
