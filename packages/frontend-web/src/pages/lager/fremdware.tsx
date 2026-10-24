import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'lager/fremdware'

export default function FremdwarePage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      return
    }
    if (actionKey === 'print') {
      window.print()
      return
    }
    const reason = window.prompt('Grund (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    const id = encodeURIComponent(String(row.id ?? ''))
    let body: Record<string, unknown> = { reason }
    if (actionKey === 'transfer') {
      const warehouseId = window.prompt('Ziellager:', String(row.warehouse_id ?? ''))?.trim()
      if (!warehouseId) return
      const location = window.prompt('Lagerort:', String(row.lagerort ?? ''))?.trim() || null
      body = { reason, warehouse_id: warehouseId, location }
    } else if (actionKey === 'complete') {
      const remaining = window.prompt('Restmenge nach Auslagerung:', '0')?.trim()
      if (remaining == null || remaining === '' || Number.isNaN(Number(remaining))) return
      body = { reason, remaining_quantity: Number(remaining) }
    } else return
    try {
      await apiClient.post(`/api/v1/foreign-goods/${id}/${actionKey}`, body)
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Fremdware aktualisiert' })
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
      testId="fremdware"
      permissions={['inventory.foreign-goods.write']}
      onAction={handleAction}
    />
  )
}
