import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/charge/liste.tsx'),
  'utf8',
)

describe('Chargen-Liste UIX', () => {
  it('ist eine Studio-Liste aus der ScreenDefinition charge/liste', () => {
    // MASK-STUDIO-ROLLOUT: 44-px-Zeilen, Suche, Export und Touch-Verhalten liefert der universelle Renderer.
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="charge/liste"')
    expect(src).not.toContain('apiClient')
  })
})
