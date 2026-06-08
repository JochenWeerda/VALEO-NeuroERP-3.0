import { useEffect, useMemo } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { apiClient } from '@/lib/api-client'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { useAccountingPeriods, useFibuCockpit } from '@/lib/api/fibu'
import { summarizeFibuOps } from '@/lib/professional-control-centers'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type CockpitChecklist = {
  id: string
  period: string
  closing_type: string
  status: string
  progress_percentage: number
  completed_required_items: number
  required_items: number
  updated_at?: string | null
}

type ClosingCockpitSummary = {
  tenant_id: string
  period?: string | null
  periods: { open: number; closed: number; adjusting: number }
  checklists: { total: number; completed: number; in_progress: number; blocked: number; avg_progress: number }
  blockers: CockpitChecklist[]
  latest_checklists: CockpitChecklist[]
}

const EMPTY_CLOSING_COCKPIT_SUMMARY: ClosingCockpitSummary = {
  tenant_id: '',
  period: null,
  periods: { open: 0, closed: 0, adjusting: 0 },
  checklists: { total: 0, completed: 0, in_progress: 0, blocked: 0, avg_progress: 0 },
  blockers: [],
  latest_checklists: [],
}

export default function AbschlussCockpitPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')

  const { data, isLoading, error } = useQuery({
    queryKey: ['finance', 'closing-cockpit-summary'],
    queryFn: async () => (await apiClient.get<ClosingCockpitSummary>('/api/v1/finance/closing-checklists/cockpit/summary')).data,
    initialData: EMPTY_CLOSING_COCKPIT_SUMMARY,
    staleTime: 30_000,
  })
  const { data: fibuCockpit } = useFibuCockpit()
  const { data: periods } = useAccountingPeriods()

  const blockers = useMemo(() => data.blockers, [data])
  const adjustingPeriods = periods.filter((period) => period.status === 'ADJUSTING').length
  const fibuOps = summarizeFibuOps(fibuCockpit, adjustingPeriods)
  const operationalStatus = normalizeOperationalStatus(
    blockers.length > 0 || fibuOps.reorgRisk === 'hoch'
      ? 'eskaliert'
      : !fibuCockpit.annual_close.ready_for_year_close || fibuOps.interestPressure === 'mittel'
        ? 'wartet_auf_mensch'
        : data.checklists.in_progress > 0
          ? 'in_pruefung'
          : 'abgeschlossen',
  )
  const contextSections = [
    {
      title: 'Periodenlage',
      items: [
        { label: 'Offen', value: String(data.periods.open) },
        { label: 'Adjusting', value: String(data.periods.adjusting) },
        { label: 'Geschlossen', value: String(data.periods.closed) },
      ],
    },
    {
      title: 'Operatorbild',
      items: [
        { label: 'Zinsdruck', value: fibuOps.interestPressure },
        { label: 'Reorg-Risiko', value: fibuOps.reorgRisk },
        { label: 'Naechste Aktion', value: fibuOps.nextAction },
      ],
    },
    {
      title: 'Revision',
      items: [
        { label: 'Exportlaeufe', value: String(fibuCockpit.revision.export_runs) },
        { label: 'Letzter Eintrag', value: fibuCockpit.revision.last_entry_date || 'n/a' },
        { label: 'Jahreswechsel', value: fibuCockpit.annual_close.ready_for_year_close ? 'bereit' : 'offen' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: blockers.length > 0 ? 'Blocker im Abschluss' : 'Keine kritischen Blocker',
      detail: blockers.length > 0 ? `${blockers.length} Checklisten oder Perioden mit Eskalationsbedarf.` : 'Aktuell kein Abschlussblocker in den letzten Checklisten.',
      timestamp: blockers[0]?.updated_at || undefined,
    },
    {
      label: adjustingPeriods > 0 ? 'Reorganisator aktiv' : 'Reorganisator ruhig',
      detail: adjustingPeriods > 0 ? `${adjustingPeriods} Adjusting-Perioden sind in Nachbearbeitung.` : 'Keine offenen Adjusting-Perioden im aktuellen Ausschnitt.',
    },
    {
      label: fibuCockpit.interest.candidate_count > 0 ? 'Zinskandidaten offen' : 'Zinslage unkritisch',
      detail: fibuCockpit.interest.candidate_count > 0
        ? `${fibuCockpit.interest.candidate_count} Zinskandidaten mit ${fibuCockpit.interest.candidate_amount.toFixed(0)} EUR Bezugsmenge.`
        : 'Kein aktueller Zinsdruck im ausgewerteten Cockpit.',
    },
  ]

  useEffect(() => {
    if (!workflowProcess || !workflowInstanceId) return
    void saveFlowSpineResumeCheckpoint(workflowProcess, workflowInstanceId, {
      resume_node_id: 'close',
      resume_route: `/fibu/abschluss-cockpit?${searchParams.toString()}`,
      resume_payload: {
        screen: 'closing-cockpit',
        workflowCase: workflowCase || undefined,
      },
      business_status: 'abschluss_in_bearbeitung',
      action_label: 'Close-Cockpit geoeffnet',
    })
  }, [workflowCase, workflowInstanceId, workflowProcess, searchParams])

  const openChecklistDetail = async (itemId: string) => {
    const query = workflowInstanceId ? `?workflowInstanceId=${workflowInstanceId}&workflowProcess=${workflowProcess ?? ''}&workflowCase=${workflowCase ?? ''}` : ''
    const target = `/fibu/abschluss-checklist-detail/${itemId}${query}`
    if (workflowProcess && workflowInstanceId) {
      await saveFlowSpineResumeCheckpoint(workflowProcess, workflowInstanceId, {
        resume_node_id: 'close',
        resume_route: target,
        resume_payload: {
          screen: 'closing-checklist-detail',
          checklistId: itemId,
          workflowCase: workflowCase || undefined,
        },
        business_status: 'abschluss_checkliste_in_bearbeitung',
        action_label: 'Abschluss-Checkliste geoeffnet',
      })
    }
    navigate(target)
  }

  if (isLoading) {
    return <div className="p-6 text-sm text-muted-foreground">Lade Abschluss-Cockpit...</div>
  }

  if (error) {
    return <div className="p-6 text-sm text-red-600">Abschluss-Cockpit konnte nicht geladen werden.</div>
  }

  return (
    <div className="space-y-6 p-6">
      {workflowInstanceId && (
        <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
          Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      )}
      <div>
        <h1 className="text-3xl font-bold">Abschluss-Cockpit</h1>
        <p className="text-muted-foreground">Status der Perioden und Abschluss-Checklisten inkl. Blocker-Uebersicht.</p>
      </div>

      <OperationalCaseHeader
        title="FIBU-Operatorlauf"
        description="Der Abschlussraum fuehrt Periodendruck, Reorganisator, Zinslage und Revisionspfad als einen Operatorfall."
        status={operationalStatus}
        owner="Finance Operations"
        blocker={blockers.length > 0 ? `${blockers.length} Blocker bremsen den Abschluss oder die technische Nacharbeit.` : null}
        nextAction={fibuOps.nextAction}
        caseLabel={data.period || 'Laufender Abschluss'}
        tags={['FIBU', 'Abschluss', 'Operator']}
      />

      <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
        <OperationalTimeline title="Abschlussverlauf" items={timelineItems} />
        <OperationalContextPanel title="FIBU-Kontext" sections={contextSections} />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Perioden offen</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{data.periods.open}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Checklisten total</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{data.checklists.total}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Abgeschlossen</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{data.checklists.completed}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Blocker</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{blockers.length}</div></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Zinsdruck</CardTitle></CardHeader>
          <CardContent><Badge variant={fibuOps.interestPressure === 'hoch' ? 'destructive' : 'outline'}>{fibuOps.interestPressure}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Reorg-Risiko</CardTitle></CardHeader>
          <CardContent><Badge variant={fibuOps.reorgRisk === 'hoch' ? 'destructive' : 'outline'}>{fibuOps.reorgRisk}</Badge></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Aktion</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuOps.nextAction}</div></CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Jahreswechsel</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Reorganisator</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{adjustingPeriods}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Exportläufe</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{fibuCockpit.revision.export_runs}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Mahn-/Zinsparameter</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.master_data.dunning_parameters_ready && fibuCockpit.master_data.interest_groups_ready ? 'vollständig' : 'prüfen'}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Aktuelle Checklisten</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {data.latest_checklists.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded border p-3">
              <div>
                <div className="font-medium">{item.period} · {item.closing_type}</div>
                <div className="text-xs text-muted-foreground">
                  Pflicht: {item.completed_required_items}/{item.required_items} · Fortschritt: {item.progress_percentage.toFixed(1)}%
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={item.status === 'blocked' ? 'destructive' : 'outline'}>{item.status}</Badge>
                <Button variant="outline" size="sm" onClick={() => { void openChecklistDetail(item.id) }}>
                  Details
                </Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
