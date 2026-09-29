import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/verkauf/kunden-stamm.tsx'),
  'utf8',
)

describe('Kundenstamm UIX (Außendienst)', () => {
  it('zeigt Register ohne Entwickler-Tabnummern', () => {
    expect(src).toContain('variant="register"')
    expect(src).toContain('aria-label="Kundenakte"')
    expect(src).toMatch(/TabsTrigger value="tab23"[^>]*>Anschriften</)
    expect(src).toMatch(/TabsTrigger value="tab24"[^>]*>Kontoauszug</)
    expect(src).toMatch(/TabsTrigger value="tab25"[^>]*>CPD-Konto</)
    expect(src).not.toMatch(/Tab 2[1-5]/)
  })

  it('haelt Speichern und Zeilenaktionen auf 44 px', () => {
    expect(src).toContain('min-h-touch min-w-[136px]')
    expect(src).not.toMatch(/size="sm"/)
    expect(src).toContain('deleteInstructionMutation.variables === row.id')
    expect(src).toContain('deleteContactMutation.variables === c.id')
  })
})
