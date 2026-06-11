import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Zahlungseingang / OP-Auszifferung (DOM-FIN-004.3).
 * Backend: app/api/v1/endpoints/finance_clearing.py
 */

export type Clearing = {
  datum: string | null
  betrag: number | null
  skonto: number | null
  ausgleich: number | null
  zahlungsart: string | null
  status: string | null
  storniert: boolean
}

export type PaymentInput = {
  rechnungsnr: string
  betrag: number
  skontoBetrag?: number
  zahlungsart?: string
}

const BASE = '/api/v1/finance/zahlungseingang'

export function useClearings(rechnungsnr: string | null) {
  return useQuery({
    queryKey: ['finance-clearing', rechnungsnr],
    enabled: !!rechnungsnr,
    queryFn: async () => (await apiClient.get<{ items: Clearing[] }>(`${BASE}/clearings`, { params: { rechnungsnr } })).data?.items ?? [],
  })
}

export function useRecordPayment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: PaymentInput) =>
      (await apiClient.post<{ ok: boolean; neu_offen: number; voll_ausgeziffert: boolean }>(BASE, input)).data,
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: ['finance-clearing', vars.rechnungsnr] })
      void qc.invalidateQueries({ queryKey: ['finance-op'] })
    },
  })
}
