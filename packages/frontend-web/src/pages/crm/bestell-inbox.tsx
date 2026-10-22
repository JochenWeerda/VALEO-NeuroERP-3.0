import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'crm/bestell-inbox'

export default function BestellInboxPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    const id = String(row.id ?? '')
    if (!id) return
    try {
      if (actionKey === 'bestaetigen') {
        await apiClient.post(`/api/v1/crm/bestell-inbox/${encodeURIComponent(id)}/bestaetigen`, {})
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Bestellung bestaetigt' })
        return
      }
      if (actionKey === 'verwerfen') {
        if (!window.confirm('Eintrag wirklich verwerfen?')) return
        await apiClient.post(`/api/v1/crm/bestell-inbox/${encodeURIComponent(id)}/verwerfen`, {})
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Eintrag verworfen' })
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
      testId="crm-bestell-inbox"
      permissions={['crm.bestell_inbox.write']}
      onAction={handleAction}
    />
  )
}
