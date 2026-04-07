/**
 * Schaeden (Schadenmeldungen) API Client
 * TanStack Query Hooks für Schadenmeldung und Versicherungen
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Versicherung = {
  id: string
  bezeichnung: string
  vertragsnummer: string
  typ: string
  versicherer: string
  gueltig_bis?: string
}

export type SchadenMeldungCreate = {
  art: string
  datum: string
  ort?: string
  beschreibung: string
  schadenhoehe: number
  versicherung_id?: string
  zeuge?: string
}

export type SchadenMeldungResponse = {
  id: string
  meldungsnummer: string
  art: string
  datum: string
  ort?: string
  beschreibung: string
  schadenhoehe: number
  versicherung_id?: string
  versicherung_bezeichnung?: string
  zeuge?: string
  status: string
  erstellt_am: string
  aktualisiert_am: string
}

// ========== QUERY KEYS ==========

export const schaedenKeys = {
  all: ['schaeden'] as const,
  versicherungen: () => [...schaedenKeys.all, 'versicherungen'] as const,
  meldungen: () => [...schaedenKeys.all, 'meldungen'] as const,
}

// ========== HOOKS ==========

export function useVersicherungen() {
  return useQuery({
    queryKey: schaedenKeys.versicherungen(),
    queryFn: async () => {
      const response = await apiClient.get<Versicherung[]>('/api/v1/schaeden/versicherungen')
      return response.data
    },
    initialData: [],
  })
}

export function useSchadenMeldungErstellen() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: SchadenMeldungCreate) => {
      const response = await apiClient.post<SchadenMeldungResponse>(
        '/api/v1/schaeden/meldungen',
        data,
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: schaedenKeys.meldungen() })
    },
  })
}
