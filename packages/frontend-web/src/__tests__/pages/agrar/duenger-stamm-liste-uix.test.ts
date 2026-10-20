import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/duenger/liste.tsx'),
  'utf8',
)

describe('Düngemittel-Stamm-Liste UIX', () => {
  it('ist dieselbe Studio-Liste wie /agrar/duenger-liste (Deaktivieren als Kommando-Weg mit Grund)', () => {
    expect(src).toContain("export { default } from '../duenger-liste'")
  })
})
