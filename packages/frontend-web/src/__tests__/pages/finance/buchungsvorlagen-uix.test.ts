import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/finance/buchungsvorlagen.tsx'),
  'utf8',
)

describe('Buchungsvorlagen UIX (Buchhaltung)', () => {
  it('hat 44-px-Anwenden/Löschen, deutsche Filter und ehrliches Anlegen', () => {
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).toContain('CATEGORY_LABELS')
    expect(src).toContain('Anlegen folgt noch')
    expect(src).toContain('wirklich löschen')
    expect(src).not.toMatch(/size="sm"/)
  })
})
