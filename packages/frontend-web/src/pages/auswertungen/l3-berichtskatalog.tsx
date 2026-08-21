import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'auswertungen/l3-berichtskatalog'

export default function L3BerichtskatalogPage(): JSX.Element {
  const { toast } = useToast()
  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    const reportId = encodeURIComponent(String(row.id ?? '')); const today = new Date(); const from = new Date(today); from.setFullYear(today.getFullYear() - 1)
    const query = `from_date=${from.toISOString().slice(0, 10)}&to_date=${today.toISOString().slice(0, 10)}`
    try {
      if (actionKey === 'export') { const reason = window.prompt('Exportgrund (Audit):')?.trim(); if (!reason || reason.length < 5) return; window.open(`/api/v1/l3-report-catalog/${reportId}/export.csv?${query}&reason=${encodeURIComponent(reason)}`, '_blank', 'noopener,noreferrer'); return }
      if (actionKey === 'run') { const result = await apiClient.get<Record<string, unknown>>(`/api/v1/l3-report-catalog/${reportId}/run?${query}`); toast({ title: String(row.title ?? 'Bericht'), description: `${String(result.total ?? 0)} Ergebnisgruppen berechnet.` }); return }
      if (actionKey === 'drilldown') { const value = window.prompt('Dimensions-ID fuer Beleg-Drilldown:')?.trim(); if (!value) return; const items = await apiClient.get<unknown[]>(`/api/v1/l3-report-catalog/${reportId}/drilldown?${query}&dimension_value=${encodeURIComponent(value)}`); toast({ title: 'Beleg-Drilldown', description: `${items.length} Quellbelege gefunden.` }) }
    } catch (error) { toast({ title: 'Bericht fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' }) }
  }
  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="l3-berichtskatalog" permissions={['reporting.catalog.read']} onAction={handleAction} />
}
