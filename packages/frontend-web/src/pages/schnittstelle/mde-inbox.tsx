import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'schnittstelle/mde-inbox'

export default function MdeInboxPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, payload: Record<string, unknown>): Promise<void> {
    if (actionKey === 'retry_event') {
      const eventId = String(payload.id ?? '')
      if (!eventId) return
      const reason = window.prompt('Grund fuer die Wiederholung (wird auditiert):')?.trim()
      if (!reason || reason.length < 5) return
      try {
        await apiClient.post(`/api/v1/mobile/sync-queue/${encodeURIComponent(eventId)}/retry`, { reason })
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'MDE-Ereignis erneut eingeplant', description: eventId })
      } catch (error) {
        toast({
          title: 'Wiederholung fehlgeschlagen',
          description: error instanceof Error ? error.message : 'Unbekannter Fehler',
          variant: 'destructive',
        })
      }
      return
    }
    if (actionKey !== 'process_pending') return
    if (!window.confirm('Ausstehende MDE-Ereignisse jetzt verarbeiten?')) return
    try {
      const response = await apiClient.post<{ processed: number; failed: number }>(
        '/api/v1/mobile/sync-process',
        { reason: 'Manuelle Verarbeitung aus dem MDE-Eingangskorb' },
      )
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({
        title: 'MDE-Verarbeitung abgeschlossen',
        description: `${response.data.processed} verarbeitet, ${response.data.failed} fehlgeschlagen.`,
      })
    } catch (error) {
      toast({
        title: 'MDE-Verarbeitung fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="mde-inbox"
      permissions={['mobile.sync.process']}
      onAction={handleAction}
    />
  )
}
