import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'crm/klaerfall-inbox'

export default function KlaerfallInboxPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    const id = String(row.id ?? '')
    if (!id) return
    try {
      if (actionKey === 'assign') {
        const kundenNr = window.prompt('Kundennummer fuer die Zuordnung:')?.trim()
        if (!kundenNr) return
        await apiClient.post(`/api/v1/crm/kim/capture-inbox/${encodeURIComponent(id)}/assign`, {
          kunden_nr: kundenNr,
          resolved_by: 'current-user',
        })
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Klaerfall zugeordnet' })
        return
      }
      if (actionKey === 'dismiss') {
        if (!window.confirm('Klaerfall wirklich verwerfen?')) return
        await apiClient.post(`/api/v1/crm/kim/capture-inbox/${encodeURIComponent(id)}/dismiss`, {})
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Klaerfall verworfen' })
      }
    } catch (error) {
      toast({
        title: 'Aktion fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="crm-klaerfall-inbox"
      permissions={['crm.capture_inbox.write']}
      onAction={handleAction}
    />
  )
}
