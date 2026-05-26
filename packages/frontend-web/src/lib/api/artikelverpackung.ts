/**
 * Artikelverpackung — TanStack Query Hooks für /api/v1/artikel/verpackungen
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type ArtikelVerpackung = {
  id: string
  verpackungs_nr: string
  bezeichnung: string
  stufen: number
  stufe1_bezeichnung: string | null
  stufe1_menge: number | null
  stufe1_einheit: string | null
  stufe1_gewicht_kg: number | null
  stufe2_bezeichnung: string | null
  stufe2_menge: number | null
  stufe2_einheit: string | null
  stufe2_gewicht_kg: number | null
  stufe3_bezeichnung: string | null
  stufe3_menge: number | null
  stufe3_einheit: string | null
  stufe3_gewicht_kg: number | null
  aktiv: boolean
  created_at: string
}

export type ArtikelVerpackungCreate = {
  verpackungs_nr: string
  bezeichnung: string
  stufen?: number
  stufe1_bezeichnung?: string | null
  stufe1_menge?: number | null
  stufe1_einheit?: string | null
  stufe1_gewicht_kg?: number | null
  stufe2_bezeichnung?: string | null
  stufe2_menge?: number | null
  stufe2_einheit?: string | null
  stufe2_gewicht_kg?: number | null
  stufe3_bezeichnung?: string | null
  stufe3_menge?: number | null
  stufe3_einheit?: string | null
  stufe3_gewicht_kg?: number | null
}

// ========== QUERY KEYS ==========

export const avKeys = {
  list: () => ['artikel-verpackung'] as const,
}

const BASE = '/api/v1/artikel/verpackungen'

// ========== HOOKS ==========

export function useArtikelVerpackungen() {
  return useQuery({
    queryKey: avKeys.list(),
    queryFn: async () => {
      const res = await apiClient.get<ArtikelVerpackung[]>(BASE)
      return res.data
    },
  })
}

export function useCreateArtikelVerpackung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ArtikelVerpackungCreate) => {
      const res = await apiClient.post<ArtikelVerpackung>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: avKeys.list() })
    },
  })
}

export function useDeleteArtikelVerpackung() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (verpackungs_nr: string) => {
      await apiClient.delete(`${BASE}/${encodeURIComponent(verpackungs_nr)}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: avKeys.list() })
    },
  })
}
