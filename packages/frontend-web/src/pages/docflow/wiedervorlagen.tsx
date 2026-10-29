import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'docflow/wiedervorlagen'

export default function DocflowWiedervorlagenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey !== 'complete') return
    const id = String(row.id ?? row.followup_id ?? '')
    if (!id) return
    try {
      await apiClient.post(`/api/v1/docflow/evidence/followups/${encodeURIComponent(id)}/complete`, {})
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Wiedervorlage erledigt' })
    } catch (error) {
      toast({
        title: 'Erledigen fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="docflow-wiedervorlagen"
      permissions={['docflow.followup.write']}
      onAction={handleAction}
    />
  )
}
