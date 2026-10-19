import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { seg, useMaskRowCommands } from '@/components/mask-builder/runtime/useMaskRowCommands'

const SCREEN_ID = 'crm/mail-arbeitsplatz'

export default function MailArbeitsplatzPage(): JSX.Element {
  const queryClient = useQueryClient(); const { toast } = useToast()
  // Senden und DMS-Uebernahme ueber die Kommando-Wege der Maske, die auch CLI und MCP rufen.
  const command = useMaskRowCommands({
    screenId: SCREEN_ID,
    commands: {
      queue: row => `/api/v1/mail-workspace/${seg(row.id)}/actions/queue`,
      transfer: row => `/api/v1/mail-workspace/attachments/${seg(row.id)}/actions/transfer`,
    },
    reasonPrompt: 'Grund (Audit):',
    successTitle: 'Mail-Arbeitsplatz aktualisiert',
  })
  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'queue' || actionKey === 'transfer') { await command(actionKey, row); return }
    if (actionKey === 'open_document') { const route = String(row.document_route ?? ''); if (route.startsWith('/')) window.location.assign(route); return }
    try {
      if (actionKey === 'draft') {
        const role = window.prompt('Rollenpostfach:')?.trim(); const recipient = window.prompt('Empfaenger:')?.trim(); const subject = window.prompt('Betreff:')?.trim(); const body = window.prompt('Nachricht:') ?? ''; const reason = window.prompt('Grund (Audit):')?.trim()
        if (!role || !recipient || !subject || !reason || reason.length < 5) return
        await apiClient.post('/api/v1/mail-workspace/drafts', { role_key: role, to_addresses: [recipient], subject, body_text: body, reason })
      } else if (actionKey === 'assign') {
        const contactId = window.prompt('Kontakt-ID:', String(row.contact_id ?? ''))?.trim() || null; const documentRef = window.prompt('Belegreferenz:', String(row.document_ref ?? ''))?.trim() || null; const documentRoute = window.prompt('Belegroute:', String(row.document_route ?? ''))?.trim() || null; const reason = window.prompt('Grund (Audit):')?.trim()
        if (!reason || reason.length < 5) return
        await apiClient.post(`/api/v1/mail-workspace/${encodeURIComponent(String(row.id ?? ''))}/assign`, { contact_id: contactId, document_ref: documentRef, document_route: documentRoute, reason })
      } else return
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] }); toast({ title: 'Mail-Arbeitsplatz aktualisiert' })
    } catch (error) { toast({ title: 'Aktion fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' }) }
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="mail-arbeitsplatz" permissions={['crm.mail.write']} onAction={handleAction} />
}
