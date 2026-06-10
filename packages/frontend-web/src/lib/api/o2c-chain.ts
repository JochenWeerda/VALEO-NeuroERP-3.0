import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Order-to-Cash-Kette (DOM-SALES-004): Angebot→Auftrag→Lieferschein→Rechnung.
 * Backend: app/api/v1/endpoints/o2c_chain.py
 */

export type O2COrder = {
  order_number: string
  kunde: string | null
  status: string
  betrag: number | null
  datum: string | null
  hat_lieferschein: boolean
  hat_rechnung: boolean
  vollstaendig: boolean
}

export type O2CNode = {
  stage: 'angebot' | 'auftrag' | 'lieferschein' | 'rechnung'
  label: string
  ref: string | null
  status: string | null
  betrag?: number | null
  kunde?: string | null
  zeitpunkt?: string | null
  rechnung?: string | null
}

export type O2CResult = {
  found: boolean
  detail?: string
  order_number?: string
  kunde?: string | null
  kette?: O2CNode[]
  luecken?: Array<{ stufe: string; schwere: string; text: string }>
  summary?: { stufen: number; lieferscheine: number; rechnungen: number; status: string; vollstaendig: boolean; offene_luecken: number }
}

export function useO2COrders(limit = 50) {
  return useQuery({
    queryKey: ['o2c', 'orders', limit],
    queryFn: async () => {
      const res = await apiClient.get<{ items: O2COrder[] }>('/api/v1/sales/o2c/orders', { params: { limit } })
      return res.data?.items ?? []
    },
  })
}

export function useO2C(auftrag: string | null) {
  return useQuery({
    queryKey: ['o2c', 'chain', auftrag],
    enabled: !!auftrag,
    queryFn: async () => {
      const res = await apiClient.get<O2CResult>('/api/v1/sales/o2c', { params: { auftrag } })
      return res.data
    },
  })
}
