import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'auswertungen/abfrage-center'

function downloadJson(value: unknown): void {
  const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }))
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'valeo-abfrage.json'; anchor.click(); URL.revokeObjectURL(url)
}

export default function AbfrageCenterPage(): JSX.Element {
  const queryClient = useQueryClient(); const { toast } = useToast()
  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    if (actionKey === 'print') { window.print(); return }
    try {
      if (actionKey === 'preview') {
        await apiClient.post('/api/v1/query-center/preview', { ...row, limit: 100 })
        toast({ title: 'Vorschau erstellt', description: 'Maximal 100 Zeilen wurden sicher ausgewertet.' }); return
      }
      if (actionKey === 'export') {
        const reason = window.prompt('Grund (Audit):')?.trim(); if (!reason || reason.length < 5) return
        const bundle = await apiClient.post(`/api/v1/query-center/${encodeURIComponent(String(row.id ?? ''))}/export`, { reason })
        downloadJson(bundle); return
      }
      if (actionKey === 'create') {
        const name = window.prompt('Name der Abfrage:')?.trim(); if (!name) return
        const product = window.prompt('Freigegebenes Datenprodukt:')?.trim(); if (!product) return
        const fields = window.prompt('Felder (kommagetrennt):')?.split(',').map((field) => field.trim()).filter(Boolean) ?? []
        const reason = window.prompt('Grund (Audit):')?.trim(); if (!reason || reason.length < 5) return
        await apiClient.post('/api/v1/query-center', { name, data_product_id: product, selected_fields: fields, filter_spec: {}, aggregations: [], is_favorite: false, reason })
      } else if (actionKey === 'import') {
        const raw = window.prompt('Signiertes JSON einfuegen:')?.trim(); if (!raw) return
        const reason = window.prompt('Grund (Audit):')?.trim(); if (!reason || reason.length < 5) return
        await apiClient.post('/api/v1/query-center/import', { bundle: JSON.parse(raw), reason })
      } else return
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] }); toast({ title: 'Abfrage-Center aktualisiert' })
    } catch (error) {
      toast({ title: 'Aktion fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="abfrage-center" permissions={['reporting.query.write']} onAction={handleAction} />
}
