import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/bodenproben/liste.tsx'),
  'utf8',
)

describe('Bodenproben-Liste UIX', () => {
  it('öffnet Proben per 44-px-Tipp und stellt Suche vor KPI', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Bodenproben')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('{!isTouch ? (')
    expect(src).not.toContain('text-blue-600')
    expect(src).toContain('Nährstoff-Analysen')
  })
})
