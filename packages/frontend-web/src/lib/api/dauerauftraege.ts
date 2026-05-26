/**
 * Daueraufträge [DA] — TanStack Query Hooks für /api/v1/dauerauftraege
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type PeriodTyp = 'monatlich' | 'woechentlich' | 'quartalsweise' | 'jaehrlich'

export type DauerauftragPosition = {
  id: string
  pos_nr: number
  artikel_nr: string
  menge: number
  mengeneinheit: string | null
  preis_eur: number | null
}

export type Dauerauftrag = {
  id: string
  da_nr: string
  kunden_nr: string
  bezeichnung: string | null
  da_anfang: string
  da_naechster: string
  da_ende: string | null
  perioden_typ: PeriodTyp
  perioden_wert: number
  aktiv: boolean
  letzter_lauf: string | null
  positionen: DauerauftragPosition[]
}

export type DauerauftragPositionCreate = {
  pos_nr: number
  artikel_nr: string
  menge: number
  mengeneinheit?: string | null
  preis_eur?: number | null
}

export type DauerauftragCreate = {
  da_nr?: string
  kunden_nr: string
  bezeichnung?: string | null
  da_anfang: string
  da_naechster: string
  da_ende?: string | null
  perioden_typ?: PeriodTyp
  perioden_wert?: number
  positionen: DauerauftragPositionCreate[]
}

// ========== QUERY KEYS ==========

export const daKeys = {
  list: (params?: Record<string, string>) => ['dauerauftraege', params ?? {}] as const,
}

const BASE = '/api/v1/dauerauftraege'

// ========== HOOKS ==========

export function useDauerauftraege(params?: { kunden_nr?: string; aktiv?: boolean }) {
  return useQuery({
    queryKey: daKeys.list(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<Dauerauftrag[]>(BASE, { params: params ?? {} })
      return res.data
    },
  })
}

export function useCreateDauerauftrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: DauerauftragCreate) => {
      const res = await apiClient.post<Dauerauftrag>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['dauerauftraege'] })
    },
  })
}

export function useDeleteDauerauftrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (da_nr: string) => {
      await apiClient.delete(`${BASE}/${encodeURIComponent(da_nr)}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['dauerauftraege'] })
    },
  })
}

export function useStartenDauerauftrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (da_nr: string) => {
      const res = await apiClient.post<{ rechnung_nr: string }>(
        `${BASE}/${encodeURIComponent(da_nr)}/starten`
      )
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['dauerauftraege'] })
    },
  })
}
