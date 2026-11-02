import type { ScreenTextFormat } from '../schema'
import wertetypen from './wertetypen.generated.json'

/** Pruefregeln der Wertetypen; Muster und Beispiele aus config/wertetypen.json (wie app/core/wertetypen.py). */
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
const TELEFON = /^\+?[0-9][0-9 ()/-]{4,}$/
const UST_ID_MUSTER: Record<string, RegExp> = Object.fromEntries(
  Object.entries(wertetypen.ustIdMuster).map(([land, muster]) => [land, new RegExp(muster)]),
)

/** IBAN nach ISO 13616: Laenderkennung, Pruefziffer, Mod-97 = 1. Leerzeichen sind erlaubt. */
export function validIban(raw: string): boolean {
  const iban = raw.replace(/\s+/g, '').toUpperCase()
  if (!/^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$/.test(iban)) return false
  const umgestellt = `${iban.slice(4)}${iban.slice(0, 4)}`
  let rest = 0
  for (const zeichen of umgestellt) {
    const ziffern = /[A-Z]/.test(zeichen) ? String(zeichen.charCodeAt(0) - 55) : zeichen
    for (const ziffer of ziffern) rest = (rest * 10 + Number(ziffer)) % 97
  }
  return rest === 1
}

/** GS1-Mod-10 (GLN, GTIN, SSCC): Gewicht 3 ab der Stelle vor der Pruefziffer. */
export function gs1CheckDigit(ziffern: string): number {
  const summe = [...ziffern].reverse().reduce((s, z, i) => s + Number(z) * (i % 2 === 0 ? 3 : 1), 0)
  return (10 - (summe % 10)) % 10
}

function gs1(laengen: number[]): (_wert: string) => boolean {
  return (wert) => /^\d+$/.test(wert) && laengen.includes(wert.length) && gs1CheckDigit(wert.slice(0, -1)) === Number(wert.slice(-1))
}

export function validVatId(raw: string): boolean {
  const wert = raw.replace(/[\s-]/g, '').toUpperCase()
  return UST_ID_MUSTER[wert.slice(0, 2)]?.test(wert) ?? false
}

function validMonthDay(wert: string): boolean {
  const treffer = /^(\d{2})-(\d{2})$/.exec(wert)
  if (!treffer) return false
  const monat = Number(treffer[1])
  const tag = Number(treffer[2])
  // Schaltjahr als Bezug: der 29.02. ist ein zulaessiger Stichtag.
  return monat >= 1 && monat <= 12 && tag >= 1 && tag <= new Date(Date.UTC(2024, monat, 0)).getUTCDate()
}

/** Buchungs-/Meldeperiode JJJJ-MM. */
export function validPeriod(raw: unknown): boolean {
  const text = String(raw ?? '').trim()
  if (text === '') return true
  const monat = Number(/^(\d{4})-(\d{2})$/.exec(text)?.[2] ?? 0)
  return monat >= 1 && monat <= 12
}

const PRUEFUNG: Record<ScreenTextFormat, (_wert: string) => boolean> = {
  email: (w) => EMAIL.test(w),
  phone: (w) => TELEFON.test(w),
  iban: validIban,
  vatId: validVatId,
  gln: gs1([13]),
  gtin: gs1([8, 12, 13, 14]),
  sscc: gs1([18]),
  hsCode: (w) => /^\d{8}$/.test(w),
  currencyCode: (w) => /^[A-Z]{3}$/.test(w),
  monthDay: validMonthDay,
}

/** Leer ist gueltig (Pflicht prueft die eigene Regel). */
export function validTextFormat(format: ScreenTextFormat, value: unknown): boolean {
  const text = String(value ?? '').trim()
  return text === '' || PRUEFUNG[format](text)
}

export const FORMAT_MESSAGE: Record<ScreenTextFormat, string> = {
  email: 'bitte eine gültige E-Mail-Adresse eingeben.',
  phone: 'bitte eine gültige Telefonnummer eingeben.',
  iban: 'die IBAN ist ungültig (Prüfziffer).',
  vatId: 'die USt-IdNr. hat kein gültiges Format (z. B. DE123456789).',
  gln: 'die GLN braucht 13 Ziffern mit gültiger Prüfziffer.',
  gtin: 'die GTIN/EAN braucht 8, 12, 13 oder 14 Ziffern mit gültiger Prüfziffer.',
  sscc: 'die SSCC braucht 18 Ziffern mit gültiger Prüfziffer.',
  hsCode: 'die Warennummer (HS-Code) hat genau 8 Ziffern.',
  currencyCode: 'bitte einen Währungscode nach ISO 4217 eingeben (z. B. EUR).',
  monthDay: 'bitte einen Stichtag als MM-TT eingeben (z. B. 07-01).',
}

/** Anzeige: IBAN in Vierergruppen, USt-IdNr. ohne Trenner, sonst unveraendert. */
export function formatTextValue(format: ScreenTextFormat | undefined, value: string): string {
  if (format === 'iban') return value.replace(/\s+/g, '').toUpperCase().replace(/(.{4})/g, '$1 ').trim()
  if (format === 'vatId') return value.replace(/[\s-]/g, '').toUpperCase()
  return value
}

/** Anzeige einer Periode als MM/JJJJ. */
export function formatPeriod(raw: string): string {
  const treffer = /^(\d{4})-(\d{2})$/.exec(raw.trim())
  return treffer ? `${treffer[2]}/${treffer[1]}` : raw
}
