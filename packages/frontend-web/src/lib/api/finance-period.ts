import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Periodenabschluss & Storno-Konsistenz (DOM-FIN-004.4).
 * Backend: app/api/v1/endpoints/finance_period.py
 */

export type AccountingPeriod = {
  period: string
  start: string
  end: string
  status: 'offen' | 'closed' | string
  closed_at: string | null
  closed_by: string | null
  offen_count: number
  storno_inkonsistent: number
  abschlussreif: boolean
}

const BASE = '/api/v1/finance/perioden'

export function usePeriods() {
  return useQuery({
    queryKey: ['finance-period', 'list'],
    queryFn: async () => (await apiClient.get<{ items: AccountingPeriod[] }>(BASE)).data?.items ?? [],
  })
}

export function useClosePeriod() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { period: string; force?: boolean }) =>
      (await apiClient.post<{ ok: boolean; status: string; erzwungen: boolean }>(`${BASE}/${encodeURIComponent(input.period)}/close`, { force: input.force ?? false })).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['finance-period'] }) },
  })
}

export function useReopenPeriod() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { period: string; grund: string }) =>
      (await apiClient.post<{ ok: boolean; status: string }>(`${BASE}/${encodeURIComponent(input.period)}/reopen`, { grund: input.grund })).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['finance-period'] }) },
  })
}
