import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/duenger-liste.tsx'),
  'utf8',
)

describe('Dünger-Liste UIX', () => {
  it('öffnet Dünger per 44-px-Tipp, KPI nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Dünger')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Anzeigen')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('{!isTouch ? (')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="sm"')
  })
})
