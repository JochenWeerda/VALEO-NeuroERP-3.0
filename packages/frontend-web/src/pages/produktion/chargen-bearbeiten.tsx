import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

const SCREEN_ID = 'produktion/chargen-bearbeiten'

export default function ChargenBearbeitenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'open_source') {
      const id = String(row.id ?? '')
      if (id) window.location.assign(`/charge/details/${encodeURIComponent(id)}`)
      return
    }
    try {
      if (actionKey === 'edit_metadata') {
        const id = String(row.id ?? '')
        if (!id) return
        const supplierBatch = window.prompt('Lieferanten-Charge', String(row.lieferanten_charge ?? ''))
        if (supplierBatch === null) return
        const approvalNumber = window.prompt('Anerkennungs-Nr.', String(row.anerkennungs_nr ?? ''))
        if (approvalNumber === null) return
        await apiClient.patch(`/api/v1/chargen/${encodeURIComponent(id)}`, {
          lieferanten_charge: supplierBatch.trim() || null,
          anerkennungs_nr: approvalNumber.trim() || null,
        })
      } else if (actionKey === 'bulk_release') {
        const ids = Array.isArray(row.selectedIds) ? row.selectedIds.map(String) : []
        if (!ids.length) return
        const reason = window.prompt(`Grund fuer die Freigabe von ${ids.length} Charge(n) (Audit):`)?.trim()
        if (!reason || reason.length < 5) return
        await apiClient.post('/api/v1/chargen/operator/bulk-release', { ids, reason })
      } else return
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: actionKey === 'bulk_release' ? 'Chargen freigegeben' : 'Chargenkennzeichen gespeichert' })
    } catch (error) {
      toast({ title: 'Chargenbearbeitung fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="chargen-bearbeiten" permissions={['inventory.charges.write']} onAction={handleAction} />
}
