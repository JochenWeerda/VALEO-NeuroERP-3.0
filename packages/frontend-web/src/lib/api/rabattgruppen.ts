/**
 * Rabattgruppen, Rabattklassen und Rabattsätze API Client
 * TanStack Query Hooks für /api/v1/preise/rabatte
 * Entitäten: Rabattgruppen [RAG], Rabattklassen [RAK], Rabattsätze
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Richtung = 'EK' | 'VK'

export type Rabattgruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
  aktiv: boolean
  created_at: string
}

export type RabattgruppeCreate = {
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
}

export type Rabattklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: Richtung
  aktiv: boolean
  created_at: string
}

export type RabattklasseCreate = {
  klasse_nr: string
  bezeichnung: string
  richtung: Richtung
}

export type Rabattsatz = {
  id: string
  rabattgruppe_nr: string
  rabattklasse_nr: string
  richtung: Richtung
  rabatt_prozent: number
  ab_menge: number | null
  gueltig_ab: string | null
  gueltig_bis: string | null
  created_at: string
}

export type RabattsatzCreate = {
  rabattgruppe_nr: string
  rabattklasse_nr: string
  richtung: Richtung
  rabatt_prozent: number
  ab_menge?: number | null
  gueltig_ab?: string | null
  gueltig_bis?: string | null
}

// ========== QUERY KEYS ==========

export const rabattKeys = {
  gruppen: (richtung?: Richtung) => ['rabatt', 'gruppen', richtung ?? 'all'] as const,
  klassen: (richtung?: Richtung) => ['rabatt', 'klassen', richtung ?? 'all'] as const,
  saetze: (params?: Record<string, string>) => ['rabatt', 'saetze', params ?? {}] as const,
}

// ========== RABATTGRUPPEN ==========

export function useRabattgruppen(richtung?: Richtung) {
  return useQuery({
    queryKey: rabattKeys.gruppen(richtung),
    queryFn: async () => {
      const params = richtung ? { richtung } : {}
      const res = await apiClient.get<Rabattgruppe[]>('/api/v1/preise/rabatte/gruppen', { params })
      return res.data
    },
  })
}

export function useCreateRabattgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RabattgruppeCreate) => {
      const res = await apiClient.post<Rabattgruppe>('/api/v1/preise/rabatte/gruppen', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rabatt', 'gruppen'] })
    },
  })
}

export function useDeleteRabattgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/preise/rabatte/gruppen/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rabatt', 'gruppen'] })
    },
  })
}

// ========== RABATTKLASSEN ==========

export function useRabattklassen(richtung?: Richtung) {
  return useQuery({
    queryKey: rabattKeys.klassen(richtung),
    queryFn: async () => {
      const params = richtung ? { richtung } : {}
      const res = await apiClient.get<Rabattklasse[]>('/api/v1/preise/rabatte/klassen', { params })
      return res.data
    },
  })
}

export function useCreateRabattklasse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RabattklasseCreate) => {
      const res = await apiClient.post<Rabattklasse>('/api/v1/preise/rabatte/klassen', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rabatt', 'klassen'] })
    },
  })
}

export function useDeleteRabattklasse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/preise/rabatte/klassen/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rabatt', 'klassen'] })
    },
  })
}

// ========== RABATTSÄTZE ==========

export function useRabattsaetze(params?: {
  rabattgruppe_nr?: string
  rabattklasse_nr?: string
  richtung?: Richtung
}) {
  return useQuery({
    queryKey: rabattKeys.saetze(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<Rabattsatz[]>('/api/v1/preise/rabatte/saetze', {
        params: params ?? {},
      })
      return res.data
    },
  })
}

export function useCreateRabattsatz() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RabattsatzCreate) => {
      const res = await apiClient.post<Rabattsatz>('/api/v1/preise/rabatte/saetze', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rabatt', 'saetze'] })
    },
  })
}

export function useDeleteRabattsatz() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/preise/rabatte/saetze/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['rabatt', 'saetze'] })
    },
  })
}
