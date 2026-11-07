import { useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'lager/inventur-nebenlaeufe'

export default function InventurNebenlaeufePage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const countSheetKeys = useRef(new Map<string, string>())

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
    const batchType = actionKey === 'create_count_sheet' ? 'count_sheet'
      : actionKey === 'create_control' ? 'control_run'
        : actionKey === 'create_valuation' ? 'preliminary_valuation'
          : actionKey === 'create_opening' ? 'opening_balance' : undefined
    if (batchType) {
      const countId = window.prompt('Inventur-ID:')?.trim()
      const reason = window.prompt('Grund / Zweck (Audit):')?.trim()
      if (!countId || !reason || reason.length < 5) return
      try {
        if (batchType === 'count_sheet') {
          const { data } = await apiClient.get<{ inventory_count_id: string; revision: string }>(
            `/api/v1/inventory/auxiliary/counts/${encodeURIComponent(countId)}/count-sheet-snapshot`,
          )
          if (data.inventory_count_id !== countId || !/^[a-f0-9]{64}$/.test(data.revision)) {
            throw new Error('Der Inventurstand ist ungültig. Bitte erneut laden.')
          }
          const intent = JSON.stringify([countId, data.revision, reason])
          const key = countSheetKeys.current.get(intent) ?? crypto.randomUUID()
          countSheetKeys.current.set(intent, key)
          const response = await apiClient.post<{ success: boolean; error?: string }>(
            '/api/v1/inventory/auxiliary/actions/create_count_sheet', {
              inventory_count_id: countId, expected_revision: data.revision,
              _auditReason: reason, _idempotencyKey: key,
            },
          )
          if (response.data?.success !== true) throw new Error(response.data?.error || 'Zaehlliste abgelehnt.')
          countSheetKeys.current.delete(intent)
        } else {
          await apiClient.post('/api/v1/inventory/auxiliary/batches', {
            inventory_count_id: countId, batch_type: batchType, reason,
          })
        }
        await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
        toast({ title: 'Inventur-Nebenlauf erzeugt' })
      } catch (error) {
        toast({ title: 'Erzeugung fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
      }
      return
    }
    const target = actionKey === 'review' ? 'reviewed' : actionKey === 'approve' ? 'approved'
      : actionKey === 'apply' ? 'applied' : undefined
    const batchId = String(row.id ?? '')
    if (!target || !batchId) return
    const reason = window.prompt('Grund fuer den Statuswechsel (Audit):')?.trim()
    if (!reason || reason.length < 5) return
    try {
      await apiClient.post(`/api/v1/inventory/auxiliary/batches/${encodeURIComponent(batchId)}/transition`, { target, reason })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Inventur-Nebenlauf aktualisiert' })
    } catch (error) {
      toast({ title: 'Statuswechsel fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="inventur-nebenlaeufe"
    permissions={['inventory.aux.write']} onAction={handleAction} />
}
