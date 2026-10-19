import { useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

/** Kommando-Wege der ScreenDefinition — dieselben, die CLI und MCP rufen (MASK-COMMANDS-ROLLOUT). */
const COMMANDS = new Set(['assign_me', 'start_work', 'resolve', 'waive'])

type MaskActionResult = { success: boolean; summary?: string | null; error?: string | null }

/**
 * Belegkontrolle und ihre gespeicherten L3-Sichten. Die Seite fragt nur die Begruendung ab; Bearbeiter,
 * Zustaendiger, Statusregeln, Audit und Wiederholungsschutz liegen beim Kommando-Endpunkt.
 */
export function DocumentControlScopePage({ screenId, testId }: { screenId: string; testId?: string }): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  // Je Fall und Aktion, nicht global: andere Zeilen bleiben bedienbar (Per-Entity Pending State).
  const pending = useRef(new Set<string>())

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    const caseId = String(row.id ?? '')
    if (!caseId || !COMMANDS.has(actionKey)) return
    const key = `${caseId}:${actionKey}`
    if (pending.current.has(key)) return
    const reason = window.prompt('Grund fuer die Bearbeitung (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    pending.current.add(key)
    try {
      const { data } = await apiClient.post<MaskActionResult>(
        `/api/v1/document-control/exceptions/${encodeURIComponent(caseId)}/actions/${actionKey}`,
        { _auditReason: reason, _idempotencyKey: crypto.randomUUID() },
      )
      // Eine fachliche Ablehnung kommt mit HTTP 200 und success=false — sie ist kein Erfolg.
      if (!data?.success) throw new Error(data?.error ?? 'Die Aktion wurde abgelehnt.')
      await queryClient.invalidateQueries({ queryKey: [screenId] })
      toast({ title: 'Belegkontrolle aktualisiert', description: data.summary ?? undefined })
    } catch (error) {
      toast({ title: 'Bearbeitung fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    } finally {
      pending.current.delete(key)
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={screenId}
      testId={testId ?? screenId.replace('/', '-')}
      permissions={['document_control.write']}
      onAction={handleAction}
    />
  )
}
