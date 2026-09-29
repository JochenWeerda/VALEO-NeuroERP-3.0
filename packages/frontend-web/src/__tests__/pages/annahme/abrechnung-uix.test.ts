import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/annahme/abrechnung.tsx'),
  'utf8',
)

describe('Annahme-Abrechnung UIX (Buchhaltung/Waage)', () => {
  it('stellt Lieferdaten vor Theater, 44-px-Korrekturen und deutsche Operator-Copy', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('<Label htmlFor="supplierId">Lieferant</Label>')
    expect(src).toContain('Bestehende Abrechnungen')
    expect(src).toContain('settlementStatusLabel')
    expect(src).toContain('approvePendingId === s.id')
    expect(src).toContain('className="min-h-touch touch-manipulation"')
    expect(src).toContain('{createSettlement.isPending ? \'Speichere...\' : \'Speichern\'}')
    expect(src).not.toMatch(/size="sm"/)
    expect(src).not.toContain('Supplier ID')
    expect(src).not.toContain('Self-billing')
    expect(src).not.toContain('text-orange-700')
  })
})
