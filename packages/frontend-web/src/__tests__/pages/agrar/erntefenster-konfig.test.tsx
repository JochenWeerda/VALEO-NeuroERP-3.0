import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/erntefenster-konfig.tsx'),
  'utf8',
)

describe('ErntefensterKonfigPage', () => {
  it('stellt die geroutete Seite als NativeListPage (Studio) dar', () => {
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="agrar/erntefenster-konfig"')
    expect(src).toContain('testId="screen-agrar/erntefenster-konfig"')
  })
})
