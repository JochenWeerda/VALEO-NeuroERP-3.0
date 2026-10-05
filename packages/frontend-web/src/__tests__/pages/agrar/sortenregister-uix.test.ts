import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/saatgut/sortenregister.tsx'),
  'utf8',
)

describe('Sortenregister UIX', () => {
  it('öffnet Sorten per 44-px-Tipp ohne Hover-Blau', () => {
    expect(src).toContain('Suche Sorten')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('min-h-touch gap-2 touch-manipulation')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('Suche...')
  })
})
