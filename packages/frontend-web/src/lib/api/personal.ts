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
  email: string
  abteilung: string
  position: string
  eintrittsdatum: string
  status: MitarbeiterStatus
}

export type MitarbeiterInput = {
  name: string
  email: string
  abteilung: string
  position: string
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

export type StundenzettelEintrag = {
  id: string
  datum: string
  fahrer: string
  kennzeichen: string
  touren: Array<Record<string, unknown>>
  gesamtArbeitszeit: number
  ueberstunden: number
  erstelltAm: string
}

export type QualificationLevel = 'basic' | 'advanced' | 'expert'

export type Qualifikation = {
  id: string
  employeeRef: string
  roleCode: string
  qualificationLevel: QualificationLevel
  skills: string[]
  notes?: string
  validUntil?: string
}

export type OnboardingStatus = 'not_started' | 'in_progress' | 'completed' | 'cancelled'

export type OnboardingRun = {
  id: string
  checklistId: string
  checklistCode?: string
  checklistTitle?: string
  employeeRef: string
  assignedBy?: string
  startedAt?: string
  dueDate?: string
  completedAt?: string
  status: OnboardingStatus
  progressPercent: number
}

export const personalKeys = {
  all: ['personal'] as const,
  mitarbeiter: (filters?: Record<string, unknown>) => [...personalKeys.all, 'mitarbeiter', filters] as const,
  zeiterfassung: (datum?: string) => [...personalKeys.all, 'zeit', datum] as const,
  schulungen: (filters?: Record<string, unknown>) => [...personalKeys.all, 'schulungen', filters] as const,
  qualifikationen: (filters?: Record<string, unknown>) => [...personalKeys.all, 'qualifikationen', filters] as const,
  onboardingRuns: (filters?: Record<string, unknown>) => [...personalKeys.all, 'onboarding-runs', filters] as const,
  onboardingChecklists: () => [...personalKeys.all, 'onboarding-checklists'] as const,
  mitarbeiterDetail: (id: string) => [...personalKeys.all, 'mitarbeiter-detail', id] as const,
  stundenzettelListe: (filters?: Record<string, unknown>) => [...personalKeys.all, 'stundenzettel-liste', filters] as const,
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

export function useMitarbeiterDetail(id?: string) {
  return useQuery({
    queryKey: personalKeys.mitarbeiterDetail(id || ''),
    enabled: Boolean(id),
    queryFn: async () => {
      return (await apiClient.get<Mitarbeiter>(`/api/v1/personal/mitarbeiter/${id}`)).data
    },
    staleTime: 60_000,
  })
}

export function useCreateMitarbeiter() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: MitarbeiterInput) => (await apiClient.post<Mitarbeiter>('/api/v1/personal/mitarbeiter', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.mitarbeiter() })
    },
  })
}

export function useUpdateMitarbeiter(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: MitarbeiterInput) => (await apiClient.put<Mitarbeiter>(`/api/v1/personal/mitarbeiter/${id}`, data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.mitarbeiter() })
      queryClient.invalidateQueries({ queryKey: personalKeys.mitarbeiterDetail(id) })
    },
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

export function useStundenzettelListe(filters?: { datumVon?: string; datumBis?: string }) {
  return useQuery({
    queryKey: personalKeys.stundenzettelListe(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.datumVon) params.append('datum_von', filters.datumVon)
      if (filters?.datumBis) params.append('datum_bis', filters.datumBis)
      return (await apiClient.get<StundenzettelEintrag[]>(`/api/v1/personal/stundenzettel?${String(params)}`)).data
    },
    staleTime: 30_000,
  })
}

type QualificationApi = {
  id: string
  employee_ref: string
  role_code: string
  qualification_level: QualificationLevel
  skills?: unknown
  notes?: string
  valid_until?: string
}

type OnboardingChecklistApi = {
  id: string
  checklist_code: string
  title: string
}

type OnboardingRunApi = {
  id: string
  checklist_id: string
  checklist_code?: string
  checklist_title?: string
  employee_ref: string
  assigned_by?: string
  started_at?: string
  due_date?: string
  completed_at?: string
  status: OnboardingStatus
  progress_percent?: number
}

const toQualification = (item: QualificationApi): Qualifikation => ({
  id: item.id,
  employeeRef: item.employee_ref,
  roleCode: item.role_code,
  qualificationLevel: item.qualification_level,
  skills: Array.isArray(item.skills) ? item.skills.map((s) => String(s)) : [],
  notes: item.notes || undefined,
  validUntil: item.valid_until || undefined,
})

const toOnboardingRun = (item: OnboardingRunApi): OnboardingRun => ({
  id: item.id,
  checklistId: item.checklist_id,
  checklistCode: item.checklist_code || undefined,
  checklistTitle: item.checklist_title || undefined,
  employeeRef: item.employee_ref,
  assignedBy: item.assigned_by || undefined,
  startedAt: item.started_at || undefined,
  dueDate: item.due_date || undefined,
  completedAt: item.completed_at || undefined,
  status: item.status,
  progressPercent: Number(item.progress_percent ?? 0),
})

export function useQualifikationen(filters?: { employeeRef?: string }) {
  return useQuery({
    queryKey: personalKeys.qualifikationen(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.employeeRef) params.append('employee_ref', filters.employeeRef)
      const rows = (await apiClient.get<QualificationApi[]>(`/api/v1/training/qualifications?${String(params)}`)).data
      return rows.map(toQualification)
    },
    staleTime: 60_000,
  })
}

export function useCreateQualifikation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<Qualifikation, 'id'>) => {
      await apiClient.post('/api/v1/training/qualifications', {
        data: {
          employee_ref: data.employeeRef,
          role_code: data.roleCode,
          qualification_level: data.qualificationLevel,
          skills: data.skills,
          notes: data.notes ?? null,
          valid_until: data.validUntil ?? null,
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.qualifikationen() })
    },
  })
}

export function useOnboardingChecklists() {
  return useQuery({
    queryKey: personalKeys.onboardingChecklists(),
    queryFn: async () => {
      return (await apiClient.get<OnboardingChecklistApi[]>('/api/v1/training/onboarding/checklists')).data
    },
    staleTime: 60_000,
  })
}

export function useOnboardingRuns(filters?: { employeeRef?: string; status?: OnboardingStatus }) {
  return useQuery({
    queryKey: personalKeys.onboardingRuns(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.employeeRef) params.append('employee_ref', filters.employeeRef)
      if (filters?.status) params.append('status', filters.status)
      const rows = (await apiClient.get<OnboardingRunApi[]>(`/api/v1/training/onboarding/runs?${String(params)}`)).data
      return rows.map(toOnboardingRun)
    },
    staleTime: 60_000,
  })
}

export function useCreateOnboardingRun() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<OnboardingRun, 'id' | 'checklistCode' | 'checklistTitle'>) => {
      await apiClient.post('/api/v1/training/onboarding/runs', {
        data: {
          checklist_id: data.checklistId,
          employee_ref: data.employeeRef,
          assigned_by: data.assignedBy ?? null,
          started_at: data.startedAt ?? null,
          due_date: data.dueDate ?? null,
          completed_at: data.completedAt ?? null,
          status: data.status,
          progress_percent: data.progressPercent,
          state: {},
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.onboardingRuns() })
    },
  })
}
