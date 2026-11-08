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
    render(<span>{formatCellValue(250, 'quantity', 'EUR', 'dt')}|{formatCellValue(12.5, 'percentage')}</span>)
    expect(screen.getByText('250 dt|12,5 %')).toBeInTheDocument()
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

describe('Wertetypen wie im Backend (config/wertetypen.json)', async () => {
  const { default: wertetypen } = await import('@/components/mask-builder/runtime/wertetypen.generated.json')
  const { validPeriod } = await import('@/components/mask-builder/runtime/text-format')
  for (const [format, faelle] of Object.entries(wertetypen.beispiele)) {
    it(`${format}: dieselben Beispiele wie app/core/wertetypen.py`, () => {
      const pruefe = (wert: string) => format === 'period' ? validPeriod(wert)
        : validTextFormat(format as Parameters<typeof validTextFormat>[0], wert)
      for (const wert of faelle.gueltig) expect(pruefe(wert), wert).toBe(true)
      for (const wert of faelle.ungueltig) expect(pruefe(wert), wert).toBe(false)
    })
  }
  it('zeigt Periode und Kennungen lesbar', async () => {
    const { formatPeriod } = await import('@/components/mask-builder/runtime/text-format')
    expect(formatPeriod('2026-11')).toBe('11/2026')
    expect(formatReadOnlyValue('period', '2026-11')).toBe('11/2026')
    expect(formatReadOnlyValue('text', 'de 123-456-789', 'EUR', undefined, 'vatId')).toBe('DE123456789')
  })
})

describe('Einheiten wie agrar_units (Landhandel: Masse in dt)', async () => {
  const { convertQuantity, normalizeUnit, sumQuantities, unitKind } = await import('@/components/mask-builder/runtime/units')
  it('rechnet Masse und Volumen exakt, Zaehleinheiten nie', () => {
    expect(convertQuantity(25000, 'kg', 'dt')).toBe(250)
    expect(convertQuantity(3, 'to', 'dt')).toBe(30)
    expect(convertQuantity(2, 'Doppelzentner', 'kg')).toBe(200)
    expect(convertQuantity(5, 'hl', 'l')).toBe(500)
    expect(convertQuantity(4, 'Sack', 'kg')).toBeNull()
    expect(convertQuantity(1, 'kg', 'l')).toBeNull()
    expect(normalizeUnit('BigBag:500')).toBe('big_bag:500')
    expect(unitKind('Big Bag')).toBe('andere')
  })
  it('summiert gemischte Masse in dt und verweigert Sack plus kg', () => {
    expect(sumQuantities([{ wert: 2500, einheit: 'kg' }, { wert: 3, einheit: 't' }, { wert: 10, einheit: 'dt' }])).toEqual({ wert: 65, einheit: 'dt' })
    expect(sumQuantities([{ wert: 2, einheit: 'kg' }, { wert: 3, einheit: 'kg' }])).toEqual({ wert: 5, einheit: 'kg' })
    expect(sumQuantities([{ wert: 2, einheit: 'kg' }, { wert: 3, einheit: 'Sack' }])).toBeNull()
    expect(sumQuantities([{ wert: 25000, einheit: 'kg' }], 'dt')).toEqual({ wert: 250, einheit: 'dt' })
  })
  it('laesst eine Anzeigeeinheit nur an Mengenspalten mit Masse/Volumen zu', () => {
    const tabelle = (spalte: object) => ({ ...basis, mode: 'list' as const, tables: [{ key: 't', label: 'T', columns: [spalte] }] }) as ScreenDefinition
    expect(validateScreenDefinition(tabelle({ key: 'm', label: 'Menge', renderKind: 'quantity', unit: 'kg', displayUnit: 'dt' }))).not.toContain('displayUnit is invalid')
    expect(validateScreenDefinition(tabelle({ key: 'm', label: 'Menge', renderKind: 'quantity', displayUnit: 'Sack' }))).toContain('displayUnit is invalid')
    expect(validateScreenDefinition(tabelle({ key: 'm', label: 'Menge', renderKind: 'number', displayUnit: 'dt' }))).toContain('displayUnit is invalid')
  })
})

describe('Preis je Einheit (Landhandel: je dt / 100 kg)', async () => {
  const { convertUnitPrice } = await import('@/components/mask-builder/runtime/units')
  it('rechnet Preise exakt und umgekehrt zur Menge', () => {
    expect(convertUnitPrice(500, 't', 'dt')).toBe(50)
    expect(convertUnitPrice(25, 'dt', 'kg')).toBe(0.25)
    expect(convertUnitPrice(8, 'l', 'hl')).toBe(800)
    expect(convertUnitPrice(12, 'sack', 'kg')).toBeNull()
  })
  it('laesst die Preisbezugseinheit nur an Betragsspalten mit Masse/Volumen zu', () => {
    const tabelle = (spalte: object) => ({ ...basis, mode: 'list' as const, tables: [{ key: 't', label: 'T', columns: [spalte] }] }) as ScreenDefinition
    expect(validateScreenDefinition(tabelle({ key: 'p', label: 'Preis je dt', renderKind: 'currency', pricePer: 't', displayPricePer: 'dt' }))).not.toContain('pricePer is invalid')
    expect(validateScreenDefinition(tabelle({ key: 'p', label: 'Preis', renderKind: 'currency', pricePer: 'sack', displayPricePer: 'kg' }))).toContain('pricePer is invalid')
    expect(validateScreenDefinition(tabelle({ key: 'p', label: 'Preis', renderKind: 'currency', pricePer: 't', displayPricePer: 'l' }))).toContain('pricePer is invalid')
  })
})
