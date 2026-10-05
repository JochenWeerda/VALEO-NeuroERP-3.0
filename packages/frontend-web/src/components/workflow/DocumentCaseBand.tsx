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

/**
 * Was ueber den Vorgang dieses Belegs bekannt ist.
 *
 * `unerreichbar` ist der Zustand, den F5 gefordert hat: Er ist nicht dasselbe
 * wie `geprueft` ohne Treffer. „Es gibt keinen Vorgang" und „ich konnte nicht
 * nachsehen" sahen vorher beide wie eine leere Flaeche aus.
 */
type Suchstand = 'ruht' | 'laeuft' | 'geprueft' | 'unerreichbar'

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
  const [stand, setStand] = useState<Suchstand>('ruht')
  const [laeuft, setLaeuft] = useState(false)
  const [fehler, setFehler] = useState<string | null>(null)
  const [erneut, setErneut] = useState(0)

  const suchen = Boolean(documentId && !handoverContext?.instanceId)

  useEffect(() => {
    let aktuell = true
    setHit(null)
    if (!suchen) {
      setStand('ruht')
      return
    }
    setStand('laeuft')
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
        setStand('geprueft')
      })
      .catch(() => {
        // Faellt die Suche aus, wird ueber den Vorgang nichts behauptet — wohl
        // aber ueber den eigenen Kenntnisstand. Das ist der Unterschied, den
        // F5 verlangt.
        if (aktuell) setStand('unerreichbar')
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

  // Solange nicht gesucht wird oder die Suche laeuft, bleibt die Flaeche leer:
  // Der Beleg hat noch keine Nummer, oder die Antwort steht noch aus. Beides
  // ist ein Augenblick, keine Auskunft.
  if (stand === 'ruht' || stand === 'laeuft') return null

  // F5: Der Ausfall der Suche bekommt eine eigene Zeile. Ohne sie waere ein
  // fehlendes Band nicht von „kein Prozess" zu unterscheiden — der Beleg saehe
  // in beiden Faellen gleich aus. Behauptet wird dabei nichts ueber den
  // Vorgang, sondern etwas ueber den eigenen Kenntnisstand: nicht ermittelt.
  if (stand === 'unerreichbar') {
    return (
      <Alert className={className} data-testid="document-case-unknown">
        <AlertTitle>Prozessstand nicht ermittelt</AlertTitle>
        <AlertDescription className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <span>
            Ob dieser Beleg zu einem Vorgang gehoert, konnte nicht abgerufen
            werden. Es ist keine Aussage darueber, dass keiner existiert.
          </span>
          <Button type="button" variant="outline" onClick={() => setErneut((wert) => wert + 1)}>
            Erneut abrufen
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  // Ab hier ist geprueft und nichts gefunden. Das ist eine Auskunft und wird
  // auch dann gegeben, wenn die Maske das Verknuepfen nicht anbietet — sonst
  // fiele der bekannte Fall wieder mit dem unbekannten zusammen. Eine
  // Schaltflaeche ohne Wirkung gibt es weiterhin nicht.
  return (
    <Alert className={className} data-testid="document-case-link-offer">
      <AlertTitle>Kein Vorgang zu diesem Beleg</AlertTitle>
      <AlertDescription className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span>
          {fehler ?? 'Der Beleg ist gespeichert, gehoert aber zu keinem Prozessvorgang.'}
        </span>
        {onLink ? (
          <Button type="button" onClick={() => void verknuepfen()} disabled={laeuft}>
            {laeuft ? 'Wird verknuepft …' : linkLabel}
          </Button>
        ) : null}
      </AlertDescription>
    </Alert>
  )
}
