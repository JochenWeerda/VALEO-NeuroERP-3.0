import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/saatgut-liste.tsx'),
  'utf8',
)

describe('Saatgut-Liste UIX', () => {
  it('ist eine Studio-Liste; Zeilen oeffnen die native Objektmaske', () => {
    // MASK-STUDIO-ROLLOUT: 44-px-Zeilen, Suche und Touch-Verhalten liefert der universelle Renderer.
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="agrar/saatgut-liste"')
    expect(src).not.toContain('apiClient')
  })
})
