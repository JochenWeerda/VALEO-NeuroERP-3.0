import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'docflow/dokumenten-ruecklauf'

export default function DokumentenRuecklaufPage(): JSX.Element {
  const { toast } = useToast()
  // Statuswechsel ueber den Kommando-Weg der Maske, den auch CLI und MCP rufen (nicht unter /docflow:
  // dort gelten die versionierten Beleg-Adapter).
  const command = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: Object.fromEntries(['mark_sent', 'mark_received', 'verify_return'].map(k =>
      [k, (row: Record<string, unknown>) => `/api/v1/document-returns/${seg(row.id)}/actions/${k}`])),
    navigation: { open_source: row => row.source_route },
    reasonPrompt: 'Grund fuer den Statuswechsel (Audit):',
    successTitle: 'Ruecklaufstatus aktualisiert',
  })
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
    await command(key, row)
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="document-return-inbox" permissions={['docflow.returns.write']} onAction={handleAction} />
}
