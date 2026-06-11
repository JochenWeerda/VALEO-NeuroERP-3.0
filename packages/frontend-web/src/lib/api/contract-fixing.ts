import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kontrakt-Fixierung & MATIF-Bewertung (DOM-CON-004.2).
 * Teilfixierung MATIF-bepreister Kontrakte + Mark-to-Market gegen Marktnotierung.
 * Backend: app/api/v1/endpoints/contract_fixing.py
 */

export type Fixing = {
  fixing_no: number
  menge: number | null
  matif_price: number | null
  praemie: number | null
  effektiv_preis: number | null
  datum: string | null
  referenz: string | null
  notiz: string | null
  bediener: string | null
}

export type FixingPosition = {
  position_no: number
  line_id: string
  artikel: string | null
  bezeichnung: string | null
  is_matif: boolean
  menge_kontrakt: number | null
  fixiert: number | null
  offen_zu_fixieren: number | null
  fixierungsgrad_pct: number
  avg_fixpreis_effektiv: number | null
  symbol: string | null
  notierung: { preis: number; datum: string; markt_effektiv: number; quelle: string | null } | null
  bewertung_fixiert_eur: number | null
  marktwert_offen_eur: number | null
  fixings: Fixing[]
}

export type FixingWorkspace = {
  found: boolean
  detail?: string
  contract_no?: string
  contract_type?: string
  party_id?: string | null
  einheit?: string | null
  status?: string | null
  pricing?: { modell: string | null; praemie_typ: string | null; praemie_wert: number | null; basis: string | null }
  positionen?: FixingPosition[]
  summary?: {
    menge_kontrakt: number
    fixiert: number
    offen_zu_fixieren: number
    fixierungsgrad_pct: number
    bewertbar: boolean
    bewertung_fixiert_eur: number | null
    marktwert_offen_eur: number | null
  }
}

export type CreateFixingInput = {
  kontrakt: string
  position?: string
  menge: number
  matifPreis: number
  praemie?: number
  matifReferenz?: string
  notiz?: string
}

const BASE = '/api/v1/contracts'

export function useFixingWorkspace(kontrakt: string | null) {
  return useQuery({
    queryKey: ['contract-fixing', 'workspace', kontrakt],
    enabled: !!kontrakt,
    queryFn: async () => {
      const res = await apiClient.get<FixingWorkspace>(`${BASE}/fixing/workspace`, { params: { kontrakt } })
      return res.data
    },
  })
}

export function useCreateFixing() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: CreateFixingInput) =>
      (await apiClient.post<{ ok: boolean; fixing_no: number; offen_nach: number }>(`${BASE}/fixing`, input)).data,
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: ['contract-fixing', 'workspace', vars.kontrakt] })
    },
  })
}

export function useUpsertQuote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { symbol: string; preis: number; datum?: string }) =>
      (await apiClient.post<{ ok: boolean; symbol: string; price: number }>(`${BASE}/matif-quote`, input)).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['contract-fixing', 'workspace'] })
    },
  })
}
