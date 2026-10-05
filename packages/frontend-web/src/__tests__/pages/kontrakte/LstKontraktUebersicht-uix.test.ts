import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/kontrakte/LstKontraktUebersicht.tsx'),
  'utf8',
)

describe('Kontrakt-Übersicht UIX', () => {
  it('öffnet per Tipp statt Doppelklick und macht Pager 44 px', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-mono text-primary')
    expect(src).not.toContain('onDoubleClick')
    expect(src).not.toContain('size="sm"')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).not.toContain('text-blue-700')
    expect(src).not.toContain('text-fuchsia-700')
    expect(src.indexOf('<h1')).toBeLessThan(src.indexOf('Ausweichbereit'))
  })
})
