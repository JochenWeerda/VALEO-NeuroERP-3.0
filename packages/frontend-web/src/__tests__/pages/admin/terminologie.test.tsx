import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

/** Terminologie ist seit 09.11.2026 die Studio-Liste admin/terminologie (Leseweg /terminology/begriffe). */
describe('TerminologiePage', () => {
  it('bindet die Studio-Liste statt der handgebauten Seite', () => {
    const src = readFileSync(resolve(__dirname, '../../../pages/admin/terminologie.tsx'), 'utf-8')
    expect(src).toContain('screenId="admin/terminologie"')
    expect(src).toContain('NativeListPage')
  })
})
