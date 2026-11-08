import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'docflow/gobd-export'

export default function GobdExportPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey !== 'export_gobd') return
    const doc = String(row.doc_number ?? row.doc ?? row.id ?? '')
    if (!doc) return
    try {
      const res = await apiClient.post<{ found?: boolean; detail?: string }>('/api/v1/docflow/evidence/gobd-export', { doc })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({
        title: res.data.found === false ? 'Export nicht moeglich' : 'GoBD-Paket erzeugt',
        description: res.data.detail,
        variant: res.data.found === false ? 'destructive' : 'default',
      })
    } catch (error) {
      toast({
        title: 'GoBD-Export fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="docflow-gobd-export"
      permissions={['docflow.gobd.export']}
      onAction={handleAction}
    />
  )
}
