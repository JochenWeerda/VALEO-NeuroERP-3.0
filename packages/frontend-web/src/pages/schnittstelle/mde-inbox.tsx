import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'schnittstelle/mde-inbox'

export default function MdeInboxPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  // Wiederholen laeuft ueber den Kommando-Weg der Maske, den auch CLI und MCP rufen.
  const retryEvent = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: { retry_event: row => `/api/v1/mobile/sync-queue/${seg(row.id)}/actions/retry_event` },
    reasonPrompt: 'Grund fuer die Wiederholung (wird auditiert):',
    successTitle: 'MDE-Ereignis erneut eingeplant',
  })

  async function handleAction(actionKey: string, payload: Record<string, unknown>): Promise<void> {
    if (actionKey === 'retry_event') {
      await retryEvent(actionKey, payload)
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
