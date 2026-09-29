import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/psm/liste.tsx'),
  'utf8',
)

describe('PSM-Liste UIX', () => {
  it('öffnet Mittel per 44-px-Tipp ohne Hover-Blau', () => {
    expect(src).toContain('Suche Pflanzenschutzmittel')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).toContain('min-h-touch gap-2 touch-manipulation')
  })
})
