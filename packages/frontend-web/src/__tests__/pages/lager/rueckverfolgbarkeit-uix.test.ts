import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/rueckverfolgbarkeit.tsx'),
  'utf8',
)

describe('Rueckverfolgbarkeit UIX', () => {
  it('oeffnet Wiegescheine per 44-px-Tipp und zeigt Stufen ohne Hover-only', () => {
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Wiegeschein suchen')
    expect(src).toContain('aria-label={stages.map')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-red-50')
    expect(src).not.toContain('title={label}')
    expect(src).toContain('Wiegeschein wählen')
  })
})
