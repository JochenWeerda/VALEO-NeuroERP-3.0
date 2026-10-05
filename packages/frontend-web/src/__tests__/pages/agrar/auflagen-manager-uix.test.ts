import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/psm/auflagen-manager.tsx'),
  'utf8',
)

describe('PSM-Auflagen UIX', () => {
  it('stellt PSM 44 px, Erledigt beschriftet, KPI nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Erledigt')
    expect(src).toContain('Suche Auflagen')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-red-50')
  })
})
