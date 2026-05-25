import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ── Types ─────────────────────────────────────────────────────────────────────

export type Hausbank = {
  id: string
  bank_nr: string
  bezeichnung: string
  iban: string
  bic: string | null
  bank_name: string | null
  kontonummer: string | null
  blz: string | null
  waehrung: string
  erechnung_aktiv: boolean
  sepa_glaeubiger_id: string | null
  standard: boolean
  aktiv: boolean
  created_at: string
  updated_at: string
}

export type HausbankCreate = {
  bank_nr: string
  bezeichnung: string
  iban: string
  bic?: string | null
  bank_name?: string | null
  kontonummer?: string | null
  blz?: string | null
  waehrung?: string
  erechnung_aktiv?: boolean
  sepa_glaeubiger_id?: string | null
  standard?: boolean
}

// ── Query Keys ────────────────────────────────────────────────────────────────

const keys = {
  all: (nurAktive?: boolean) => ['hausbanken', nurAktive ?? true] as const,
}

// ── Hooks ─────────────────────────────────────────────────────────────────────

export function useHausbanken(nurAktive = true) {
  return useQuery({
    queryKey: keys.all(nurAktive),
    queryFn: async () => {
      const res = await apiClient.get<Hausbank[]>('/api/v1/stammdaten/hausbanken', {
        params: { nur_aktive: nurAktive },
      })
      return res.data
    },
  })
}

export function useCreateHausbank() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: HausbankCreate) => {
      const res = await apiClient.post<Hausbank>('/api/v1/stammdaten/hausbanken', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['hausbanken'] })
    },
  })
}

export function useUpdateHausbank() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ bankNr, payload }: { bankNr: string; payload: HausbankCreate }) => {
      const res = await apiClient.put<Hausbank>(`/api/v1/stammdaten/hausbanken/${bankNr}`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['hausbanken'] })
    },
  })
}

export function useDeleteHausbank() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (bankNr: string) => {
      await apiClient.delete(`/api/v1/stammdaten/hausbanken/${bankNr}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['hausbanken'] })
    },
  })
}
