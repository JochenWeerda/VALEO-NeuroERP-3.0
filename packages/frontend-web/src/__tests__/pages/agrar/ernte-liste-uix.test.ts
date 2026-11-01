import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/ernte/liste.tsx'),
  'utf8',
)

describe('Ernte-Liste UIX', () => {
  it('nutzt NativeListPage auf agrar/ernte-liste', () => {
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="agrar/ernte-liste"')
  })
})
