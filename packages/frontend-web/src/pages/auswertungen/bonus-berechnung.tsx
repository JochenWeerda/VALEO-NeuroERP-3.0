import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

const SCREEN_ID = 'auswertungen/bonus-berechnung'

export default function BonusBerechnungPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string, row: Record<string, unknown>): Promise<void> {
    try {
      if (actionKey === 'calculate') {
        const reportChoice = window.prompt('Berechnung: kunden oder artikelgruppe?', 'kunden')?.trim().toLowerCase()
        if (!reportChoice) return
        const reportId = reportChoice.startsWith('artikel') ? 'bonus-by-article-group' : 'bonus-by-customer'
        const year = new Date().getFullYear()
        const fromDate = window.prompt('Periode von (JJJJ-MM-TT)', `${year}-01-01`)?.trim()
        const toDate = window.prompt('Periode bis (JJJJ-MM-TT)', `${year}-12-31`)?.trim()
        const ratePct = Number(window.prompt('Bonussatz in Prozent', '1.00'))
        const reason = window.prompt('Berechnungsgrund (Audit):')?.trim()
        if (!fromDate || !toDate || !Number.isFinite(ratePct) || !reason || reason.length < 5) return
        await apiClient.post('/api/v1/l3-report-catalog/bonus-runs', {
          report_id: reportId, from_date: fromDate, to_date: toDate, rate_pct: ratePct, reason,
        })
      } else if (actionKey === 'correct') {
        const id = String(row.id ?? '')
        const amount = Number(window.prompt('Korrekturbetrag (negativ fuer Abzug)', '0.00'))
        const reason = window.prompt('Korrekturgrund (Audit):')?.trim()
        if (!id || !Number.isFinite(amount) || !reason || reason.length < 5) return
        await apiClient.post(`/api/v1/l3-report-catalog/bonus-runs/${encodeURIComponent(id)}/corrections`, { amount, reason })
      } else if (actionKey === 'export') {
        const id = String(row.id ?? '')
        const reason = window.prompt('Exportgrund (Audit):')?.trim()
        if (!id || !reason || reason.length < 5) return
        window.open(`/api/v1/l3-report-catalog/bonus-runs/${encodeURIComponent(id)}/export.csv?reason=${encodeURIComponent(reason)}`, '_blank', 'noopener,noreferrer')
        return
      } else return
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: actionKey === 'correct' ? 'Korrekturlauf angelegt' : 'Bonuslauf berechnet' })
    } catch (error) {
      toast({ title: 'Bonusverarbeitung fehlgeschlagen', description: error instanceof Error ? error.message : 'Unbekannter Fehler', variant: 'destructive' })
    }
  }

  return <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="bonus-berechnung" permissions={['reporting.bonus.write']} onAction={handleAction} />
}
