import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/einkauf/lieferanten-liste.tsx'),
  'utf8',
)

describe('Lieferanten-Liste UIX', () => {
  it('ist eine Studio-Liste aus derselben Quelle wie die Objektmaske', () => {
    // MASK-STUDIO-ROLLOUT: Suche, 44-px-Zeilen und Touch-Verhalten liefert der universelle Renderer.
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="einkauf/lieferanten"')
    expect(src).not.toContain('/api/v1/crm/suppliers')
  })
})
