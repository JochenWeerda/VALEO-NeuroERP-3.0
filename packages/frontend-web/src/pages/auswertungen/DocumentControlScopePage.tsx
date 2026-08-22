import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

export function DocumentControlScopePage({ screenId }: { screenId: string }): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    const caseId = String(row.id ?? '')
    if (!caseId) return
    const reason = window.prompt('Grund fuer die Bearbeitung (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    try {
      if (actionKey === 'assign_me') {
        await apiClient.post(`/api/v1/document-control/exceptions/${encodeURIComponent(caseId)}/assign`, {
          assigned_user: 'current-user', reason,
        })
      } else {
        const target = { start_work: 'in_progress', resolve: 'resolved', waive: 'waived' }[actionKey]
        if (!target) return
        await apiClient.post(`/api/v1/document-control/exceptions/${encodeURIComponent(caseId)}/transition`, { target, reason })
      }
      await queryClient.invalidateQueries({ queryKey: [screenId] })
      toast({ title: 'Belegkontrolle aktualisiert' })
    } catch (error) {
      toast({ title: 'Bearbeitung fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }

  return <UniversalNativeCockpitPage screenId={screenId} testId={screenId.replace('/', '-')} permissions={['document_control.write']} onAction={handleAction} />
}
