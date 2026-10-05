import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/einkauf/lieferanten-liste.tsx'),
  'utf8',
)

describe('Lieferanten-Liste UIX', () => {
  it('stellt Suche vor den KPI-Karten und oeffnet per 44-px-Tipp', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Lieferanten')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('hover:underline')
    expect(src).toContain('min-h-touch gap-2 touch-manipulation')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Suche Lieferanten')
  })
})
