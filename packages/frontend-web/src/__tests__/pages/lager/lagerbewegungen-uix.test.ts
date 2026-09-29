import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/lagerbewegungen.tsx'),
  'utf8',
)

describe('Lagerbewegungen UIX', () => {
  it('stellt Buchungen 44 px, deutsche Typen, Theater nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('Loeschen')
    expect(src).toContain("in: 'Zugang'")
    expect(src).toContain('Suche Lagerbewegungen')
    expect(src).not.toContain('size="icon"')
    expect(src).not.toContain('indigo-500')
  })
})
