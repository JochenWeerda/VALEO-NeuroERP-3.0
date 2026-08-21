import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

export default function LegacyAdapterMonitorPage(): JSX.Element {
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (!['stage', 'reconcile', 'approve'].includes(actionKey)) return
    const reason = window.prompt('Begruendung (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    const result = await apiClient.post<Record<string, unknown>>(
      `/api/v1/legacy-interface-adapters/batches/${encodeURIComponent(String(row.id ?? ''))}/${actionKey}`,
      { reason },
    )
    toast({
      title: 'Adapter-Batch aktualisiert',
      description: `Status: ${String(result.status ?? 'unbekannt')}. Produktivbuchung bleibt gesperrt.`,
    })
    window.location.reload()
  }

  return (
    <UniversalNativeCockpitPage
      screenId="schnittstelle/legacy-adapter-monitor"
      testId="legacy-adapter-monitor"
      permissions={['integration.legacy-adapter.read']}
      onAction={handleAction}
    />
  )
}
