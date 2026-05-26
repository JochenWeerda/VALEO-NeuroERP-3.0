/**
 * Mengeneinheiten & Einheitengruppen API Client
 * TanStack Query Hooks für /api/v1/artikel/mengeneinheiten
 * Entitäten: Mengeneinheiten, Mengeneinheitengruppen
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Mengeneinheit = {
  id: string
  einheit_kuerzel: string
  bezeichnung: string
  basis_einheit: string | null
  umrechnungsfaktor: number | null
  dezimalstellen: number
  aktiv: boolean
  created_at: string
}

export type MengeneinheitCreate = {
  einheit_kuerzel: string
  bezeichnung: string
  basis_einheit?: string | null
  umrechnungsfaktor?: number | null
  dezimalstellen?: number
}

export type Mengeneinheitengruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  bestand_einheit: string
  ek_einheit: string | null
  vk_einheit: string | null
  preis_einheit: string | null
  aktiv: boolean
  created_at: string
}

export type MengeneinheitengruppeCreate = {
  gruppe_nr: string
  bezeichnung: string
  bestand_einheit: string
  ek_einheit?: string | null
  vk_einheit?: string | null
  preis_einheit?: string | null
}

// ========== QUERY KEYS ==========

export const mengeneinheitKeys = {
  stamm: () => ['mengeneinheiten', 'stamm'] as const,
  gruppen: () => ['mengeneinheiten', 'gruppen'] as const,
}

// ========== MENGENEINHEITEN ==========

export function useMengeneinheiten() {
  return useQuery({
    queryKey: mengeneinheitKeys.stamm(),
    queryFn: async () => {
      const res = await apiClient.get<Mengeneinheit[]>('/api/v1/artikel/mengeneinheiten/stamm')
      return res.data
    },
  })
}

export function useCreateMengeneinheit() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MengeneinheitCreate) => {
      const res = await apiClient.post<Mengeneinheit>(
        '/api/v1/artikel/mengeneinheiten/stamm',
        payload,
      )
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mengeneinheitKeys.stamm() })
    },
  })
}

export function useDeleteMengeneinheit() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (einheit_kuerzel: string) => {
      await apiClient.delete(`/api/v1/artikel/mengeneinheiten/stamm/${einheit_kuerzel}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mengeneinheitKeys.stamm() })
    },
  })
}

// ========== MENGENEINHEITENGRUPPEN ==========

export function useMengeneinheitengruppen() {
  return useQuery({
    queryKey: mengeneinheitKeys.gruppen(),
    queryFn: async () => {
      const res = await apiClient.get<Mengeneinheitengruppe[]>(
        '/api/v1/artikel/mengeneinheiten/gruppen',
      )
      return res.data
    },
  })
}

export function useCreateMengeneinheitengruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MengeneinheitengruppeCreate) => {
      const res = await apiClient.post<Mengeneinheitengruppe>(
        '/api/v1/artikel/mengeneinheiten/gruppen',
        payload,
      )
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mengeneinheitKeys.gruppen() })
    },
  })
}

export function useDeleteMengeneinheitengruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (gruppe_nr: string) => {
      await apiClient.delete(`/api/v1/artikel/mengeneinheiten/gruppen/${gruppe_nr}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mengeneinheitKeys.gruppen() })
    },
  })
}
