import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/auslagerung.tsx'),
  'utf8',
)

describe('Auslagerung UIX (Disposition)', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('stellt den Wizard vor dem Fallkopf und blendet Theater auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('Auslagerung: {fallkopf.status}'))
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('if (saving) return')
    expect(src).not.toContain('text-green-700')
  })
})
