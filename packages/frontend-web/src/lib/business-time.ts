/**
 * Geschaeftstag in der Betriebszeitzone (Gegenstueck zu app/core/business_time.py).
 *
 * Ein Buchungs-, Liefer- oder Faelligkeitsdatum ist ein Kalendertag des Betriebs, kein UTC-Zeitpunkt.
 * Reine Datumswerte (YYYY-MM-DD) werden deshalb nie ueber `new Date()` gelesen (das waere UTC-Mitternacht und
 * kann einen Tag springen); Zeitpunkte werden in der Betriebszeitzone angezeigt.
 */
const DEFAULT_BUSINESS_TIMEZONE = 'Europe/Berlin'
const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/

function gueltigeZone(name: string | undefined): string {
  if (!name) return DEFAULT_BUSINESS_TIMEZONE
  try {
    new Intl.DateTimeFormat('de-DE', { timeZone: name })
    return name
  } catch {
    // Eine unbekannte Zeitzone darf keine Eingabe verhindern; der dokumentierte Standard ist verlaesslicher.
    return DEFAULT_BUSINESS_TIMEZONE
  }
}

export const BUSINESS_TIMEZONE = gueltigeZone(import.meta.env?.VITE_BUSINESS_TIMEZONE as string | undefined)

/** Geschaeftstag eines Zeitpunkts als YYYY-MM-DD. */
export function businessDateAt(instant: Date): string {
  const teile = new Intl.DateTimeFormat('en-CA', { timeZone: BUSINESS_TIMEZONE, year: 'numeric', month: '2-digit', day: '2-digit' })
    .formatToParts(instant)
  const wert = (typ: string) => teile.find((teil) => teil.type === typ)?.value ?? ''
  return `${wert('year')}-${wert('month')}-${wert('day')}`
}

export function businessToday(): string {
  return businessDateAt(new Date())
}

/** Kalendertag `days` Tage nach `from` (Vorgabe: heute). Rechnet auf dem Kalender, nicht in Stunden. */
export function businessDateAfter(days: number, from: string = businessToday()): string {
  const match = ISO_DATE.exec(from)
  if (!match) throw new Error(`Kein Kalendertag: ${from}`)
  const tag = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]) + days))
  return tag.toISOString().slice(0, 10)
}

/** Anzeige eines Kalendertags (TT.MM.JJJJ); ein Zeitpunkt zeigt seinen Geschaeftstag. */
export function formatBusinessDate(raw: string): string | null {
  const text = raw.trim()
  const tag = /^(\d{4})-(\d{2})-(\d{2})/.exec(text)
  if (tag && text.length === 10) return `${tag[3]}.${tag[2]}.${tag[1]}`
  const zeitpunkt = new Date(text)
  if (Number.isNaN(zeitpunkt.getTime())) return null
  const [jahr, monat, tagImMonat] = businessDateAt(zeitpunkt).split('-')
  return `${tagImMonat}.${monat}.${jahr}`
}

/** Anzeige eines Zeitpunkts in der Betriebszeitzone. */
export function formatBusinessDateTime(raw: string): string | null {
  const zeitpunkt = new Date(raw.trim())
  if (Number.isNaN(zeitpunkt.getTime())) return null
  return zeitpunkt.toLocaleString('de-DE', { timeZone: BUSINESS_TIMEZONE })
}
