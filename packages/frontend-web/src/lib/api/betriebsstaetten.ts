/**
 * Betriebsstätten/Filialen API Client
 * TanStack Query Hooks für /api/v1/stammdaten/betriebsstaetten
 * Direktsprung [FILS]
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Betriebsstaette = {
  id: string
  filial_nr: string
  bezeichnung: string
  ist_zentrale: boolean
  zentrale_filial_nr: string | null
  ident_untergrenze: number | null
  ident_obergrenze: number | null
  strasse: string | null
  plz: string | null
  ort: string | null
  land: string | null
  telefon: string | null
  email: string | null
  aktiv: boolean
  created_at: string
  untergeordnete: string[]
}

export type BetriebsstaetteCreate = {
  filial_nr: string
  bezeichnung: string
  ist_zentrale?: boolean
  zentrale_filial_nr?: string | null
  ident_untergrenze?: number | null
  ident_obergrenze?: number | null
  strasse?: string | null
  plz?: string | null
  ort?: string | null
  land?: string | null
  telefon?: string | null
  email?: string | null
}

// ========== QUERY KEYS ==========

export const betriebsstaetteKeys = {
  list: (params?: { nur_zentralen?: boolean; nur_aktive?: boolean }) =>
    ['betriebsstaetten', 'list', params ?? {}] as const,
  detail: (filialNr: string) => ['betriebsstaetten', 'detail', filialNr] as const,
}

// ========== HOOKS ==========

export function useBetriebsstaetten(params?: {
  nur_zentralen?: boolean
  nur_aktive?: boolean
}) {
  return useQuery({
    queryKey: betriebsstaetteKeys.list(params),
    queryFn: async () => {
      const res = await apiClient.get<Betriebsstaette[]>(
        '/api/v1/stammdaten/betriebsstaetten',
        { params: params ?? {} },
      )
      return res.data
    },
  })
}

export function useBetriebsstaette(filialNr: string) {
  return useQuery({
    queryKey: betriebsstaetteKeys.detail(filialNr),
    queryFn: async () => {
      const res = await apiClient.get<Betriebsstaette>(
        `/api/v1/stammdaten/betriebsstaetten/${filialNr}`,
      )
      return res.data
    },
    enabled: !!filialNr,
  })
}

export function useCreateBetriebsstaette() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: BetriebsstaetteCreate) => {
      const res = await apiClient.post<Betriebsstaette>(
        '/api/v1/stammdaten/betriebsstaetten',
        payload,
      )
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['betriebsstaetten'] })
    },
  })
}

export function useUpdateBetriebsstaette() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ filialNr, payload }: { filialNr: string; payload: BetriebsstaetteCreate }) => {
      const res = await apiClient.put<Betriebsstaette>(
        `/api/v1/stammdaten/betriebsstaetten/${filialNr}`,
        payload,
      )
      return res.data
    },
    onSuccess: (_data, { filialNr }) => {
      qc.invalidateQueries({ queryKey: ['betriebsstaetten'] })
      qc.invalidateQueries({ queryKey: betriebsstaetteKeys.detail(filialNr) })
    },
  })
}

export function useDeleteBetriebsstaette() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (filialNr: string) => {
      await apiClient.delete(`/api/v1/stammdaten/betriebsstaetten/${filialNr}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['betriebsstaetten'] })
    },
  })
}
