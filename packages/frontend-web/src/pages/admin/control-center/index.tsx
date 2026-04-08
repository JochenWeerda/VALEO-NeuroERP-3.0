import { useDeferredValue, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CalendarClock, Filter, Siren, TimerReset } from 'lucide-react'
import { AgentenIntegrationWorkspace } from '@/pages/admin/agenten-integration'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'

type ControlCenterPlanning = {
  tenant_id: string
  storage_path: string
  calendar_window: string
  suggested_items: Array<{
    plan_id: string
    kind: string
    title: string
    owner: string
    cadence: string
    status: string
    next_hint: string
  }>
  planned_items: Array<{
    plan_id: string
    title: string
    kind: string
    owner: string
    scheduled_for: string
    status: string
    notes?: string | null
  }>
  summary: {
    heartbeat_count: number
    planned_item_count: number
    blocked_connector_count: number
  }
}

type ControlCenterIncident = {
  incident_id: string
  source: string
  severity: string
  title: string
  status: string
  owner?: string
  escalation_target?: string
  recommended_action: string
  detail?: Record<string, unknown>
}

type ControlCenterIncidents = {
  tenant_id: string
  incident_count: number
  open_quarantine_count: number
  blocked_connector_count: number
  stale_ticket_count: number
  review_ticket_count: number
  journal_error_count: number
  incidents: ControlCenterIncident[]
}

type IncidentFilter = 'all' | 'agent_ops' | 'superglue' | 'high'
type PlanningFilter = 'all' | 'planned' | 'blocked' | 'heartbeat'

function formatDateTime(value: string): string {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }
  return new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parsed)
}

function severityVariant(severity: string): 'default' | 'destructive' | 'outline' | 'secondary' {
  if (severity === 'high') {
    return 'destructive'
  }
  if (severity === 'medium') {
    return 'secondary'
  }
  return 'outline'
}

function sourceLabel(source: string): string {
  if (source === 'agent_ops') {
    return 'Agent Ops'
  }
  if (source === 'superglue_quarantine') {
    return 'Superglue Quarantaene'
  }
  if (source === 'superglue_readiness') {
    return 'Superglue Readiness'
  }
  return source
}

export default function AdminControlCenterPage(): JSX.Element {
  const [scheduledFor, setScheduledFor] = useState('2026-04-09T09:00')
  const [incidentFilter, setIncidentFilter] = useState<IncidentFilter>('all')
  const [planningFilter, setPlanningFilter] = useState<PlanningFilter>('all')
  const [incidentSearch, setIncidentSearch] = useState('')
  const deferredIncidentSearch = useDeferredValue(incidentSearch.trim().toLowerCase())

  const planningQuery = useQuery({
    queryKey: ['agent', 'control-center-planning'],
    queryFn: async () => (await apiClient.get<ControlCenterPlanning>('/api/v1/agents/neuroassist/ops/planning', { params: { tenant_id: 'default' } })).data,
  })
  const incidentsQuery = useQuery({
    queryKey: ['agent', 'control-center-incidents'],
    queryFn: async () => (await apiClient.get<ControlCenterIncidents>('/api/v1/agents/neuroassist/ops/incidents', { params: { tenant_id: 'default' } })).data,
  })

  const refetchAll = async (): Promise<void> => {
    await Promise.all([planningQuery.refetch(), incidentsQuery.refetch()])
  }

  const addPlanningItem = async (): Promise<void> => {
    await apiClient.post('/api/v1/agents/neuroassist/ops/planning/items', {
      tenant_id: 'default',
      plan_id: 'manual:daily-rollout-review',
      title: 'Daily Rollout Review',
      kind: 'manual_ops',
      owner: 'tenant_operations_lead',
      scheduled_for: scheduledFor,
      status: 'planned',
      notes: 'Admin Kontrollzentrum',
    })
    await refetchAll()
  }

  const actOnIncident = async (incidentId: string, action: string): Promise<void> => {
    await apiClient.post(`/api/v1/agents/neuroassist/ops/incidents/${encodeURIComponent(incidentId)}/actions`, {
      tenant_id: 'default',
      action,
      requested_by: 'admin-ui',
      note: `Applied from Control Center: ${action}`,
    })
    await refetchAll()
  }

  if (planningQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingState message="Kontrollzentrum wird geladen..." />
  }

  if (planningQuery.isError || incidentsQuery.isError || !planningQuery.data || !incidentsQuery.data) {
    return <ErrorState error={(planningQuery.error ?? incidentsQuery.error) as Error} onRetry={() => void refetchAll()} />
  }

  const planning = planningQuery.data
  const incidents = incidentsQuery.data
  const highestPriorityIncident = incidents.incidents.find((incident) => incident.severity === 'high') ?? incidents.incidents[0]
  const filteredIncidents = incidents.incidents.filter((incident) => {
    if (incidentFilter === 'agent_ops' && incident.source !== 'agent_ops') {
      return false
    }
    if (incidentFilter === 'superglue' && !incident.source.startsWith('superglue')) {
      return false
    }
    if (incidentFilter === 'high' && incident.severity !== 'high') {
      return false
    }
    if (!deferredIncidentSearch) {
      return true
    }
    const haystack = `${incident.title} ${incident.source} ${incident.owner ?? ''} ${incident.recommended_action}`.toLowerCase()
    return haystack.includes(deferredIncidentSearch)
  })
  const filteredSuggestedItems = planning.suggested_items.filter((item) => {
    if (planningFilter === 'planned') {
      return item.status === 'planned'
    }
    if (planningFilter === 'blocked') {
      return item.status === 'blocked'
    }
    if (planningFilter === 'heartbeat') {
      return item.kind === 'agent_heartbeat'
    }
    return true
  })

  return (
    <div className="space-y-6">
      <AgentenIntegrationWorkspace
        section="overview"
        title="Admin Kontroll- und Ueberwachungszentrum"
        subtitle="Zentraler Leitstand fuer Agenten, Superglue, API-Zugaenge und operativen Integrationszustand."
      />

      <div className="grid gap-4 px-6 xl:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <Siren className="h-5 w-5 text-red-600" />
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Offene Vorfaelle</p>
              <p className="text-2xl font-semibold">{incidents.incident_count}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Blockierte Connectoren</p>
              <p className="text-2xl font-semibold">{incidents.blocked_connector_count}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <TimerReset className="h-5 w-5 text-slate-600" />
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Stale / Review</p>
              <p className="text-2xl font-semibold">{incidents.stale_ticket_count + incidents.review_ticket_count}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <CalendarClock className="h-5 w-5 text-blue-600" />
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Geplante Slots</p>
              <p className="text-2xl font-semibold">{planning.summary.planned_item_count}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 px-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <CardHeader>
            <CardTitle>Prioritaet und Quick Actions</CardTitle>
            <CardDescription>
              Der wichtigste Vorfall und die naechsten sinnvollen Leitstandsaktionen ohne Kontextwechsel.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {highestPriorityIncident ? (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={severityVariant(highestPriorityIncident.severity)}>{highestPriorityIncident.severity}</Badge>
                  <Badge variant="outline">{sourceLabel(highestPriorityIncident.source)}</Badge>
                </div>
                <p className="mt-3 text-lg font-semibold">{highestPriorityIncident.title}</p>
                <p className="text-sm text-muted-foreground">
                  Owner: {highestPriorityIncident.owner ?? 'n/a'} · Escalation: {highestPriorityIncident.escalation_target ?? 'n/a'}
                </p>
                <p className="mt-2 text-sm">{highestPriorityIncident.recommended_action}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {highestPriorityIncident.source === 'agent_ops' ? (
                    <Button type="button" onClick={() => void actOnIncident(highestPriorityIncident.incident_id, 'escalate')}>Jetzt eskalieren</Button>
                  ) : null}
                  {highestPriorityIncident.source === 'superglue_quarantine' ? (
                    <>
                      <Button type="button" onClick={() => void actOnIncident(highestPriorityIncident.incident_id, 'resolve')}>Resolve</Button>
                      <Button type="button" variant="outline" onClick={() => void actOnIncident(highestPriorityIncident.incident_id, 'retry')}>Retry</Button>
                    </>
                  ) : null}
                </div>
              </div>
            ) : (
              <div className="rounded border border-dashed p-4 text-sm text-muted-foreground">
                Keine offenen Vorfaelle. Der Leitstand ist aktuell ruhig.
              </div>
            )}

            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded border p-3 text-sm">
                <p className="font-medium">Quarantaene</p>
                <p>{incidents.open_quarantine_count} offen</p>
              </div>
              <div className="rounded border p-3 text-sm">
                <p className="font-medium">Journal Errors</p>
                <p>{incidents.journal_error_count} Laufzeitfehler</p>
              </div>
              <div className="rounded border p-3 text-sm">
                <p className="font-medium">Planungsfenster</p>
                <p>{planning.calendar_window}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Leitstand Slot anlegen</CardTitle>
            <CardDescription>
              Schneller manueller Review-Slot fuer Rollout, Freigaben oder Incident-Steuerung.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <label htmlFor="plan-time" className="text-sm font-medium">Naechster Leitstand-Slot</label>
            <Input id="plan-time" value={scheduledFor} onChange={(event) => setScheduledFor(event.target.value)} />
            <Button type="button" onClick={() => void addPlanningItem()}>Planungseintrag anlegen</Button>
            <p className="text-xs text-muted-foreground">
              Persistiert unter <code>{planning.storage_path}</code>
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 px-6 pb-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle>Scheduling und Planung</CardTitle>
                <CardDescription>
                  Heartbeats, Connector-Rollouts und manuelle Leitstandsplanung mit Fokusfilter.
                </CardDescription>
              </div>
              <div className="flex flex-wrap gap-2">
                {(['all', 'blocked', 'heartbeat', 'planned'] as PlanningFilter[]).map((filter) => (
                  <Button
                    key={filter}
                    type="button"
                    size="sm"
                    variant={planningFilter === filter ? 'default' : 'outline'}
                    onClick={() => setPlanningFilter(filter)}
                  >
                    {filter}
                  </Button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex flex-wrap gap-2">
              <Badge>{planning.calendar_window}</Badge>
              <Badge variant="outline">Heartbeat: {planning.summary.heartbeat_count}</Badge>
              <Badge variant="outline">Planned: {planning.summary.planned_item_count}</Badge>
              <Badge variant="secondary">Blocked Connectoren: {planning.summary.blocked_connector_count}</Badge>
            </div>

            <div className="space-y-2">
              <p className="font-medium">Suggested Matrix</p>
              {filteredSuggestedItems.length > 0 ? filteredSuggestedItems.slice(0, 6).map((item) => (
                <div key={item.plan_id} className="rounded border p-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant={item.status === 'blocked' ? 'destructive' : item.status === 'ready' ? 'secondary' : 'outline'}>{item.status}</Badge>
                    <Badge variant="outline">{item.kind}</Badge>
                  </div>
                  <p className="mt-2 font-medium">{item.title}</p>
                  <p className="text-muted-foreground">{item.owner} · {item.cadence}</p>
                  <p className="mt-1 text-muted-foreground">{item.next_hint}</p>
                </div>
              )) : (
                <div className="rounded border border-dashed p-4 text-muted-foreground">
                  Keine Eintraege fuer den gewaehlten Fokus.
                </div>
              )}
            </div>

            <div className="space-y-2">
              <p className="font-medium">Planned Items</p>
              {planning.planned_items.length > 0 ? planning.planned_items.slice(0, 6).map((item) => (
                <div key={item.plan_id} className="rounded border p-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline">{item.kind}</Badge>
                    <Badge variant={item.status === 'planned' ? 'default' : 'secondary'}>{item.status}</Badge>
                  </div>
                  <p className="mt-2 font-medium">{item.title}</p>
                  <p className="text-muted-foreground">{item.owner} · {formatDateTime(item.scheduled_for)}</p>
                  {item.notes ? <p className="mt-1 text-muted-foreground">{item.notes}</p> : null}
                </div>
              )) : (
                <div className="rounded border border-dashed p-4 text-muted-foreground">
                  Noch keine geplanten Slots. Lege oben einen Leitstand-Eintrag an.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle>Incident / Alert / Escalation Center</CardTitle>
                <CardDescription>
                  Gemeinsame Vorfallsliste fuer stale Agent-Tickets, Superglue-Blocker und offene Quarantaene.
                </CardDescription>
              </div>
              <div className="flex flex-wrap gap-2">
                {(['all', 'high', 'agent_ops', 'superglue'] as IncidentFilter[]).map((filter) => (
                  <Button
                    key={filter}
                    type="button"
                    size="sm"
                    variant={incidentFilter === filter ? 'default' : 'outline'}
                    onClick={() => setIncidentFilter(filter)}
                  >
                    {filter}
                  </Button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <Input
                value={incidentSearch}
                onChange={(event) => setIncidentSearch(event.target.value)}
                placeholder="Vorfaelle filtern..."
              />
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge variant="destructive">Incidents: {incidents.incident_count}</Badge>
              <Badge variant="secondary">Quarantaene: {incidents.open_quarantine_count}</Badge>
              <Badge variant="outline">Stale: {incidents.stale_ticket_count}</Badge>
              <Badge variant="outline">Review: {incidents.review_ticket_count}</Badge>
            </div>

            {filteredIncidents.length > 0 ? filteredIncidents.slice(0, 8).map((incident) => (
              <div key={incident.incident_id} className="rounded border p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={severityVariant(incident.severity)}>{incident.severity}</Badge>
                  <Badge variant="outline">{sourceLabel(incident.source)}</Badge>
                  <Badge variant="secondary">{incident.status}</Badge>
                </div>
                <p className="mt-2 font-medium">{incident.title}</p>
                <p className="text-muted-foreground">
                  Owner: {incident.owner ?? 'n/a'} · Escalation: {incident.escalation_target ?? 'n/a'}
                </p>
                <p className="mt-1 text-muted-foreground">{incident.recommended_action}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {incident.source === 'agent_ops' ? (
                    <Button type="button" size="sm" variant="outline" onClick={() => void actOnIncident(incident.incident_id, 'escalate')}>Eskalieren</Button>
                  ) : null}
                  {incident.source === 'superglue_quarantine' ? (
                    <>
                      <Button type="button" size="sm" onClick={() => void actOnIncident(incident.incident_id, 'resolve')}>Resolve</Button>
                      <Button type="button" size="sm" variant="outline" onClick={() => void actOnIncident(incident.incident_id, 'retry')}>Retry</Button>
                    </>
                  ) : null}
                </div>
              </div>
            )) : (
              <div className="rounded border border-dashed p-4 text-muted-foreground">
                Kein Vorfall trifft auf den aktuellen Filter.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
