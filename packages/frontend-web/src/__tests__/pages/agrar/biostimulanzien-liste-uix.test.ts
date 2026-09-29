import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/biostimulanzien-liste.tsx'),
  'utf8',
)

describe('Biostimulanzien-Liste UIX', () => {
  it('stellt Anzeigen und Bearbeiten 44 px beschriftet', () => {
    expect(src).toContain('Anzeigen')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('title="Anzeigen"')
    expect(src).not.toContain('bg-gray-100')
  })
})
