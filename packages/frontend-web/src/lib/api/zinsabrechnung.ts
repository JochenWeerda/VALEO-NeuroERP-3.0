/**
 * Zinsabrechnung — TanStack Query Hooks für /api/v1/zinsabrechnung
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type ZinsabrechnungStatus = 'berechnet' | 'gebucht' | 'storniert'

export type Zinsabrechnung = {
  id: string
  kontrakt_nr: string
  lieferant_nr: string
  lieferant_name: string | null
  zinssatz_prozent: number
  basisbetrag_eur: number
  von_datum: string
  bis_datum: string
  tage: number
  zinsbetrag_eur: number
  mwst_satz: number
  mwst_betrag_eur: number
  status: ZinsabrechnungStatus
  beleg_nr: string | null
  buchungs_periode: string | null
  created_at: string
}

export type ZinsabrechnungCreate = {
  kontrakt_nr: string
  lieferant_nr: string
  lieferant_name?: string | null
  zinssatz_prozent: number
  basisbetrag_eur: number
  von_datum: string
  bis_datum: string
  mwst_satz?: number
  buchungs_periode?: string | null
  bemerkung?: string | null
}

// ========== QUERY KEYS ==========

export const zabrKeys = {
  list: (params?: Record<string, string>) => ['zinsabrechnung', params ?? {}] as const,
}

const BASE = '/api/v1/zinsabrechnung'

// ========== HOOKS ==========

export function useZinsabrechnungen(params?: {
  kontrakt_nr?: string
  lieferant_nr?: string
  status?: ZinsabrechnungStatus
}) {
  return useQuery({
    queryKey: zabrKeys.list(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<Zinsabrechnung[]>(BASE, { params: params ?? {} })
      return res.data
    },
  })
}

export function useCreateZinsabrechnung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ZinsabrechnungCreate) => {
      const res = await apiClient.post<Zinsabrechnung>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zinsabrechnung'] })
    },
  })
}

export function useBuchenZinsabrechnung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post<Zinsabrechnung>(`${BASE}/${id}/buchen`)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zinsabrechnung'] })
    },
  })
}

export function useStornierenZinsabrechnung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post<Zinsabrechnung>(`${BASE}/${id}/stornieren`)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zinsabrechnung'] })
    },
  })
}
