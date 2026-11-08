/**
 * Uebersetzt die Ablehnung „Insufficient role. Required: ('FINANCE_LESEN', …)“ in einen Satz,
 * mit dem ein Mensch etwas anfangen kann.
 *
 * Seit Oktober 2026 pruefen rund 360 Finanzwege die Rolle. Ohne diese Uebersetzung zeigte fast jede
 * Maske den englischen Satz, „Fehler beim Laden“ oder eine leere Liste — und niemand erfuhr, dass
 * nur eine Rolle fehlt.
 *
 * Die Rollennamen bleiben woertlich: Wer die Rolle vergibt, braucht genau diesen Namen. `admin` und
 * `manager` werden nicht genannt — sie sind keine Rollen, um die man fuer eine Fachaufgabe bittet.
 */
const ALLGEMEIN = new Set(['admin', 'manager', 'user'])

export function rollenHinweis(detail: unknown): string | null {
  if (typeof detail !== 'string' || !detail.startsWith('Insufficient role')) return null
  const rollen = Array.from(detail.matchAll(/'([A-Za-z0-9_:.-]+)'/g), (treffer) => treffer[1])
    .filter((rolle) => !ALLGEMEIN.has(rolle))
  const eindeutig = Array.from(new Set(rollen))
  if (eindeutig.length === 0) {
    return 'Dafür fehlt Ihnen die Berechtigung. Bitte wenden Sie sich an Ihre Administration.'
  }
  const nennung = eindeutig.length === 1 ? `die Rolle ${eindeutig[0]}` : `eine dieser Rollen: ${eindeutig.join(', ')}`
  return `Dafür fehlt Ihnen die Berechtigung. Nötig ist ${nennung}. Bitte wenden Sie sich an Ihre Administration.`
}
