/**
 * Lager API Client — Wave 11 Partiestamm & Partiegruppen
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type Partiegruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  aktiv: boolean
  created_at: string
}

export type PartiegruppeCreate = {
  gruppe_nr: string
  bezeichnung: string
}

export type Partiestamm = {
  id: string
  partie_nr: string
  bezeichnung: string | null
  artikel_nr: string
  lager_nr: string | null
  partie_typ: string
  gruppe_id: string | null
  erntejahr: number | null
  herkunftsland: string | null
  status: string
  aktiv: boolean
  created_at: string
}

export type PartiestammCreate = {
  partie_nr?: string | null
  bezeichnung?: string | null
  artikel_nr: string
  lager_nr?: string | null
  partie_typ?: string
  gruppe_id?: string | null
  erntejahr?: number | null
  herkunftsland?: string | null
}

export const PARTIE_TYPEN = ['artikelstamm', 'artikel_lager'] as const
export const PARTIE_STATUS = ['aktiv', 'gesperrt', 'abgeschlossen'] as const

export const lagerKeys = {
  all: ['lager'] as const,
  partien: (filters?: { artikel_nr?: string; lager_nr?: string; gruppe_id?: string; erntejahr?: number }) =>
    [...lagerKeys.all, 'partien', filters ?? {}] as const,
  partiegruppen: () => [...lagerKeys.all, 'partiegruppen'] as const,
}

export function usePartien(filters?: {
  artikel_nr?: string
  lager_nr?: string
  gruppe_id?: string
  erntejahr?: number
}) {
  return useQuery({
    queryKey: lagerKeys.partien(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.artikel_nr) params.set('artikel_nr', filters.artikel_nr)
      if (filters?.lager_nr) params.set('lager_nr', filters.lager_nr)
      if (filters?.gruppe_id) params.set('gruppe_id', filters.gruppe_id)
      if (filters?.erntejahr != null) params.set('erntejahr', String(filters.erntejahr))
      const suffix = params.size > 0 ? `?${params.toString()}` : ''
      return (await apiClient.get<Partiestamm[]>(`/api/v1/lager/partien${suffix}`)).data
    },
    placeholderData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function usePartiegruppen() {
  return useQuery({
    queryKey: lagerKeys.partiegruppen(),
    queryFn: async () =>
      (await apiClient.get<Partiegruppe[]>('/api/v1/lager/partien/gruppen')).data,
    placeholderData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useCreatePartie() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PartiestammCreate) =>
      (await apiClient.post<Partiestamm>('/api/v1/lager/partien', payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...lagerKeys.all, 'partien'] })
    },
  })
}

export function useSetPartieStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ partie_nr, status }: { partie_nr: string; status: string }) =>
      (
        await apiClient.patch<{ partie_nr: string; status: string }>(
          `/api/v1/lager/partien/${encodeURIComponent(partie_nr)}/status?status=${encodeURIComponent(status)}`,
        )
      ).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...lagerKeys.all, 'partien'] })
    },
  })
}

export function useDeletePartie() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (partie_nr: string) =>
      apiClient.delete(`/api/v1/lager/partien/${encodeURIComponent(partie_nr)}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...lagerKeys.all, 'partien'] })
    },
  })
}

export function useCreatePartiegruppe() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PartiegruppeCreate) =>
      (await apiClient.post<Partiegruppe>('/api/v1/lager/partien/gruppen', payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: lagerKeys.partiegruppen() }),
  })
}

export function useDeletePartiegruppe() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (gruppe_nr: string) =>
      apiClient.delete(`/api/v1/lager/partien/gruppen/${encodeURIComponent(gruppe_nr)}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: lagerKeys.partiegruppen() }),
  })
}
