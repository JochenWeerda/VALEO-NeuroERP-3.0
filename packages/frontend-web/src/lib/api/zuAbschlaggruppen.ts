/**
 * Zu-/Abschlaggruppen [ZAGR], Zu-/Abschlagklassen [ZAKL] und Konditionen [ZAK]
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

export type ZuAbschlaggruppeCreate = {
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
}

export type ZuAbschlagklasse = {
  id: string
  klasse_nr: string
  bezeichnung: string
  richtung: Richtung
  aktiv: boolean
  created_at: string
}

export type ZuAbschlagklasseCreate = {
  klasse_nr: string
  bezeichnung: string
  richtung: Richtung
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

export type ZuAbschlagKonditionCreate = {
  gruppe_id: string
  klasse_id: string
  kondition_typ: KonditionTyp
  wert: number
  gueltig_ab: string
  gueltig_bis?: string | null
  beschreibung?: string | null
}

// ========== QUERY KEYS ==========

export const zaKeys = {
  gruppen: (richtung?: Richtung) => ['zu-abschlag', 'gruppen', richtung ?? 'all'] as const,
  klassen: (richtung?: Richtung) => ['zu-abschlag', 'klassen', richtung ?? 'all'] as const,
  konditionen: (params?: Record<string, string>) =>
    ['zu-abschlag', 'konditionen', params ?? {}] as const,
}

const BASE = '/api/v1/preise/zu-abschlaege'

// ========== ZU-/ABSCHLAGGRUPPEN ==========

export function useZuAbschlaggruppen(richtung?: Richtung) {
  return useQuery({
    queryKey: zaKeys.gruppen(richtung),
    queryFn: async () => {
      const params = richtung ? { richtung } : {}
      const res = await apiClient.get<ZuAbschlaggruppe[]>(`${BASE}/gruppen`, { params })
      return res.data
    },
  })
}

export function useCreateZuAbschlaggruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ZuAbschlaggruppeCreate) => {
      const res = await apiClient.post<ZuAbschlaggruppe>(`${BASE}/gruppen`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlag', 'gruppen'] })
    },
  })
}

export function useDeleteZuAbschlaggruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ gruppe_nr, richtung }: { gruppe_nr: string; richtung: Richtung }) => {
      await apiClient.delete(`${BASE}/gruppen/${encodeURIComponent(gruppe_nr)}`, {
        params: { richtung },
      })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlag', 'gruppen'] })
    },
  })
}

// ========== ZU-/ABSCHLAGKLASSEN ==========

export function useZuAbschlagklassen(richtung?: Richtung) {
  return useQuery({
    queryKey: zaKeys.klassen(richtung),
    queryFn: async () => {
      const params = richtung ? { richtung } : {}
      const res = await apiClient.get<ZuAbschlagklasse[]>(`${BASE}/klassen`, { params })
      return res.data
    },
  })
}

export function useCreateZuAbschlagklasse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ZuAbschlagklasseCreate) => {
      const res = await apiClient.post<ZuAbschlagklasse>(`${BASE}/klassen`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlag', 'klassen'] })
    },
  })
}

export function useDeleteZuAbschlagklasse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ klasse_nr, richtung }: { klasse_nr: string; richtung: Richtung }) => {
      await apiClient.delete(`${BASE}/klassen/${encodeURIComponent(klasse_nr)}`, {
        params: { richtung },
      })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlag', 'klassen'] })
    },
  })
}

// ========== KONDITIONEN ==========

export function useZuAbschlagKonditionen(params?: {
  gruppe_id?: string
  klasse_id?: string
}) {
  return useQuery({
    queryKey: zaKeys.konditionen(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<ZuAbschlagKondition[]>(`${BASE}/konditionen`, {
        params: params ?? {},
      })
      return res.data
    },
  })
}

export function useCreateZuAbschlagKondition() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ZuAbschlagKonditionCreate) => {
      const res = await apiClient.post<ZuAbschlagKondition>(`${BASE}/konditionen`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['zu-abschlag', 'konditionen'] })
    },
  })
}
