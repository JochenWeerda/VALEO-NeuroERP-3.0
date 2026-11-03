import wertetypen from './wertetypen.generated.json'

/**
 * Einheiten wie app/core/agrar_units.py (erzeugte Kopie): Masse und Volumen sind exakt umrechenbar, Zaehleinheiten
 * (Sack, Big Bag, Einheit ...) nie global - ein Sack Duenger ist nicht ein Sack Saatgut. Im Landhandel ist die
 * Handelsgroesse fuer Masse dt (100 kg); t ist die Ausnahme.
 */
const { masseInKg, volumenInL, aliase, anzeigeMasse, anzeigeVolumen } = wertetypen.einheiten
const MASSE: Record<string, number> = masseInKg
const VOLUMEN: Record<string, number> = volumenInL
const ALIASE: Record<string, string> = aliase

export type UnitKind = 'masse' | 'volumen' | 'andere'

/** Schreibweise vereinheitlichen wie agrar_units.normalisiere (Auspraegung hinter ':' bleibt). */
export function normalizeUnit(einheit: string | null | undefined): string {
  const roh = String(einheit ?? '').trim().toLowerCase().replace(/ /g, '_').replace(/-/g, '_')
  const [kopf, ...rest] = roh.split(':')
  const norm = ALIASE[kopf] ?? kopf
  return rest.length ? `${norm}:${rest.join(':')}` : norm
}

export function unitKind(einheit: string | null | undefined): UnitKind {
  const norm = normalizeUnit(einheit)
  if (norm in MASSE) return 'masse'
  if (norm in VOLUMEN) return 'volumen'
  return 'andere'
}

export function isConvertibleUnit(einheit: string | null | undefined): boolean {
  return unitKind(einheit) !== 'andere'
}

/** Wert von `von` nach `nach`, oder null, wenn die Einheiten nicht exakt umrechenbar sind. */
export function convertQuantity(wert: number, von: string | null | undefined, nach: string | null | undefined): number | null {
  const a = normalizeUnit(von)
  const b = normalizeUnit(nach)
  if (a === b) return wert
  const art = unitKind(a)
  if (art === 'andere' || art !== unitKind(b)) return null
  const tabelle = art === 'masse' ? MASSE : VOLUMEN
  return (wert * tabelle[a]) / tabelle[b]
}

/**
 * Preis je `von` als Preis je `nach` (z. B. 500 EUR je t -> 50 EUR je dt). null, wenn nicht exakt umrechenbar.
 * Ein Preis verhaelt sich umgekehrt zur Menge: je groesser die Bezugseinheit, desto hoeher der Preis.
 */
export function convertUnitPrice(preis: number, von: string | null | undefined, nach: string | null | undefined): number | null {
  const anteil = convertQuantity(1, nach, von)
  return anteil === null ? null : preis * anteil
}

/**
 * Summe ueber Zeilen mit eigener Einheit. Einheitlich: in dieser Einheit. Gemischt, aber alle Masse bzw. Volumen:
 * umgerechnet in die Zieleinheit (Vorgabe dt bzw. l). Sonst null - eine Summe ueber Sack und kg gibt es nicht.
 */
export function sumQuantities(
  zeilen: Array<{ wert: number | null; einheit: string | null | undefined }>,
  ziel?: string,
): { wert: number; einheit: string } | null {
  const mit = zeilen.filter((z): z is { wert: number; einheit: string | null | undefined } => z.wert !== null)
  const einheiten = new Set(mit.map((z) => normalizeUnit(z.einheit)))
  let zielEinheit = ziel ? normalizeUnit(ziel) : undefined
  if (!zielEinheit) {
    if (einheiten.size <= 1) zielEinheit = [...einheiten][0] ?? ''
    else {
      const arten = new Set([...einheiten].map((e) => unitKind(e)))
      if (arten.size !== 1 || arten.has('andere')) return null
      zielEinheit = arten.has('masse') ? anzeigeMasse : anzeigeVolumen
    }
  }
  let summe = 0
  for (const zeile of mit) {
    const umgerechnet = convertQuantity(zeile.wert, zeile.einheit, zielEinheit)
    if (umgerechnet === null) return null
    summe += umgerechnet
  }
  return { wert: Math.round((summe + Number.EPSILON) * 1000) / 1000, einheit: zielEinheit }
}
