import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Lieferungs-Storno & Gutschrift-Übersicht (DOM-SALES-004.4).
 * Backend: app/api/v1/endpoints/sales_storno.py
 */

export type StornoDelivery = {
  lieferschein: string
  status: string | null
  rechnung: string | null
  storno_grund: string | null
  storno_moeglich: boolean
  storno_sperrgrund: string | null
  datum: string | null
}

export type CreditNote = { gutschrift: string; betrag: number | null; status: string | null; grund: string | null }

export type StornoStatus = {
  found: boolean
  detail?: string
  order_number?: string
  kunde?: string | null
  lieferscheine?: StornoDelivery[]
  gutschriften?: CreditNote[]
  summary?: { lieferscheine: number; storniert: number; gutschriften: number }
}

const BASE = '/api/v1/sales'

export function useStornoStatus(auftrag: string | null) {
  return useQuery({
    queryKey: ['sales-storno', 'status', auftrag],
    enabled: !!auftrag,
    queryFn: async () => (await apiClient.get<StornoStatus>(`${BASE}/storno/status`, { params: { auftrag } })).data,
  })
}

export function useStornoDelivery(auftrag: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { lieferschein: string; grund: string }) =>
      (await apiClient.post<{ ok: boolean; status: string }>(`${BASE}/deliveries/${encodeURIComponent(input.lieferschein)}/storno`, { grund: input.grund })).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['sales-storno', 'status', auftrag] })
      void qc.invalidateQueries({ queryKey: ['sales-match', 'detail', auftrag] })
    },
  })
}
