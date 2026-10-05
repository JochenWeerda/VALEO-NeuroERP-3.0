import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/qualitaet/labor-auftrag.tsx'),
  'utf8',
)

describe('Labor-Auftrag UIX', () => {
  it('haelt Wizard-Felder und Auswahl auf 44 px mit Pending-Guard', () => {
    expect(src).toContain('min-h-touch')
    expect(src).toContain('className="h-11 w-11"')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('loading={createMutation.isPending}')
    expect(src).toContain('if (createMutation.isPending) return')
    expect(src).not.toContain('h-4 w-4')
    expect(src).not.toContain('-- Wählen --')
  })
})
