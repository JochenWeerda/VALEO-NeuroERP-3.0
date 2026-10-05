import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

export default function LetzteDokumentePage(): JSX.Element {
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open') {
      const route = String(row.route ?? '')
      if (route.startsWith('/') && !route.startsWith('//')) window.location.assign(route)
      return
    }
    if (actionKey === 'remove') {
      await apiClient.delete(`/api/v1/recent-documents/${encodeURIComponent(String(row.id ?? ''))}`)
      toast({ title: 'Eintrag entfernt', description: 'Das Dokument wurde nur aus Ihrer persoenlichen Historie entfernt.' })
      window.location.reload()
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId="workspace/letzte-dokumente"
      testId="letzte-dokumente"
      permissions={['workspace.recent-documents.read']}
      onAction={handleAction}
    />
  )
}
