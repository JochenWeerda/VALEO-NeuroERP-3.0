import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/finance/buchungsvorlagen.tsx'),
  'utf8',
)

describe('Buchungsvorlagen UIX (Buchhaltung)', () => {
  // Seit 20.10.2026 Studio-Liste: Anwenden (mit Bestaetigung und Eingaben) und Loeschen (mit Bestaetigung) stehen
  // in der ScreenDefinition finance/buchungsvorlagen; die 44-px-Ziele liefert der Renderer.
  it('rendert die Studio-Liste aus der ScreenDefinition', () => {
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="finance/buchungsvorlagen"')
  })
})
