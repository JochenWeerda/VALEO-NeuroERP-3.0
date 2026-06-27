import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { AlertTriangle, Bot, CalendarCheck, CalendarDays, CheckCircle2, ChevronLeft, ChevronRight, Clock, FileDown, Pencil, Plus, Printer, Route, Save, Search, ShieldCheck, Truck, Users } from 'lucide-react'
import {
  useAbsences,
  useCalendarEvents,
  useCampaignCapacity,
  useCorrectTimeEntry,
  useCreateCalendarEvent,
  useCreateCampaignCapacity,
  useCreateFieldServicePlan,
  useCreatePayrollExport,
  useCreateShift,
  useCreateTimeEntry,
  useFieldServicePlan,
  useImportAbsence,
  usePayrollExports,
  useShifts,
  useSubmitTimeEntry,
  useTimeCockpit,
  useUpdateDriverTimeEvent,
  useWorkPlan,
  useZeiterfassung,
  type Absence,
  type CalendarEvent,
  type CampaignCapacity,
  type DriverTimeEvent,
  type DriverTimeFindingSeverity,
  type FieldServicePlan,
  type PayrollExport,
  type Shift,
  type TimeCockpit,
  type WorkPlanAssignment,
  type WorkPlanFinding,
  type ZeitEintrag,
} from '@/lib/api/personal'

const getFindingBadgeVariant = (severity: DriverTimeFindingSeverity): 'destructive' | 'secondary' | 'outline' => {
  if (severity === 'blocker') return 'destructive'
  if (severity === 'warning') return 'secondary'
  return 'outline'
}

const getStatusBadgeVariant = (status: string): 'destructive' | 'secondary' | 'outline' => {
  if (['blocked', 'blockiert', 'warning'].includes(status)) return status === 'warning' ? 'secondary' : 'destructive'
  if (['Approved', 'Genehmigt', 'ready', 'planned', 'synced'].includes(status)) return 'outline'
  return 'secondary'
}

const splitCsv = (value: string): string[] => value.split(',').map((item) => item.trim()).filter(Boolean)

const addDays = (dateText: string, days: number): string => {
  const value = new Date(`${dateText}T00:00:00`)
  value.setDate(value.getDate() + days)
  return value.toISOString().split('T')[0]
}

const normalizeText = (value: unknown): string => String(value ?? '').toLowerCase()

type HrTimeQuickFilter = 'all' | 'blockers' | 'warnings' | 'printReady' | 'drivers' | 'payroll'
type HrTimeSortMode = 'priority' | 'date' | 'employee' | 'status'

export default function ZeiterfassungPage(): JSX.Element {
  const initialDate = new Date().toISOString().split('T')[0]
  const [selectedDate, setSelectedDate] = useState(initialDate)
  const { data: zeiten, isLoading } = useZeiterfassung(selectedDate)
  const { data: cockpit, isLoading: isCockpitLoading } = useTimeCockpit(selectedDate)
  const { data: absences = [] } = useAbsences({ datumVon: selectedDate, datumBis: selectedDate })
  const { data: shifts = [] } = useShifts({ datumVon: selectedDate, datumBis: selectedDate })
  const { data: calendarEvents = [] } = useCalendarEvents({ start: `${selectedDate}T00:00:00+02:00`, end: `${selectedDate}T23:59:59+02:00` })
  const { data: payrollExports = [] } = usePayrollExports()
  const { data: campaignCapacity = [] } = useCampaignCapacity()
  const { data: fieldServicePlan = [] } = useFieldServicePlan()
  const { data: workPlan } = useWorkPlan({
    periodFrom: selectedDate,
    periodTo: addDays(selectedDate, 7),
    holidayDates: [addDays(selectedDate, 1)],
    bridgeDays: [addDays(selectedDate, 2)],
    schoolHolidayDates: [selectedDate],
  })
  const createTimeEntry = useCreateTimeEntry()
  const submitTimeEntry = useSubmitTimeEntry()
  const correctTimeEntry = useCorrectTimeEntry()
  const importAbsence = useImportAbsence()
  const createShift = useCreateShift()
  const createCalendarEvent = useCreateCalendarEvent()
  const createPayrollExport = useCreatePayrollExport()
  const createCampaignCapacity = useCreateCampaignCapacity()
  const createFieldServicePlan = useCreateFieldServicePlan()
  const [activeTab, setActiveTab] = useState('steuerung')
  const [searchTerm, setSearchTerm] = useState('')
  const [quickFilter, setQuickFilter] = useState<HrTimeQuickFilter>('all')
  const [sortMode, setSortMode] = useState<HrTimeSortMode>('priority')
  const list = useMemo(() => zeiten ?? [], [zeiten])
  const driverTime = cockpit?.driverTime
  const driverRows = useMemo(() => driverTime?.events ?? [], [driverTime?.events])
  const [timeForm, setTimeForm] = useState({ employeeRef: 'warehouse-1', startTime: '07:00', endTime: '16:00', hours: '8', entryType: 'Arbeit', costCenter: 'LAG', workArea: 'Lager' })
  const [absenceForm, setAbsenceForm] = useState({ employeeRef: 'driver-1', absenceType: 'Urlaub' as const, fromDate: selectedDate, toDate: selectedDate, externalRef: '' })
  const [shiftForm, setShiftForm] = useState({ name: 'Ernteannahme Waage', startTime: '06:00', endTime: '14:00', locationCode: 'main', requiredRole: 'waage', requiredQualifications: 'forklift', requiredHeadcount: '2', assignedEmployeeRefs: 'warehouse-1' })
  const [calendarForm, setCalendarForm] = useState({ eventType: 'shift', title: 'Teamkalender Blocker', employeeRef: 'warehouse-1', startsAt: `${selectedDate}T06:00:00+02:00`, endsAt: `${selectedDate}T14:00:00+02:00`, visibility: 'team' })
  const [campaignForm, setCampaignForm] = useState({ campaignCode: 'ERNTE-2026', name: 'Ernteannahme 2026', periodFrom: selectedDate, periodTo: selectedDate, locationCode: 'main', roleCode: 'lkw_fahrer', demand: '2', expectedVolume: '12000' })
  const [fieldForm, setFieldForm] = useState({ employeeRef: 'berater-1', customerRef: 'kunde-42', territoryCode: 'north', campaignCode: 'SAAT-2026', startsAt: `${selectedDate}T09:00:00+02:00`, endsAt: `${selectedDate}T11:00:00+02:00` })
  const [correctionForm, setCorrectionForm] = useState({ entryId: '', startTime: '07:00', endTime: '16:00', hours: '8', entryType: 'Arbeit', reason: 'Nachbearbeitung nach Pruefung', costCenter: 'LOG', workArea: 'Tour' })
  const [selectedTimeEntry, setSelectedTimeEntry] = useState<ZeitEintrag | null>(null)
  const [selectedWorkPlanItem, setSelectedWorkPlanItem] = useState<WorkPlanAssignment | null>(null)
  const [selectedDriverEvent, setSelectedDriverEvent] = useState<DriverTimeEvent | null>(null)
  const [driverPatchForm, setDriverPatchForm] = useState({ vehicleId: '', tourRef: '', notes: '' })
  const updateDriverTimeEvent = useUpdateDriverTimeEvent()

  const startCorrection = (entry: ZeitEintrag) => {
    setCorrectionForm((prev) => ({
      ...prev,
      entryId: entry.id,
      startTime: entry.kommen === '-' ? prev.startTime : entry.kommen,
      endTime: entry.gehen === '-' ? prev.endTime : entry.gehen,
      hours: String(entry.stunden),
      entryType: entry.typ,
      reason: prev.reason || 'Nachbearbeitung nach Pruefung',
    }))
    setActiveTab('crud')
  }

  const agentHints = useMemo(() => {
    const hints: Array<{ severity: DriverTimeFindingSeverity; title: string; detail: string }> = []
    if ((cockpit?.kpis.pendingApprovals ?? 0) > 0) hints.push({ severity: 'warning', title: 'Freigaben', detail: `${cockpit?.kpis.pendingApprovals} Zeitbuchungen warten auf Entscheidung.` })
    if ((cockpit?.kpis.blockerCount ?? 0) > 0) hints.push({ severity: 'blocker', title: 'Compliance', detail: `${cockpit?.kpis.blockerCount} Blocker muessen vor Payroll/Planung geklaert werden.` })
    const blockedShiftCount = shifts.filter((item) => item.status === 'blocked').length
    if (blockedShiftCount > 0) hints.push({ severity: 'blocker', title: 'Schichten', detail: `${blockedShiftCount} Schichten sind wegen Besetzung, Qualifikation oder Abwesenheit blockiert.` })
    const blockedCampaignCount = campaignCapacity.filter((item) => item.status === 'blocked').length
    if (blockedCampaignCount > 0) hints.push({ severity: 'blocker', title: 'Kampagnen', detail: `${blockedCampaignCount} Kampagnenplaene haben Rollenengpaesse.` })
    const warningFieldCount = fieldServicePlan.filter((item) => item.status !== 'planned').length
    if (warningFieldCount > 0) hints.push({ severity: 'warning', title: 'Aussendienst', detail: `${warningFieldCount} Besuche haben Kalender- oder Abwesenheitskonflikte.` })
    if (hints.length === 0) hints.push({ severity: 'info', title: 'Arbeitsvorrat', detail: 'Keine akuten HR-Time Blocker im aktuellen Cockpit.' })
    return hints
  }, [campaignCapacity, cockpit?.kpis.blockerCount, cockpit?.kpis.pendingApprovals, fieldServicePlan, shifts])

  const filteredWorkPlanAssignments = useMemo(() => {
    const search = normalizeText(searchTerm)
    const matchesSearch = (item: WorkPlanAssignment) => {
      if (!search) return true
      return [
        item.employeeRef,
        item.label,
        item.sourceType,
        item.status,
        item.findings.map((finding) => finding.code).join(' '),
      ].some((value) => normalizeText(value).includes(search))
    }
    const matchesFilter = (item: WorkPlanAssignment) => {
      if (quickFilter === 'all') return true
      if (quickFilter === 'blockers') return item.status === 'blocked' || item.findings.some((finding) => finding.severity === 'blocker')
      if (quickFilter === 'warnings') return item.status === 'warning' || item.findings.some((finding) => finding.severity === 'warning')
      if (quickFilter === 'printReady') return item.printReady
      if (quickFilter === 'drivers') return normalizeText(item.employeeRef).includes('driver') || normalizeText(item.label).includes('tour')
      if (quickFilter === 'payroll') return normalizeText(item.sourceType).includes('payroll')
      return true
    }
    const severityRank = (item: WorkPlanAssignment) => {
      if (item.status === 'blocked' || item.findings.some((finding) => finding.severity === 'blocker')) return 0
      if (item.status === 'warning' || item.findings.some((finding) => finding.severity === 'warning')) return 1
      return 2
    }
    return (workPlan?.assignments ?? [])
      .filter((item) => matchesSearch(item) && matchesFilter(item))
      .sort((a, b) => {
        if (sortMode === 'priority') return severityRank(a) - severityRank(b) || a.datum.localeCompare(b.datum)
        if (sortMode === 'employee') return a.employeeRef.localeCompare(b.employeeRef) || a.datum.localeCompare(b.datum)
        if (sortMode === 'status') return a.status.localeCompare(b.status) || a.datum.localeCompare(b.datum)
        return `${a.datum} ${a.startTime ?? ''}`.localeCompare(`${b.datum} ${b.startTime ?? ''}`)
      })
  }, [quickFilter, searchTerm, sortMode, workPlan?.assignments])

  const filteredTimeEntries = useMemo(() => {
    const search = normalizeText(searchTerm)
    return list
      .filter((item) => {
        const matchesSearch = !search || [item.id, item.mitarbeiter, item.datum, item.kommen, item.gehen, item.typ].some((value) => normalizeText(value).includes(search))
        if (!matchesSearch) return false
        if (quickFilter === 'all') return true
        if (quickFilter === 'warnings') return item.typ === 'Ueberstunden'
        if (quickFilter === 'drivers') return normalizeText(item.mitarbeiter).includes('driver') || normalizeText(item.mitarbeiter).includes('fahrer')
        if (quickFilter === 'payroll') return item.typ !== 'Urlaub'
        return quickFilter !== 'blockers'
      })
      .sort((a, b) => {
        if (sortMode === 'employee') return a.mitarbeiter.localeCompare(b.mitarbeiter) || a.kommen.localeCompare(b.kommen)
        if (sortMode === 'status') return a.typ.localeCompare(b.typ) || a.mitarbeiter.localeCompare(b.mitarbeiter)
        if (sortMode === 'priority') return Number(b.typ === 'Ueberstunden') - Number(a.typ === 'Ueberstunden') || a.kommen.localeCompare(b.kommen)
        return a.kommen.localeCompare(b.kommen)
      })
  }, [list, quickFilter, searchTerm, sortMode])

  const columns = [
    { key: 'mitarbeiter' as const, label: 'Mitarbeiter' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (z: ZeitEintrag) => new Date(z.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kommen' as const,
      label: 'Kommen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.kommen}</span>,
    },
    {
      key: 'gehen' as const,
      label: 'Gehen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.gehen}</span>,
    },
    {
      key: 'stunden' as const,
      label: 'Stunden',
      render: (z: ZeitEintrag) => <span className="font-semibold">{z.stunden} h</span>,
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (z: ZeitEintrag) => (
        <Badge variant={z.typ === 'Ueberstunden' ? 'destructive' : z.typ === 'Urlaub' ? 'secondary' : 'outline'}>
          {z.typ}
        </Badge>
      ),
    },
    {
      key: 'id' as const,
      label: 'Aktion',
      render: (z: ZeitEintrag) => (
        <Button type="button" size="sm" variant="outline" className="gap-2" onClick={() => startCorrection(z)}>
          <Pencil className="h-4 w-4" />
          Bearbeiten
        </Button>
      ),
    },
  ]

  const gesamtStunden = list.reduce((sum, z) => sum + z.stunden, 0)
  const driverBlocker = driverTime?.kpis.blocker ?? 0
  const driverWarnings = driverTime?.kpis.warnings ?? 0
  const fahrzeitStunden = driverTime?.kpis.fahrzeitStunden ?? 0
  const complianceColumns = [
    { key: 'severity' as const, label: 'Schwere', render: (row: TimeCockpit['complianceIssues'][number]) => (
      <Badge variant={getFindingBadgeVariant(row.severity)}>{row.severity}</Badge>
    ) },
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'datum' as const, label: 'Datum' },
    { key: 'code' as const, label: 'Code', render: (row: TimeCockpit['complianceIssues'][number]) => (
      <span className="font-mono text-xs">{row.code}</span>
    ) },
    { key: 'message' as const, label: 'Befund' },
  ]
  const approvalColumns = [
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'datum' as const, label: 'Datum' },
    { key: 'hours' as const, label: 'Stunden', render: (row: TimeCockpit['approvalQueue'][number]) => (
      <span className="font-semibold">{row.hours.toFixed(2)} h</span>
    ) },
    { key: 'entryType' as const, label: 'Typ' },
    { key: 'risk' as const, label: 'Risiko', render: (row: TimeCockpit['approvalQueue'][number]) => (
      <Badge variant={row.risk === 'blockiert' ? 'destructive' : 'secondary'}>{row.risk}</Badge>
    ) },
    { key: 'nextAction' as const, label: 'Naechste Aktion' },
  ]
  const driverColumns = [
    { key: 'fahrer' as const, label: 'Fahrer' },
    {
      key: 'tour' as const,
      label: 'Tour',
      render: (row: DriverTimeEvent) => <span className="font-mono text-xs">{row.tour ?? '-'}</span>,
    },
    {
      key: 'fahrzeug' as const,
      label: 'Fahrzeug',
      render: (row: DriverTimeEvent) => (
        <span className={!row.fahrzeug ? 'font-semibold text-destructive' : 'font-mono text-xs'}>
          {row.fahrzeug ?? 'fehlt'}
        </span>
      ),
    },
    {
      key: 'start' as const,
      label: 'Zeit',
      render: (row: DriverTimeEvent) => <span className="font-mono">{row.start} - {row.ende}</span>,
    },
    { key: 'taetigkeit' as const, label: 'Taetigkeit' },
    {
      key: 'quelle' as const,
      label: 'Quelle',
      render: (row: DriverTimeEvent) => <Badge variant="outline">{row.quelle}</Badge>,
    },
    {
      key: 'dauer' as const,
      label: 'Dauer',
      render: (row: DriverTimeEvent) => <span className="font-semibold">{row.dauer.toFixed(2)} h</span>,
    },
    {
      key: 'findings' as const,
      label: 'Check',
      render: (row: DriverTimeEvent) => (
        <div className="flex flex-wrap gap-1">
          {row.findings.length === 0 ? (
            <Badge variant="outline">ok</Badge>
          ) : row.findings.map((finding) => (
            <Badge key={`${row.id}-${finding.code}`} variant={getFindingBadgeVariant(finding.severity)}>
              {finding.message}
            </Badge>
          ))}
        </div>
      ),
    },
  ]
  const absenceColumns = [
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'datum' as const, label: 'Datum' },
    { key: 'absenceType' as const, label: 'Typ' },
    { key: 'status' as const, label: 'Status', render: (row: Absence) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'planningBlockers' as const, label: 'Blocker', render: (row: Absence) => <span>{row.planningBlockers.join(', ') || '-'}</span> },
  ]
  const shiftColumns = [
    { key: 'name' as const, label: 'Schicht' },
    { key: 'locationCode' as const, label: 'Standort' },
    { key: 'requiredRole' as const, label: 'Rolle' },
    { key: 'startTime' as const, label: 'Zeit', render: (row: Shift) => <span className="font-mono">{row.startTime} - {row.endTime}</span> },
    { key: 'status' as const, label: 'Status', render: (row: Shift) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'conflicts' as const, label: 'Checks', render: (row: Shift) => <span>{row.conflicts.map((item) => item.code).join(', ') || 'ok'}</span> },
  ]
  const calendarColumns = [
    { key: 'eventType' as const, label: 'Typ' },
    { key: 'title' as const, label: 'Titel' },
    { key: 'employeeRef' as const, label: 'Mitarbeiter', render: (row: CalendarEvent) => row.employeeRef ?? '-' },
    { key: 'startsAt' as const, label: 'Start', render: (row: CalendarEvent) => <span className="font-mono text-xs">{row.startsAt}</span> },
    { key: 'syncState' as const, label: 'Sync', render: (row: CalendarEvent) => <Badge variant={getStatusBadgeVariant(row.syncState)}>{row.syncState}</Badge> },
    { key: 'conflictLevel' as const, label: 'Konflikt', render: (row: CalendarEvent) => <Badge variant={getStatusBadgeVariant(row.conflictLevel)}>{row.conflictLevel}</Badge> },
  ]
  const payrollColumns = [
    { key: 'periodFrom' as const, label: 'Von' },
    { key: 'periodTo' as const, label: 'Bis' },
    { key: 'targetSystem' as const, label: 'Ziel' },
    { key: 'status' as const, label: 'Status', render: (row: PayrollExport) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'items' as const, label: 'Items', render: (row: PayrollExport) => row.items.length },
    { key: 'blockers' as const, label: 'Blocker', render: (row: PayrollExport) => row.blockers.length },
  ]
  const campaignColumns = [
    { key: 'campaignCode' as const, label: 'Kampagne' },
    { key: 'name' as const, label: 'Name' },
    { key: 'periodFrom' as const, label: 'Zeitraum', render: (row: CampaignCapacity) => `${row.periodFrom} - ${row.periodTo}` },
    { key: 'status' as const, label: 'Status', render: (row: CampaignCapacity) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'findings' as const, label: 'Befunde', render: (row: CampaignCapacity) => row.findings.map((item) => item.code).join(', ') || 'ok' },
  ]
  const fieldColumns = [
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'customerRef' as const, label: 'Kunde' },
    { key: 'territoryCode' as const, label: 'Gebiet' },
    { key: 'startsAt' as const, label: 'Zeit', render: (row: FieldServicePlan) => <span className="font-mono text-xs">{row.startsAt}</span> },
    { key: 'status' as const, label: 'Status', render: (row: FieldServicePlan) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'conflicts' as const, label: 'Checks', render: (row: FieldServicePlan) => row.conflicts.map((item) => item.code).join(', ') || 'ok' },
  ]
  const workPlanColumns = [
    { key: 'datum' as const, label: 'Datum' },
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'label' as const, label: 'Arbeitsplan' },
    { key: 'sourceType' as const, label: 'Quelle', render: (row: WorkPlanAssignment) => <Badge variant="outline">{row.sourceType}</Badge> },
    { key: 'startTime' as const, label: 'Zeit', render: (row: WorkPlanAssignment) => <span className="font-mono text-xs">{row.startTime ?? '-'} - {row.endTime ?? '-'}</span> },
    { key: 'status' as const, label: 'Status', render: (row: WorkPlanAssignment) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'findings' as const, label: 'Planungschecks', render: (row: WorkPlanAssignment) => (
      <div className="flex flex-wrap gap-1">
        {row.findings.length === 0 ? <Badge variant="outline">ok</Badge> : row.findings.map((finding: WorkPlanFinding) => (
          <Badge key={`${row.id}-${finding.code}`} variant={getFindingBadgeVariant(finding.severity as DriverTimeFindingSeverity)}>{finding.code}</Badge>
        ))}
      </div>
    ) },
    { key: 'printReady' as const, label: 'Druck', render: (row: WorkPlanAssignment) => <Badge variant={row.printReady ? 'outline' : 'destructive'}>{row.printReady ? 'bereit' : 'blockiert'}</Badge> },
  ]

  const handleCreateTime = () => {
    createTimeEntry.mutate({
      employeeRef: timeForm.employeeRef,
      datum: selectedDate,
      startTime: timeForm.startTime,
      endTime: timeForm.endTime,
      hours: Number(timeForm.hours || 0),
      entryType: timeForm.entryType,
      source: 'manual',
      costCenter: timeForm.costCenter,
      workArea: timeForm.workArea,
    })
  }

  const handleImportAbsence = () => {
    importAbsence.mutate({ ...absenceForm, status: 'Approved', sourceSystem: 'ui', externalRef: absenceForm.externalRef || null })
  }

  const handleCreateShift = () => {
    createShift.mutate({
      ...shiftForm,
      datum: selectedDate,
      requiredQualifications: splitCsv(shiftForm.requiredQualifications),
      requiredHeadcount: Number(shiftForm.requiredHeadcount || 1),
      assignedEmployeeRefs: splitCsv(shiftForm.assignedEmployeeRefs),
    })
  }

  const handleCreateCalendarEvent = () => {
    createCalendarEvent.mutate({ ...calendarForm, sourceSystem: 'valeo', provider: 'internal', status: 'confirmed', syncState: 'pending', conflictLevel: 'none', metadata: {} })
  }

  const handleCreatePayroll = () => {
    createPayrollExport.mutate({ periodFrom: selectedDate, periodTo: selectedDate, targetSystem: 'datev', createdBy: 'ui' })
  }

  const handleCreateCampaign = () => {
    createCampaignCapacity.mutate({
      campaignCode: campaignForm.campaignCode,
      name: campaignForm.name,
      periodFrom: campaignForm.periodFrom,
      periodTo: campaignForm.periodTo,
      locationCode: campaignForm.locationCode,
      roleDemand: { [campaignForm.roleCode]: Number(campaignForm.demand || 1) },
      expectedVolume: Number(campaignForm.expectedVolume || 0),
    })
  }

  const handleCreateField = () => {
    createFieldServicePlan.mutate({ ...fieldForm, visitType: 'field_visit', notes: null })
  }

  const handleCorrectTimeEntry = () => {
    if (!correctionForm.entryId) return
    correctTimeEntry.mutate({
      entryId: correctionForm.entryId,
      data: {
        startTime: correctionForm.startTime,
        endTime: correctionForm.endTime,
        hours: Number(correctionForm.hours || 0),
        entryType: correctionForm.entryType,
        costCenter: correctionForm.costCenter,
        workArea: correctionForm.workArea,
        correctionReason: correctionForm.reason,
        notes: 'UI-Nachbearbeitung',
      },
    })
  }

  const handlePrintWorkPlan = () => {
    window.print()
  }

  if (isLoading || isCockpitLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!cockpit) return <></>

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Zeiterfassung</h1>
            <p className="text-muted-foreground">Time & Labor, Abwesenheiten, Fahrerzeit und Payroll-Freigabe</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" onClick={() => setSelectedDate(addDays(selectedDate, -1))}>
              <ChevronLeft className="mr-2 h-4 w-4" />
              Zurueck
            </Button>
            <Input className="h-9 w-[150px]" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
            <Button variant="outline" size="sm" onClick={() => setSelectedDate(initialDate)}>
              <Clock className="mr-2 h-4 w-4" />
              Heute
            </Button>
            <Button variant="outline" size="sm" onClick={() => setSelectedDate(addDays(selectedDate, 1))}>
              Weiter
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handlePrintWorkPlan}>
              <Printer className="mr-2 h-4 w-4" />
              Arbeitsplan drucken
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCreatePayroll}
              disabled={createPayrollExport.isPending || cockpit.payrollReadiness.status !== 'ready' || cockpit.payrollReadiness.blockers.length > 0}
              title={cockpit.payrollReadiness.blockers.length > 0 ? `${cockpit.payrollReadiness.blockers.length} Blocker vor Export loesen` : undefined}
            >
              <FileDown className="mr-2 h-4 w-4" />
              {cockpit.payrollReadiness.blockers.length > 0
                ? `${cockpit.payrollReadiness.blockers.length} Blocker offen`
                : 'Payroll vorbereiten'}
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-3 rounded-md border bg-card p-3 lg:grid-cols-[minmax(220px,1fr)_190px_190px_auto]">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            aria-label="HR-Time Suche"
            className="pl-9"
            placeholder="Mitarbeiter, Tour, Schicht, Kampagne, Befund suchen"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="hr-time-quick-filter" className="sr-only">HR-Time Schnellfilter</Label>
          <NativeSelect
            id="hr-time-quick-filter"
            value={quickFilter}
            onValueChange={(value) => setQuickFilter(value as HrTimeQuickFilter)}
            options={[
              { value: 'all', label: 'Alle' },
              { value: 'blockers', label: 'Nur Blocker' },
              { value: 'warnings', label: 'Nur Warnungen' },
              { value: 'printReady', label: 'Druckbereit' },
              { value: 'drivers', label: 'Fahrer' },
              { value: 'payroll', label: 'Payroll' },
            ]}
          />
        </div>
        <div>
          <Label htmlFor="hr-time-sort" className="sr-only">HR-Time Sortierung</Label>
          <NativeSelect
            id="hr-time-sort"
            value={sortMode}
            onValueChange={(value) => setSortMode(value as HrTimeSortMode)}
            options={[
              { value: 'priority', label: 'Prioritaet' },
              { value: 'date', label: 'Datum/Zeit' },
              { value: 'employee', label: 'Mitarbeiter' },
              { value: 'status', label: 'Status' },
            ]}
          />
        </div>
        <Button type="button" variant="outline" onClick={() => { setSearchTerm(''); setQuickFilter('all'); setSortMode('priority') }}>
          Filter resetten
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Anwesend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{cockpit.kpis.presentEmployees}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stunden Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.totalHours.toFixed(1)} h</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.absentEmployees}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fahrerzeit Blocker</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              <span className="text-2xl font-bold">{driverBlocker}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigaben offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-sky-700" />
              <span className="text-2xl font-bold">{cockpit.kpis.pendingApprovals}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Payroll Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle2 className={cockpit.payrollReadiness.status === 'ready' ? 'h-5 w-5 text-emerald-700' : 'h-5 w-5 text-amber-700'} />
              <span className="text-2xl font-bold">{cockpit.payrollReadiness.status === 'ready' ? 'bereit' : 'blockiert'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Payroll bereit</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.payrollReadyEntries}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Payroll blockiert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.payrollBlockedEntries}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fahrzeit Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-emerald-700" />
              <span className="text-2xl font-bold">{fahrzeitStunden.toFixed(2)} h</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Touren</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
            <Route className="h-5 w-5 text-cyan-700" />
              <span className="text-2xl font-bold">{driverTime?.kpis.tourCount ?? 0}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abwesenheitskollisionen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CalendarCheck className="h-5 w-5 text-amber-700" />
              <span className="text-2xl font-bold">
                {(driverTime?.findings ?? []).filter((finding) => finding.code === 'ABSENCE_COLLISION').length}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tacho-Abgleich</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-indigo-700" />
              <span className="text-2xl font-bold">{driverWarnings}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="agent">Agent</TabsTrigger>
          <TabsTrigger value="steuerung">Steuerung</TabsTrigger>
          <TabsTrigger value="crud">Erfassen</TabsTrigger>
          <TabsTrigger value="arbeitsplan">Arbeitsplan</TabsTrigger>
          <TabsTrigger value="planung">Planung</TabsTrigger>
          <TabsTrigger value="driver">Fahrerzeit</TabsTrigger>
          <TabsTrigger value="zeiten">Arbeitszeit</TabsTrigger>
          <TabsTrigger value="payroll">Payroll</TabsTrigger>
        </TabsList>

        <TabsContent value="agent" className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
            <Card>
              <CardHeader>
                <CardTitle>Agent Worklist</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {agentHints.map((hint) => (
                  <div key={`${hint.title}-${hint.detail}`} className="flex items-start gap-3 rounded-md border p-3">
                    <Bot className="mt-0.5 h-4 w-4 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-medium">{hint.title}</span>
                        <Badge variant={getFindingBadgeVariant(hint.severity)}>{hint.severity}</Badge>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">{hint.detail}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Nächste Aktionen</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  className="w-full justify-start gap-2"
                  variant="outline"
                  onClick={handleCreatePayroll}
                  disabled={createPayrollExport.isPending || cockpit.payrollReadiness.status !== 'ready' || cockpit.payrollReadiness.blockers.length > 0}
                >
                  <FileDown className="h-4 w-4" />
                  {cockpit.payrollReadiness.blockers.length > 0 ? `${cockpit.payrollReadiness.blockers.length} Blocker loesen` : 'Payroll-Paket erzeugen'}
                </Button>
                <Button className="w-full justify-start gap-2" variant="outline" onClick={handleCreateShift} disabled={createShift.isPending}>
                  <CalendarDays className="h-4 w-4" />
                  Schicht prüfen
                </Button>
                <Button className="w-full justify-start gap-2" variant="outline" onClick={handleCreateField} disabled={createFieldServicePlan.isPending}>
                  <Route className="h-4 w-4" />
                  Außendienst prüfen
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="steuerung" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Freigabequeue</CardTitle>
              </CardHeader>
              <CardContent>
                <DataTable data={cockpit.approvalQueue} columns={approvalColumns} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance-Befunde</CardTitle>
              </CardHeader>
              <CardContent>
                <DataTable data={cockpit.complianceIssues} columns={complianceColumns} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="crud" className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-4">
            <Card>
              <CardHeader>
                <CardTitle>Zeitbuchung</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-2">
                  <Label htmlFor="time-employee">Mitarbeiter</Label>
                  <Input id="time-employee" value={timeForm.employeeRef} onChange={(event) => setTimeForm((prev) => ({ ...prev, employeeRef: event.target.value }))} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-2">
                    <Label htmlFor="time-start">Start</Label>
                    <Input id="time-start" value={timeForm.startTime} onChange={(event) => setTimeForm((prev) => ({ ...prev, startTime: event.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="time-end">Ende</Label>
                    <Input id="time-end" value={timeForm.endTime} onChange={(event) => setTimeForm((prev) => ({ ...prev, endTime: event.target.value }))} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-2">
                    <Label htmlFor="time-hours">Stunden</Label>
                    <Input id="time-hours" value={timeForm.hours} onChange={(event) => setTimeForm((prev) => ({ ...prev, hours: event.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="time-type">Typ</Label>
                    <NativeSelect
                      id="time-type"
                      value={timeForm.entryType}
                      onValueChange={(value) => setTimeForm((prev) => ({ ...prev, entryType: value }))}
                      options={[
                        { value: 'Arbeit', label: 'Arbeit' },
                        { value: 'Bereitschaft', label: 'Bereitschaft' },
                        { value: 'Schulung', label: 'Schulung' },
                      ]}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input value={timeForm.costCenter} onChange={(event) => setTimeForm((prev) => ({ ...prev, costCenter: event.target.value }))} placeholder="Kostenstelle" />
                  <Input value={timeForm.workArea} onChange={(event) => setTimeForm((prev) => ({ ...prev, workArea: event.target.value }))} placeholder="Arbeitsbereich" />
                </div>
                <Button className="w-full gap-2" onClick={handleCreateTime} disabled={createTimeEntry.isPending}>
                  <Plus className="h-4 w-4" />
                  Zeitbuchung anlegen
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Abwesenheit</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-2">
                  <Label htmlFor="absence-employee">Mitarbeiter</Label>
                  <Input id="absence-employee" value={absenceForm.employeeRef} onChange={(event) => setAbsenceForm((prev) => ({ ...prev, employeeRef: event.target.value }))} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="absence-type">Typ</Label>
                  <NativeSelect
                    id="absence-type"
                    value={absenceForm.absenceType}
                    onValueChange={(value) => setAbsenceForm((prev) => ({ ...prev, absenceType: value as typeof absenceForm.absenceType }))}
                    options={[
                      { value: 'Urlaub', label: 'Urlaub' },
                      { value: 'Krank', label: 'Krank' },
                      { value: 'Unbezahlt', label: 'Unbezahlt' },
                      { value: 'Sonstiges', label: 'Sonstiges' },
                    ]}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input value={absenceForm.fromDate} onChange={(event) => setAbsenceForm((prev) => ({ ...prev, fromDate: event.target.value }))} />
                  <Input value={absenceForm.toDate} onChange={(event) => setAbsenceForm((prev) => ({ ...prev, toDate: event.target.value }))} />
                </div>
                <Input value={absenceForm.externalRef} onChange={(event) => setAbsenceForm((prev) => ({ ...prev, externalRef: event.target.value }))} placeholder="Externe Referenz" />
                <Button className="w-full gap-2" onClick={handleImportAbsence} disabled={importAbsence.isPending}>
                  <Plus className="h-4 w-4" />
                  Abwesenheit importieren
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Schicht</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input value={shiftForm.name} onChange={(event) => setShiftForm((prev) => ({ ...prev, name: event.target.value }))} placeholder="Schichtname" />
                <div className="grid grid-cols-2 gap-3">
                  <Input value={shiftForm.startTime} onChange={(event) => setShiftForm((prev) => ({ ...prev, startTime: event.target.value }))} />
                  <Input value={shiftForm.endTime} onChange={(event) => setShiftForm((prev) => ({ ...prev, endTime: event.target.value }))} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input value={shiftForm.locationCode} onChange={(event) => setShiftForm((prev) => ({ ...prev, locationCode: event.target.value }))} placeholder="Standort" />
                  <Input value={shiftForm.requiredRole} onChange={(event) => setShiftForm((prev) => ({ ...prev, requiredRole: event.target.value }))} placeholder="Rolle" />
                </div>
                <Input value={shiftForm.requiredQualifications} onChange={(event) => setShiftForm((prev) => ({ ...prev, requiredQualifications: event.target.value }))} placeholder="Qualifikationen, kommagetrennt" />
                <div className="grid grid-cols-[90px_1fr] gap-3">
                  <Input value={shiftForm.requiredHeadcount} onChange={(event) => setShiftForm((prev) => ({ ...prev, requiredHeadcount: event.target.value }))} />
                  <Input value={shiftForm.assignedEmployeeRefs} onChange={(event) => setShiftForm((prev) => ({ ...prev, assignedEmployeeRefs: event.target.value }))} placeholder="Mitarbeiter, kommagetrennt" />
                </div>
                <Button className="w-full gap-2" onClick={handleCreateShift} disabled={createShift.isPending}>
                  <Plus className="h-4 w-4" />
                  Schicht anlegen
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Nachbearbeitung</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input value={correctionForm.entryId} onChange={(event) => setCorrectionForm((prev) => ({ ...prev, entryId: event.target.value }))} placeholder="Zeitbuchungs-ID" />
                <div className="grid grid-cols-2 gap-3">
                  <Input value={correctionForm.startTime} onChange={(event) => setCorrectionForm((prev) => ({ ...prev, startTime: event.target.value }))} placeholder="Start" />
                  <Input value={correctionForm.endTime} onChange={(event) => setCorrectionForm((prev) => ({ ...prev, endTime: event.target.value }))} placeholder="Ende" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input value={correctionForm.hours} onChange={(event) => setCorrectionForm((prev) => ({ ...prev, hours: event.target.value }))} placeholder="Stunden" />
                  <NativeSelect
                    value={correctionForm.entryType}
                    onValueChange={(value) => setCorrectionForm((prev) => ({ ...prev, entryType: value }))}
                    options={[
                      { value: 'Arbeit', label: 'Arbeit' },
                      { value: 'Bereitschaft', label: 'Bereitschaft' },
                      { value: 'Korrektur', label: 'Korrektur' },
                    ]}
                  />
                </div>
                <Textarea value={correctionForm.reason} onChange={(event) => setCorrectionForm((prev) => ({ ...prev, reason: event.target.value }))} rows={2} />
                <div className="grid grid-cols-2 gap-2">
                  <Button className="gap-2" variant="outline" onClick={() => correctionForm.entryId && submitTimeEntry.mutate(correctionForm.entryId)} disabled={!correctionForm.entryId || submitTimeEntry.isPending}>
                    <Save className="h-4 w-4" />
                    Einreichen
                  </Button>
                  <Button className="gap-2" onClick={handleCorrectTimeEntry} disabled={!correctionForm.entryId || correctTimeEntry.isPending}>
                    <Pencil className="h-4 w-4" />
                    Korrigieren
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="arbeitsplan" className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <CardTitle>{workPlan?.printTitle || 'Arbeitsplan'}</CardTitle>
                  <Button variant="outline" size="sm" onClick={handlePrintWorkPlan}>
                    <Printer className="mr-2 h-4 w-4" />
                    Drucken
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <DataTable data={filteredWorkPlanAssignments} columns={workPlanColumns} onRowFocus={setSelectedWorkPlanItem} />
              </CardContent>
            </Card>
            {selectedWorkPlanItem ? (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Arbeitsplan Detail</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Mitarbeiter</p>
                    <p className="font-semibold">{selectedWorkPlanItem.employeeRef}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Eintrag</p>
                    <p className="font-medium">{selectedWorkPlanItem.label}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Datum</p>
                      <p className="font-mono text-sm">{selectedWorkPlanItem.datum}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Zeit</p>
                      <p className="font-mono text-sm">{selectedWorkPlanItem.startTime ?? '-'} – {selectedWorkPlanItem.endTime ?? '-'}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant={getStatusBadgeVariant(selectedWorkPlanItem.status)}>{selectedWorkPlanItem.status}</Badge>
                    <Badge variant="outline">{selectedWorkPlanItem.sourceType}</Badge>
                    <Badge variant={selectedWorkPlanItem.printReady ? 'outline' : 'destructive'}>
                      {selectedWorkPlanItem.printReady ? 'druckbereit' : 'Druck blockiert'}
                    </Badge>
                  </div>
                  {selectedWorkPlanItem.findings.length > 0 && (
                    <div>
                      <p className="mb-1 text-sm text-muted-foreground">Planungschecks</p>
                      <div className="space-y-1">
                        {selectedWorkPlanItem.findings.map((finding) => (
                          <div key={`${selectedWorkPlanItem.id}-${finding.code}`} className="rounded border p-2 text-xs">
                            <Badge variant={getFindingBadgeVariant(finding.severity as DriverTimeFindingSeverity)} className="mb-1">{finding.severity}</Badge>
                            <p className="font-mono">{finding.code}: {finding.message}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="border-t pt-3">
                    <Button size="sm" variant="outline" className="w-full gap-2" onClick={handlePrintWorkPlan}>
                      <Printer className="h-4 w-4" />
                      Arbeitsplan drucken
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Praeferenz-Checks</CardTitle>
                </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-sm text-muted-foreground">Planungsbefunde</p>
                    <p className="text-2xl font-semibold">{workPlan?.findings.length ?? 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Druckbereit</p>
                    <p className="text-2xl font-semibold">{filteredWorkPlanAssignments.filter((item) => item.printReady).length}</p>
                  </div>
                </div>
                {(workPlan?.preferences ?? []).map((preference) => (
                  <div key={preference.employeeRef} className="rounded-md border p-3">
                    <div className="font-medium">{preference.employeeRef}</div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {preference.prefersNightTours ? <Badge variant="outline">Nachttour bevorzugt</Badge> : null}
                      {preference.avoidNightTours ? <Badge variant="secondary">Nachttour vermeiden</Badge> : null}
                      {preference.childcareSensitive ? <Badge variant="secondary">Schulferien beachten</Badge> : null}
                      <Badge variant="outline">{preference.bridgeDayPolicy}</Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="planung" className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Kalender</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input value={calendarForm.title} onChange={(event) => setCalendarForm((prev) => ({ ...prev, title: event.target.value }))} placeholder="Titel" />
                <Input value={calendarForm.employeeRef} onChange={(event) => setCalendarForm((prev) => ({ ...prev, employeeRef: event.target.value }))} placeholder="Mitarbeiter" />
                <div className="grid grid-cols-2 gap-3">
                  <Input value={calendarForm.startsAt} onChange={(event) => setCalendarForm((prev) => ({ ...prev, startsAt: event.target.value }))} />
                  <Input value={calendarForm.endsAt} onChange={(event) => setCalendarForm((prev) => ({ ...prev, endsAt: event.target.value }))} />
                </div>
                <Button className="w-full gap-2" onClick={handleCreateCalendarEvent} disabled={createCalendarEvent.isPending}>
                  <Plus className="h-4 w-4" />
                  Kalenderblocker anlegen
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Kampagne</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input value={campaignForm.campaignCode} onChange={(event) => setCampaignForm((prev) => ({ ...prev, campaignCode: event.target.value }))} placeholder="Code" />
                <Input value={campaignForm.name} onChange={(event) => setCampaignForm((prev) => ({ ...prev, name: event.target.value }))} placeholder="Name" />
                <div className="grid grid-cols-2 gap-3">
                  <Input value={campaignForm.periodFrom} onChange={(event) => setCampaignForm((prev) => ({ ...prev, periodFrom: event.target.value }))} />
                  <Input value={campaignForm.periodTo} onChange={(event) => setCampaignForm((prev) => ({ ...prev, periodTo: event.target.value }))} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input value={campaignForm.roleCode} onChange={(event) => setCampaignForm((prev) => ({ ...prev, roleCode: event.target.value }))} placeholder="Rolle" />
                  <Input value={campaignForm.demand} onChange={(event) => setCampaignForm((prev) => ({ ...prev, demand: event.target.value }))} placeholder="Bedarf" />
                </div>
                <Input value={campaignForm.expectedVolume} onChange={(event) => setCampaignForm((prev) => ({ ...prev, expectedVolume: event.target.value }))} placeholder="Menge" />
                <Button className="w-full gap-2" onClick={handleCreateCampaign} disabled={createCampaignCapacity.isPending}>
                  <Plus className="h-4 w-4" />
                  Kampagne prüfen
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Außendienst</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input value={fieldForm.employeeRef} onChange={(event) => setFieldForm((prev) => ({ ...prev, employeeRef: event.target.value }))} placeholder="Mitarbeiter" />
                <Input value={fieldForm.customerRef} onChange={(event) => setFieldForm((prev) => ({ ...prev, customerRef: event.target.value }))} placeholder="Kunde" />
                <div className="grid grid-cols-2 gap-3">
                  <Input value={fieldForm.territoryCode} onChange={(event) => setFieldForm((prev) => ({ ...prev, territoryCode: event.target.value }))} placeholder="Gebiet" />
                  <Input value={fieldForm.campaignCode} onChange={(event) => setFieldForm((prev) => ({ ...prev, campaignCode: event.target.value }))} placeholder="Kampagne" />
                </div>
                <Textarea value={`${fieldForm.startsAt}\n${fieldForm.endsAt}`} onChange={(event) => {
                  const [startsAt = fieldForm.startsAt, endsAt = fieldForm.endsAt] = event.target.value.split('\n')
                  setFieldForm((prev) => ({ ...prev, startsAt, endsAt }))
                }} rows={2} />
                <Button className="w-full gap-2" onClick={handleCreateField} disabled={createFieldServicePlan.isPending}>
                  <Plus className="h-4 w-4" />
                  Besuch planen
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <Card><CardHeader><CardTitle>Schichten</CardTitle></CardHeader><CardContent><DataTable data={shifts} columns={shiftColumns} /></CardContent></Card>
            <Card><CardHeader><CardTitle>Kalender</CardTitle></CardHeader><CardContent><DataTable data={calendarEvents} columns={calendarColumns} /></CardContent></Card>
            <Card><CardHeader><CardTitle>Kampagnen</CardTitle></CardHeader><CardContent><DataTable data={campaignCapacity} columns={campaignColumns} /></CardContent></Card>
            <Card><CardHeader><CardTitle>Außendienst</CardTitle></CardHeader><CardContent><DataTable data={fieldServicePlan} columns={fieldColumns} /></CardContent></Card>
          </div>
        </TabsContent>

        <TabsContent value="driver">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <CardTitle>Driver-Dispo</CardTitle>
                  <div className="flex gap-2">
                    {driverBlocker > 0 && <Badge variant="destructive">{driverBlocker} Blocker</Badge>}
                    {driverWarnings > 0 && <Badge variant="secondary">{driverWarnings} Warnungen</Badge>}
                    <Badge variant="outline">{fahrzeitStunden.toFixed(2)} h Fahrzeit</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <DataTable
                  data={driverRows}
                  columns={driverColumns}
                  onRowFocus={(row) => {
                    setSelectedDriverEvent(row)
                    setDriverPatchForm({ vehicleId: row.fahrzeug ?? '', tourRef: row.tour ?? '', notes: '' })
                  }}
                />
              </CardContent>
            </Card>
            {selectedDriverEvent ? (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Fahrer-Detail / Tour-Plausibilitaet</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Fahrer</p>
                      <p className="font-semibold">{selectedDriverEvent.fahrer}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Datum</p>
                      <p className="font-mono text-sm">{selectedDriverEvent.datum}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Tour</p>
                      <p className="font-mono text-sm">{selectedDriverEvent.tour ?? '—'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Fahrzeug</p>
                      <p className={selectedDriverEvent.fahrzeug ? 'font-mono text-sm' : 'text-sm text-destructive'}>
                        {selectedDriverEvent.fahrzeug ?? 'fehlt'}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Zeit</p>
                      <p className="font-mono text-sm">{selectedDriverEvent.start} – {selectedDriverEvent.ende}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Dauer</p>
                      <p className="font-semibold">{selectedDriverEvent.dauer.toFixed(2)} h</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant="outline">{selectedDriverEvent.taetigkeit}</Badge>
                    <Badge variant="outline">{selectedDriverEvent.quelle}</Badge>
                  </div>
                  {selectedDriverEvent.findings.length > 0 && (
                    <div>
                      <p className="mb-1 text-sm font-medium text-muted-foreground">Plausibilitaets-Checks</p>
                      <div className="space-y-1">
                        {selectedDriverEvent.findings.map((finding) => (
                          <div key={`${selectedDriverEvent.id}-${finding.code}`} className="rounded border p-2 text-xs">
                            <Badge variant={getFindingBadgeVariant(finding.severity)} className="mb-1">{finding.severity}</Badge>
                            <p>{finding.message}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="space-y-2 border-t pt-3">
                    <p className="text-sm font-medium">Tour / Fahrzeug korrigieren</p>
                    <Input
                      placeholder="Fahrzeug-ID"
                      value={driverPatchForm.vehicleId}
                      onChange={(e) => setDriverPatchForm((prev) => ({ ...prev, vehicleId: e.target.value }))}
                    />
                    <Input
                      placeholder="Tour-Referenz"
                      value={driverPatchForm.tourRef}
                      onChange={(e) => setDriverPatchForm((prev) => ({ ...prev, tourRef: e.target.value }))}
                    />
                    <Input
                      placeholder="Notiz (optional)"
                      value={driverPatchForm.notes}
                      onChange={(e) => setDriverPatchForm((prev) => ({ ...prev, notes: e.target.value }))}
                    />
                    <Button
                      size="sm"
                      className="w-full gap-2"
                      disabled={updateDriverTimeEvent.isPending}
                      onClick={() => {
                        if (!selectedDriverEvent) return
                        updateDriverTimeEvent.mutate({
                          eventId: selectedDriverEvent.id,
                          data: {
                            vehicle_id: driverPatchForm.vehicleId || null,
                            tour_ref: driverPatchForm.tourRef || null,
                            notes: driverPatchForm.notes || null,
                          },
                        })
                      }}
                    >
                      <Save className="h-4 w-4" />
                      Tour / Fahrzeug speichern
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="flex items-center justify-center">
                <CardContent className="py-8 text-center text-sm text-muted-foreground">
                  Fahrer-Zeile auswaehlen fuer Detail und Tour-Korrektur
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="zeiten">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
            <Card>
              <CardHeader>
                <CardTitle>Klassische Arbeitszeit</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <DataTable data={filteredTimeEntries} columns={columns} onRowFocus={setSelectedTimeEntry} />
                <div className="mt-6 flex justify-between border-t pt-4 font-bold">
                  <span>Gesamt-Stunden Heute:</span>
                  <span>{gesamtStunden.toFixed(1)} h</span>
                </div>
              </CardContent>
            </Card>
            {selectedTimeEntry ? (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Zeitbuchung Detail</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Mitarbeiter</p>
                    <p className="font-semibold">{selectedTimeEntry.mitarbeiter}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Datum</p>
                      <p className="font-mono text-sm">{new Date(selectedTimeEntry.datum).toLocaleDateString('de-DE')}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Stunden</p>
                      <p className="font-semibold">{selectedTimeEntry.stunden} h</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Kommen</p>
                      <p className="font-mono">{selectedTimeEntry.kommen}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Gehen</p>
                      <p className="font-mono">{selectedTimeEntry.gehen}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Typ</p>
                    <Badge variant={selectedTimeEntry.typ === 'Ueberstunden' ? 'destructive' : selectedTimeEntry.typ === 'Urlaub' ? 'secondary' : 'outline'}>
                      {selectedTimeEntry.typ}
                    </Badge>
                  </div>
                  {cockpit.complianceIssues.filter((issue) => issue.employeeRef === selectedTimeEntry.mitarbeiter).length > 0 && (
                    <div>
                      <p className="mb-1 text-sm text-muted-foreground">Compliance-Befunde</p>
                      <div className="space-y-1">
                        {cockpit.complianceIssues
                          .filter((issue) => issue.employeeRef === selectedTimeEntry.mitarbeiter)
                          .map((issue) => (
                            <div key={`${issue.employeeRef}-${issue.code}`} className="rounded border p-2 text-xs">
                              <Badge variant={getFindingBadgeVariant(issue.severity)} className="mb-1">{issue.severity}</Badge>
                              <p>{issue.message}</p>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                  <div className="space-y-2 border-t pt-3">
                    <Button size="sm" variant="outline" className="w-full gap-2" onClick={() => startCorrection(selectedTimeEntry)}>
                      <Pencil className="h-4 w-4" />
                      Bearbeiten / Korrigieren
                    </Button>
                    <Button size="sm" variant="outline" className="w-full gap-2" onClick={() => submitTimeEntry.mutate(selectedTimeEntry.id)} disabled={submitTimeEntry.isPending}>
                      <Save className="h-4 w-4" />
                      Zur Freigabe einreichen
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="flex items-center justify-center text-muted-foreground">
                <CardContent className="py-8 text-center text-sm">
                  Zeile auswaehlen fuer Details und Aktionen
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="payroll">
          <div className="space-y-4">
            {cockpit.payrollReadiness.blockers.length > 0 ? (
              <div className="flex items-start gap-3 rounded-md border border-destructive/50 bg-destructive/5 p-4">
                <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
                <div className="flex-1">
                  <p className="font-semibold text-destructive">Export gesperrt — {cockpit.payrollReadiness.blockers.length} Blocker offen</p>
                  <p className="mt-1 text-sm text-muted-foreground">Alle Blocker muessen behoben oder begruendet sein, bevor das Exportpaket erstellt werden kann.</p>
                  <div className="mt-3 space-y-2">
                    {cockpit.payrollReadiness.blockers.map((blocker, index) => (
                      <div key={`${blocker}-${index}`} className="flex items-center gap-2 rounded border border-destructive/30 bg-background px-3 py-2">
                        <Badge variant="destructive" className="shrink-0">Blocker</Badge>
                        <span className="text-sm">{blocker}</span>
                        <Button size="sm" variant="outline" className="ml-auto gap-1 text-xs" onClick={() => setActiveTab('steuerung')}>
                          Pruefen
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 rounded-md border border-emerald-200 bg-emerald-50 p-4">
                <CheckCircle2 className="h-5 w-5 text-emerald-700" />
                <div className="flex-1">
                  <p className="font-semibold text-emerald-800">Export freigegeben</p>
                  <p className="text-sm text-muted-foreground">{cockpit.payrollReadiness.exportHint}</p>
                </div>
                <Button size="sm" className="gap-2" onClick={handleCreatePayroll} disabled={createPayrollExport.isPending}>
                  <FileDown className="h-4 w-4" />
                  Export erstellen
                </Button>
              </div>
            )}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <CardTitle>Payroll-Readiness</CardTitle>
                  <Badge variant={cockpit.payrollReadiness.status === 'ready' ? 'outline' : 'destructive'}>
                    {cockpit.payrollReadiness.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <p className="text-sm text-muted-foreground">Bereite Eintraege</p>
                    <p className="text-xl font-semibold text-emerald-700">{cockpit.payrollReadiness.readyEntries}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Blockierte Eintraege</p>
                    <p className="text-xl font-semibold text-destructive">{cockpit.payrollReadiness.blockedEntries}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Offene Blocker</p>
                    <p className="text-xl font-semibold">{cockpit.payrollReadiness.blockers.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <div className="grid gap-4 xl:grid-cols-2">
              <Card><CardHeader><CardTitle>Payroll-Exporte</CardTitle></CardHeader><CardContent><DataTable data={payrollExports} columns={payrollColumns} /></CardContent></Card>
              <Card><CardHeader><CardTitle>Abwesenheiten</CardTitle></CardHeader><CardContent><DataTable data={absences} columns={absenceColumns} /></CardContent></Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
