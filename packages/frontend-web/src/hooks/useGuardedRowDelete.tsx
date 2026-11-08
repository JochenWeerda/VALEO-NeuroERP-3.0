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
  version: string
}

export interface GuardedRowDeleteOptions {
  /** Kommandoweg je Zeile, z. B. `/api/v1/training/qualifications/{id}/actions/loeschen`. */
  endpoint: (id: string) => string
  /** Liste, die nach dem Loeschen neu geladen wird. */
  queryKey: QueryKey
  /** Fachwort im Toast, z. B. "Qualifikation" → "Qualifikation gelöscht". */
  entityLabel: string
}

/**
 * Zeilen-Loeschen mit Versionspruefung, Idempotenzschluessel je Absicht (id + Version)
 * und Sperre je Zeile (Per-Entity Pending State). Der Schluessel bleibt bei Fehlern erhalten,
 * damit ein Wiederholen desselben Versuchs serverseitig als Replay erkannt wird.
 */
export function useGuardedRowDelete({ endpoint, queryKey, entityLabel }: GuardedRowDeleteOptions) {
  const queryClient = useQueryClient()
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())
  const [deleteCandidate, setDeleteCandidate] = useState<RowDeleteCandidate | null>(null)
  const deleteKeys = useRef(new Map<string, string>())
  const deleting = useRef(new Set<string>())

  const loeschen = useCallback(async ({ id, name, version }: RowDeleteCandidate) => {
    if (!id || deleting.current.has(id)) return
    if (!version) { toast.error('Löschen nicht möglich', { description: 'Version fehlt. Bitte Liste neu laden.' }); return }
    const intent = `${id}:${version}`
    const key = deleteKeys.current.get(intent) ?? crypto.randomUUID()
    deleteKeys.current.set(intent, key)
    deleting.current.add(id)
    setPendingDeletes((prev) => new Set(prev).add(id))
    try {
      await apiClient.post(endpoint(encodeURIComponent(id)), {
        expected_revision: version, _idempotencyKey: key,
      })
      deleteKeys.current.delete(intent)
      toast.success(`${entityLabel} gelöscht`, { description: name })
      await queryClient.invalidateQueries({ queryKey })
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
  }, [endpoint, entityLabel, queryClient, queryKey])

  return { pendingDeletes, deleteCandidate, setDeleteCandidate, loeschen }
}

export function RowDeleteConfirmDialog({
  candidate,
  onCancel,
  onConfirm,
}: {
  candidate: RowDeleteCandidate | null
  onCancel: () => void
  onConfirm: (candidate: RowDeleteCandidate) => void
}) {
  return (
    <AlertDialog open={candidate !== null} onOpenChange={(open) => { if (!open) onCancel() }}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Eintrag löschen?</AlertDialogTitle>
          <AlertDialogDescription>Der ausgewählte Eintrag {candidate?.name} wird gelöscht.</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Abbrechen</AlertDialogCancel>
          <AlertDialogAction onClick={() => { if (candidate) onConfirm(candidate) }}>Löschen bestätigen</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
