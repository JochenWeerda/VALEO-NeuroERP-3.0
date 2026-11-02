import type { ScreenTextFormat } from '../schema'

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
const TELEFON = /^\+?[0-9][0-9 ()/-]{4,}$/

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

/** Leer ist gueltig (Pflicht prueft die eigene Regel). */
export function validTextFormat(format: ScreenTextFormat, value: unknown): boolean {
  const text = String(value ?? '').trim()
  if (text === '') return true
  if (format === 'email') return EMAIL.test(text)
  if (format === 'phone') return TELEFON.test(text)
  return validIban(text)
}

export const FORMAT_MESSAGE: Record<ScreenTextFormat, string> = {
  email: 'bitte eine gültige E-Mail-Adresse eingeben.',
  phone: 'bitte eine gültige Telefonnummer eingeben.',
  iban: 'die IBAN ist ungültig (Prüfziffer).',
}

/** Anzeige: IBAN in Vierergruppen, sonst unveraendert. */
export function formatTextValue(format: ScreenTextFormat | undefined, value: string): string {
  if (format !== 'iban') return value
  return value.replace(/\s+/g, '').toUpperCase().replace(/(.{4})/g, '$1 ').trim()
}
