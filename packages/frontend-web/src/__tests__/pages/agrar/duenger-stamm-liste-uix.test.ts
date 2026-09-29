import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/duenger/liste.tsx'),
  'utf8',
)

describe('Düngemittel-Stamm-Liste UIX', () => {
  it('stellt Name 44 px, Loeschen pro Id, KPI nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('deletePendingId')
    expect(src).toContain('Anzeigen')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="sm"')
  })
})
