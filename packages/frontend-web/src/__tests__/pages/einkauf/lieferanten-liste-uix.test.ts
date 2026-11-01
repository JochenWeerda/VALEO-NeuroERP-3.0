import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/einkauf/lieferanten-liste.tsx'),
  'utf8',
)

describe('Lieferanten-Liste UIX', () => {
  it('läuft über NativeListPage und ScreenDefinition einkauf/lieferanten', () => {
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="einkauf/lieferanten"')
  })
})
