/**
 * UIX-060 Abnahme-Fixture: 20 Kern-Intents treffen Maske+Filter exakt,
 * 5 Negativfälle ergeben none. Katalog = echter buildPaletteCommands-Ausgang
 * (agrarEnabled, ohne MaskRegistry — deterministisch).
 */
import { describe, expect, it } from 'vitest'
import { buildPaletteCommands } from '@/components/navigation/command-palette-model'
import {
  compileIntent,
  compileIntents,
  extractDateFilters,
  normalize,
} from '@/lib/omnibox/intent-compiler'

const CATALOG = buildPaletteCommands({
  agrarEnabled: true,
  navigationShortcuts: [],
  maskRegistry: undefined,
})

const TODAY = '2026-07-07' // Dienstag

function best(query: string) {
  const plan = compileIntent(query, CATALOG, { today: TODAY })
  if (plan.kind !== 'navigate') {
    throw new Error(`Kein Navigate-Plan für "${query}" (suggestions: ${plan.suggestions.join(', ')})`)
  }
  return plan
}

describe('normalize', () => {
  it('faltet Umlaute und Sonderzeichen', () => {
    expect(normalize('Überfällige Aufträge!')).toBe('ueberfaellige auftraege')
  })
})

describe('extractDateFilters', () => {
  it('überfällig → overdue=1', () => {
    const { filters } = extractDateFilters(['ueberfaellige', 'rechnungen'], TODAY)
    expect(filters).toEqual([{ key: 'overdue', label: 'überfällig', value: '1' }])
  })
  it('> 30 tage → due_lt heute−30', () => {
    const { filters } = extractDateFilters(['op', '>', '30', 'tage'], TODAY)
    expect(filters).toContainEqual({ key: 'due_lt', label: 'älter als 30 Tage', value: '2026-06-07' })
  })
  it('nächste woche → Mo–So-Fenster', () => {
    const { filters } = extractDateFilters(['naechste', 'woche'], TODAY)
    expect(filters).toContainEqual({ key: 'from', label: 'nächste Woche', value: '2026-07-13' })
    expect(filters).toContainEqual({ key: 'to', label: 'bis', value: '2026-07-19' })
  })
})

describe('Kern-Intents (20)', () => {
  it('1 offene posten debitoren', () => {
    expect(best('offene posten debitoren').command.id).toBe('nav-op-debitoren')
  })
  it('2 op kreditoren', () => {
    expect(best('op kreditoren').command.id).toBe('nav-op-kreditoren')
  })
  it('3 überfällige rechnungen → Rechnungen + overdue', () => {
    const plan = best('überfällige rechnungen')
    expect(plan.command.id).toBe('nav-rechnungen')
    expect(plan.routePath).toContain('overdue=1')
  })
  it('4 offene posten folkerts → OP + q-Filter', () => {
    const plan = best('offene posten debitoren folkerts')
    expect(plan.command.id).toBe('nav-op-debitoren')
    expect(plan.filters).toContainEqual({ key: 'q', label: 'folkerts', value: 'folkerts' })
    expect(plan.routePath).toContain('q=folkerts')
  })
  it('5 op > 30 tage → due_lt-Filter', () => {
    const plan = best('op debitoren > 30 tage')
    expect(plan.command.id).toBe('nav-op-debitoren')
    expect(plan.routePath).toContain('due_lt=2026-06-07')
  })
  it('6 mahnwesen', () => {
    expect(best('mahnvorschlag').command.id).toBe('nav-mahnwesen')
  })
  it('7 zahlungsläufe', () => {
    expect(best('zahlungslauf juli').command.id).toBe('nav-zahlungslaeufe')
  })
  it('8 neuer auftrag → Schnellaktion', () => {
    expect(best('neuer verkaufsauftrag').command.id).toBe('action-new-sales-order')
  })
  it('9 lieferscheine heute → date-Filter', () => {
    const plan = best('lieferscheine heute')
    expect(plan.command.id).toBe('nav-lieferscheine')
    expect(plan.routePath).toContain(`date=${TODAY}`)
  })
  it('10 bestellungen baywa → q-Filter', () => {
    const plan = best('bestellungen baywa')
    expect(plan.command.id).toBe('nav-bestellungen')
    expect(plan.filters).toContainEqual({ key: 'q', label: 'baywa', value: 'baywa' })
  })
  it('11 wareneingang', () => {
    expect(best('wareneingang annahme').command.id).toBe('nav-wareneingang')
  })
  it('12 lagerbestand weizen → q-Filter', () => {
    const plan = best('lagerbestand weizen')
    expect(plan.command.id).toBe('nav-lagerbestand')
    expect(plan.routePath).toContain('q=weizen')
  })
  it('13 inventur', () => {
    expect(best('inventur zählung').command.id).toBe('nav-inventur')
  })
  it('14 ernte annahme', () => {
    expect(best('ernte annahme').command.id).toBe('nav-ernte-annahme')
  })
  it('15 agrar kontrakte raps → Verträge + q', () => {
    const plan = best('agrar kontrakt raps')
    expect(plan.command.id).toBe('nav-agrar-vertraege')
    expect(plan.filters).toContainEqual({ key: 'q', label: 'raps', value: 'raps' })
  })
  it('16 silo status', () => {
    expect(best('silo status').command.id).toBe('nav-silos')
  })
  it('17 kunden crm', () => {
    expect(best('kunden stammdaten').command.id).toBe('nav-crm-kunden')
  })
  it('18 aktivitäten crm', () => {
    expect(best('crm aktivitäten').command.id).toBe('nav-crm-aktivitaeten')
  })
  it('19 tagesabschluss kasse', () => {
    expect(best('tagesabschluss kasse').command.id).toBe('nav-tagesabschluss')
  })
  it('20 ustva', () => {
    expect(best('ustva voranmeldung').command.id).toBe('nav-ustva')
  })
})

describe('Negativfälle (5) → none', () => {
  const cases = [
    'xyzzy quux',
    'blubberblase am strand',
    '🙂',
    'zeig mir bitte',            // nur Stopwords
    'qqqq wwww eeee',
  ]
  for (const q of cases) {
    it(`"${q}"`, () => {
      const plan = compileIntent(q, CATALOG, { today: TODAY })
      expect(plan.kind).toBe('none')
    })
  }
})

describe('compileIntents (Vorschau)', () => {
  it('liefert Top-3 mit bestem Plan an Index 0', () => {
    const plans = compileIntents('offene posten', CATALOG, { today: TODAY })
    expect(plans.length).toBeGreaterThanOrEqual(2)
    expect(plans.length).toBeLessThanOrEqual(3)
    expect(plans[0].confidence).toBeGreaterThanOrEqual(plans[1].confidence)
    expect(['nav-op-debitoren', 'nav-op-kreditoren']).toContain(plans[0].command.id)
  })
  it('mutiert nie — alle Pläne sind navigate', () => {
    for (const q of ['neuer verkaufsauftrag', 'buchung erfassen', 'zahlungslauf']) {
      for (const plan of compileIntents(q, CATALOG, { today: TODAY })) {
        expect(plan.kind).toBe('navigate')
      }
    }
  })
})
