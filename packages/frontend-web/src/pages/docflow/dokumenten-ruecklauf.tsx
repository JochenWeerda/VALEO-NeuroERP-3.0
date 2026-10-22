import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'docflow/dokumenten-ruecklauf'

export default function DokumentenRuecklaufPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  async function handleAction(key: string, row: Record<string, unknown>): Promise<void> {
    if (key === 'preview_evidence') {
      try {
        const response = await apiClient.get<{ file_name?: string; content_hash_sha256?: string; preview_available: boolean }>(
          `/api/v1/docflow/returns/${encodeURIComponent(String(row.id))}/evidence`,
        )
        toast({
          title: response.data.preview_available ? response.data.file_name ?? 'Dokumentvorschau' : 'Keine Vorschau abgelegt',
          description: response.data.content_hash_sha256 ? `SHA-256: ${response.data.content_hash_sha256}` : 'Metadaten des Ursprungsbelegs sind verfuegbar.',
        })
      } catch (error) {
        toast({ title: 'Vorschau fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
      }
      return
    }
    if (key === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    const transition = key === 'mark_sent' ? { kind: 'shipping', target: 'sent' }
      : key === 'mark_received' ? { kind: 'return', target: 'received' }
        : key === 'verify_return' ? { kind: 'return', target: 'verified' } : undefined
    if (!transition) return
    const reason = window.prompt('Grund fuer den Statuswechsel (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    try {
      await apiClient.post(`/api/v1/docflow/returns/${encodeURIComponent(String(row.id))}/transition`, { ...transition, reason })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Ruecklaufstatus aktualisiert' })
    } catch (error) {
      toast({ title: 'Statuswechsel fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="document-return-inbox" permissions={['docflow.returns.write']} onAction={handleAction} />
}
