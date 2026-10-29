import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { useNavigate } from '@/app/routing/typed-router'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import {
  assertInboxDoesNotBook,
  clearInboxPrefill,
  inboxOpenDecision,
  type InboxQueueItem,
} from '@/components/adaptive-workspace/inbox'
import { openInboxItemInMask } from '@/workspace/sibling-slots'

const SCREEN_ID = 'inbox'

export default function InboxPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const navigate = useNavigate()
  const schema = useScreenDefinition(SCREEN_ID)
  const permissions = useScreenPermissions(schema.data)

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    const id = String(row.id ?? '')
    if (!id) return
    try {
      if (actionKey === 'create_beleg') {
        const res = await apiClient.post<{ ok: boolean; booking_allowed: boolean; item: InboxQueueItem }>(
          `/api/mcp/documents/inbox/${encodeURIComponent(id)}/prepare`, {},
        )
        const item = res.data.item
        if (res.data.ok !== true || res.data.booking_allowed !== false || !item || item.id !== id) {
          throw new Error('Der vorbereitete Vorschlag passt nicht zum ausgewählten Dokument.')
        }
        assertInboxDoesNotBook(item)
        const decision = inboxOpenDecision(item)
        if (item.can_open !== true || !item.actions.some(action => action.key === 'open_mask' && action.enabled === true) || !decision.href) {
          throw new Error(decision.reason || 'Dieser Vorschlag darf nicht geöffnet werden.')
        }
        clearInboxPrefill()
        openInboxItemInMask(item, navigate)
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
      permissions={permissions}
      onAction={handleAction}
    />
  )
}
