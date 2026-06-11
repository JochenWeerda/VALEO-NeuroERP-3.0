import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Mahnlauf & Mahnstufen-Eskalation (DOM-FIN-004.2).
 * Backend: app/api/v1/endpoints/finance_dunning.py
 */

export type DunningCandidate = {
  op_id: string
  rechnungsnr: string | null
  partner: string | null
  faelligkeit: string | null
  tage_ueberfaellig: number
  offen: number
  aktuelle_stufe: number
  naechste_stufe: number
  dunning_fee: number
  interest: number
  total_amount: number
}

export type DunningNotice = {
  stufe: number
  datum: string | null
  offen: number | null
  gebuehr: number | null
  zinsen: number | null
  gesamt: number | null
  frist: string | null
  status: string | null
  rechnungsnr: string | null
  partner: string | null
}

const BASE = '/api/v1/finance/mahnlauf'

export function useDunningCandidates() {
  return useQuery({
    queryKey: ['finance-dunning', 'candidates'],
    queryFn: async () => (await apiClient.get<{ items: DunningCandidate[] }>(`${BASE}/candidates`)).data?.items ?? [],
  })
}

export function useDunningNotices() {
  return useQuery({
    queryKey: ['finance-dunning', 'notices'],
    queryFn: async () => (await apiClient.get<{ items: DunningNotice[] }>(`${BASE}/notices`)).data?.items ?? [],
  })
}

export function useRunDunning() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { rechnungsnr?: string } = {}) =>
      (await apiClient.post<{ ok: boolean; erzeugt: number }>(`${BASE}/run`, input)).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['finance-dunning'] })
    },
  })
}
