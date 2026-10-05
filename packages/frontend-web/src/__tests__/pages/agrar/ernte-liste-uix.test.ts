import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/ernte/liste.tsx'),
  'utf8',
)

describe('Ernte-Liste UIX', () => {
  it('öffnet Schläge per 44-px-Tipp und stellt Suche vor KPI', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Ernten')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).toContain('{!isTouch ? (')
  })
})
