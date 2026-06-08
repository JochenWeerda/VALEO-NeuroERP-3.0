import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { FileDown, HeadphonesIcon, Plus, Search, Wrench } from 'lucide-react'
import { useServiceAnfragen, type ServiceAnfrage } from '@/lib/api/betrieb'
import { ErrorState } from '@/components/ErrorState'
import {
  CrudCapabilityChecklist,
  EmptyStateWithAction,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'

function exportCsv(rows: ServiceAnfrage[]): void {
  const header = ['Ticket-Nr.', 'Kunde', 'Betreff', 'Datum', 'Prioritaet', 'Status']
  const lines = rows.map((item) =>
    [item.nummer, item.kunde, item.betreff, item.datum, item.prioritaet, item.status]
      .map((value) => `"${String(value).replaceAll('"', '""')}"`)
      .join(';'),
  )
  const blob = new Blob([[header.join(';'), ...lines].join('\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `service-anfragen-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

type ServiceRole = 'service' | 'aussendienst' | 'disposition' | 'leitung'

const serviceRoles = [
  {
    id: 'service',
    label: 'Service',
    description: 'Anfragen annehmen, priorisieren und die naechste Kundenaktion starten.',
  },
  {
    id: 'aussendienst',
    label: 'Aussendienst',
    description: 'Einsaetze vorbereiten und Rueckmeldungen nach Besuch erfassen.',
  },
  {
    id: 'disposition',
    label: 'Disposition',
    description: 'Offene Tickets nach Dringlichkeit, Termin und Ressourcen steuern.',
  },
  {
    id: 'leitung',
    label: 'Leitung',
    description: 'Rueckstand, Hoch-Prioritaeten und Abschlussfaehigkeit pruefen.',
  },
] satisfies Array<{ id: ServiceRole; label: string; description: string }>

export default function ServiceAnfragenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFocus, setRoleFocus] = useState<ServiceRole>('service')
  const { data: anfragen = [], isError, error, refetch } = useServiceAnfragen()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const navigateWithWorkflowResume = async (targetPath: string, resumeNodeId: string): Promise<void> => {
    const query = workflowContext ? searchParams.toString() : ''
    const target = `${targetPath}${query ? `?${query}` : ''}`
    if (workflowContext?.process && workflowContext.instanceId) {
      await saveFlowSpineResumeCheckpoint(workflowContext.process, workflowContext.instanceId, {
        resume_node_id: resumeNodeId,
        resume_route: target,
        resume_payload: {
          screen: targetPath.includes('/neu')
            ? 'service-request-create'
            : targetPath.includes('/rueckmeldung')
              ? 'service-feedback'
              : 'service-request-detail',
          targetPath,
          workflowCase: workflowContext.caseNumber || undefined,
        },
        business_status: 'servicefall_in_bearbeitung',
        action_label: `Service-Resume nach ${targetPath}`,
      })
    }
    navigate(target)
  }

  const filteredAnfragen = useMemo(() => {
    if (!searchTerm) return anfragen
    const query = searchTerm.toLowerCase()
    return anfragen.filter(
      (item) =>
        item.nummer.toLowerCase().includes(query) ||
        item.kunde.toLowerCase().includes(query) ||
        item.betreff.toLowerCase().includes(query),
    )
  }, [anfragen, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const neu = anfragen.filter((a) => a.status === 'neu').length
  const inBearbeitung = anfragen.filter((a) => a.status === 'in-bearbeitung').length
  const erledigt = anfragen.filter((a) => a.status === 'erledigt').length
  const hoch = anfragen.filter((a) => a.prioritaet === 'hoch' && a.status !== 'erledigt').length
  const focusRequest = filteredAnfragen[0]
  const serviceReady = hoch === 0 && neu === 0
  const nextServiceAction = focusRequest
    ? focusRequest.status === 'neu'
      ? `${focusRequest.nummer} pruefen, Prioritaet bestaetigen und Bearbeitung starten.`
      : focusRequest.status === 'in-bearbeitung'
        ? `${focusRequest.nummer} mit Rueckmeldung oder Aussendienst-Termin weiterfuehren.`
        : `${focusRequest.nummer} fuer Abschluss und Kundennachweis pruefen.`
    : searchTerm
      ? 'Suche anpassen oder eine neue Service-Anfrage erfassen.'
      : 'Neue Service-Anfrage erfassen, sobald ein Kunde Hilfe benoetigt.'

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Ticket-Nr.',
      render: (a: ServiceAnfrage) => (
        <button
          onClick={() => { void navigateWithWorkflowResume(`/service/anfrage/${a.id}`, 'service') }}
          className="font-medium text-blue-600 hover:underline"
        >
          {a.nummer}
        </button>
      ),
    },
    { key: 'kunde' as const, label: 'Kunde' },
    { key: 'betreff' as const, label: 'Betreff' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (a: ServiceAnfrage) => new Date(a.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'prioritaet' as const,
      label: 'Prioritaet',
      render: (a: ServiceAnfrage) => (
        <Badge variant={a.prioritaet === 'hoch' ? 'destructive' : a.prioritaet === 'normal' ? 'secondary' : 'outline'}>
          {a.prioritaet === 'hoch' ? 'Hoch' : a.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: ServiceAnfrage) => (
        <Badge variant={a.status === 'erledigt' ? 'outline' : a.status === 'in-bearbeitung' ? 'secondary' : 'default'}>
          {a.status === 'neu' ? 'Neu' : a.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Erledigt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      {workflowContext ? (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Service-to-Customer"
          description="Ticketdaten, Prioritaet, Einsatzplanung und Rueckmeldung werden jetzt in den Service-Masken gepflegt. Der Flow-Fall bleibt als Referenz erhalten."
        />
      ) : null}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Service-Anfragen</h1>
          <p className="text-muted-foreground">Kundenservice, Rueckmeldung und Aussendienst in einem Vorgang.</p>
        </div>
        <Button onClick={() => { void navigateWithWorkflowResume('/service/anfrage/neu', 'service') }} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Anfrage
        </Button>
      </div>

      <RoleFocusBar
        roles={serviceRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={filteredAnfragen.length}
        totalCount={anfragen.length}
        title="Arbeitsrolle fuer diese Service-Liste"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: serviceReady,
          allowedLabel: 'Service steuerbar',
          blockedLabel: 'Rueckstand klaeren',
          summary: serviceReady
            ? 'Es gibt keine neuen oder hoch priorisierten offenen Service-Anfragen. Laufende Faelle koennen regulaer bearbeitet, rueckgemeldet oder abgeschlossen werden.'
            : 'Neue oder hoch priorisierte Service-Anfragen brauchen zuerst eine klare Bearbeitung. Erst danach ist die Service-Lage fuer Abschluss und Reporting belastbar.',
          blockerCount: serviceReady ? 0 : neu + hoch,
          nextFocus: nextServiceAction,
          template: {
            label: 'Service-Ticket-Nachweis',
            href: '/docs/service/service-ticket-nachweis.md',
          },
        }}
      />

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Anfragen Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><HeadphonesIcon className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{anfragen.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Neu</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-red-600">{neu}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{inBearbeitung}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abschlussfaehig</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-700">{erledigt}</span></CardContent></Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Service-Arbeitsplan"
          items={[
            {
              label: 'Anfrage erfassen',
              done: anfragen.length > 0,
              hint: 'Kunde, Betreff und Dringlichkeit muessen fuer die Bearbeitung klar sein.',
            },
            {
              label: 'Prioritaet pruefen',
              done: hoch === 0,
              hint: hoch > 0 ? `${hoch} hoch priorisierte Anfrage(n) zuerst klaeren.` : 'Keine offene Hoch-Prioritaet in der aktuellen Service-Lage.',
            },
            {
              label: 'Rueckmeldung erfassen',
              done: inBearbeitung === 0,
              hint: inBearbeitung > 0 ? `${inBearbeitung} Ticket(s) brauchen eine Rueckmeldung oder Folgetermin.` : 'Keine laufenden Tickets ohne Folgeaktion.',
            },
            {
              label: 'Abschluss nachhalten',
              done: erledigt > 0,
              hint: 'Erledigte Tickets koennen fuer Kundennachweis, Export oder Abschluss geprueft werden.',
            },
          ]}
        />
        <NextActionPanel action={nextServiceAction} tone={serviceReady ? 'emerald' : hoch > 0 ? 'red' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{
              label: 'Service-Rueckmeldeprotokoll',
              href: '/docs/service/service-rueckmeldung.md',
            }}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Anlegen', available: true, hint: 'Neue Anfrage ueber die Schaltflaeche erfassen.' },
              { key: 'read', label: 'Lesen', available: true, hint: 'Liste, Suche, Status und Prioritaet sind direkt sichtbar.' },
              { key: 'update', label: 'Bearbeiten', available: true, hint: 'Detailseite und Rueckmeldung fuehren den Fall weiter.' },
              { key: 'export', label: 'Export', available: true, hint: 'CSV-Export erzeugt einen einfachen Nachweis der gefilterten Liste.' },
            ]}
          />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardHeader><CardTitle>Service-Tickets</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
              </div>
              <Button variant="outline" className="gap-2" onClick={() => exportCsv(filteredAnfragen)}>
                <FileDown className="h-4 w-4" />
                Export
              </Button>
            </div>
            {filteredAnfragen.length > 0 ? (
              <DataTable data={filteredAnfragen} columns={columns} />
            ) : (
              <EmptyStateWithAction
                title="Keine Service-Anfragen gefunden"
                description="Die aktuelle Suche liefert keinen Treffer. Passe die Suche an oder lege direkt eine neue Anfrage an."
                actionLabel="Neue Anfrage"
                onAction={() => { void navigateWithWorkflowResume('/service/anfrage/neu', 'service') }}
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Naechste empfohlene Aktion</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {focusRequest ? (
              <>
                <div className="rounded-2xl border bg-muted/40 p-4">
                  <div className="text-sm text-muted-foreground">{focusRequest.nummer}</div>
                  <div className="font-semibold">{focusRequest.kunde}</div>
                  <div className="text-sm">{focusRequest.betreff}</div>
                </div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>Service-Arbeit wird jetzt als fachlicher Vorgang gefuehrt: Anfrage, Rueckmeldung, Abschluss und optionaler Feldservice liegen direkt beieinander.</p>
                  <p>Export, Dokumentation und Eskalation sind keine isolierten Aktionen mehr, sondern Teil des Ticket-Fortschritts.</p>
                </div>
                <div className="grid gap-2">
                  <Button onClick={() => { void navigateWithWorkflowResume(`/service/anfrage/${focusRequest.id}`, 'service') }}>Anfrage oeffnen</Button>
                  <Button variant="outline" onClick={() => { void navigateWithWorkflowResume(`/service/rueckmeldung?anfrage_id=${focusRequest.id}`, 'service') }}>Rueckmeldung erfassen</Button>
                  <Button variant="outline" onClick={() => navigate('/agribusiness/field-service-tasks')}>
                    <Wrench className="mr-2 h-4 w-4" />
                    Aussendienst koordinieren
                  </Button>
                </div>
              </>
            ) : (
              <div className="rounded-2xl border border-dashed p-4 text-sm text-muted-foreground">
                Keine Service-Anfragen fuer die aktuelle Suche gefunden.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
