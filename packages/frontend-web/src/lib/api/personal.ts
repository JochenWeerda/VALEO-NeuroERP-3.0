/**
 * Personal API Hooks
 * TanStack Query hooks for HR management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

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
  typ: 'Arbeit' | 'Überstunden' | 'Urlaub'
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

// ── Query Keys ─────────────────────────────────────────────────────────

export const personalKeys = {
  all: ['personal'] as const,
  mitarbeiter: (filters?: Record<string, unknown>) => [...personalKeys.all, 'mitarbeiter', filters] as const,
  zeiterfassung: (datum?: string) => [...personalKeys.all, 'zeit', datum] as const,
  schulungen: (filters?: Record<string, unknown>) => [...personalKeys.all, 'schulungen', filters] as const,
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackMitarbeiter: Mitarbeiter[] = [
  { id: '1', name: 'Max Schmidt', abteilung: 'Lager', position: 'Lagerleiter', eintrittsdatum: '2018-03-15', status: 'aktiv' },
  { id: '2', name: 'Anna Müller', abteilung: 'Vertrieb', position: 'Verkaufsleiter', eintrittsdatum: '2019-08-01', status: 'aktiv' },
  { id: '3', name: 'Tom Weber', abteilung: 'Annahme', position: 'Schichtleiter', eintrittsdatum: '2020-01-10', status: 'urlaub' },
  { id: '4', name: 'Lisa Bauer', abteilung: 'Buchhaltung', position: 'Sachbearbeiterin', eintrittsdatum: '2021-04-01', status: 'aktiv' },
  { id: '5', name: 'Hans Müller', abteilung: 'Agrar', position: 'Berater', eintrittsdatum: '2017-02-01', status: 'krank' },
]

const fallbackZeiten: ZeitEintrag[] = [
  { id: '1', mitarbeiter: 'Max Schmidt', datum: '2026-02-10', kommen: '07:00', gehen: '16:30', stunden: 9.5, typ: 'Arbeit' },
  { id: '2', mitarbeiter: 'Anna Müller', datum: '2026-02-10', kommen: '08:00', gehen: '17:00', stunden: 9.0, typ: 'Arbeit' },
  { id: '3', mitarbeiter: 'Tom Weber', datum: '2026-02-10', kommen: '-', gehen: '-', stunden: 8.0, typ: 'Urlaub' },
  { id: '4', mitarbeiter: 'Lisa Bauer', datum: '2026-02-10', kommen: '07:30', gehen: '16:00', stunden: 8.5, typ: 'Arbeit' },
]

const fallbackSchulungen: Schulung[] = [
  {
    id: '1', mitarbeiter: 'Hans Müller', personalnr: 'P-001',
    thema: 'PSM-Sachkunde Fortbildung', typ: 'PSM',
    datum: '2024-03-15', dauer: 8, schulungsleiter: 'LWK Niedersachsen',
    zertifikatNr: 'SK-NDS-2024-123', gueltigBis: '2027-03-15', status: 'gueltig',
  },
  {
    id: '2', mitarbeiter: 'Maria Schmidt', personalnr: 'P-002',
    thema: 'Gabelstapler-Führerschein', typ: 'Gabelstapler',
    datum: '2023-01-20', dauer: 16, schulungsleiter: 'TÜV Nord',
    zertifikatNr: 'TÜV-GS-2023-456', gueltigBis: '2028-01-20', status: 'gueltig',
  },
  {
    id: '3', mitarbeiter: 'Thomas Weber', personalnr: 'P-003',
    thema: 'Erste Hilfe Grundkurs', typ: 'Erste Hilfe',
    datum: '2023-06-10', dauer: 8, schulungsleiter: 'DRK Rotenburg',
    gueltigBis: '2025-06-10', status: 'ablaufend',
  },
]

// ── Hooks ──────────────────────────────────────────────────────────────

export function useMitarbeiter(filters?: { search?: string; status?: MitarbeiterStatus }) {
  return useQuery({
    queryKey: personalKeys.mitarbeiter(filters),
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (filters?.search) params.append('search', filters.search)
        if (filters?.status) params.append('status', filters.status)
        const response = await apiClient.get<Mitarbeiter[]>(`/api/v1/personal/mitarbeiter?${String(params)}`)
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      let items = [...fallbackMitarbeiter]
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(m => m.name.toLowerCase().includes(s) || m.abteilung.toLowerCase().includes(s))
      }
      if (filters?.status) items = items.filter(m => m.status === filters.status)
      return items
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useZeiterfassung(datum?: string) {
  return useQuery({
    queryKey: personalKeys.zeiterfassung(datum),
    queryFn: async () => {
      try {
        const params = datum ? `?datum=${datum}` : ''
        const response = await apiClient.get<ZeitEintrag[]>(`/api/v1/personal/zeiterfassung${params}`)
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackZeiten
    },
    staleTime: 30 * 1000,
  })
}

export function useSchulungen(filters?: { typ?: SchulungTyp; status?: SchulungStatus }) {
  return useQuery({
    queryKey: personalKeys.schulungen(filters),
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (filters?.typ) params.append('typ', filters.typ)
        if (filters?.status) params.append('status', filters.status)
        const response = await apiClient.get<Schulung[]>(`/api/v1/personal/schulungen?${String(params)}`)
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      let items = [...fallbackSchulungen]
      if (filters?.typ) items = items.filter(s => s.typ === filters.typ)
      if (filters?.status) items = items.filter(s => s.status === filters.status)
      return items
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useSaveStundenzettel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: StundenzettelData) => {
      const response = await apiClient.post<StundenzettelData>('/api/v1/personal/stundenzettel', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.zeiterfassung() })
    },
  })
}
