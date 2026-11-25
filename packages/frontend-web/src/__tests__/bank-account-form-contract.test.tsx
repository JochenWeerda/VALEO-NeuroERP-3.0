import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { expect, it } from 'vitest'

/**
 * Bankkonto-Neuanlage laeuft native (UniversalNativeCreatePage).
 * Server validiert IBAN bei POST /api/v1/banken/konten; der Legacy-Client-
 * Lookup (useIbanLookup) gehoerte zur ObjectPage-Altmaske und ist absichtlich
 * nicht mehr Teil der produktiven Stamm-Route.
 */
it('bankkonten-stamm uses native create without legacy ObjectPage', () => {
  const src = readFileSync(
    resolve(__dirname, '../pages/finance/bankkonten-stamm.tsx'),
    'utf8',
  )
  expect(src).toContain('createStammNativeDetailPage')
  expect(src).toContain("'finance/bankkonto'")
  expect(src).not.toContain('-legacy')
  expect(src).not.toContain('useIbanLookup')
})
