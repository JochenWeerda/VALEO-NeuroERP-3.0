export interface DispositionsTour {
  datum: string | null
  status: string
  fahrzeug: string | null
  fahrer: string | null
}

export interface Dispositionsstand {
  status: 'disponierbar' | 'offen' | 'keine' | 'gesperrt'
  label: string
  naechste: string
  tone: 'success' | 'warning' | 'danger'
}

function heuteIso(bezug: Date = new Date()): string {
  return bezug.toISOString().slice(0, 10)
}

function istHeute(datum: string | null, bezug: Date): boolean {
  return Boolean(datum && datum.slice(0, 10) === heuteIso(bezug))
}

function ohneBesetzung(tour: DispositionsTour): boolean {
  const fahrzeug = (tour.fahrzeug ?? '').trim()
  const fahrer = (tour.fahrer ?? '').trim()
  return fahrzeug.length === 0 || fahrer.length === 0 || fahrer === '—'
}

/** Grün nur bei heutiger Tour, ohne Chargensperre und mit Fahrzeug plus Fahrer auf jeder geplanten Tour. */
export function dispositionsstand(
  touren: DispositionsTour[],
  chargeGesperrt: boolean,
  bezug: Date = new Date(),
): Dispositionsstand {
  const heute = touren.filter((tour) => istHeute(tour.datum, bezug) && tour.status !== 'storniert')
  if (chargeGesperrt) {
    return {
      status: 'gesperrt',
      label: 'Disposition offen',
      naechste: 'Gesperrte Charge klären.',
      tone: 'danger',
    }
  }
  if (heute.length === 0) {
    return {
      status: 'keine',
      label: 'Keine Tour',
      naechste: 'Lieferschein auflösen und die Tour anlegen.',
      tone: 'warning',
    }
  }
  if (heute.some((tour) => tour.status === 'geplant' && ohneBesetzung(tour))) {
    return {
      status: 'offen',
      label: 'Disposition offen',
      naechste: 'Fahrzeug und Fahrer zuordnen.',
      tone: 'warning',
    }
  }
  return {
    status: 'disponierbar',
    label: 'Disponierbar',
    naechste: 'Beladung starten.',
    tone: 'success',
  }
}

/** Heutige, nicht stornierte Touren dieses Fahrers. Das gespeicherte Zählfeld bleibt unberührt. */
export function tourenHeuteFuerFahrer(
  touren: Array<{ datum: string | null; status: string; fahrer: string | null }>,
  fahrerId: string,
  bezug: Date = new Date(),
): number {
  return touren.filter((tour) => (
    tour.fahrer === fahrerId
    && tour.status !== 'storniert'
    && istHeute(tour.datum, bezug)
  )).length
}
