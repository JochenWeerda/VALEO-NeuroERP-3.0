/**
 * Massebilanz — TanStack Query Hooks für /api/v1/massebilanz
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type MassebilanzStatus = 'offen' | 'festgeschrieben'
export type Vorzeichen = '+' | '-'

export type Massebilanz = {
  id: string
  periode: string
  artikel_nr: string | null
  lager_nr: string | null
  anfangsbestand_kg: number
  zugaenge_kg: number
  abgaenge_kg: number
  endbestand_kg: number
  differenz_kg: number
  status: MassebilanzStatus
  festgeschrieben_am: string | null
  created_at: string
}

export type MassebilanzCreate = {
  periode: string
  artikel_nr?: string | null
  lager_nr?: string | null
  anfangsbestand_kg?: number
  bemerkung?: string | null
}

export type Bewegung = {
  id: string
  buchungsdatum: string
  menge_kg: number
  vorzeichen: Vorzeichen
  beleg_nr: string | null
  beleg_typ: string | null
  kontrakt_nr: string | null
  lieferant_nr: string | null
  storniert: boolean
  created_at: string
}

export type BewegungCreate = {
  buchungsdatum: string
  menge_kg: number
  vorzeichen: Vorzeichen
  beleg_nr?: string | null
  beleg_typ?: string | null
  kontrakt_nr?: string | null
  lieferant_nr?: string | null
}

// ========== QUERY KEYS ==========

export const mbKeys = {
  list: (params?: Record<string, string>) => ['massebilanz', params ?? {}] as const,
  bewegungen: (bilanz_id: string) => ['massebilanz', bilanz_id, 'bewegungen'] as const,
}

const BASE = '/api/v1/massebilanz'

// ========== HOOKS ==========

export function useMassebilanzen(params?: {
  periode?: string
  artikel_nr?: string
  lager_nr?: string
  status?: MassebilanzStatus
}) {
  return useQuery({
    queryKey: mbKeys.list(params as Record<string, string>),
    queryFn: async () => {
      const res = await apiClient.get<Massebilanz[]>(BASE, { params: params ?? {} })
      return res.data
    },
  })
}

export function useCreateMassebilanz() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MassebilanzCreate) => {
      const res = await apiClient.post<Massebilanz>(BASE, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['massebilanz'] })
    },
  })
}

export function useMassebilanzBewegungen(bilanz_id: string) {
  return useQuery({
    queryKey: mbKeys.bewegungen(bilanz_id),
    queryFn: async () => {
      const res = await apiClient.get<Bewegung[]>(`${BASE}/${bilanz_id}/bewegungen`)
      return res.data
    },
    enabled: Boolean(bilanz_id),
  })
}

export function useCreateBewegung(bilanz_id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: BewegungCreate) => {
      const res = await apiClient.post<Bewegung>(`${BASE}/${bilanz_id}/bewegungen`, payload)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mbKeys.bewegungen(bilanz_id) })
      qc.invalidateQueries({ queryKey: ['massebilanz'] })
    },
  })
}

export function useFestschreibenMassebilanz() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (bilanz_id: string) => {
      const res = await apiClient.post<Massebilanz>(`${BASE}/${bilanz_id}/festschreiben`)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['massebilanz'] })
    },
  })
}
