import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'inbox'

export default function InboxPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    const id = String(row.id ?? '')
    if (!id) return
    try {
      if (actionKey === 'create_beleg') {
        const res = await apiClient.post<{ ok?: boolean; number?: string; message?: string }>(`/api/v1/dms/inbox/${encodeURIComponent(id)}/create`, {})
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: res.data.number ? `Beleg ${res.data.number} angelegt` : 'Beleg angelegt' })
        return
      }
      if (actionKey === 'discard') {
        if (!window.confirm('Dokument wirklich verwerfen?')) return
        await apiClient.delete(`/api/v1/dms/inbox/${encodeURIComponent(id)}`)
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Dokument verworfen' })
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
      testId="inbox"
      permissions={['dms.inbox.write']}
      onAction={handleAction}
    />
  )
}
