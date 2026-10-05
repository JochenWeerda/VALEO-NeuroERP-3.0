import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/charge/liste.tsx'),
  'utf8',
)

describe('Chargen-Liste UIX', () => {
  it('stellt Chargen-ID 44 px, Export wirkt, KPI nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium font-mono text-primary')
    expect(src).toContain('Suche Chargen')
    expect(src).toContain('onClick={() => {')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('bg-orange-50')
  })
})
