/**
 * Artikel-Bestandteile — TanStack Query Hooks für /api/v1/artikel/bestandteile
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type BestandteilDef = {
  id: string
  bestandteil_nr: string
  bezeichnung: string
  einheit: string | null
  grenzwert_min: number | null
  grenzwert_max: number | null
  nutzung: string | null
  typ_schad_naehr: string | null
  waage_qualitaet_nr: string | null
  aktiv: boolean
  created_at: string
}

export type BestandteilDefCreate = {
  bestandteil_nr: string
  bezeichnung: string
  einheit?: string | null
  grenzwert_min?: number | null
  grenzwert_max?: number | null
  nutzung?: string | null
  typ_schad_naehr?: string | null
  waage_qualitaet_nr?: string | null
}

// ========== QUERY KEYS ==========

export const abKeys = {
  list: () => ['artikel-bestandteile'] as const,
}

const BASE = '/api/v1/artikel/bestandteile'

// ========== HOOKS ==========

export function useBestandteilDefs() {
  return useQuery({
    queryKey: abKeys.list(),
    queryFn: async () => {
      const res = await apiClient.get<BestandteilDef[]>(`${BASE}/stamm`)
      return res.data
    },
  })
}

export function useCreateBestandteilDef() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: BestandteilDefCreate) => {
      const res = await apiClient.post<BestandteilDef>(`${BASE}/stamm`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: abKeys.list() })
    },
  })
}

export function useDeleteBestandteilDef() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (bestandteil_nr: string) => {
      await apiClient.delete(`${BASE}/stamm/${encodeURIComponent(bestandteil_nr)}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: abKeys.list() })
    },
  })
}
