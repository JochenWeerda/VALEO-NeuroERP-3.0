/**
 * Reklamation Detail — ObjectPage mit Tabs
 * Backend: app/api/v1/endpoints/reklamation_api.py
 */

import { useState } from 'react'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/typed-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import {
  ArrowLeft,
  CheckCircle,
  ClipboardList,
  FileText,
  Link2,
  Loader2,
  Shield,
} from 'lucide-react'

// ── Types ────────────────────────────────────────────────────────────────────

type ReklamationDetail = {
  reklamation_id: string
  tenant_id: string
  kontrakt_id: string | null
  lieferant_id: string
  typ: string
  status: string
  positionen: Array<{
    artikel_id: string
    bezeichnung: string
    beanstandete_menge: number
    anerkannte_menge: number
    beanstandeter_wert_eur: number
    einheit: string
    grund: string
  }>
  zustaendiger: string
  frist_datum: string
  erstellt_am: string
  crm_referenz: {
    crm_system: string
    crm_case_id: string
    crm_ticket_id?: string
    crm_status?: string
    crm_url?: string
  } | null
  dms_referenzen: Array<{
    dokument_id: string
    dokument_typ?: string
    dateiname?: string
    source_uri?: string
  }>
  gobd_beleg_id: string | null
  sla_status: string
  tage_bis_frist: number
  ist_ueberfaellig: boolean
  hat_crm_bezug: boolean
  hat_dms_bezug: boolean
  gesamtwert_beanstandet_eur: number
  gesamtwert_anerkannt_eur: number
  audit_eintrag_anzahl: number
}

type AuditEntry = {
  eintrag_id: string
  reklamation_id: string
  aktion: string
  zeitstempel: string
  aktor_id: string
  vor_status: string | null
  nach_status: string | null
  beschreibung: string
}

type AuditResponse = {
  reklamation_id: string
  count: number
  audit_integritaet_ok: boolean
  audit_trail: AuditEntry[]
}

type E2EResponse = {
  reklamation: ReklamationDetail
  crm_case_id: string | null
  dms_document_ids: string[]
  sla_status: string
  audit_count: number
  e2e_complete: boolean
}

// ── Valid transitions per status ─────────────────────────────────────────────

const VALID_TRANSITIONS: Record<string, Array<{ value: string; label: string }>> = {
  offen: [
    { value: 'in_pruefung', label: 'In Pruefung nehmen' },
    { value: 'abgelehnt', label: 'Ablehnen' },
  ],
  in_pruefung: [
    { value: 'anerkannt', label: 'Anerkennen' },
    { value: 'teilweise_anerkannt', label: 'Teilweise anerkennen' },
    { value: 'abgelehnt', label: 'Ablehnen' },
  ],
  teilweise_anerkannt: [{ value: 'geschlossen', label: 'Schliessen' }],
  anerkannt: [{ value: 'geschlossen', label: 'Schliessen' }],
  abgelehnt: [{ value: 'geschlossen', label: 'Schliessen' }],
  geschlossen: [],
}

const STATUS_LABELS: Record<string, string> = {
  offen: 'Offen',
  in_pruefung: 'In Pruefung',
  anerkannt: 'Anerkannt',
  teilweise_anerkannt: 'Teilweise anerkannt',
  abgelehnt: 'Abgelehnt',
  geschlossen: 'Geschlossen',
}

const SLA_LABELS: Record<string, string> = {
  in_frist: 'In Frist',
  bald_faellig: 'Bald faellig',
  ueberfaellig: 'Ueberfaellig',
  erledigt: 'Erledigt',
}

// ── Component ────────────────────────────────────────────────────────────────

export default function ReklamationDetailPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const [activeTab, setActiveTab] = useState('uebersicht')
  const [crmCaseId, setCrmCaseId] = useState('')
  const [dmsDocId, setDmsDocId] = useState('')
  const [dmsDocType, setDmsDocType] = useState('')

  // ── Queries ──────────────────────────────────────────────────────────────

  const {
    data: reklamation,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['reklamation', id],
    queryFn: async () =>
      (await apiClient.get<ReklamationDetail>(`/api/v1/reklamationen/${id}`)).data,
    enabled: !!id,
  })

  const { data: auditData } = useQuery({
    queryKey: ['reklamation', id, 'audit'],
    queryFn: async () =>
      (await apiClient.get<AuditResponse>(`/api/v1/reklamationen/${id}/audit`)).data,
    enabled: !!id && activeTab === 'audit',
  })

  const { data: e2eData } = useQuery({
    queryKey: ['reklamation', id, 'e2e'],
    queryFn: async () =>
      (await apiClient.get<E2EResponse>(`/api/v1/reklamationen/${id}/e2e`)).data,
    enabled: !!id,
    staleTime: 30_000,
  })

  // ── Mutations ────────────────────────────────────────────────────────────

  const transitionMutation = useMutation({
    mutationFn: async (neuerStatus: string) =>
      (
        await apiClient.post(`/api/v1/reklamationen/${id}/transition`, {
          neuer_status: neuerStatus,
        })
      ).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['reklamation', id] })
      void queryClient.invalidateQueries({ queryKey: ['qualitaet', 'reklamationen'] })
      toast({ title: 'Status geaendert', description: 'Der Reklamationsstatus wurde aktualisiert.' })
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Statusuebergang fehlgeschlagen.', variant: 'destructive' })
    },
  })

  const handleTransition = async (neuerStatus: string) => {
    await transitionMutation.mutateAsync(neuerStatus)
    // Also advance flow-spine if in workflow context (best-effort)
    if (workflowContext?.instanceId && workflowContext?.process) {
      try {
        await apiClient.post(
          `/api/v1/process/flow-spines/${workflowContext.process}/instances/${workflowContext.instanceId}/transitions`,
          { node_id: 'reklamation', new_status: 'ok', action_label: `Status -> ${neuerStatus}` },
        )
      } catch {
        // best-effort
      }
    }
  }

  const crmMutation = useMutation({
    mutationFn: async () =>
      (
        await apiClient.post(`/api/v1/reklamationen/${id}/crm-reference`, {
          crm_referenz: { crm_system: 'crm', crm_case_id: crmCaseId },
        })
      ).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['reklamation', id] })
      setCrmCaseId('')
      toast({ title: 'CRM verknuepft', description: 'CRM-Fall wurde verknuepft.' })
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'CRM-Verknuepfung fehlgeschlagen.', variant: 'destructive' })
    },
  })

  const dmsMutation = useMutation({
    mutationFn: async () =>
      (
        await apiClient.post(`/api/v1/reklamationen/${id}/dms-referenzen`, {
          dms_referenzen: [{ dokument_id: dmsDocId, dokument_typ: dmsDocType || 'sonstiges' }],
        })
      ).data,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['reklamation', id] })
      setDmsDocId('')
      setDmsDocType('')
      toast({ title: 'Dokument angehangen', description: 'DMS-Dokument wurde verknuepft.' })
    },
    onError: () => {
      toast({
        title: 'Fehler',
        description: 'DMS-Verknuepfung fehlgeschlagen.',
        variant: 'destructive',
      })
    },
  })

  // ── Loading / Error ──────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (isError || !reklamation) {
    return (
      <div className="p-6">
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-red-600">Reklamation konnte nicht geladen werden.</p>
            <Button variant="outline" className="mt-4" onClick={() => navigate('/qualitaet/reklamationen')}>
              Zurueck zur Liste
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const transitions = VALID_TRANSITIONS[reklamation.status] ?? []

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6 p-6">
      {/* Workflow Banner */}
      {workflowContext && (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Complaint-to-Resolution"
          description="Reklamationsfall, Kundenbezug, Dokumente und Bearbeitungsstatus werden hier gepflegt."
        />
      )}

      <OperationalCaseHeader
        title={`Reklamation ${reklamation.reklamation_id.slice(0, 8)}`}
        description="Reklamationsvorgang mit SLA-, CRM-, DMS- und Auditbezug."
        status={reklamation.ist_ueberfaellig ? 'eskaliert' : normalizeOperationalStatus(reklamation.status)}
        owner={reklamation.zustaendiger || 'Qualitaet / Service'}
        blocker={reklamation.ist_ueberfaellig ? 'Die Reklamation ist ueberfaellig und braucht Eskalation.' : null}
        nextAction={
          reklamation.status === 'offen'
            ? 'In Pruefung nehmen'
            : reklamation.status === 'in_pruefung'
              ? 'Entscheidung treffen'
              : 'Vorgang abschliessen'
        }
        caseLabel={workflowContext?.caseNumber || 'Reklamationsfall'}
        tags={[SLA_LABELS[reklamation.sla_status] ?? reklamation.sla_status, STATUS_LABELS[reklamation.status] ?? reklamation.status]}
      />

      <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
        <OperationalTimeline
          title="Fallhistorie"
          items={(auditData?.audit_trail || []).slice(0, 4).map((entry) => ({
            label: entry.aktion,
            detail: entry.beschreibung,
            timestamp: entry.zeitstempel,
          }))}
        />
        <OperationalContextPanel
          title="Reklamationskontext"
          sections={[
            {
              title: 'Objekt',
              items: [
                { label: 'Typ', value: reklamation.typ },
                { label: 'Kontrakt', value: reklamation.kontrakt_id || '-' },
              ],
            },
            {
              title: 'Wirtschaftslage',
              items: [
                { label: 'Beanstandet', value: `${reklamation.gesamtwert_beanstandet_eur.toFixed(2)} EUR` },
                { label: 'Anerkannt', value: `${reklamation.gesamtwert_anerkannt_eur.toFixed(2)} EUR` },
              ],
            },
            {
              title: 'Governance',
              items: [
                { label: 'CRM-Bezug', value: reklamation.hat_crm_bezug ? 'Vorhanden' : 'Offen' },
                { label: 'DMS-Bezug', value: reklamation.hat_dms_bezug ? 'Vorhanden' : 'Offen' },
              ],
            },
          ]}
        />
      </div>

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/qualitaet/reklamationen')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Reklamation {reklamation.reklamation_id.slice(0, 8)}</h1>
            <p className="text-muted-foreground">
              Typ: {reklamation.typ} | Lieferant: {reklamation.lieferant_id}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Badge
            variant={
              reklamation.status === 'geschlossen'
                ? 'outline'
                : reklamation.status === 'abgelehnt'
                  ? 'destructive'
                  : 'default'
            }
          >
            {STATUS_LABELS[reklamation.status] ?? reklamation.status}
          </Badge>
          <Badge
            variant={
              reklamation.sla_status === 'ueberfaellig'
                ? 'destructive'
                : reklamation.sla_status === 'bald_faellig'
                  ? 'secondary'
                  : 'outline'
            }
          >
            SLA: {SLA_LABELS[reklamation.sla_status] ?? reklamation.sla_status}
          </Badge>
        </div>
      </div>

      {/* Transition Buttons */}
      {transitions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {transitions.map((t) => (
            <Button
              key={t.value}
              variant={t.value === 'abgelehnt' ? 'destructive' : 'default'}
              disabled={transitionMutation.isPending}
              onClick={() => void handleTransition(t.value)}
              className="gap-2"
            >
              {transitionMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="h-4 w-4" />
              )}
              {t.label}
            </Button>
          ))}
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="uebersicht">Uebersicht</TabsTrigger>
          <TabsTrigger value="crm">CRM</TabsTrigger>
          <TabsTrigger value="dokumente">Dokumente</TabsTrigger>
          <TabsTrigger value="audit">Audit</TabsTrigger>
        </TabsList>

        {/* Tab: Uebersicht */}
        <TabsContent value="uebersicht" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ClipboardList className="h-5 w-5" />
                  Stammdaten
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">Reklamations-ID</span>
                  <span className="font-medium">{reklamation.reklamation_id.slice(0, 8)}</span>
                  <span className="text-muted-foreground">Typ</span>
                  <span className="font-medium">{reklamation.typ}</span>
                  <span className="text-muted-foreground">Status</span>
                  <span className="font-medium">{STATUS_LABELS[reklamation.status] ?? reklamation.status}</span>
                  <span className="text-muted-foreground">Lieferant</span>
                  <span className="font-medium">{reklamation.lieferant_id}</span>
                  <span className="text-muted-foreground">Zustaendiger</span>
                  <span className="font-medium">{reklamation.zustaendiger}</span>
                  <span className="text-muted-foreground">Frist</span>
                  <span className="font-medium">{reklamation.frist_datum}</span>
                  <span className="text-muted-foreground">Erstellt am</span>
                  <span className="font-medium">
                    {new Date(reklamation.erstellt_am).toLocaleDateString('de-DE')}
                  </span>
                  <span className="text-muted-foreground">Kontrakt</span>
                  <span className="font-medium">{reklamation.kontrakt_id ?? '–'}</span>
                  <span className="text-muted-foreground">GoBD Beleg</span>
                  <span className="font-medium">{reklamation.gobd_beleg_id ?? '–'}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Werte</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">Beanstandet (EUR)</span>
                  <span className="font-medium">
                    {reklamation.gesamtwert_beanstandet_eur.toLocaleString('de-DE', {
                      minimumFractionDigits: 2,
                    })}
                  </span>
                  <span className="text-muted-foreground">Anerkannt (EUR)</span>
                  <span className="font-medium">
                    {reklamation.gesamtwert_anerkannt_eur.toLocaleString('de-DE', {
                      minimumFractionDigits: 2,
                    })}
                  </span>
                  <span className="text-muted-foreground">SLA Tage bis Frist</span>
                  <span className="font-medium">{reklamation.tage_bis_frist}</span>
                  <span className="text-muted-foreground">CRM verknuepft</span>
                  <span className="font-medium">{reklamation.hat_crm_bezug ? 'Ja' : 'Nein'}</span>
                  <span className="text-muted-foreground">DMS verknuepft</span>
                  <span className="font-medium">{reklamation.hat_dms_bezug ? 'Ja' : 'Nein'}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Positionen */}
          {reklamation.positionen.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Positionen</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left">
                        <th className="pb-2 pr-4">Artikel</th>
                        <th className="pb-2 pr-4">Bezeichnung</th>
                        <th className="pb-2 pr-4">Beanstandet</th>
                        <th className="pb-2 pr-4">Anerkannt</th>
                        <th className="pb-2 pr-4">Wert (EUR)</th>
                        <th className="pb-2">Grund</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reklamation.positionen.map((pos, idx) => (
                        <tr key={idx} className="border-b last:border-0">
                          <td className="py-2 pr-4 font-medium">{pos.artikel_id}</td>
                          <td className="py-2 pr-4">{pos.bezeichnung}</td>
                          <td className="py-2 pr-4">
                            {pos.beanstandete_menge} {pos.einheit}
                          </td>
                          <td className="py-2 pr-4">
                            {pos.anerkannte_menge} {pos.einheit}
                          </td>
                          <td className="py-2 pr-4">
                            {pos.beanstandeter_wert_eur.toLocaleString('de-DE', {
                              minimumFractionDigits: 2,
                            })}
                          </td>
                          <td className="py-2">{pos.grund}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* E2E Status */}
          {e2eData && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  E2E-Uebersicht
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
                  <div>
                    <span className="text-muted-foreground">CRM-Fall</span>
                    <p className="font-medium">{e2eData.crm_case_id ?? '–'}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">DMS-Dokumente</span>
                    <p className="font-medium">{e2eData.dms_document_ids.length}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">SLA</span>
                    <p className="font-medium">{SLA_LABELS[e2eData.sla_status] ?? e2eData.sla_status}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">E2E Komplett</span>
                    <p className="font-medium">{e2eData.e2e_complete ? 'Ja' : 'Nein'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Tab: CRM */}
        <TabsContent value="crm" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-5 w-5" />
                CRM-Verknuepfung
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {reklamation.crm_referenz ? (
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span className="text-muted-foreground">CRM System</span>
                  <span className="font-medium">{reklamation.crm_referenz.crm_system}</span>
                  <span className="text-muted-foreground">Fall-ID</span>
                  <span className="font-medium">{reklamation.crm_referenz.crm_case_id}</span>
                  {reklamation.crm_referenz.crm_ticket_id && (
                    <>
                      <span className="text-muted-foreground">Ticket-ID</span>
                      <span className="font-medium">{reklamation.crm_referenz.crm_ticket_id}</span>
                    </>
                  )}
                  {reklamation.crm_referenz.crm_status && (
                    <>
                      <span className="text-muted-foreground">CRM Status</span>
                      <span className="font-medium">{reklamation.crm_referenz.crm_status}</span>
                    </>
                  )}
                  {reklamation.crm_referenz.crm_url && (
                    <>
                      <span className="text-muted-foreground">URL</span>
                      <a
                        href={reklamation.crm_referenz.crm_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-blue-600 hover:underline"
                      >
                        Zum CRM-Fall
                      </a>
                    </>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Noch kein CRM-Fall verknuepft.</p>
              )}

              <div className="border-t pt-4">
                <h4 className="mb-2 text-sm font-semibold">CRM-Fall verknuepfen</h4>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Label htmlFor="crm-case-id">CRM Fall-ID</Label>
                    <Input
                      id="crm-case-id"
                      placeholder="z.B. CRM-2026-0042"
                      value={crmCaseId}
                      onChange={(e) => setCrmCaseId(e.target.value)}
                    />
                  </div>
                  <Button
                    className="mt-6 gap-2"
                    disabled={!crmCaseId.trim() || crmMutation.isPending}
                    onClick={() => crmMutation.mutate()}
                  >
                    {crmMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                    Verknuepfen
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Dokumente */}
        <TabsContent value="dokumente" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                DMS-Dokumente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {reklamation.dms_referenzen.length > 0 ? (
                <div className="space-y-2">
                  {reklamation.dms_referenzen.map((ref, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded border p-3 text-sm"
                    >
                      <div>
                        <p className="font-medium">{ref.dateiname ?? ref.dokument_id}</p>
                        <p className="text-muted-foreground">{ref.dokument_typ ?? 'Unbekannt'}</p>
                      </div>
                      <Badge variant="outline">{ref.dokument_id.slice(0, 8)}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Keine Dokumente verknuepft.</p>
              )}

              <div className="border-t pt-4">
                <h4 className="mb-2 text-sm font-semibold">Dokument anhaengen</h4>
                <div className="flex flex-wrap gap-2">
                  <div className="flex-1">
                    <Label htmlFor="dms-doc-id">Dokument-ID</Label>
                    <Input
                      id="dms-doc-id"
                      placeholder="z.B. DOC-00123"
                      value={dmsDocId}
                      onChange={(e) => setDmsDocId(e.target.value)}
                    />
                  </div>
                  <div className="w-48">
                    <Label htmlFor="dms-doc-type">Dokumenttyp</Label>
                    <Input
                      id="dms-doc-type"
                      placeholder="z.B. gutachten"
                      value={dmsDocType}
                      onChange={(e) => setDmsDocType(e.target.value)}
                    />
                  </div>
                  <Button
                    className="mt-6 gap-2"
                    disabled={!dmsDocId.trim() || dmsMutation.isPending}
                    onClick={() => dmsMutation.mutate()}
                  >
                    {dmsMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                    Anhaengen
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Audit */}
        <TabsContent value="audit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Audit Trail
                {auditData && (
                  <Badge variant={auditData.audit_integritaet_ok ? 'outline' : 'destructive'}>
                    {auditData.audit_integritaet_ok ? 'Integritaet OK' : 'Integritaet verletzt'}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {auditData?.audit_trail.length ? (
                <div className="space-y-3">
                  {auditData.audit_trail.map((entry) => (
                    <div
                      key={entry.eintrag_id}
                      className="flex items-start gap-3 rounded border p-3 text-sm"
                    >
                      <div className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-blue-500" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{entry.beschreibung}</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(entry.zeitstempel).toLocaleString('de-DE')}
                          </span>
                        </div>
                        <p className="text-muted-foreground">
                          Aktion: {entry.aktion} | Akteur: {entry.aktor_id}
                          {entry.vor_status && entry.nach_status && (
                            <span>
                              {' '}
                              | {entry.vor_status} &rarr; {entry.nach_status}
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Keine Audit-Eintraege vorhanden.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
