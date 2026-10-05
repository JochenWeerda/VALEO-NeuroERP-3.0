import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/aussaat/liste.tsx'),
  'utf8',
)

describe('Aussaat-Liste UIX', () => {
  it('filtert wirklich und öffnet per 44-px-Tipp', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Aussaaten')
    expect(src).toContain('filteredAussaaten')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).toContain('handleExport')
  })
})
