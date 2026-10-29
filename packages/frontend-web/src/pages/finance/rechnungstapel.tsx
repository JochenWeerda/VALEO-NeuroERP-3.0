import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'finance/rechnungstapel'

export default function RechnungstapelPage(): JSX.Element {
  const queryClient = useQueryClient(); const { toast } = useToast()
  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source' || actionKey === 'open_evidence') {
      const route = String(row[actionKey === 'open_source' ? 'source_route' : 'evidence_route'] ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    const reason = window.prompt('Grund (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    const id = String(row.id ?? '')
    const path = actionKey === 'retry' ? `/api/v1/billing-batches/lines/${encodeURIComponent(id)}/retry`
      : `/api/v1/billing-batches/${encodeURIComponent(id)}/${actionKey}`
    try {
      await apiClient.post(path, { reason }); await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Rechnungstapel aktualisiert' })
    } catch (error) {
      toast({ title: 'Aktion fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="rechnungstapel"
    permissions={['billing.batch.write']} onAction={handleAction} />
}
