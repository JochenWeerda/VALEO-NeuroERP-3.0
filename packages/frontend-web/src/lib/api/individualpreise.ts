/**
 * Individualpreise API Client
 * TanStack Query Hooks für /api/v1/preise/individualpreise
 * Entitäten: Individualpreise [PRI/PRIE]
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type PreisTyp = 'VK' | 'EK'

export type Individualpreis = {
  id: string
  preis_typ: PreisTyp
  artikel_nr: string
  partner_nr: string | null
  gueltig_von: string
  gueltig_bis: string | null
  preis_eur: number
  mengeneinheit: string | null
  staffel_menge: number
  waehrung: string
  notiz: string | null
  created_at: string
}

export type IndividualpreisCreate = {
  preis_typ: PreisTyp
  artikel_nr: string
  partner_nr?: string | null
  gueltig_von: string
  gueltig_bis?: string | null
  preis_eur: number
  staffel_menge?: number
  mengeneinheit?: string | null
  waehrung?: string
  notiz?: string | null
}

export type PreisLookupResult = {
  preis_eur: number
  preis_typ: PreisTyp
  artikel_nr: string
  partner_nr: string | null
  gueltig_von: string
  gueltig_bis: string | null
  mengeneinheit: string | null
  waehrung: string
}

// ========== QUERY KEYS ==========

export const individualpreisKeys = {
  list: (params?: Record<string, string>) => ['individualpreise', 'list', params ?? {}] as const,
  lookup: (params: Record<string, string>) => ['individualpreise', 'lookup', params] as const,
}

// ========== HOOKS ==========

export function useIndividualpreise(params?: {
  preis_typ?: PreisTyp
  artikel_nr?: string
  partner_nr?: string
  gueltig_am?: string
}) {
  return useQuery({
    queryKey: individualpreisKeys.list(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<Individualpreis[]>('/api/v1/preise/individualpreise', {
        params: params ?? {},
      })
      return res.data
    },
  })
}

export function useCreateIndividualpreis() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: IndividualpreisCreate) => {
      const res = await apiClient.post<Individualpreis>('/api/v1/preise/individualpreise', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['individualpreise'] })
    },
  })
}

export function useDeleteIndividualpreis() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/preise/individualpreise/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['individualpreise'] })
    },
  })
}

export function usePreisLookup(params: {
  artikel_nr: string
  partner_nr?: string
  preis_typ?: PreisTyp
  datum?: string
}) {
  return useQuery({
    queryKey: individualpreisKeys.lookup(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<PreisLookupResult>(
        '/api/v1/preise/individualpreise/lookup',
        { params },
      )
      return res.data
    },
    enabled: Boolean(params.artikel_nr),
  })
}
