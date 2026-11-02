import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { computeValue, sumColumn, validComputation } from '@/components/mask-builder/runtime/computed-fields'
import { formatTextValue, validIban, validTextFormat } from '@/components/mask-builder/runtime/text-format'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'
import { formatCellValue } from '@/components/mask-builder/renderers/FastTableRenderer'
import { formatReadOnlyValue } from '@/components/mask-builder/renderers/FieldRenderer'

const basis: ScreenDefinition = { schemaVersion: 1, id: 'test/feldklassen', title: 'Feldklassen', mode: 'detail', domain: 'sales' }

describe('rechnende Felder', () => {
  it('rechnet die fuenf Operationen und rundet', () => {
    const werte: Record<string, unknown> = { menge: '2,5', preis: 4, netto: 100, steuer: 19 }
    const lies = (key: string) => werte[key]
    expect(computeValue({ op: 'product', of: ['menge', 'preis'] }, lies)).toBe(10)
    expect(computeValue({ op: 'sum', of: ['netto', 'steuer'] }, lies)).toBe(119)
    expect(computeValue({ op: 'difference', of: ['netto', 'steuer'] }, lies)).toBe(81)
    expect(computeValue({ op: 'ratio', of: ['netto', 'menge'] }, lies)).toBe(40)
    expect(computeValue({ op: 'percentOf', of: ['steuer', 'netto'], round: 1 }, lies)).toBe(19)
  })
  it('liefert null statt einer falschen Zahl', () => {
    expect(computeValue({ op: 'product', of: ['a', 'b'] }, (k) => ({ a: 2, b: '' } as Record<string, unknown>)[k])).toBeNull()
    expect(computeValue({ op: 'ratio', of: ['a', 'b'] }, (k) => ({ a: 2, b: 0 } as Record<string, unknown>)[k])).toBeNull()
  })
  it('laesst nur deklarierte Operationen zu', () => {
    expect(validComputation({ op: 'product', of: ['a', 'b'] })).toBe(true)
    for (const falsch of [{ op: 'eval', of: ['a', 'b'] }, { op: 'difference', of: ['a', 'b', 'c'] }, { op: 'sum', of: ['a'] },
      { op: 'sum', of: ['a', 'a'] }, { op: 'sum', of: ['a', 'b'], round: 9 }, { op: 'sum', of: ['a', 'b'], expr: 'x' }]) {
      expect(validComputation(falsch)).toBe(false)
    }
  })
  it('prueft Operanden und Feldtyp im Vertrag', () => {
    const ok = { ...basis, fields: [{ key: 'menge', label: 'Menge', type: 'quantity' as const, unit: 'kg' },
      { key: 'preis', label: 'Preis', type: 'currency' as const },
      { key: 'betrag', label: 'Betrag', type: 'currency' as const, computed: { op: 'product' as const, of: ['menge', 'preis'] } }] }
    expect(validateScreenDefinition(ok)).not.toContain('computed is invalid')
    const fehlt = { ...ok, fields: [...ok.fields.slice(0, 2), { ...ok.fields[2], computed: { op: 'product' as const, of: ['menge', 'rabatt'] } }] }
    expect(validateScreenDefinition(fehlt)).toContain('computed is invalid')
    const text = { ...ok, fields: [...ok.fields.slice(0, 2), { ...ok.fields[2], type: 'text' as const }] }
    expect(validateScreenDefinition(text)).toContain('computed is invalid')
  })
  it('erlaubt die Summenzeile nur an Zahlenspalten', () => {
    const tabelle = (spalte: object) => ({ ...basis, mode: 'list' as const, tables: [{ key: 't', label: 'T', columns: [spalte] }] })
    expect(validateScreenDefinition(tabelle({ key: 'betrag', label: 'Betrag', renderKind: 'currency', aggregate: 'sum' }) as ScreenDefinition))
      .not.toContain('aggregate is invalid')
    expect(validateScreenDefinition(tabelle({ key: 'name', label: 'Name', aggregate: 'sum' }) as ScreenDefinition)).toContain('aggregate is invalid')
    expect(sumColumn([{ b: '1,5' }, { b: 2 }, { b: 'x' }], (r) => r.b)).toBe(3.5)
  })
})

describe('Spezialfelder', () => {
  it('zeigt Mengen mit Einheit und Prozent', () => {
    expect(formatReadOnlyValue('quantity', 1250.5, 'EUR', 'kg')).toBe('1.250,5 kg')
    render(<span>{formatCellValue(25000, 'quantity', 'EUR', 't')}|{formatCellValue(12.5, 'percentage')}</span>)
    expect(screen.getByText('25.000 t|12,5 %')).toBeInTheDocument()
  })
  it('prueft IBAN, E-Mail und Telefon', () => {
    expect(validIban('DE89 3704 0044 0532 0130 00')).toBe(true)
    expect(validIban('DE89 3704 0044 0532 0130 01')).toBe(false)
    expect(validTextFormat('email', 'dispo@haus.example')).toBe(true)
    expect(validTextFormat('email', 'dispo@haus')).toBe(false)
    expect(validTextFormat('phone', '+49 4941 123-45')).toBe(true)
    expect(validTextFormat('phone', 'abc')).toBe(false)
    expect(validTextFormat('iban', '')).toBe(true)
    expect(formatTextValue('iban', 'de89370400440532013000')).toBe('DE89 3704 0044 0532 0130 00')
  })
})

describe('Geschaeftstag', () => {
  it('nimmt den Kalendertag des Betriebs, nicht den UTC-Tag', async () => {
    const { businessDateAt, businessDateAfter, formatBusinessDate } = await import('@/lib/business-time')
    // 31.10. 23:30 UTC ist in Berlin (MEZ) schon der 01.11. - eine Buchung gehoert in die Novemberperiode.
    expect(businessDateAt(new Date('2026-10-31T23:30:00Z'))).toBe('2026-11-01')
    expect(businessDateAfter(30, '2026-01-31')).toBe('2026-03-02')
    expect(formatBusinessDate('2026-11-02')).toBe('02.11.2026')
    expect(formatCellValue('2026-03-29', 'date')).toBe('29.03.2026')
  })
})
