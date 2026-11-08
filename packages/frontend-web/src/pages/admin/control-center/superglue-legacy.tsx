import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AgentenIntegrationWorkspace } from '@/pages/admin/agenten-integration'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

type SuperglueAdminState = {
  tenant_id: string
  storage_path: string
  connector_overrides: Record<string, { system_url?: string; system_name?: string }>
  policy_overrides: {
    execution_enabled?: boolean
    require_tenant_secrets?: boolean
    run_retention_days?: number
    artifact_retention_days?: number
  }
  wizard: {
    current_step?: string
    completed_steps?: string[]
  }
}

type SuperglueWizard = {
  tenant_id: string
  current_step: string
  completed_steps: string[]
  recommended_actions: string[]
  steps: Array<{
    step_key: string
    title: string
    status: string
    details: unknown
  }>
}

export default function AdminControlCenterSupergluePage(): JSX.Element {
  const { toast } = useToast()
  const [connectorKey, setConnectorKey] = useState('document_search')
  const [systemUrl, setSystemUrl] = useState('https://documents.example.invalid/api')
  const [runRetentionDays, setRunRetentionDays] = useState('30')
  const [pendingAction, setPendingAction] = useState<string | null>(null)

  const adminStateQuery = useQuery({
    queryKey: ['agent', 'superglue-admin-state'],
    queryFn: async () => (await apiClient.get<SuperglueAdminState>('/api/v1/agent/integrations/providers/superglue/tenants/default/admin-state')).data,
  })
  const wizardQuery = useQuery({
    queryKey: ['agent', 'superglue-wizard'],
    queryFn: async () => (await apiClient.get<SuperglueWizard>('/api/v1/agent/integrations/providers/superglue/tenants/default/wizard')).data,
  })

  const refetchAll = async (): Promise<void> => {
    await Promise.all([adminStateQuery.refetch(), wizardQuery.refetch()])
  }

  const applyConnectorOverride = async (): Promise<void> => {
    if (pendingAction) return
    setPendingAction('connector')
    try {
      await apiClient.post(`/api/v1/agent/integrations/providers/superglue/tenants/default/connectors/${connectorKey}/config`, {
        system_url: systemUrl,
      })
      await apiClient.post('/api/v1/agent/integrations/providers/superglue/tenants/default/wizard/apply', {
        connector_key: connectorKey,
        system_url: systemUrl,
        completed_step: 'systems',
        next_step: 'policy',
      })
      await refetchAll()
      toast({ title: 'Connector Override gespeichert' })
    } catch (_rawErr: unknown) {
      const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Fehler', description: err?.response?.data?.detail ?? err?.message, variant: 'destructive' })
    } finally {
      setPendingAction(null)
    }
  }

  const applyPolicyOverride = async (): Promise<void> => {
    if (pendingAction) return
    setPendingAction('policy')
    try {
      await apiClient.post('/api/v1/agent/integrations/providers/superglue/tenants/default/policy', {
        execution_enabled: true,
        require_tenant_secrets: true,
        run_retention_days: Number(runRetentionDays) || 30,
        artifact_retention_days: 14,
      })
      await apiClient.post('/api/v1/agent/integrations/providers/superglue/tenants/default/wizard/apply', {
        execution_enabled: true,
        require_tenant_secrets: true,
        run_retention_days: Number(runRetentionDays) || 30,
        artifact_retention_days: 14,
        completed_step: 'policy',
        next_step: 'bootstrap',
      })
      await refetchAll()
      toast({ title: 'Policy Override gespeichert' })
    } catch (_rawErr: unknown) {
      const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Fehler', description: err?.response?.data?.detail ?? err?.message, variant: 'destructive' })
    } finally {
      setPendingAction(null)
    }
  }

  const markCredentialsPrepared = async (): Promise<void> => {
    if (pendingAction) return
    setPendingAction('credentials')
    try {
      await apiClient.post('/api/v1/agent/integrations/providers/superglue/tenants/default/wizard/apply', {
        completed_step: 'credentials',
        next_step: 'systems',
      })
      await refetchAll()
      toast({ title: 'Credentials als vorbereitet markiert' })
    } catch (_rawErr: unknown) {
      const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Fehler', description: err?.response?.data?.detail ?? err?.message, variant: 'destructive' })
    } finally {
      setPendingAction(null)
    }
  }

  const adminState = adminStateQuery.data
  const wizard = wizardQuery.data

  return (
    <div className="space-y-6">
      <AgentenIntegrationWorkspace
        section="superglue"
        title="Admin Kontrollzentrum: Superglue"
        subtitle="Dedizierte Betriebsflaeche fuer Connectoren, Live Readiness, Onboarding, Quarantaene und Monitoring."
      />

      <div className="grid gap-6 px-6 pb-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Superglue Admin Mutations</CardTitle>
            <CardDescription>
              Connector- und Policy-Overrides fuer Tenant-Rollouts direkt im Admin-Unterbereich.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm"><strong>Storage:</strong> <code>{adminState?.storage_path ?? 'runtime/superglue/admin-state.json'}</code></p>
              <p className="text-sm"><strong>Current Step:</strong> {adminState?.wizard?.current_step ?? 'credentials'}</p>
              <div className="flex flex-wrap gap-2">
                {(adminState?.wizard?.completed_steps ?? []).map((step) => (
                  <Badge key={step} variant="secondary">{step}</Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="connector-key">Connector</label>
              <Input id="connector-key" value={connectorKey} onChange={(event) => setConnectorKey(event.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="system-url">System URL</label>
              <Input id="system-url" value={systemUrl} onChange={(event) => setSystemUrl(event.target.value)} />
            </div>
            <Button type="button" disabled={pendingAction !== null} onClick={() => void applyConnectorOverride()}>
              {pendingAction === 'connector' ? 'Speichert…' : 'Connector Override speichern'}
            </Button>

            <div className="space-y-2 border-t pt-4">
              <label className="text-sm font-medium" htmlFor="run-retention">Run Retention Days</label>
              <Input id="run-retention" value={runRetentionDays} onChange={(event) => setRunRetentionDays(event.target.value)} />
              <Button type="button" variant="outline" disabled={pendingAction !== null} onClick={() => void applyPolicyOverride()}>
                {pendingAction === 'policy' ? 'Speichert…' : 'Policy Override speichern'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tenant Onboarding Wizard</CardTitle>
            <CardDescription>
              Fuehrt Credentials, System-URLs, Policy und Bootstrap als explizite Rollout-Schritte zusammen.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Badge>{wizard?.current_step ?? 'credentials'}</Badge>
              <Badge variant="outline">completed: {(wizard?.completed_steps ?? []).length}</Badge>
            </div>
            <div className="space-y-2">
              {(wizard?.steps ?? []).map((step) => (
                <div key={step.step_key} className="rounded border p-3 text-sm">
                  <p><strong>{step.title}</strong> · {step.status}</p>
                  <p className="text-muted-foreground">{step.step_key}</p>
                </div>
              ))}
            </div>
            <div className="space-y-2 text-sm">
              {(wizard?.recommended_actions ?? []).map((action) => (
                <p key={action}>{action}</p>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="outline" disabled={pendingAction !== null} onClick={() => void markCredentialsPrepared()}>
                {pendingAction === 'credentials' ? 'Markiert…' : 'Credentials vorbereitet'}
              </Button>
              <Button type="button" variant="outline" disabled={pendingAction !== null} onClick={() => void applyConnectorOverride()}>
                {pendingAction === 'connector' ? 'Speichert…' : 'Systeme anwenden'}
              </Button>
              <Button type="button" disabled={pendingAction !== null} onClick={() => void applyPolicyOverride()}>
                {pendingAction === 'policy' ? 'Speichert…' : 'Policy anwenden'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
