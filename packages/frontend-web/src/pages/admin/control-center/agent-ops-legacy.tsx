import { useQuery } from '@tanstack/react-query'
import { AgentenIntegrationWorkspace } from '@/pages/admin/agenten-integration'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'

type AgentOpsPersistenceStatus = {
  tenant_id: string
  state_path: string
  history_path: string
  persisted: boolean
  persisted_at?: string | null
  history_count: number
  recent_events: Array<{
    event_type?: string
    reason?: string
    persisted_at?: string
    timestamp?: string
  }>
  snapshot_counts: {
    budget_count?: number
    ticket_count?: number
    revision_count?: number
    intervention_count?: number
  }
}

export default function AdminControlCenterAgentOpsPage(): JSX.Element {
  const persistenceQuery = useQuery({
    queryKey: ['agent', 'ops-persistence'],
    queryFn: async () => (await apiClient.get<AgentOpsPersistenceStatus>('/api/v1/agents/neuroassist/ops/persistence', { params: { tenant_id: 'default' } })).data,
  })

  const persistence = persistenceQuery.data

  return (
    <div className="space-y-6">
      <AgentenIntegrationWorkspace
        section="agents"
        title="Admin Kontrollzentrum: Agent Ops"
        subtitle="Ticket-zentrierte Steuerung fuer NeuroASSIST mit Chain of Command, Revisionssicht und fokussierten Eingriffen."
      />

      <div className="px-6 pb-6">
        <Card>
          <CardHeader>
            <CardTitle>Persistente Read Models</CardTitle>
            <CardDescription>
              Zustand und Revisionshistorie der Agent-Ops-Snapshots fuer den Leitstand.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={persistence?.persisted ? 'default' : 'secondary'}>
                {persistence?.persisted ? 'persistiert' : 'nur runtime'}
              </Badge>
              <span>History: {persistence?.history_count ?? 0}</span>
            </div>
            <p><strong>State Path:</strong> <code>{persistence?.state_path ?? 'runtime/agent-ops/state.json'}</code></p>
            <p><strong>History Path:</strong> <code>{persistence?.history_path ?? 'runtime/agent-ops/history.jsonl'}</code></p>
            <p><strong>Persisted At:</strong> {persistence?.persisted_at ?? 'noch kein Snapshot'}</p>
            <p>
              <strong>Snapshot:</strong> Budgets {persistence?.snapshot_counts?.budget_count ?? 0} · Tickets {persistence?.snapshot_counts?.ticket_count ?? 0} ·
              Revisions {persistence?.snapshot_counts?.revision_count ?? 0} · Interventionen {persistence?.snapshot_counts?.intervention_count ?? 0}
            </p>
            <div className="space-y-2">
              {(persistence?.recent_events ?? []).slice(0, 5).map((event, index) => (
                <div key={`${event.timestamp ?? event.persisted_at ?? 'evt'}-${index}`} className="rounded border p-2">
                  <p><strong>{event.event_type ?? 'event'}</strong> · {event.reason ?? 'snapshot'}</p>
                  <p className="text-muted-foreground">{event.persisted_at ?? event.timestamp ?? 'n/a'}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
