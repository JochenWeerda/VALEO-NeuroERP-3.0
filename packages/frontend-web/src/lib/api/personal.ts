/**
 * Personal API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type MitarbeiterStatus = 'aktiv' | 'urlaub' | 'krank'

export type Mitarbeiter = {
  id: string
  name: string
  abteilung: string
  position: string
  eintrittsdatum: string
  status: MitarbeiterStatus
}

export type ZeitEintrag = {
  id: string
  mitarbeiter: string
  datum: string
  kommen: string
  gehen: string
  stunden: number
  typ: 'Arbeit' | 'Ueberstunden' | 'Urlaub'
}

export type SchulungTyp = 'PSM' | 'Gefahrstoffe' | 'Gabelstapler' | 'Erste Hilfe' | 'Brandschutz' | 'Arbeitssicherheit'
export type SchulungStatus = 'gueltig' | 'ablaufend' | 'abgelaufen'

export type Schulung = {
  id: string
  mitarbeiter: string
  personalnr: string
  thema: string
  typ: SchulungTyp
  datum: string
  dauer: number
  schulungsleiter: string
  zertifikatNr?: string
  gueltigBis?: string
  status: SchulungStatus
}

export type StundenzettelData = {
  datum: string
  fahrer: string
  kennzeichen: string
  touren: Array<{
    id: string
    start: string
    ende: string
    km: number
    pause: number
  }>
  gesamtArbeitszeit: number
  ueberstunden: number
  unterschrift?: string
}

export const personalKeys = {
  all: ['personal'] as const,
  mitarbeiter: (filters?: Record<string, unknown>) => [...personalKeys.all, 'mitarbeiter', filters] as const,
  zeiterfassung: (datum?: string) => [...personalKeys.all, 'zeit', datum] as const,
  schulungen: (filters?: Record<string, unknown>) => [...personalKeys.all, 'schulungen', filters] as const,
}

export function useMitarbeiter(filters?: { search?: string; status?: MitarbeiterStatus }) {
  return useQuery({
    queryKey: personalKeys.mitarbeiter(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      return (await apiClient.get<Mitarbeiter[]>(`/api/v1/personal/mitarbeiter?${String(params)}`)).data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useZeiterfassung(datum?: string) {
  return useQuery({
    queryKey: personalKeys.zeiterfassung(datum),
    queryFn: async () => {
      const params = datum ? `?datum=${datum}` : ''
      return (await apiClient.get<ZeitEintrag[]>(`/api/v1/personal/zeiterfassung${params}`)).data
    },
    staleTime: 30 * 1000,
  })
}

export function useSchulungen(filters?: { typ?: SchulungTyp; status?: SchulungStatus }) {
  return useQuery({
    queryKey: personalKeys.schulungen(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.typ) params.append('typ', filters.typ)
      if (filters?.status) params.append('status', filters.status)
      return (await apiClient.get<Schulung[]>(`/api/v1/personal/schulungen?${String(params)}`)).data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useSaveStundenzettel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: StundenzettelData) => (await apiClient.post<StundenzettelData>('/api/v1/personal/stundenzettel', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.zeiterfassung() })
    },
  })
}
