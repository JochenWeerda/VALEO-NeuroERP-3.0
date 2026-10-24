import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'tankstelle/adapter-inbox'

export default function TankAdapterInboxPage(): JSX.Element {
  const queryClient = useQueryClient(); const { toast } = useToast()
  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source') { window.location.assign(`/tankstelle/adapter-inbox?focus=${encodeURIComponent(String(row.id ?? ''))}`); return }
    if (!['validate', 'process', 'retry'].includes(actionKey)) return
    const reason = window.prompt('Grund (Audit):')?.trim(); if (!reason || reason.length < 5) return
    let body: Record<string, unknown> = { reason }
    if (actionKey === 'retry') { const corrected = window.prompt('Korrigiertes Payload als JSON (leer = unveraendert):')?.trim(); if (corrected) body = { reason, corrected_payload: JSON.parse(corrected) } }
    try {
      await apiClient.post(`/api/v1/tank-adapter/intake/${encodeURIComponent(String(row.id ?? ''))}/${actionKey}`, body)
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] }); toast({ title: 'Tankanlagen-Eingang aktualisiert' })
    } catch (error) { toast({ title: 'Aktion fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' }) }
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="tank-adapter-inbox" permissions={['tank.adapter.write']} onAction={handleAction} />
}
