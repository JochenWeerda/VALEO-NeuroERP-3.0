/**
 * Etiketten (Label Printing) API Client
 * TanStack Query Hooks für Drucker und Druckaufträge
 */
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Drucker = {
  id: string
  name: string
  standort: string
  typ: string
  modell: string
  status: string
  ip?: string
}

export type DruckauftragCreate = {
  chargen_id: string
  artikel?: string
  menge?: number
  lieferant?: string
  eingang?: string
  anzahl_etiketten: number
  drucker_id: string
}

export type DruckauftragResponse = {
  id: string
  auftrags_nr: string
  chargen_id: string
  artikel?: string
  menge?: number
  lieferant?: string
  eingang?: string
  anzahl_etiketten: number
  drucker_id: string
  drucker_name: string
  status: string
  erstellt_am: string
}

// ========== QUERY KEYS ==========

export const etikettenKeys = {
  all: ['etiketten'] as const,
  drucker: () => [...etikettenKeys.all, 'drucker'] as const,
}

// ========== HOOKS ==========

export function useDrucker() {
  return useQuery({
    queryKey: etikettenKeys.drucker(),
    queryFn: async () => {
      const response = await apiClient.get<Drucker[]>('/api/v1/etiketten/drucker')
      return response.data
    },
    initialData: [],
  })
}

export function useDruckauftragErstellen() {
  return useMutation({
    mutationFn: async (data: DruckauftragCreate) => {
      const response = await apiClient.post<DruckauftragResponse>(
        '/api/v1/etiketten/druckauftrag',
        data,
      )
      return response.data
    },
  })
}
