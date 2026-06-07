/**
 * Artikel-Stoffstrom & THG (Fachliche Vertiefung Wave 3).
 * TanStack-Query-Hooks für /api/v1/artikel/stoffstrom.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/artikel/stoffstrom'

export type Stoffstrom = {
  id: string
  artikel_nr: string
  anbauland: string | null
  rohstoff_kategorie: string | null
  co2_aequivalent_kg_per_t: number | null
  thg_wert: number | null
  nachhaltig: boolean
  iscc_zertifiziert: boolean
  red_konform: boolean
  gueltig_ab: string | null
  gueltig_bis: string | null
  bemerkung: string | null
  created_at: string
  updated_at: string
}

export type StoffstromCreate = {
  artikel_nr: string
  anbauland?: string | null
  rohstoff_kategorie?: string | null
  co2_aequivalent_kg_per_t?: number | null
  thg_wert?: number | null
  nachhaltig?: boolean
  iscc_zertifiziert?: boolean
  red_konform?: boolean
  gueltig_ab?: string | null
  gueltig_bis?: string | null
  bemerkung?: string | null
}

export function useStoffstroeme() {
  return useQuery({
    queryKey: ['stoffstrom', 'list'],
    queryFn: async () => (await apiClient.get<Stoffstrom[]>(BASE)).data,
  })
}

export function useCreateStoffstrom() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: StoffstromCreate) => (await apiClient.post<Stoffstrom>(BASE, body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['stoffstrom'] }),
  })
}

export function useDeleteStoffstrom() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => (await apiClient.delete(`${BASE}/${encodeURIComponent(id)}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['stoffstrom'] }),
  })
}

export type ThgSummary = { artikel_nr: string; anzahl: number; avg_thg_wert: number | null; avg_co2: number | null }

export function useThgSummary() {
  return useQuery({
    queryKey: ['stoffstrom', 'thg-summary'],
    queryFn: async () => (await apiClient.get<ThgSummary[]>(`${BASE}/report/thg-summary`)).data,
  })
}
