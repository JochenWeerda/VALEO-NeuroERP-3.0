import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AgentenIntegrationWorkspace } from '@/pages/admin/agenten-integration'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
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

type ControlCenterIncidents = {
  tenant_id: string
  incident_count: number
  open_quarantine_count: number
  blocked_connector_count: number
  stale_ticket_count: number
  review_ticket_count: number
  journal_error_count: number
  incidents: Array<{
    incident_id: string
    source: string
    severity: string
    title: string
    status: string
    owner?: string
    escalation_target?: string
    recommended_action: string
    detail?: Record<string, unknown>
  }>
}

export default function AdminControlCenterPage(): JSX.Element {
  const [scheduledFor, setScheduledFor] = useState('2026-04-09T09:00')

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

  const planning = planningQuery.data
  const incidents = incidentsQuery.data

  return (
    <div className="space-y-6">
      <AgentenIntegrationWorkspace
        section="overview"
        title="Admin Kontroll- und Ueberwachungszentrum"
        subtitle="Zentraler Leitstand fuer Agenten, Superglue, API-Zugaenge und operativen Integrationszustand."
      />

      <div className="grid gap-6 px-6 pb-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Scheduling und Planung</CardTitle>
            <CardDescription>
              Heartbeats, Connector-Rollouts und manuelle Leitstandsplanung in einer Scheduling-Matrix.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex flex-wrap gap-2">
              <Badge>{planning?.calendar_window ?? '14d'}</Badge>
              <Badge variant="outline">Heartbeat: {planning?.summary.heartbeat_count ?? 0}</Badge>
              <Badge variant="outline">Planned: {planning?.summary.planned_item_count ?? 0}</Badge>
              <Badge variant="secondary">Blocked Connectoren: {planning?.summary.blocked_connector_count ?? 0}</Badge>
            </div>
            <p><strong>Storage:</strong> <code>{planning?.storage_path ?? 'runtime/agent-ops/planning.json'}</code></p>

            <div className="space-y-2">
              <label htmlFor="plan-time" className="font-medium">Naechster Leitstand-Slot</label>
              <Input id="plan-time" value={scheduledFor} onChange={(event) => setScheduledFor(event.target.value)} />
              <Button type="button" onClick={() => void addPlanningItem()}>Planungseintrag anlegen</Button>
            </div>

            <div className="space-y-2">
              <p className="font-medium">Suggested Matrix</p>
              {(planning?.suggested_items ?? []).slice(0, 6).map((item) => (
                <div key={item.plan_id} className="rounded border p-2">
                  <p><strong>{item.title}</strong> · {item.kind}</p>
                  <p>{item.owner} · {item.cadence} · {item.status}</p>
                  <p className="text-muted-foreground">{item.next_hint}</p>
                </div>
              ))}
            </div>

            <div className="space-y-2">
              <p className="font-medium">Planned Items</p>
              {(planning?.planned_items ?? []).slice(0, 6).map((item) => (
                <div key={item.plan_id} className="rounded border p-2">
                  <p><strong>{item.title}</strong> · {item.status}</p>
                  <p>{item.owner} · {item.scheduled_for}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Incident / Alert / Escalation Center</CardTitle>
            <CardDescription>
              Gemeinsame Vorfallsliste fuer stale Agent-Tickets, Superglue-Blocker und offene Quarantaene.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex flex-wrap gap-2">
              <Badge variant="destructive">Incidents: {incidents?.incident_count ?? 0}</Badge>
              <Badge variant="secondary">Quarantaene: {incidents?.open_quarantine_count ?? 0}</Badge>
              <Badge variant="outline">Stale: {incidents?.stale_ticket_count ?? 0}</Badge>
              <Badge variant="outline">Review: {incidents?.review_ticket_count ?? 0}</Badge>
            </div>

            <div className="space-y-2">
              {(incidents?.incidents ?? []).slice(0, 8).map((incident) => (
                <div key={incident.incident_id} className="rounded border p-3">
                  <p><strong>{incident.title}</strong> · {incident.source} · {incident.severity}</p>
                  <p>{incident.status} · Owner: {incident.owner ?? 'n/a'} · Escalation: {incident.escalation_target ?? 'n/a'}</p>
                  <p className="text-muted-foreground">{incident.recommended_action}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {incident.source === 'agent_ops' ? (
                      <Button type="button" size="sm" variant="outline" onClick={() => void actOnIncident(incident.incident_id, 'escalate')}>Eskalieren</Button>
                    ) : null}
                    {incident.source === 'superglue_quarantine' ? (
                      <>
                        <Button type="button" size="sm" variant="outline" onClick={() => void actOnIncident(incident.incident_id, 'resolve')}>Resolve</Button>
                        <Button type="button" size="sm" variant="outline" onClick={() => void actOnIncident(incident.incident_id, 'retry')}>Retry</Button>
                      </>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
