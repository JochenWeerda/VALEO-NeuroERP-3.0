import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'produktion/produktionsleitstand'

export default function ProduktionsleitstandPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    if (actionKey === 'print') {
      window.location.assign('/produktion/produktions-dokumente-drucken')
      return
    }
    const target = actionKey === 'release' ? 'released' : actionKey === 'start' ? 'running'
      : actionKey === 'complete' ? 'completed' : actionKey === 'mark_rework' ? 'rework' : undefined
    const operationId = String(row.id ?? '')
    if (!target || !operationId) return
    const reason = window.prompt('Grund fuer den Statuswechsel (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    try {
      await apiClient.post(`/api/v1/production-control/operations/${encodeURIComponent(operationId)}/transition`, { target, reason })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Produktionsvorgang aktualisiert' })
    } catch (error) {
      toast({ title: 'Statuswechsel fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="produktionsleitstand"
    permissions={['production.control.write']} onAction={handleAction} />
}
