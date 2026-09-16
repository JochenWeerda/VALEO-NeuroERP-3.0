import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { Link } from '@/app/routing/typed-router'
import { cn } from '@/lib/utils'
import { formatMenge, type InvoiceLineOrigin } from '@/lib/api/sales-invoices'

/**
 * FSX-RECHNUNGSMASKE — die Herkunft einer berechneten Menge.
 *
 * `PositionAllocationState` liest die Zuordnung vom Lieferschein nach vorn
 * ("100 dt geliefert, 60 dt berechnet"). Dieser Baustein liest **dieselbe**
 * Zuordnung von der Rechnung aus rueckwaerts: Woher kommen die 60 dt, die hier
 * in Rechnung stehen?
 *
 * Drei Aussagen, die sich unterscheiden muessen:
 *
 * - **Belegt.** Die Summe der Herkunftsmengen deckt die berechnete Menge.
 * - **Teilweise belegt.** Sie deckt sie nicht — dann steht die Luecke als Zahl
 *   da. Eine Rechnungsposition, deren Menge nur teilweise aus Zuordnungen
 *   stammt, ist der Fall, den niemand von selbst bemerkt.
 * - **Ohne Herkunft.** Gar keine Zuordnung. Das ist kein Ladezustand, sondern
 *   eine Auskunft: Die Position ist entstanden, ohne dass eine Quelle dafuer
 *   verbraucht wurde.
 *
 * Die Quelle ist verlinkt, soweit es fuer ihre Belegart eine Maske gibt —
 * deshalb setzt der Baustein den Router voraus. Nachgeladen wird **nichts**:
 * Die Herkunft kommt mit dem Beleg in derselben Abfrage; eine Rechnung ueber
 * zwanzig Positionen soll nicht zwanzig Aufrufe ausloesen.
 */

/**
 * Belegarten, deren Bezeichnung wir kennen. Ein unbekannter Schluessel wird
 * **nicht** verschwiegen: Lieber "Beleg (weighing_ticket)" als eine Zeile, die
 * so tut, als gaebe es keine Quelle.
 */
const BELEGART: Record<string, string> = {
  delivery_note: 'Lieferschein',
  sales_order: 'Auftrag',
  purchase_order: 'Bestellung',
  weighing_ticket: 'Wiegeschein',
  contract: 'Kontrakt',
}

function belegartLabel(typ: string): string {
  return BELEGART[typ] ?? `Beleg (${typ})`
}

/** Zielmaske einer Quelle, soweit es eine gibt. */
function belegPfad(typ: string, id: string): string | null {
  if (typ === 'delivery_note') return `/sales/delivery-note/${encodeURIComponent(id)}`
  return null
}

/** Summe der Herkunftsmengen — nur, wenn alle dieselbe Einheit tragen. */
function summeInEinheit(
  origins: InvoiceLineOrigin[],
  einheit: string,
): number | null {
  let summe = 0
  for (const herkunft of origins) {
    if (herkunft.unit !== einheit) return null
    const zahl = Number(herkunft.quantity)
    if (!Number.isFinite(zahl)) return null
    summe += zahl
  }
  return summe
}

export type OriginCoverage =
  | { art: 'ohne' }
  | { art: 'belegt'; quellen: number }
  | { art: 'teilweise'; quellen: number; fehlend: string }
  | { art: 'unvergleichbar'; quellen: number }

/**
 * Deckung der berechneten Menge durch ihre Quellen.
 *
 * `unvergleichbar` ist kein Fehler: Quellen in verschiedenen Einheiten lassen
 * sich hier nicht addieren, und eine geratene Umrechnung waere schlimmer als
 * die offene Auskunft.
 */
export function bewerteHerkunft(
  menge: string,
  einheit: string,
  origins: InvoiceLineOrigin[],
): OriginCoverage {
  if (origins.length === 0) return { art: 'ohne' }
  const summe = summeInEinheit(origins, einheit)
  const berechnet = Number(menge)
  if (summe === null || !Number.isFinite(berechnet)) {
    return { art: 'unvergleichbar', quellen: origins.length }
  }
  // Tausendstel Toleranz: Die Mengen stehen mit sechs Nachkommastellen in der
  // Datenbank; ein Rundungsrest ist keine Luecke.
  const luecke = berechnet - summe
  if (Math.abs(luecke) < 0.001) return { art: 'belegt', quellen: origins.length }
  return {
    art: 'teilweise',
    quellen: origins.length,
    fehlend: new Intl.NumberFormat('de-DE', { maximumFractionDigits: 3 }).format(luecke),
  }
}

function zusammenfassung(deckung: OriginCoverage, einheit: string): string {
  switch (deckung.art) {
    case 'ohne':
      return 'Keine Herkunft hinterlegt'
    case 'belegt':
      return deckung.quellen === 1 ? 'Herkunft: 1 Quelle' : `Herkunft: ${deckung.quellen} Quellen`
    case 'teilweise':
      return `Herkunft: ${deckung.quellen} Quellen · ${deckung.fehlend} ${einheit} ohne Zuordnung`
    case 'unvergleichbar':
      return `Herkunft: ${deckung.quellen} Quellen in abweichenden Einheiten`
  }
}

const KLASSE: Record<OriginCoverage['art'], string> = {
  ohne: 'text-status-warning',
  belegt: 'text-muted-foreground',
  teilweise: 'text-status-warning',
  unvergleichbar: 'text-muted-foreground',
}

export function InvoiceLineOrigins({
  lineNo,
  quantity,
  unit,
  origins,
  className,
}: {
  lineNo: string
  quantity: string
  unit: string
  origins: InvoiceLineOrigin[]
  className?: string
}): JSX.Element {
  const [aufgeklappt, setAufgeklappt] = useState(false)
  const deckung = bewerteHerkunft(quantity, unit, origins)
  const leer = origins.length === 0

  return (
    <div className={cn('text-xs', className)} data-testid={`invoice-line-origins-${lineNo}`}>
      <button
        type="button"
        onClick={() => setAufgeklappt(!aufgeklappt)}
        aria-expanded={aufgeklappt}
        disabled={leer}
        className="flex items-center gap-1.5 rounded px-1 py-0.5 text-left hover:bg-accent disabled:hover:bg-transparent"
      >
        {leer ? (
          <span className="w-3.5" aria-hidden="true" />
        ) : aufgeklappt ? (
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
        )}
        <span className={KLASSE[deckung.art]} data-testid={`invoice-origin-summary-${lineNo}`}>
          {zusammenfassung(deckung, unit)}
        </span>
      </button>

      {aufgeklappt && !leer ? (
        <ul className="ml-6 mt-1 space-y-1 border-l pl-3">
          {origins.map((herkunft, index) => {
            const pfad = belegPfad(herkunft.source_document_type, herkunft.source_document_id)
            return (
              <li
                key={`${herkunft.source_document_id}-${herkunft.source_line_id}-${index}`}
                className="flex flex-wrap items-baseline gap-x-2"
              >
                <span className="text-muted-foreground">
                  {belegartLabel(herkunft.source_document_type)}
                </span>
                {pfad ? (
                  <Link to={pfad} className="font-medium underline-offset-2 hover:underline">
                    {herkunft.source_document_id}
                  </Link>
                ) : (
                  <span className="font-medium">{herkunft.source_document_id}</span>
                )}
                <span className="text-muted-foreground">Position {herkunft.source_line_id}</span>
                <span className="tabular-nums">
                  {formatMenge(herkunft.quantity, herkunft.unit)}
                </span>
                {herkunft.reason ? (
                  <span className="text-muted-foreground">· {herkunft.reason}</span>
                ) : null}
              </li>
            )
          })}
        </ul>
      ) : null}
    </div>
  )
}
