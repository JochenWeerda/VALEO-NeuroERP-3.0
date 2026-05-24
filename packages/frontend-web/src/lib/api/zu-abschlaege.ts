/**
 * Zu-/Abschlaggruppen, -klassen und -konditionen API Client
 * TanStack Query Hooks für /api/v1/preise/zu-abschlaege
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Richtung = 'ek' | 'vk'
export type KonditionTyp = 'betrag' | 'prozent'

export type ZuAbschlaggruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
  aktiv: boolean
  created_at: string
}

export type ZuAbschlagklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: Richtung
  aktiv: boolean
  created_at: string
}

export type ZuAbschlagKondition = {
  id: string
  gruppe_id: string
  klasse_id: string
  kondition_typ: KonditionTyp
  wert: number
  gueltig_ab: string
  gueltig_bis: string | null
  beschreibung: string | null
  aktiv: boolean
  created_at: string
}

// ========== QUERY KEYS ==========

export const ZA_KEYS = {
  gruppen: (richtung?: Richtung) => ['zu-abschlaggruppen', richtung ?? 'all'] as const,
  klassen: (richtung?: Richtung) => ['zu-abschlagklassen', richtung ?? 'all'] as const,
  konditionen: (gruppeId?: string, klasseId?: string) =>
    ['zu-abschlag-konditionen', gruppeId ?? '', klasseId ?? ''] as const,
}

// ========== GRUPPEN ==========

export function useZuAbschlaggruppen(richtung?: Richtung) {
  return useQuery({
    queryKey: ZA_KEYS.gruppen(richtung),
    queryFn: async () => {
      const params = richtung ? `?richtung=${richtung}` : ''
      const res = await apiClient.get<ZuAbschlaggruppe[]>(
        `/api/v1/preise/zu-abschlaege/gruppen${params}`
      )
      return res.data
    },
  })
}

export function useCreateZuAbschlaggruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { gruppe_nr: string; bezeichnung: string; richtung: Richtung }) =>
      apiClient.post<ZuAbschlaggruppe>('/api/v1/preise/zu-abschlaege/gruppen', payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlaggruppen'] })
    },
  })
}

export function useDeleteZuAbschlaggruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ gruppe_nr, richtung }: { gruppe_nr: string; richtung: Richtung }) =>
      apiClient.delete(`/api/v1/preise/zu-abschlaege/gruppen/${gruppe_nr}?richtung=${richtung}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlaggruppen'] })
    },
  })
}

// ========== KLASSEN ==========

export function useZuAbschlagklassen(richtung?: Richtung) {
  return useQuery({
    queryKey: ZA_KEYS.klassen(richtung),
    queryFn: async () => {
      const params = richtung ? `?richtung=${richtung}` : ''
      const res = await apiClient.get<ZuAbschlagklasse[]>(
        `/api/v1/preise/zu-abschlaege/klassen${params}`
      )
      return res.data
    },
  })
}

export function useCreateZuAbschlagklasse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { klasse_nr: string; bezeichnung: string; richtung: Richtung }) =>
      apiClient.post<ZuAbschlagklasse>('/api/v1/preise/zu-abschlaege/klassen', payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlagklassen'] })
    },
  })
}

export function useDeleteZuAbschlagklasse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ klasse_nr, richtung }: { klasse_nr: string; richtung: Richtung }) =>
      apiClient.delete(`/api/v1/preise/zu-abschlaege/klassen/${klasse_nr}?richtung=${richtung}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlagklassen'] })
    },
  })
}

// ========== KONDITIONEN ==========

export function useZuAbschlagKonditionen(gruppeId?: string, klasseId?: string) {
  return useQuery({
    queryKey: ZA_KEYS.konditionen(gruppeId, klasseId),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (gruppeId) params.set('gruppe_id', gruppeId)
      if (klasseId) params.set('klasse_id', klasseId)
      const qs = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<ZuAbschlagKondition[]>(
        `/api/v1/preise/zu-abschlaege/konditionen${qs}`
      )
      return res.data
    },
  })
}

export function useCreateZuAbschlagKondition() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      gruppe_id: string
      klasse_id: string
      kondition_typ: KonditionTyp
      wert: number
      gueltig_ab: string
      gueltig_bis?: string | null
      beschreibung?: string | null
    }) => apiClient.post<ZuAbschlagKondition>('/api/v1/preise/zu-abschlaege/konditionen', payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlag-konditionen'] })
    },
  })
}
