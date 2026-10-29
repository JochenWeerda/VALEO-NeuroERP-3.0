import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

describe('Reklamationen Studio-Einstieg', () => {
  it('verwendet ausschließlich die zentrale NativeListPage statt eigener Maskenlogik', () => {
    const source = readFileSync(resolve(__dirname, '../../../pages/qualitaet/reklamationen.tsx'), 'utf8')
    expect(source).toContain('NativeListPage')
    expect(source).toContain('screenId="qualitaet/reklamationen-liste"')
    expect(source).not.toContain('DataTable')
    expect(source).not.toContain('useReklamationen')
  })
})
