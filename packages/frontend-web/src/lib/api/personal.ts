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
  type TrainingAssignmentApi = {
    id: string
    employee_ref: string
    course_code?: string
    course_title?: string
    assigned_at?: string
    assigned_by?: string
    status?: string
    due_date?: string
    completed_at?: string
    evidence_url?: string
  }

  const toSchulungTyp = (item: TrainingAssignmentApi): SchulungTyp => {
    const raw = `${item.course_code ?? ''} ${item.course_title ?? ''}`.toLowerCase()
    if (raw.includes('psm')) return 'PSM'
    if (raw.includes('gefahr')) return 'Gefahrstoffe'
    if (raw.includes('stapler')) return 'Gabelstapler'
    if (raw.includes('erste')) return 'Erste Hilfe'
    if (raw.includes('brand')) return 'Brandschutz'
    return 'Arbeitssicherheit'
  }

  const toStatus = (item: TrainingAssignmentApi): SchulungStatus => {
    if (item.status === 'overdue') return 'abgelaufen'
    if (!item.due_date) return 'gueltig'
    const due = new Date(item.due_date)
    if (Number.isNaN(due.getTime())) return 'gueltig'
    const now = new Date()
    if (due < now) return 'abgelaufen'
    const warning = new Date()
    warning.setDate(warning.getDate() + 60)
    if (due <= warning) return 'ablaufend'
    return 'gueltig'
  }

  const toSchulung = (item: TrainingAssignmentApi): Schulung => {
    const date = item.assigned_at || item.completed_at || new Date().toISOString()
    const thema = item.course_title || item.course_code || 'Schulung'
    return {
      id: item.id,
      mitarbeiter: item.employee_ref,
      personalnr: item.employee_ref,
      thema,
      typ: toSchulungTyp(item),
      datum: date,
      dauer: 0,
      schulungsleiter: item.assigned_by || 'System',
      zertifikatNr: item.evidence_url || undefined,
      gueltigBis: item.due_date || undefined,
      status: toStatus(item),
    }
  }

  return useQuery({
    queryKey: personalKeys.schulungen(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.status === 'abgelaufen') params.append('status', 'overdue')
      if (filters?.status === 'gueltig') params.append('status', 'completed')
      const rows = (await apiClient.get<TrainingAssignmentApi[]>(`/api/v1/training/assignments?${String(params)}`)).data
      let mapped = rows.map(toSchulung)
      if (filters?.typ) {
        mapped = mapped.filter((item) => item.typ === filters.typ)
      }
      if (filters?.status) {
        mapped = mapped.filter((item) => item.status === filters.status)
      }
      return mapped
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
