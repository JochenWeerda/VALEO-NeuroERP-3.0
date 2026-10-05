import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/kontrakte/mengenzeitraeume.tsx'),
  'utf8',
)

describe('Mengenzeiträume UIX', () => {
  it('lädt Kontrakte per 44-px-Tipp und löscht nicht per Icon-only', () => {
    expect(src).toContain('min-h-touch')
    expect(src).toContain('aria-label="Kontrakt-Staffeln"')
    expect(src).toContain('handleDeleteZeitraum')
    expect(src).toContain('Löschen')
    expect(src).not.toContain('size="icon"')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('Links eine Gruppe')
  })
})
