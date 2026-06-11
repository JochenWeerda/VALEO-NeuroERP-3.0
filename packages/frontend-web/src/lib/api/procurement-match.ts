import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
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

export type MatchInvoice = {
  id: string
  rechnungsnummer: string
  datum: string | null
  gesamt_netto: number | null
  status: string | null
}

export type ThreeWaySummary = {
  bestellt_wert: number | null
  geliefert_wert: number | null
  fakturiert_netto: number | null
  bezug: number | null
  fakturiert: number | null
  differenz: number | null
  abweichung_pct: number | null
  status: string
  abweichung: boolean
  drei_wege_abgeglichen: boolean
}

export type MatchException = {
  pos_nr?: number
  schwere: string
  code?: string
  text: string
}

export type MatchFollowUp = {
  id: string
  action_type: string
  ausnahme_code: string | null
  grund: string
  eskalationsstufe: number
  created_at: string | null
  created_by: string | null
}

export type FollowUpCreate = {
  bestellnummer: string
  action_type: 'nachforderung' | 'reklamation' | 'eskalation' | 'freigabe'
  grund: string
  ausnahme_code?: string | null
  created_by?: string | null
}

export type ErsPreview = {
  betrag_netto: number
  positionen: Array<Record<string, unknown>>
  berechtigt: boolean
  anzahl_zeilen: number
}

export type ErsCredit = {
  id: string
  gutschrift_nummer: string
  betrag_netto: number
  grund: string
  ausnahme_code: string | null
  status: string
  positionen: Array<Record<string, unknown>>
  created_at: string | null
  created_by: string | null
}

export type ErsCreditCreate = {
  bestellnummer: string
  grund?: string | null
  created_by?: string | null
}

export type MatchResult = {
  found: boolean
  detail?: string
  bestellnummer?: string
  status?: string
  netto_summe?: number | null
  positionen?: MatchPosition[]
  wareneingaenge?: Array<{ gr_number: string; datum: string | null; status: string; lieferschein: string | null }>
  luecken?: MatchException[]
  rechnungen?: MatchInvoice[]
  three_way?: ThreeWaySummary
  ausnahmen?: MatchException[]
  follow_ups?: MatchFollowUp[]
  ers_preview?: ErsPreview
  ers_credits?: ErsCredit[]
  summary?: {
    positionen: number
    wareneingaenge: number
    vollstaendig_geliefert: boolean
    hat_abweichung: boolean
    offene_luecken: number
    rechnungen?: number
    drei_wege_abgeglichen?: boolean
    hat_ausnahme?: boolean
  }
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

export function useMatch(bestellung: string | null, threeWay = true) {
  return useQuery({
    queryKey: ['procurement-match', threeWay ? 'three-way' : 'match', bestellung],
    enabled: !!bestellung,
    queryFn: async () => {
      const path = threeWay ? '/api/v1/procurement/match/three-way' : '/api/v1/procurement/match'
      const res = await apiClient.get<MatchResult>(path, { params: { bestellung } })
      return res.data
    },
  })
}

export function useCreateFollowUp(bestellung: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: FollowUpCreate) => {
      const res = await apiClient.post<MatchFollowUp>('/api/v1/procurement/match/follow-up', body)
      return res.data
    },
    onSuccess: () => {
      if (bestellung) {
        void qc.invalidateQueries({ queryKey: ['procurement-match', 'three-way', bestellung] })
      }
    },
  })
}

export function useCreateErsCredit(bestellung: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: ErsCreditCreate) => {
      const res = await apiClient.post<ErsCredit>('/api/v1/procurement/match/ers', body)
      return res.data
    },
    onSuccess: () => {
      if (bestellung) {
        void qc.invalidateQueries({ queryKey: ['procurement-match', 'three-way', bestellung] })
      }
    },
  })
}
