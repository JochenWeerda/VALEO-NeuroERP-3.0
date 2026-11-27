import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pageSrc = readFileSync(
  resolve(__dirname, '../../../pages/crm/kunden-stamm-modern.tsx'),
  'utf8',
)

describe('KundenStammModern route switch', () => {
  it('re-exports the native customer-360 mask (no legacy fallback)', () => {
    expect(pageSrc).toContain("export { default } from './customer-360-native'")
    expect(pageSrc).not.toContain('LegacyKundenStammModern')
    expect(pageSrc).not.toContain('CustomerMaskEditPage')
    expect(pageSrc).not.toContain('ENABLE_UNIVERSAL_MASK_CUSTOMER')
  })
})
