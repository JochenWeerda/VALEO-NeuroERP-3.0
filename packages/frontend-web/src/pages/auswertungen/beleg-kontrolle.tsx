import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'auswertungen/beleg-kontrolle'

export default function BelegKontrollePage(): JSX.Element {
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

    if (actionKey === 'assign_me') {
      const reason = window.prompt('Grund fuer die Zuweisung (Audit):')?.trim()
      if (!reason || reason.length < 5) return
      try {
        await apiClient.post(`/api/v1/document-control/exceptions/${encodeURIComponent(caseId)}/assign`, {
          assigned_user: 'current-user',
          reason,
        })
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Ausnahme zugewiesen' })
      } catch (error) {
        toast({
          title: 'Zuweisung fehlgeschlagen',
          description: error instanceof Error ? error.message : 'Unbekannter Fehler',
          variant: 'destructive',
        })
      }
      return
    }

    const target =
      actionKey === 'start_work'
        ? 'in_progress'
        : actionKey === 'resolve'
          ? 'resolved'
          : actionKey === 'waive'
            ? 'waived'
            : undefined
    if (!target) return
    const reason = window.prompt('Grund fuer den Statuswechsel (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    try {
      await apiClient.post(`/api/v1/document-control/exceptions/${encodeURIComponent(caseId)}/transition`, {
        target,
        reason,
      })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Belegkontrolle aktualisiert' })
    } catch (error) {
      toast({
        title: 'Statuswechsel fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="beleg-kontrolle"
      permissions={['document_control.write']}
      onAction={handleAction}
    />
  )
}
