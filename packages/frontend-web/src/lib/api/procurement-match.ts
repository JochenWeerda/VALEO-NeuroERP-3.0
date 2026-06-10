import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004): Bestellung ↔ Wareneingang.
 * Backend: app/api/v1/endpoints/procurement_match.py
 */

export type MatchOrder = {
  bestellnummer: string
  datum: string | null
  status: string
  netto_summe: number | null
  positionen: number
  hat_wareneingang: boolean
}

export type MatchPosition = {
  pos_nr: number
  artikel_nr: string | null
  bezeichnung: string | null
  einheit: string | null
  einzelpreis: number | null
  bestellt: number | null
  geliefert: number | null
  offen: number | null
  status: string
  abweichung_pct: number | null
  abweichung: boolean
  wert_offen: number | null
}

export type MatchResult = {
  found: boolean
  detail?: string
  bestellnummer?: string
  status?: string
  netto_summe?: number | null
  positionen?: MatchPosition[]
  wareneingaenge?: Array<{ gr_number: string; datum: string | null; status: string; lieferschein: string | null }>
  luecken?: Array<{ pos_nr: number; schwere: string; text: string }>
  summary?: { positionen: number; wareneingaenge: number; vollstaendig_geliefert: boolean; hat_abweichung: boolean; offene_luecken: number }
}

export function useMatchOrders(limit = 50) {
  return useQuery({
    queryKey: ['procurement-match', 'orders', limit],
    queryFn: async () => {
      const res = await apiClient.get<{ items: MatchOrder[] }>('/api/v1/procurement/match/orders', { params: { limit } })
      return res.data?.items ?? []
    },
  })
}

export function useMatch(bestellung: string | null) {
  return useQuery({
    queryKey: ['procurement-match', 'match', bestellung],
    enabled: !!bestellung,
    queryFn: async () => {
      const res = await apiClient.get<MatchResult>('/api/v1/procurement/match', { params: { bestellung } })
      return res.data
    },
  })
}
