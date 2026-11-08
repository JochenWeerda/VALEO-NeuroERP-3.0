import { useCallback, useRef, useState } from 'react'
import { type QueryKey, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'

export interface RowDeleteCandidate {
  id: string
  name: string
  /** Erwartete Revision; Pflicht, solange ``requireVersion`` nicht abgeschaltet ist. */
  version?: string
}

export interface GuardedRowDeleteOptions {
  /** Fachwort im Toast, z. B. "Qualifikation" → "Qualifikation gelöscht". */
  entityLabel: string
  /** Kommandoweg je Zeile (erhaelt die bereits kodierte ID). Sendet expected_revision + Idempotenzschluessel. */
  endpoint?: (encodedId: string) => string
  /** Alternativ: eigener Loeschaufruf, z. B. eine vorhandene Mutation. */
  perform?: (candidate: RowDeleteCandidate, idempotencyKey: string) => Promise<unknown>
  /** Liste, die nach dem Loeschen neu geladen wird (entfaellt, wenn ``perform`` das selbst erledigt). */
  queryKey?: QueryKey
  /** Toast-Beschreibung bei Erfolg; Standard ist der Name des Eintrags. */
  successDescription?: (candidate: RowDeleteCandidate) => string
  /** Ohne Revision loeschen (Kommandoweg ohne Versionspruefung). Standard: Revision Pflicht. */
  requireVersion?: boolean
}

/**
 * Zeilen-Loeschen mit Idempotenzschluessel je Absicht (id + Revision) und Sperre je Zeile
 * (Per-Entity Pending State, Ref-Guard gegen Doppelklick). Der Schluessel bleibt bei Fehlern
 * erhalten, damit ein Wiederholen desselben Versuchs serverseitig als Replay erkannt wird.
 */
export function useGuardedRowDelete({
  entityLabel, endpoint, perform, queryKey, successDescription, requireVersion = true,
}: GuardedRowDeleteOptions) {
  const queryClient = useQueryClient()
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [deleteCandidate, setDeleteCandidate] = useState<RowDeleteCandidate | null>(null)
  const deleteKeys = useRef(new Map<string, string>())
  const deleting = useRef(new Set<string>())

  const loeschen = useCallback(async (candidate: RowDeleteCandidate) => {
    const { id, version } = candidate
    if (!id || deleting.current.has(id)) return
    if (requireVersion && !version) {
      toast.error('Löschen nicht möglich', { description: 'Version fehlt. Bitte Liste neu laden.' })
      return
    }
    const intent = version ? `${id}:${version}` : id
    const key = deleteKeys.current.get(intent) ?? crypto.randomUUID()
    deleteKeys.current.set(intent, key)
    deleting.current.add(id)
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      if (perform) {
        await perform(candidate, key)
      } else if (endpoint) {
        await apiClient.post(endpoint(encodeURIComponent(id)), { expected_revision: version, _idempotencyKey: key })
      } else {
        throw new Error('Kein Löschweg konfiguriert.')
      }
      deleteKeys.current.delete(intent)
      toast.success(`${entityLabel} gelöscht`, { description: successDescription?.(candidate) ?? candidate.name })
      if (queryKey) await queryClient.invalidateQueries({ queryKey })
    } catch (error) {
      toast.error(`${entityLabel} nicht gelöscht`, { description: getAxiosErrorMessage(error) })
    } finally {
      deleting.current.delete(id)
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }, [endpoint, entityLabel, perform, queryClient, queryKey, requireVersion, successDescription])

  return { pendingDeletes, deleteCandidate, setDeleteCandidate, loeschen }
}

export function RowDeleteConfirmDialog({
  candidate,
  onCancel,
  onConfirm,
  title = 'Eintrag löschen?',
  description = (c) => `Der ausgewählte Eintrag ${c?.name ?? ''} wird gelöscht.`,
  confirmLabel = 'Löschen bestätigen',
}: {
  candidate: RowDeleteCandidate | null
  onCancel: () => void
  onConfirm: (candidate: RowDeleteCandidate) => void
  title?: string
  description?: (candidate: RowDeleteCandidate | null) => string
  confirmLabel?: string
}) {
  return (
    <AlertDialog open={candidate !== null} onOpenChange={(open) => { if (!open) onCancel() }}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description(candidate)}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Abbrechen</AlertDialogCancel>
          <AlertDialogAction onClick={() => { if (candidate) onConfirm(candidate) }}>{confirmLabel}</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
