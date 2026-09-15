import { useCallback, useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { WorkflowProcessBand } from './WorkflowProcessBand'
import type { WorkflowEntryContext } from './WorkflowEntryBanner'

/**
 * FSX-013 (Rollout) und FSX-012 (Nachlauf) fuer bestehende Belege.
 *
 * Zwei Faelle, eine Flaeche:
 *
 * 1. **Der Beleg gehoert bereits zu einem Vorgang** — dann zeigt das Prozessband
 *    Phasen, Stand und naechsten Schritt, so wie beim Handover aus dem Leitstand.
 * 2. **Der Beleg gehoert zu keinem Vorgang** — dann wird die Verknuepfung
 *    angeboten. Das ist die letzte offene Kante des Teilfehler-Pfades aus
 *    FSX-012: Wer beim Speichern den Wiederholungsversuch abbricht, kommt
 *    spaeter zurueck, und die Maske erinnert ihn daran, statt zu schweigen.
 *
 * Gefragt wird ueber die Rueckwaertssuche aus FSX-DOC-LINKS, nicht ueber den
 * Prozessfilter: ein Beleg kann **fuehrend** in einem Vorgang stehen und
 * **beteiligt** in einem anderen — eine Sammelrechnung tut genau das. Der
 * Prozessfilter wuerde den zweiten Fall uebersehen.
 *
 * Bewusst ohne react-query: der Baustein soll in beliebige Fachmasken passen,
 * und `useQuery` wuerde jeder von ihnen einen QueryClientProvider aufzwingen.
 */

type CaseHit = {
  instance_id: string
  process_key: string
  case_number?: string
  label?: string
  lifecycle_status?: string
  role: 'leading' | 'participant'
}

export function DocumentCaseBand({
  documentType,
  documentId,
  handoverContext,
  onLink,
  linkLabel = 'Vorgang verknuepfen',
  className,
}: {
  documentType: string
  /** Leer, solange der Beleg noch nicht gespeichert ist — dann passiert nichts. */
  documentId?: string | null
  /** Handover aus dem Leitstand; hat Vorrang vor der Suche. */
  handoverContext?: WorkflowEntryContext | null
  /**
   * Verknuepfung herstellen. Fehlt der Rueckruf, wird nichts angeboten — eine
   * Schaltflaeche ohne Wirkung waere schlimmer als keine.
   */
  onLink?: () => Promise<void>
  linkLabel?: string
  className?: string
}): JSX.Element | null {
  const [hit, setHit] = useState<CaseHit | null>(null)
  const [geprueft, setGeprueft] = useState(false)
  const [laeuft, setLaeuft] = useState(false)
  const [fehler, setFehler] = useState<string | null>(null)
  const [erneut, setErneut] = useState(0)

  const suchen = Boolean(documentId && !handoverContext?.instanceId)

  useEffect(() => {
    let aktuell = true
    setHit(null)
    setGeprueft(false)
    if (!suchen) return
    void apiClient
      .get<{ instances?: CaseHit[] }>(
        `/api/v1/process/flow-spines/documents/${encodeURIComponent(documentType)}/${encodeURIComponent(String(documentId))}/instances`,
      )
      .then((response) => {
        if (!aktuell) return
        const treffer = response.data?.instances ?? []
        // Der fuehrende Vorgang beschreibt diesen Beleg am besten; nur wenn es
        // keinen gibt, steht der Beleg als Beteiligter in einem fremden Vorgang.
        setHit(treffer.find((t) => t.role === 'leading') ?? treffer[0] ?? null)
        setGeprueft(true)
      })
      .catch(() => {
        // Das Band ist Orientierung, kein Arbeitsmittel. Faellt die Suche aus,
        // wird nichts behauptet — weder ein Vorgang noch dessen Abwesenheit.
        if (aktuell) setGeprueft(false)
      })
    return () => {
      aktuell = false
    }
  }, [documentType, documentId, suchen, erneut])

  const verknuepfen = useCallback(async () => {
    if (!onLink || laeuft) return
    setLaeuft(true)
    setFehler(null)
    try {
      await onLink()
      setErneut((wert) => wert + 1)
    } catch (error) {
      setFehler(
        error instanceof Error && error.message
          ? error.message
          : 'Der Vorgang konnte nicht verknuepft werden.',
      )
    } finally {
      setLaeuft(false)
    }
  }, [onLink, laeuft])

  if (handoverContext?.instanceId) {
    return <WorkflowProcessBand context={handoverContext} className={className} />
  }

  if (hit) {
    return (
      <WorkflowProcessBand
        className={className}
        context={{
          process: hit.process_key,
          instanceId: hit.instance_id,
          caseNumber: hit.case_number ?? '',
          label: hit.label ?? '',
          partnerName: '',
          subject: '',
          entryMode: '',
        }}
      />
    )
  }

  // Erst anbieten, wenn wirklich gesucht **und** nichts gefunden wurde. Ohne
  // diese Bedingung stuende das Angebot schon waehrend der Suche da und
  // behauptete eine Abwesenheit, die noch niemand geprueft hat.
  if (!suchen || !geprueft || !onLink) return null

  return (
    <Alert className={className} data-testid="document-case-link-offer">
      <AlertTitle>Kein Vorgang zu diesem Beleg</AlertTitle>
      <AlertDescription className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span>
          {fehler ?? 'Der Beleg ist gespeichert, gehoert aber zu keinem Prozessvorgang.'}
        </span>
        <Button type="button" onClick={() => void verknuepfen()} disabled={laeuft}>
          {laeuft ? 'Wird verknuepft …' : linkLabel}
        </Button>
      </AlertDescription>
    </Alert>
  )
}
