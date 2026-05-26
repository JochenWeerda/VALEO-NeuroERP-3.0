/**
 * Vermehrungsverträge (Saatzucht) — TanStack Query Hooks für /api/v1/saatzucht/vermehrungsvertraege
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type VermehrungsvertragStatus = 'angelegt' | 'aktiv' | 'beendet' | 'storniert'
export type Kategorie = 'Z1' | 'Z2' | 'SE' | 'E' | 'B'

export type Vermehrungsvertrag = {
  id: string
  vertrag_nr: string
  erntejahr: number
  vermehrer_kunden_nr: string
  sorte_nr: string | null
  sorte_bezeichnung: string | null
  kategorie: Kategorie | null
  vertrags_menge_t: number | null
  anbauflaeche_ha: number | null
  lwk_anerkennungsstelle: string | null
  vmkz: string | null
  status: VermehrungsvertragStatus
  created_at: string
}

export type VermehrungsvertragCreate = {
  vertrag_nr: string
  erntejahr: number
  vermehrer_kunden_nr: string
  sorte_nr?: string | null
  sorte_bezeichnung?: string | null
  kategorie?: Kategorie | null
  vertrags_menge_t?: number | null
  anbauflaeche_ha?: number | null
  lwk_anerkennungsstelle?: string | null
  vmkz?: string | null
  bemerkung?: string | null
}

export type VermehrungsvertragUpdate = Partial<VermehrungsvertragCreate> & {
  status?: VermehrungsvertragStatus
}

// ========== QUERY KEYS ==========

export const vvKeys = {
  list: (params?: Record<string, unknown>) => ['vermehrungsvertraege', params ?? {}] as const,
}

const BASE = '/api/v1/saatzucht/vermehrungsvertraege'

// ========== HOOKS ==========

export function useVermehrungsvertraege(params?: {
  erntejahr?: number
  vermehrer_kunden_nr?: string
  status?: VermehrungsvertragStatus
}) {
  return useQuery({
    queryKey: vvKeys.list(params as Record<string, unknown>),
    queryFn: async () => {
      const res = await apiClient.get<Vermehrungsvertrag[]>(BASE, { params: params ?? {} })
      return res.data
    },
  })
}

export function useCreateVermehrungsvertrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: VermehrungsvertragCreate) => {
      const res = await apiClient.post<Vermehrungsvertrag>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vermehrungsvertraege'] })
    },
  })
}

export function useUpdateVermehrungsvertrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: VermehrungsvertragUpdate }) => {
      const res = await apiClient.patch<Vermehrungsvertrag>(`${BASE}/${id}`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vermehrungsvertraege'] })
    },
  })
}

export function useDeleteVermehrungsvertrag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${BASE}/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vermehrungsvertraege'] })
    },
  })
}
