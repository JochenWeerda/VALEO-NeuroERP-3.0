import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Auftrag-↔-Lieferschein-Positions-Match (DOM-SALES-004.2).
 * Backend: app/api/v1/endpoints/sales_match.py
 */

export type SalesMatchPosition = {
  pos_nr: number
  artikel_nr: string | null
  bezeichnung: string | null
  einheit: string | null
  einzelpreis: number | null
  wert_offen: number | null
  bestellt: number
  geliefert: number
  offen: number
  status: 'offen' | 'teilgeliefert' | 'vollstaendig' | 'ueberliefert' | 'ohne_menge' | string
  abweichung_pct: number
  abweichung: boolean
}

export type SalesMatchDelivery = { lieferschein: string; datum: string | null; status: string | null; rechnung: string | null }

export type SalesMatch = {
  found: boolean
  detail?: string
  order_number?: string
  kunde?: string | null
  status?: string | null
  positionen?: SalesMatchPosition[]
  lieferscheine?: SalesMatchDelivery[]
  luecken?: Array<{ pos_nr: number; schwere: string; text: string }>
  summary?: {
    positionen: number
    vollstaendig_geliefert: boolean
    hat_abweichung: boolean
    offen_positionen: number
    lieferscheine: number
    offene_luecken: number
  }
}

export type SalesMatchOrderRow = {
  order_number: string
  kunde: string | null
  status: string | null
  betrag: number | null
  positionen: number
  hat_lieferschein: boolean
}

const BASE = '/api/v1/sales/match'

export function useSalesMatchOrders() {
  return useQuery({
    queryKey: ['sales-match', 'orders'],
    queryFn: async () => (await apiClient.get<{ items: SalesMatchOrderRow[] }>(`${BASE}/orders`)).data?.items ?? [],
  })
}

export function useSalesMatch(auftrag: string | null) {
  return useQuery({
    queryKey: ['sales-match', 'detail', auftrag],
    enabled: !!auftrag,
    queryFn: async () => (await apiClient.get<SalesMatch>(BASE, { params: { auftrag } })).data,
  })
}
