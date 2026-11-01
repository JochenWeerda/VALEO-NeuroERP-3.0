import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/duenger/liste.tsx'),
  'utf8',
)

describe('Düngemittel-Liste Unterpfad UIX', () => {
  it('läuft über NativeListPage und ScreenDefinition agrar/duenger-liste', () => {
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="agrar/duenger-liste"')
  })
})
