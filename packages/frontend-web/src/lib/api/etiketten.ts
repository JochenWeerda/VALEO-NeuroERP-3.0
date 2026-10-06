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
  standort?: string | null
  typ?: string | null
  modell?: string | null
  status: 'online' | 'offline' | 'fehler' | 'wartung'
  ip?: string | null
  aktiv?: boolean
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
  drucker_name?: string | null
  status: 'ANGELEGT' | 'UEBERMITTELT' | 'GEDRUCKT' | 'FEHLER' | 'ABGEBROCHEN'
  /**
   * Der Versandstand, getrennt vom Auftragsstand. `NICHT_ANGEBUNDEN` heißt: Der
   * Auftrag ist gespeichert, aber es ist kein Spooler angebunden — es wurde
   * nichts gedruckt. Bis zum 06.10.2026 antwortete der Weg `status: "erstellt"`
   * und schrieb nicht einmal eine Zeile.
   */
  uebermittlung: 'NICHT_ANGEBUNDEN' | 'UEBERMITTELT'
  uebermittelt_am?: string | null
  gedruckt_am?: string | null
  fehler?: string | null
  created_at?: string | null
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
