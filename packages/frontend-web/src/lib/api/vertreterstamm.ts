import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ── Types ─────────────────────────────────────────────────────────────────────

export type Vertretergruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  aktiv: boolean
  created_at: string
}

export type VertretergruppeCreate = {
  gruppe_nr: string
  bezeichnung: string
}

export type Vertreter = {
  id: string
  vertreter_nr: string
  name: string
  vorname: string | null
  kuerzel: string | null
  telefon: string | null
  email: string | null
  vertretergruppe_nr: string | null
  provisionsgruppe_nr: string | null
  gebiet: string | null
  aktiv: boolean
  created_at: string
  updated_at: string
}

export type VertreterCreate = {
  vertreter_nr: string
  name: string
  vorname?: string | null
  kuerzel?: string | null
  telefon?: string | null
  email?: string | null
  vertretergruppe_nr?: string | null
  provisionsgruppe_nr?: string | null
  gebiet?: string | null
}

// ── Query Keys ────────────────────────────────────────────────────────────────

const keys = {
  gruppen: () => ['vertretergruppen'] as const,
  vertreter: (gruppeNr?: string) => ['vertreter', gruppeNr ?? ''] as const,
}

// ── Vertretergruppen ──────────────────────────────────────────────────────────

export function useVertretergruppen() {
  return useQuery({
    queryKey: keys.gruppen(),
    queryFn: async () => {
      const res = await apiClient.get<Vertretergruppe[]>('/api/v1/crm/vertreter/gruppen')
      return res.data
    },
  })
}

export function useCreateVertretergruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: VertretergruppeCreate) => {
      const res = await apiClient.post<Vertretergruppe>('/api/v1/crm/vertreter/gruppen', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.gruppen() })
    },
  })
}

export function useDeleteVertretergruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (gruppeNr: string) => {
      await apiClient.delete(`/api/v1/crm/vertreter/gruppen/${gruppeNr}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.gruppen() })
    },
  })
}

// ── Vertreter ─────────────────────────────────────────────────────────────────

export function useVertreter(gruppeNr?: string) {
  return useQuery({
    queryKey: keys.vertreter(gruppeNr),
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (gruppeNr) params.vertretergruppe_nr = gruppeNr
      const res = await apiClient.get<Vertreter[]>('/api/v1/crm/vertreter', { params })
      return res.data
    },
  })
}

export function useCreateVertreter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: VertreterCreate) => {
      const res = await apiClient.post<Vertreter>('/api/v1/crm/vertreter', payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vertreter'] })
    },
  })
}

export function useUpdateVertreter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ vertreterNr, payload }: { vertreterNr: string; payload: VertreterCreate }) => {
      const res = await apiClient.put<Vertreter>(`/api/v1/crm/vertreter/${vertreterNr}`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vertreter'] })
    },
  })
}

export function useDeleteVertreter() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vertreterNr: string) => {
      await apiClient.delete(`/api/v1/crm/vertreter/${vertreterNr}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vertreter'] })
    },
  })
}
