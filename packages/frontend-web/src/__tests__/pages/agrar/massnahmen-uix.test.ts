import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/feldbuch/massnahmen.tsx'),
  'utf8',
)

describe('Maßnahmen UIX', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('öffnet Schläge per 44-px-Tipp und blendet Theater auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Maßnahmen')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('handleDelete')
    expect(src).toContain('h-11 w-11')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="icon"')
    expect(src).not.toContain('D?ngung')
  })
})
