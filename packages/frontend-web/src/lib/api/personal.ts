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

export type DriverTimeFindingSeverity = 'blocker' | 'warning' | 'info'

export type DriverTimeFinding = {
  code: string
  severity: DriverTimeFindingSeverity
  message: string
  eventIds: string[]
}

export type DriverTimeEvent = {
  id: string
  fahrer: string
  employeeRef: string
  datum: string
  tour?: string | null
  fahrzeug?: string | null
  start: string
  ende: string
  taetigkeit: string
  eventType: string
  quelle: 'Manuell' | 'Tacho' | 'Telematik' | 'Dispo' | string
  dauer: number
  findings: DriverTimeFinding[]
}

export type DriverTimeSummary = {
  datum: string
  source: string
  kpis: {
    eventCount: number
    fahrerCount: number
    tourCount: number
    vehicleCount: number
    fahrzeitStunden: number
    produktivStunden: number
    ruhezeitStunden: number
    blocker: number
    warnings: number
  }
  findings: DriverTimeFinding[]
  events: DriverTimeEvent[]
}

export type TimeCockpit = {
  datum: string
  source: string
  kpis: {
    presentEmployees: number
    absentEmployees: number
    pendingApprovals: number
    blockerCount: number
    warningCount: number
    payrollReadyEntries: number
    payrollBlockedEntries: number
    totalHours: number
    overtimeHours: number
  }
  approvalQueue: Array<{
    id: string
    employeeRef: string
    datum: string
    hours: number
    entryType: string
    status: string
    source: string
    risk: string
    nextAction: string
  }>
  complianceIssues: Array<{
    code: string
    severity: DriverTimeFindingSeverity
    employeeRef: string
    datum: string
    message: string
    sourceId?: string | null
  }>
  payrollReadiness: {
    status: 'ready' | 'blocked' | string
    readyEntries: number
    blockedEntries: number
    blockers: string[]
    exportHint: string
  }
  driverTime: DriverTimeSummary
}

export type TimeEntryBookingInput = {
  employeeRef: string
  datum: string
  startTime?: string | null
  endTime?: string | null
  hours: number
  entryType: string
  source?: string
  costCenter?: string | null
  workArea?: string | null
  notes?: string | null
}

export type TimeEntryCorrectionInput = {
  hours: number
  correctionReason: string
  startTime?: string | null
  endTime?: string | null
  entryType?: string
  costCenter?: string | null
  workArea?: string | null
  notes?: string | null
}

export type AbsenceImportInput = {
  employeeRef: string
  absenceType: 'Urlaub' | 'Krank' | 'Unbezahlt' | 'Sonstiges'
  fromDate: string
  toDate: string
  status?: string
  sourceSystem?: string
  externalRef?: string | null
  note?: string | null
}

export type Absence = {
  id: string
  employeeRef: string
  datum: string
  absenceType: string
  status: string
  source: string
  externalRef?: string | null
  planningBlockers: string[]
  note?: string | null
}

export type Shift = {
  id: string
  datum: string
  name: string
  locationCode: string
  requiredRole: string
  requiredQualifications: string[]
  requiredHeadcount: number
  startTime: string
  endTime: string
  assignedEmployeeRefs: string[]
  status: string
  conflicts: Array<{ code: string; severity: string; message: string; employeeRef?: string | null }>
  notes?: string | null
}

export type ShiftInput = {
  name: string
  datum: string
  startTime: string
  endTime: string
  locationCode?: string
  requiredRole?: string
  requiredQualifications?: string[]
  requiredHeadcount?: number
  assignedEmployeeRefs?: string[]
  notes?: string | null
}

export type CalendarEvent = {
  id: string
  sourceSystem: string
  provider: string
  externalEventRef?: string | null
  eventType: string
  title: string
  employeeRef?: string | null
  resourceRef?: string | null
  startsAt: string
  endsAt: string
  timezone: string
  visibility: string
  status: string
  syncState: string
  conflictLevel: string
  sourceRef?: string | null
  metadata: Record<string, unknown>
}

export type CalendarEventInput = {
  sourceSystem?: string
  provider?: string
  externalEventRef?: string | null
  eventType: string
  title: string
  employeeRef?: string | null
  resourceRef?: string | null
  startsAt: string
  endsAt: string
  timezone?: string
  visibility?: string
  status?: string
  syncState?: string
  conflictLevel?: string
  sourceRef?: string | null
  metadata?: Record<string, unknown>
}

export type PayrollExport = {
  id: string
  periodFrom: string
  periodTo: string
  targetSystem: string
  status: string
  items: Array<{ employeeRef: string; datum: string; hours: number; entryType: string; wageType: string; costCenter?: string | null; sourceEntryId: string }>
  blockers: Array<{ code: string; message: string; employeeRef?: string | null; sourceEntryId?: string | null }>
}

export type CampaignCapacity = {
  id: string
  campaignCode: string
  name: string
  periodFrom: string
  periodTo: string
  locationCode: string
  roleDemand: Record<string, number>
  expectedVolume?: number | null
  status: string
  findings: Array<{ code: string; severity: string; message: string; roleCode?: string | null }>
}

export type FieldServicePlan = {
  id: string
  employeeRef: string
  customerRef: string
  territoryCode: string
  campaignCode?: string | null
  visitType: string
  startsAt: string
  endsAt: string
  status: string
  conflicts: Array<{ code: string; severity: string; message: string }>
  notes?: string | null
}

export type PlanningPreference = {
  employeeRef: string
  prefersNightTours: boolean
  avoidNightTours: boolean
  childcareSensitive: boolean
  preferredWeekdays: string[]
  schoolHolidayRegions: string[]
  bridgeDayPolicy: string
  maxExtraHoursBeforeHoliday: number
}

export type WorkPlanFinding = {
  code: string
  severity: DriverTimeFindingSeverity | string
  message: string
  employeeRef?: string | null
  datum?: string | null
  sourceRef?: string | null
}

export type WorkPlanAssignment = {
  id: string
  datum: string
  employeeRef: string
  label: string
  sourceType: string
  startTime?: string | null
  endTime?: string | null
  status: string
  printReady: boolean
  findings: WorkPlanFinding[]
}

export type WorkPlan = {
  periodFrom: string
  periodTo: string
  source: string
  preferences: PlanningPreference[]
  assignments: WorkPlanAssignment[]
  findings: WorkPlanFinding[]
  printTitle: string
  generatedAt: string
}

export type HrmReadinessCapability = {
  id: string
  title: string
  status: string
  priority: string
  legalBasis: string[]
  implementedEvidence: string[]
  missingCapabilities: string[]
  nextSlices: string[]
  controls: string[]
}

export type HrmReadinessIntegration = {
  id: string
  title: string
  status: string
  direction: string
  minimumContract: string[]
  nextSlice: string
}

export type HrmReadinessAiControl = {
  id: string
  title: string
  classification: string
  allowedUse: string[]
  prohibitedUse: string[]
  requiredControls: string[]
}

export type HrmReadiness = {
  status: string
  country: string
  asOf: string
  minimumChecklist: string[]
  capabilities: HrmReadinessCapability[]
  integrations: HrmReadinessIntegration[]
  aiControls: HrmReadinessAiControl[]
  residualRisks: string[]
}

export type EmployeeFileDocumentClass = {
  documentType: string
  title: string
  legalBasis: string[]
  defaultVisibility: string
  retentionYears: number
  requiresDmsRef: boolean
  deletionRule: string
}

export type EmployeeFileDocument = {
  id: string
  employeeRef: string
  documentType: string
  title: string
  status: string
  visibility: string
  legalBasis: string[]
  issuedAt?: string | null
  validUntil?: string | null
  retentionUntil: string
  dmsDocumentId?: string | null
  canEmployeeView: boolean
  canManagerView: boolean
  deletionBlockedReason: string
  auditRef: string
}

export type EmployeeFile = {
  employeeRef: string
  source: string
  actorRole: string
  documentClasses: EmployeeFileDocumentClass[]
  documents: EmployeeFileDocument[]
  hiddenDocumentCount: number
  exportPackage: {
    available: boolean
    format: string
    includesAuditTrail: boolean
    includesRetentionPlan: boolean
    dataSubjectAccessHint: string
  }
  retention: {
    deletionConcept: string
    reviewCadence: string
    blockedDocumentCount: number
    nextReviewHint: string
  }
}

export type EmployeeFileDocumentInput = {
  documentType: string
  title: string
  issuedAt?: string | null
  validUntil?: string | null
  dmsDocumentId?: string | null
  visibility?: 'employee' | 'manager' | 'hr' | 'payroll'
  notes?: string | null
  createdBy?: string
}

export type HrmOperatingSystemModule = {
  id: string
  title: string
  status: string
  apiContracts: string[]
  controls: string[]
  externalGates: string[]
}

export type HrmOperatingSystem = {
  status: string
  asOf: string
  closedRepoGaps: string[]
  modules: HrmOperatingSystemModule[]
  timeEntryModelRules: string[]
  externalOperatingGates: string[]
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
  driverTimeSummary: (datum?: string) => [...personalKeys.all, 'driver-time-summary', datum] as const,
  timeCockpit: (datum?: string) => [...personalKeys.all, 'time-cockpit', datum] as const,
  absences: (filters?: Record<string, unknown>) => [...personalKeys.all, 'absences', filters] as const,
  shifts: (filters?: Record<string, unknown>) => [...personalKeys.all, 'shifts', filters] as const,
  calendarEvents: (filters?: Record<string, unknown>) => [...personalKeys.all, 'calendar-events', filters] as const,
  payrollExports: () => [...personalKeys.all, 'payroll-exports'] as const,
  campaignCapacity: () => [...personalKeys.all, 'campaign-capacity'] as const,
  fieldServicePlan: () => [...personalKeys.all, 'field-service-plan'] as const,
  workPlan: (filters?: Record<string, unknown>) => [...personalKeys.all, 'work-plan', filters] as const,
  hrmReadiness: () => [...personalKeys.all, 'hrm-readiness'] as const,
  hrmOperatingSystem: () => [...personalKeys.all, 'hrm-operating-system'] as const,
  employeeFile: (employeeRef?: string, actorRole?: string) => [...personalKeys.all, 'employee-file', employeeRef, actorRole] as const,
  schulungen: (filters?: Record<string, unknown>) => [...personalKeys.all, 'schulungen', filters] as const,
  qualifikationen: (filters?: Record<string, unknown>) => [...personalKeys.all, 'qualifikationen', filters] as const,
  onboardingRuns: (filters?: Record<string, unknown>) => [...personalKeys.all, 'onboarding-runs', filters] as const,
  onboardingChecklists: () => [...personalKeys.all, 'onboarding-checklists'] as const,
  mitarbeiterDetail: (id: string) => [...personalKeys.all, 'mitarbeiter-detail', id] as const,
  stundenzettelListe: (filters?: Record<string, unknown>) => [...personalKeys.all, 'stundenzettel-liste', filters] as const,
}

const EMPTY_MITARBEITER_LIST: Mitarbeiter[] = []
const EMPTY_ZEITERFASSUNG_LIST: ZeitEintrag[] = []
const EMPTY_DRIVER_TIME_SUMMARY: DriverTimeSummary = {
  datum: '',
  source: 'empty',
  kpis: {
    eventCount: 0,
    fahrerCount: 0,
    tourCount: 0,
    vehicleCount: 0,
    fahrzeitStunden: 0,
    produktivStunden: 0,
    ruhezeitStunden: 0,
    blocker: 0,
    warnings: 0,
  },
  findings: [],
  events: [],
}
const EMPTY_TIME_COCKPIT: TimeCockpit = {
  datum: '',
  source: 'empty',
  kpis: {
    presentEmployees: 0,
    absentEmployees: 0,
    pendingApprovals: 0,
    blockerCount: 0,
    warningCount: 0,
    payrollReadyEntries: 0,
    payrollBlockedEntries: 0,
    totalHours: 0,
    overtimeHours: 0,
  },
  approvalQueue: [],
  complianceIssues: [],
  payrollReadiness: {
    status: 'blocked',
    readyEntries: 0,
    blockedEntries: 0,
    blockers: [],
    exportHint: '',
  },
  driverTime: EMPTY_DRIVER_TIME_SUMMARY,
}
const EMPTY_ABSENCES: Absence[] = []
const EMPTY_SHIFTS: Shift[] = []
const EMPTY_CALENDAR_EVENTS: CalendarEvent[] = []
const EMPTY_PAYROLL_EXPORTS: PayrollExport[] = []
const EMPTY_CAMPAIGN_CAPACITY: CampaignCapacity[] = []
const EMPTY_FIELD_SERVICE_PLAN: FieldServicePlan[] = []
const EMPTY_WORK_PLAN: WorkPlan = {
  periodFrom: '',
  periodTo: '',
  source: 'empty',
  preferences: [],
  assignments: [],
  findings: [],
  printTitle: '',
  generatedAt: '',
}
const EMPTY_HRM_READINESS: HrmReadiness = {
  status: 'unknown',
  country: 'DE',
  asOf: '',
  minimumChecklist: [],
  capabilities: [],
  integrations: [],
  aiControls: [],
  residualRisks: [],
}
const EMPTY_EMPLOYEE_FILE: EmployeeFile = {
  employeeRef: '',
  source: 'empty',
  actorRole: 'employee',
  documentClasses: [],
  documents: [],
  hiddenDocumentCount: 0,
  exportPackage: {
    available: false,
    format: '',
    includesAuditTrail: false,
    includesRetentionPlan: false,
    dataSubjectAccessHint: '',
  },
  retention: {
    deletionConcept: '',
    reviewCadence: '',
    blockedDocumentCount: 0,
    nextReviewHint: '',
  },
}
const EMPTY_HRM_OPERATING_SYSTEM: HrmOperatingSystem = {
  status: 'unknown',
  asOf: '',
  closedRepoGaps: [],
  modules: [],
  timeEntryModelRules: [],
  externalOperatingGates: [],
}
const EMPTY_SCHULUNGEN_LIST: Schulung[] = []
const EMPTY_STUNDENZETTEL_LIST: StundenzettelEintrag[] = []
const EMPTY_QUALIFIKATIONEN_LIST: Qualifikation[] = []
const EMPTY_ONBOARDING_RUNS_LIST: OnboardingRun[] = []
const EMPTY_ONBOARDING_CHECKLISTS: OnboardingChecklistApi[] = []

export function useMitarbeiter(filters?: { search?: string; status?: MitarbeiterStatus }) {
  return useQuery({
    queryKey: personalKeys.mitarbeiter(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      return (await apiClient.get<Mitarbeiter[]>(`/api/v1/personal/mitarbeiter?${String(params)}`)).data
    },
    initialData: EMPTY_MITARBEITER_LIST,
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
    placeholderData: EMPTY_ZEITERFASSUNG_LIST,
    staleTime: 30 * 1000,
  })
}

export function useDriverTimeSummary(datum?: string) {
  return useQuery({
    queryKey: personalKeys.driverTimeSummary(datum),
    queryFn: async () => {
      const params = datum ? `?datum=${datum}` : ''
      return (await apiClient.get<DriverTimeSummary>(`/api/v1/personal/driver-time/summary${params}`)).data
    },
    placeholderData: EMPTY_DRIVER_TIME_SUMMARY,
    staleTime: 30 * 1000,
  })
}

export function useTimeCockpit(datum?: string) {
  return useQuery({
    queryKey: personalKeys.timeCockpit(datum),
    queryFn: async () => {
      const params = datum ? `?datum=${datum}` : ''
      return (await apiClient.get<TimeCockpit>(`/api/v1/personal/time-cockpit${params}`)).data
    },
    placeholderData: EMPTY_TIME_COCKPIT,
    staleTime: 30 * 1000,
  })
}

export function useCreateTimeEntry() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: TimeEntryBookingInput) => (await apiClient.post('/api/v1/personal/time-entries', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.zeiterfassung() })
      queryClient.invalidateQueries({ queryKey: personalKeys.timeCockpit() })
    },
  })
}

export function useSubmitTimeEntry() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (entryId: string) => (await apiClient.post(`/api/v1/personal/time-entries/${entryId}/submit`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.zeiterfassung() })
      queryClient.invalidateQueries({ queryKey: personalKeys.timeCockpit() })
    },
  })
}

export function useCorrectTimeEntry() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ entryId, data }: { entryId: string; data: TimeEntryCorrectionInput }) =>
      (await apiClient.post(`/api/v1/personal/time-entries/${entryId}/correct`, data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.zeiterfassung() })
      queryClient.invalidateQueries({ queryKey: personalKeys.timeCockpit() })
    },
  })
}

export function useAbsences(filters?: { datumVon?: string; datumBis?: string }) {
  return useQuery({
    queryKey: personalKeys.absences(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.datumVon) params.append('datum_von', filters.datumVon)
      if (filters?.datumBis) params.append('datum_bis', filters.datumBis)
      return (await apiClient.get<Absence[]>(`/api/v1/personal/absences?${String(params)}`)).data
    },
    placeholderData: EMPTY_ABSENCES,
    staleTime: 30_000,
  })
}

export function useImportAbsence() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: AbsenceImportInput) => (await apiClient.post('/api/v1/personal/absences/import', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.absences() })
      queryClient.invalidateQueries({ queryKey: personalKeys.timeCockpit() })
      queryClient.invalidateQueries({ queryKey: personalKeys.driverTimeSummary() })
    },
  })
}

export function useShifts(filters?: { datumVon?: string; datumBis?: string; location?: string }) {
  return useQuery({
    queryKey: personalKeys.shifts(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.datumVon) params.append('datum_von', filters.datumVon)
      if (filters?.datumBis) params.append('datum_bis', filters.datumBis)
      if (filters?.location) params.append('location', filters.location)
      return (await apiClient.get<Shift[]>(`/api/v1/personal/shifts?${String(params)}`)).data
    },
    placeholderData: EMPTY_SHIFTS,
    staleTime: 30_000,
  })
}

export function useCreateShift() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: ShiftInput) => (await apiClient.post<Shift>('/api/v1/personal/shifts', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.shifts() })
      queryClient.invalidateQueries({ queryKey: personalKeys.calendarEvents() })
    },
  })
}

export function useCalendarEvents(filters?: { start?: string; end?: string }) {
  return useQuery({
    queryKey: personalKeys.calendarEvents(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.start) params.append('start', filters.start)
      if (filters?.end) params.append('end', filters.end)
      return (await apiClient.get<CalendarEvent[]>(`/api/v1/personal/calendar-events?${String(params)}`)).data
    },
    placeholderData: EMPTY_CALENDAR_EVENTS,
    staleTime: 30_000,
  })
}

export function useCreateCalendarEvent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: CalendarEventInput) => (await apiClient.post<CalendarEvent>('/api/v1/personal/calendar-events', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.calendarEvents() })
    },
  })
}

export function usePayrollExports() {
  return useQuery({
    queryKey: personalKeys.payrollExports(),
    queryFn: async () => (await apiClient.get<PayrollExport[]>('/api/v1/personal/payroll-exports')).data,
    placeholderData: EMPTY_PAYROLL_EXPORTS,
    staleTime: 30_000,
  })
}

export function useCreatePayrollExport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: { periodFrom: string; periodTo: string; targetSystem?: string; createdBy?: string }) =>
      (await apiClient.post<PayrollExport>('/api/v1/personal/payroll-exports', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.payrollExports() })
      queryClient.invalidateQueries({ queryKey: personalKeys.timeCockpit() })
    },
  })
}

export function useCampaignCapacity() {
  return useQuery({
    queryKey: personalKeys.campaignCapacity(),
    queryFn: async () => (await apiClient.get<CampaignCapacity[]>('/api/v1/personal/campaign-capacity')).data,
    placeholderData: EMPTY_CAMPAIGN_CAPACITY,
    staleTime: 30_000,
  })
}

export function useCreateCampaignCapacity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<CampaignCapacity, 'id' | 'status' | 'findings'>) =>
      (await apiClient.post<CampaignCapacity>('/api/v1/personal/campaign-capacity', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.campaignCapacity() })
    },
  })
}

export function useFieldServicePlan() {
  return useQuery({
    queryKey: personalKeys.fieldServicePlan(),
    queryFn: async () => (await apiClient.get<FieldServicePlan[]>('/api/v1/personal/field-service-plan')).data,
    placeholderData: EMPTY_FIELD_SERVICE_PLAN,
    staleTime: 30_000,
  })
}

export function useCreateFieldServicePlan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: Omit<FieldServicePlan, 'id' | 'status' | 'conflicts'>) =>
      (await apiClient.post<FieldServicePlan>('/api/v1/personal/field-service-plan', data)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.fieldServicePlan() })
      queryClient.invalidateQueries({ queryKey: personalKeys.calendarEvents() })
    },
  })
}

export function useWorkPlan(filters: { periodFrom: string; periodTo: string; holidayDates?: string[]; bridgeDays?: string[]; schoolHolidayDates?: string[] }) {
  return useQuery({
    queryKey: personalKeys.workPlan(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('period_from', filters.periodFrom)
      params.append('period_to', filters.periodTo)
      if (filters.holidayDates?.length) params.append('holiday_dates', filters.holidayDates.join(','))
      if (filters.bridgeDays?.length) params.append('bridge_days', filters.bridgeDays.join(','))
      if (filters.schoolHolidayDates?.length) params.append('school_holiday_dates', filters.schoolHolidayDates.join(','))
      return (await apiClient.get<WorkPlan>(`/api/v1/personal/work-plan?${String(params)}`)).data
    },
    placeholderData: EMPTY_WORK_PLAN,
    staleTime: 30_000,
  })
}

export function useHrmReadiness() {
  return useQuery({
    queryKey: personalKeys.hrmReadiness(),
    queryFn: async () => (await apiClient.get<HrmReadiness>('/api/v1/personal/hrm-readiness')).data,
    placeholderData: EMPTY_HRM_READINESS,
    staleTime: 5 * 60 * 1000,
  })
}

export function useEmployeeFile(employeeRef?: string, actorRole = 'hr') {
  return useQuery({
    queryKey: personalKeys.employeeFile(employeeRef, actorRole),
    enabled: Boolean(employeeRef),
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('actorRole', actorRole)
      return (await apiClient.get<EmployeeFile>(`/api/v1/personal/employee-files/${employeeRef}?${String(params)}`)).data
    },
    placeholderData: EMPTY_EMPLOYEE_FILE,
    staleTime: 60_000,
  })
}

export function useHrmOperatingSystem() {
  return useQuery({
    queryKey: personalKeys.hrmOperatingSystem(),
    queryFn: async () => (await apiClient.get<HrmOperatingSystem>('/api/v1/personal/hrm-operating-system')).data,
    placeholderData: EMPTY_HRM_OPERATING_SYSTEM,
    staleTime: 5 * 60 * 1000,
  })
}

export function useCreateEmployeeFileDocument(employeeRef: string, actorRole = 'hr') {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: EmployeeFileDocumentInput) => {
      const params = new URLSearchParams()
      params.append('actorRole', actorRole)
      return (await apiClient.post<EmployeeFileDocument>(`/api/v1/personal/employee-files/${employeeRef}/documents?${String(params)}`, data)).data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: personalKeys.employeeFile(employeeRef, actorRole) })
      queryClient.invalidateQueries({ queryKey: personalKeys.hrmReadiness() })
    },
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
    initialData: EMPTY_SCHULUNGEN_LIST,
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
    initialData: null,
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
    initialData: EMPTY_STUNDENZETTEL_LIST,
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
    initialData: EMPTY_QUALIFIKATIONEN_LIST,
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
    initialData: EMPTY_ONBOARDING_CHECKLISTS,
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
    initialData: EMPTY_ONBOARDING_RUNS_LIST,
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
