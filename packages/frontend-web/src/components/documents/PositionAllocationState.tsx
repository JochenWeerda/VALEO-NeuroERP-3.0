import { useEffect, useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { cn } from '@/lib/utils'

/**
 * FSX-MENGENMODELL — der Mengenstand an der Belegposition (K5).
 *
 * Zeigt die drei Zahlen, um die es geht:
 *
 *     100 dt geliefert · 60 dt berechnet · 40 dt offen
 *
 * und klappt darunter die einzelnen Zuordnungen auf. **Anzeigen ist nicht
 * Aufloesen** — deshalb sind die Zuordnungen erreichbar, nicht nur die Summe:
 * Wer wissen will, *welche* Rechnung die 60 dt genommen hat, soll nicht in den
 * Leitstand wechseln muessen.
 *
 * Drei Zurueckhaltungen, die dieselben sind wie beim Prozessband:
 *
 * - **Kein react-query.** Der Baustein soll in beliebige Belegmasken passen,
 *   ohne ihnen einen QueryClientProvider aufzuzwingen.
 * - **Kein Fehlerbanner.** Faellt der Abruf aus, bleibt die Position ohne
 *   Mengenzeile. Ein Fehlerkasten ueber einer funktionierenden Position waere
 *   schlimmer als keine Zeile.
 * - **Keine Behauptung ueber Abwesenheit.** Solange nicht geladen ist, steht
 *   nichts da — weder Zahlen noch "keine Zuordnungen".
 */

export type AllocationEntry = {
  id: string
  target_document_type: string
  target_document_id: string
  target_line_id: string
  quantity: string
  unit: string
  entered_quantity?: string | null
  entered_unit?: string | null
  reason?: string | null
}

export type AllocationLine = {
  line_id: string
  article_id?: string | null
  unit: string
  quantity: string
  allocated_quantity: string
  open_quantity: string
  status: 'offen' | 'teilweise' | 'vollstaendig'
  allocations: AllocationEntry[]
}

const STATUS_KLASSE: Record<AllocationLine['status'], string> = {
  offen: 'text-muted-foreground',
  teilweise: 'text-status-warning',
  vollstaendig: 'text-status-success',
}

/** Menge plus Einheit, mit der Eingabe daneben, falls sie eine andere war. */
function mengeMitEingabe(eintrag: AllocationEntry): string {
  const gerechnet = `${eintrag.quantity} ${eintrag.unit}`
  if (!eintrag.entered_quantity || !eintrag.entered_unit) return gerechnet
  if (eintrag.entered_unit === eintrag.unit) return gerechnet
  // "2 big_bag (= 12 dt)" — die Eingabe bleibt sichtbar, damit niemand die
  // umgerechnete Zahl fuer die eingegebene haelt.
  return `${eintrag.entered_quantity} ${eintrag.entered_unit} (= ${gerechnet})`
}

export function PositionAllocationState({
  documentType,
  documentId,
  lineId,
  className,
}: {
  documentType: string
  documentId: string
  /** Ohne Angabe werden alle Positionen des Belegs gezeigt. */
  lineId?: string
  className?: string
}): JSX.Element | null {
  const [zeilen, setZeilen] = useState<AllocationLine[] | null>(null)
  const [offen, setOffen] = useState<string | null>(null)

  useEffect(() => {
    let aktuell = true
    setZeilen(null)
    if (!documentType || !documentId) return
    void apiClient
      .get<{ lines?: AllocationLine[] }>(
        `/api/v1/docflow/documents/${encodeURIComponent(documentType)}/${encodeURIComponent(documentId)}/allocations`,
      )
      .then((response) => {
        if (aktuell) setZeilen(response.data?.lines ?? [])
      })
      .catch(() => {
        // Kein Fehlerbanner ueber einer funktionierenden Position.
        if (aktuell) setZeilen(null)
      })
    return () => {
      aktuell = false
    }
  }, [documentType, documentId])

  if (!zeilen) return null
  const gezeigt = lineId ? zeilen.filter((z) => z.line_id === lineId) : zeilen
  if (gezeigt.length === 0) return null

  return (
    <div className={cn('space-y-1 text-sm', className)} data-testid="position-allocation-state">
      {gezeigt.map((zeile) => {
        const aufgeklappt = offen === zeile.line_id
        return (
          <div key={zeile.line_id} data-testid={`allocation-line-${zeile.line_id}`}>
            <button
              type="button"
              onClick={() => setOffen(aufgeklappt ? null : zeile.line_id)}
              aria-expanded={aufgeklappt}
              disabled={zeile.allocations.length === 0}
              className="flex w-full items-center gap-2 rounded px-1 py-0.5 text-left hover:bg-accent disabled:hover:bg-transparent"
            >
              {zeile.allocations.length > 0 ? (
                aufgeklappt ? (
                  <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
                )
              ) : (
                <span className="w-3.5" aria-hidden="true" />
              )}
              <span className="tabular-nums" data-testid={`allocation-summary-${zeile.line_id}`}>
                {zeile.quantity} {zeile.unit} geliefert
                {' · '}
                {zeile.allocated_quantity} {zeile.unit} berechnet
                {' · '}
                <span className={STATUS_KLASSE[zeile.status]}>
                  {zeile.open_quantity} {zeile.unit} offen
                </span>
              </span>
            </button>

            {aufgeklappt ? (
              <ul className="ml-6 mt-1 space-y-1 border-l pl-3">
                {zeile.allocations.map((eintrag) => (
                  <li key={eintrag.id} className="flex flex-wrap items-baseline gap-x-2 text-xs">
                    <span className="font-medium">{eintrag.target_document_id}</span>
                    <span className="text-muted-foreground">
                      Position {eintrag.target_line_id}
                    </span>
                    <span className="tabular-nums">{mengeMitEingabe(eintrag)}</span>
                    {eintrag.reason ? (
                      <span className="text-muted-foreground">· {eintrag.reason}</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        )
      })}
    </div>
  )
}
