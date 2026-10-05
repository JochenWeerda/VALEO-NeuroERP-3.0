import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/silo-mobil.tsx'),
  'utf8',
)

describe('Silo-Terminal UIX', () => {
  it('zeigt QS-Status mit Label und Tokens, Lagerwahl 44 px', () => {
    expect(src).toContain('aria-label="Lager"')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('QS ${qsLabel}')
    expect(src).not.toContain('bg-red-500')
    expect(src).not.toContain('bg-emerald-500')
    expect(src).not.toContain('-- Lager --')
    expect(src).toContain('Spülcharge')
  })
})
