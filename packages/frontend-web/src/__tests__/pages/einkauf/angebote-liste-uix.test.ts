import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/einkauf/angebote-liste.tsx'),
  'utf8',
)

describe('Einkauf-Angebotsliste UIX', () => {
  it('ist eine Studio-Liste aus der ScreenDefinition ohne eigenen Seitencode', () => {
    // MASK-STUDIO-ROLLOUT: Spalten, Aktionen, Export und Zeilenroute stehen in einkauf/angebote.
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="einkauf/angebote"')
    expect(src).not.toContain('apiClient')
  })
})
