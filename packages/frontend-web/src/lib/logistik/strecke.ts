/** Dieselbe Regel wie ``app/domains/logistik/strecke.py``. */

export type Punkt = [number, number]

function punkt(wert: Punkt | null | undefined): Punkt | null {
  if (!wert || wert.length !== 2) return null
  const [lat, lng] = wert
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null
  if (Math.abs(lat) > 90 || Math.abs(lng) > 180) return null
  return [lat, lng]
}

/** Nur Status A ist ein gültiger Fix. Webfleet liefert Mikrogramm. */
export function webfleetPunkt(
  latMikro: number | null,
  lngMikro: number | null,
  status: string | null,
): Punkt | null {
  if (status !== 'A' || latMikro === null || lngMikro === null) return null
  return punkt([latMikro / 1_000_000, lngMikro / 1_000_000])
}

export function fahrtposition(webfleet: Punkt | null, zielort: Punkt | null): Punkt | null {
  return punkt(webfleet) ?? punkt(zielort)
}

function luftlinieKm(a: Punkt, b: Punkt): number {
  const erde = 6371
  const [lat1, lng1] = a
  const [lat2, lng2] = b
  const phi1 = (lat1 * Math.PI) / 180
  const phi2 = (lat2 * Math.PI) / 180
  const dphi = ((lat2 - lat1) * Math.PI) / 180
  const dlng = ((lng2 - lng1) * Math.PI) / 180
  const h = Math.sin(dphi / 2) ** 2 + Math.cos(phi1) * Math.cos(phi2) * Math.sin(dlng / 2) ** 2
  return erde * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h))
}

export function streckeKm(punkte: Punkt[]): number | null {
  const gueltig = punkte.map((p) => punkt(p)).filter((p): p is Punkt => p !== null)
  if (gueltig.length < 2) return null
  let summe = 0
  for (let i = 1; i < gueltig.length; i += 1) {
    summe += luftlinieKm(gueltig[i - 1], gueltig[i])
  }
  return Math.round(summe * 10) / 10
}

export function streckeText(km: number | null): string {
  return km === null ? 'ohne Strecke' : `${km} km`
}
