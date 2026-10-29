import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'docflow/artefakt-freigabe'

export default function ArtefaktFreigabePage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    const artifactId = String(row.artifact_id ?? row.id ?? '')
    if (!artifactId) return
    const zielStatus = actionKey === 'freigeben' ? 'freigegeben' : actionKey === 'archivieren' ? 'archiviert' : null
    if (!zielStatus) return
    try {
      await apiClient.post(`/api/v1/docflow/evidence/artifacts/${encodeURIComponent(artifactId)}/freigabe`, { zielStatus })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: `Artefakt ${zielStatus}` })
    } catch (error) {
      toast({
        title: 'Freigabe fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="docflow-artefakt-freigabe"
      permissions={['docflow.artifact.write']}
      onAction={handleAction}
    />
  )
}
