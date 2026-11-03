import type { ScreenComputation } from '../schema'
import { convertUnitPrice, isConvertibleUnit } from './units'

/**
 * Rechnende Felder und Spalten: eine feste Liste von Operationen, kein auswertbarer Ausdruck.
 * Das Ergebnis ist eine Vorschau in der Maske; verbindlich rechnet der Server (Belege, Steuer, Buchung).
 */
export const COMPUTATION_OPS = ['sum', 'product', 'difference', 'ratio', 'percentOf'] as const

const ZWEI_OPERANDEN = new Set(['difference', 'ratio', 'percentOf'])

export function validComputation(value: unknown): value is ScreenComputation {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false
  const item = value as Record<string, unknown>
  if (Object.keys(item).some(key => !['op', 'of', 'round'].includes(key))) return false
  if (!COMPUTATION_OPS.includes(item.op as (typeof COMPUTATION_OPS)[number])) return false
  if (!Array.isArray(item.of) || item.of.length === 0 || item.of.some(key => typeof key !== 'string' || !key)) return false
  if (new Set(item.of).size !== item.of.length) return false
  if (ZWEI_OPERANDEN.has(String(item.op)) ? item.of.length !== 2 : item.of.length < 2) return false
  return item.round === undefined || (Number.isInteger(item.round) && Number(item.round) >= 0 && Number(item.round) <= 6)
}

/** Zahl aus Eingabe oder Daten; deutsches Komma erlaubt. Leer oder unlesbar ergibt null. */
function zahl(raw: unknown): number | null {
  if (typeof raw === 'number') return Number.isFinite(raw) ? raw : null
  if (typeof raw !== 'string' || raw.trim() === '') return null
  const text = raw.trim().includes(',') ? raw.trim().replace(/\./g, '').replace(',', '.') : raw.trim()
  const value = Number(text)
  return Number.isFinite(value) ? value : null
}

/** Ergebnis der Operation oder null, wenn ein Operand fehlt oder durch null geteilt wuerde. */
export function computeValue(computation: ScreenComputation, read: (_key: string) => unknown): number | null {
  const werte = computation.of.map(key => zahl(read(key)))
  if (werte.some(wert => wert === null)) return null
  const [a, b] = werte as number[]
  let ergebnis: number
  switch (computation.op) {
    case 'sum': ergebnis = (werte as number[]).reduce((s, w) => s + w, 0); break
    case 'product': ergebnis = (werte as number[]).reduce((s, w) => s * w, 1); break
    case 'difference': ergebnis = a - b; break
    case 'ratio': if (b === 0) return null; ergebnis = a / b; break
    case 'percentOf': if (b === 0) return null; ergebnis = (a / b) * 100; break
    default: return null
  }
  const stellen = computation.round ?? 2
  const faktor = 10 ** stellen
  return Math.round((ergebnis + Number.EPSILON) * faktor) / faktor
}

/** Spaltensumme fuer die Summenzeile; Zeilen ohne lesbare Zahl zaehlen nicht mit. */
export function sumColumn(rows: Record<string, unknown>[], read: (_row: Record<string, unknown>) => unknown): number {
  const summe = rows.reduce((s, row) => s + (zahl(read(row)) ?? 0), 0)
  return Math.round((summe + Number.EPSILON) * 100) / 100
}

type Feld = { key?: unknown; type?: unknown; computed?: unknown; rowFields?: unknown }
type Spalte = { key?: unknown; computed?: unknown; aggregate?: unknown; renderKind?: unknown; numeric?: unknown; displayUnit?: unknown; pricePer?: unknown; displayPricePer?: unknown }
const ZAHLENFELDER = new Set(['number', 'currency', 'percentage', 'quantity'])
const ZAHLENSPALTEN = new Set(['number', 'currency', 'quantity', 'percentage'])

function feldFehler(felder: Feld[], fehler: Set<string>): void {
  const schluessel = new Set(felder.map(f => String(f.key)))
  for (const feld of felder) {
    if (feld.computed !== undefined) {
      const ok = validComputation(feld.computed) && ZAHLENFELDER.has(String(feld.type))
        && feld.computed.of.every(key => key !== feld.key && schluessel.has(key))
      if (!ok) fehler.add('computed is invalid')
    }
    if (Array.isArray(feld.rowFields)) feldFehler(feld.rowFields as Feld[], fehler)
  }
}

/** Fehler rechnender Felder/Spalten und Summenzeilen fuer validateScreenDefinition. */
export function computedDefinitionErrors(screen: {
  fields?: Feld[]
  tabs?: Array<{ fields?: Feld[]; tables?: Array<{ columns?: Spalte[] }> }>
  tables?: Array<{ columns?: Spalte[] }>
}): string[] {
  const fehler = new Set<string>()
  feldFehler([...(screen.fields ?? []), ...(screen.tabs ?? []).flatMap(tab => tab.fields ?? [])], fehler)
  const tabellen = [...(screen.tables ?? []), ...(screen.tabs ?? []).flatMap(tab => tab.tables ?? [])]
  for (const spalte of tabellen.flatMap(tabelle => tabelle.columns ?? [])) {
    if (spalte.computed !== undefined && !(validComputation(spalte.computed) && !spalte.computed.of.includes(String(spalte.key)))) {
      fehler.add('computed is invalid')
    }
    if (spalte.displayUnit !== undefined && !(spalte.renderKind === 'quantity' && isConvertibleUnit(String(spalte.displayUnit)))) {
      fehler.add('displayUnit is invalid')
    }
    if ((spalte.pricePer !== undefined || spalte.displayPricePer !== undefined) && !(spalte.renderKind === 'currency'
      && convertUnitPrice(1, String(spalte.pricePer ?? ''), String(spalte.displayPricePer ?? '')) !== null
      && isConvertibleUnit(String(spalte.pricePer)))) {
      fehler.add('pricePer is invalid')
    }
    if (spalte.aggregate !== undefined && !(spalte.aggregate === 'sum'
      && (spalte.numeric === true || spalte.computed !== undefined || ZAHLENSPALTEN.has(String(spalte.renderKind))))) {
      fehler.add('aggregate is invalid')
    }
  }
  return [...fehler]
}
