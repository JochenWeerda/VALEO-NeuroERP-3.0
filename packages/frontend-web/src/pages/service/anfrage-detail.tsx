/**
 * Service-Anfrage Detail — Tabs mit Uebersicht, Aktivitaeten, Abschluss
 * Backend: GET/PUT /api/v1/service/anfragen/{id}
 */

import { useState } from 'react'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/react-router-compat'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { useToast } from '@/hooks/use-toast'
import {
  WorkflowEntryBanner,
  readWorkflowEntryContext,
} from '@/components/workflow/WorkflowEntryBanner'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { summarizeCustomerOperations } from '@/lib/domain-depth'
import { ArrowLeft, CheckCircle, ClipboardList, FileText, Loader2, Save, Wrench } from 'lucide-react'

// ── Types ────────────────────────────────────────────────────────────────────

type ServiceAnfrageDetail = {
  id: string
  nummer: string
  kunde: string
  betreff: string
  beschreibung?: string
  datum: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
  status: 'neu' | 'in-bearbeitung' | 'erledigt'
}

const PRIORITAET_OPTIONS = [
  { value: 'hoch', label: 'Hoch' },
  { value: 'normal', label: 'Normal' },
  { value: 'niedrig', label: 'Niedrig' },
]

const STATUS_OPTIONS = [
  { value: 'neu', label: 'Neu' },
  { value: 'in-bearbeitung', label: 'In Bearbeitung' },
  { value: 'erledigt', label: 'Erledigt' },
]

// ── Component ────────────────────────────────────────────────────────────────

export default function AnfrageDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const [activeTab, setActiveTab] = useState('uebersicht')
  const [editData, setEditData] = useState<Partial<ServiceAnfrageDetail>>({})
  const [isDirty, setIsDirty] = useState(false)

  const {
    data: anfrage,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['service', 'anfrage', id],
    queryFn: async () =>
      (await apiClient.get<ServiceAnfrageDetail>(`/api/v1/service/anfragen/${id}`)).data,
    enabled: !!id,
  })

  // Sync loaded data into edit state
  const merged = anfrage ? { ...anfrage, ...editData } : null

  const updateField = (field: string, value: string) => {
    setEditData((prev) => ({ ...prev, [field]: value }))
    setIsDirty(true)
  }

  const saveMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.put(`/api/v1/service/anfragen/${id}`, merged)).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['service', 'anfrage', id] })
      void queryClient.invalidateQueries({ queryKey: ['service', 'anfragen'] })
      setIsDirty(false)
      setEditData({})
      toast({ title: 'Gespeichert', description: 'Anfrage wurde aktualisiert.' })
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Speichern fehlgeschlagen.', variant: 'destructive' })
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError || !merged) {
    return (
      <div className="p-6">
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-red-600">Anfrage konnte nicht geladen werden.</p>
            <Button variant="outline" className="mt-4" onClick={() => navigate('/service/anfragen')}>
              Zurueck zur Liste
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const operationalStatus = normalizeOperationalStatus(
    merged.status === 'neu' ? 'offen' : merged.status === 'in-bearbeitung' ? 'in_pruefung' : 'abgeschlossen',
  )
  const operationalBlocker = merged.prioritaet === 'hoch' && merged.status !== 'erledigt'
    ? 'Hohe Prioritaet: Rueckmeldung oder Einsatz darf nicht liegen bleiben.'
    : null
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Kunde', value: merged.kunde },
        { label: 'Betreff', value: merged.betreff },
        { label: 'Ticket', value: merged.nummer },
      ],
    },
    {
      title: 'Service',
      items: [
        { label: 'Prioritaet', value: merged.prioritaet },
        { label: 'Status', value: merged.status },
        { label: 'Datum', value: new Date(merged.datum).toLocaleDateString('de-DE') },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Workflow', value: workflowContext?.label || workflowContext?.process || 'Kein Handover' },
        { label: 'Owner', value: 'Service' },
        { label: 'Naechster Fokus', value: merged.status === 'erledigt' ? 'Abschluss und Zufriedenheit' : 'Rueckmeldung oder Einsatz' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Servicefall angelegt', detail: `${merged.nummer} / ${merged.kunde}`, timestamp: merged.datum },
    { label: 'Aktueller Bearbeitungsstand', detail: merged.status === 'neu' ? 'Erstpruefung offen' : merged.status === 'in-bearbeitung' ? 'Bearbeitung laeuft' : 'Fachlich erledigt' },
    ...(workflowContext?.instanceId ? [{ label: 'Workflow-Handover', detail: workflowContext.label || workflowContext.process || undefined }] : []),
  ]
  const serviceOps = summarizeCustomerOperations({
    duplicateCount: 0,
    hasOwner: true,
    hasReachableContact: Boolean(merged.kunde),
    nextActions: merged.status === 'erledigt' ? 1 : 2,
  })

  return (
    <div className="space-y-6 p-6">
      {/* Workflow Banner */}
      {workflowContext && (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Service-to-Customer"
          description="Die Service-Anfrage wird hier bearbeitet. Der Flow-Fall bleibt als Referenz erhalten."
        />
      )}

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/service/anfragen')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Anfrage {merged.nummer}</h1>
            <p className="text-muted-foreground">Kunde: {merged.kunde}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={
              merged.prioritaet === 'hoch'
                ? 'destructive'
                : merged.prioritaet === 'normal'
                  ? 'secondary'
                  : 'outline'
            }
          >
            {merged.prioritaet === 'hoch' ? 'Hoch' : merged.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
          </Badge>
          <Badge
            variant={
              merged.status === 'erledigt'
                ? 'outline'
                : merged.status === 'in-bearbeitung'
                  ? 'secondary'
                  : 'default'
            }
          >
            {merged.status === 'neu' ? 'Neu' : merged.status === 'in-bearbeitung' ? 'In Bearbeitung' : 'Erledigt'}
          </Badge>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={!isDirty || saveMutation.isPending}
            className="gap-2"
          >
            {saveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Speichern
          </Button>
        </div>
      </div>
      <div className="space-y-4">
        <OperationalCaseHeader
          title="Servicefall steuern"
          description="Der Kopf reduziert die Service-Anfrage auf Zustand, Risiko und die naechste fachliche Aktion."
          status={operationalStatus}
          owner="Service"
          blocker={operationalBlocker}
          nextAction={merged.status === 'erledigt' ? 'Abschluss und Kundenzufriedenheit erfassen' : 'Rueckmeldung oder Aussendienst dokumentieren'}
          caseLabel={merged.nummer}
          tags={['Service', 'Kunde']}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTimeline title="Fallverlauf" items={timelineItems} />
          <OperationalContextPanel title="Servicekontext" sections={contextSections} />
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Ownership-Rahmen</CardTitle></CardHeader>
            <CardContent><div className="text-lg font-semibold">{serviceOps.ownershipRisk}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Aktion</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{serviceOps.nextAction}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Folgeobjekte</CardTitle></CardHeader>
            <CardContent><div className="text-sm text-muted-foreground">{merged.status === 'erledigt' ? 'Abschluss, Dokumentation, Kundenzufriedenheit' : 'Rueckmeldung, Aussendienst, Dokumente'}</div></CardContent>
          </Card>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="uebersicht">Uebersicht</TabsTrigger>
          <TabsTrigger value="aktivitaeten">Aktivitaeten</TabsTrigger>
          <TabsTrigger value="abschluss">Abschluss</TabsTrigger>
        </TabsList>

        {/* Tab: Uebersicht */}
        <TabsContent value="uebersicht" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Anfragedaten</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="nummer">Ticket-Nr.</Label>
                  <Input id="nummer" value={merged.nummer} readOnly />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="kunde">Kunde</Label>
                  <Input
                    id="kunde"
                    value={merged.kunde}
                    onChange={(e) => updateField('kunde', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="betreff">Betreff</Label>
                  <Input
                    id="betreff"
                    value={merged.betreff}
                    onChange={(e) => updateField('betreff', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="datum">Datum</Label>
                  <Input id="datum" type="date" value={merged.datum?.slice(0, 10)} readOnly />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="prioritaet">Prioritaet</Label>
                  <select
                    id="prioritaet"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={merged.prioritaet}
                    onChange={(e) => updateField('prioritaet', e.target.value)}
                  >
                    {PRIORITAET_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <select
                    id="status"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={merged.status}
                    onChange={(e) => updateField('status', e.target.value)}
                  >
                    {STATUS_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="beschreibung">Beschreibung</Label>
                  <Textarea
                    id="beschreibung"
                    rows={4}
                    value={merged.beschreibung ?? ''}
                    onChange={(e) => updateField('beschreibung', e.target.value)}
                    placeholder="Beschreibung der Anfrage..."
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Aktivitaeten (Placeholder) */}
        <TabsContent value="aktivitaeten">
          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Vorgangsverlauf</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-2xl border bg-muted/40 p-4">
                  <div className="font-medium">Ticketanlage</div>
                  <div className="text-sm text-muted-foreground">
                    {new Date(merged.datum).toLocaleDateString('de-DE')} · {merged.kunde}
                  </div>
                </div>
                <div className="rounded-2xl border bg-muted/40 p-4">
                  <div className="font-medium">Bearbeitungsstatus</div>
                  <div className="text-sm text-muted-foreground">
                    {merged.status === 'neu'
                      ? 'Neue Anfrage, Erstpruefung und Rueckruf stehen an.'
                      : merged.status === 'in-bearbeitung'
                        ? 'Rueckmeldung, Dokumentation oder Aussendienst-Einsatz laufen.'
                        : 'Vorgang fachlich erledigt, Abschluss und Kundenzufriedenheit pruefen.'}
                  </div>
                </div>
                {workflowContext ? (
                  <div className="rounded-2xl border bg-muted/40 p-4">
                    <div className="font-medium">Workflow-Referenz</div>
                    <div className="text-sm text-muted-foreground">
                      {workflowContext.label || workflowContext.caseNumber || workflowContext.process || 'Service-to-Customer'} · {workflowContext.instanceId}
                    </div>
                  </div>
                ) : null}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Folgeaktionen</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-2">
                <Button onClick={() => navigate(`/service/rueckmeldung?anfrage_id=${merged.id}`)} className="justify-start gap-2">
                  <ClipboardList className="h-4 w-4" />
                  Rueckmeldung erfassen
                </Button>
                <Button variant="outline" onClick={() => navigate(`/agribusiness/field-service-tasks/neu?service_request_id=${merged.id}`)} className="justify-start gap-2">
                  <Wrench className="h-4 w-4" />
                  Aussendienst-Einsatz anlegen
                </Button>
                <Button variant="outline" onClick={() => navigate('/dokumente/ablage')} className="justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Dokumentenablage oeffnen
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tab: Abschluss */}
        <TabsContent value="abschluss">
          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Abschlussbild</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="rounded-2xl border p-4">
                    <div className="text-sm text-muted-foreground">Status</div>
                    <div className="font-semibold">
                      {merged.status === 'neu' ? 'Erstkontakt offen' : merged.status === 'in-bearbeitung' ? 'Rueckmeldung laeuft' : 'Abschluss moeglich'}
                    </div>
                  </div>
                  <div className="rounded-2xl border p-4">
                    <div className="text-sm text-muted-foreground">Prioritaet</div>
                    <div className="font-semibold">
                      {merged.prioritaet === 'hoch' ? 'Sofort eskalieren falls offen' : merged.prioritaet === 'normal' ? 'Regulaere Bearbeitung' : 'Geringe Dringlichkeit'}
                    </div>
                  </div>
                  <div className="rounded-2xl border p-4">
                    <div className="text-sm text-muted-foreground">Naechster Schritt</div>
                    <div className="font-semibold">
                      {merged.status === 'erledigt' ? 'Kundenzufriedenheit erfassen' : 'Rueckmeldung oder Einsatz dokumentieren'}
                    </div>
                  </div>
                </div>
                <div className="rounded-2xl border bg-muted/40 p-4 text-sm text-muted-foreground">
                  Ein Service-Fall gilt hier erst als fachlich geschlossen, wenn Rueckmeldung, Abschlusskommentar und Kundenzufriedenheit dokumentiert sind.
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Abschlussaktionen</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-2">
                <Button onClick={() => navigate(`/service/abschluss?anfrage_id=${merged.id}`)} className="justify-start gap-2">
                  <CheckCircle className="h-4 w-4" />
                  Abschluss erfassen
                </Button>
                <Button variant="outline" onClick={() => navigate(`/service/rueckmeldung?anfrage_id=${merged.id}`)} className="justify-start gap-2">
                  <ClipboardList className="h-4 w-4" />
                  Rueckmeldung nachtragen
                </Button>
                <Button variant="outline" onClick={() => navigate('/service/anfragen')} className="justify-start gap-2">
                  <FileText className="h-4 w-4" />
                  Zur Service-Uebersicht
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
