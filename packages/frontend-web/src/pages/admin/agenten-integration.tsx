/**
 * Agenten-Integration (Gap 048): Übersicht für externe Agenten.
 * Nutzt einen maschinenlesbaren Agent-Manifest-Endpoint als Einstiegspunkt.
 */

import { useQuery } from '@tanstack/react-query'
import { Link } from '@/app/routing/react-router-compat'
import {
  BookOpen,
  Bot,
  Download,
  ExternalLink,
  FileJson,
  Key,
  Link2,
  Shield,
} from 'lucide-react'
import { AgentUxPanel, type AgentUxSource } from '@/components/agent/AgentUxPanel'
import { IdempotencyMonitoringPanel, type IdempotencyOverview } from '@/components/agent/IdempotencyMonitoringPanel'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'

type ControlCenterSection = 'all' | 'overview' | 'superglue' | 'agents'

type AgentManifest = {
  version: string
  generated_at: string
  auth: Record<string, string | boolean>
  headers: string[]
  links: Array<{
    rel: string
    href: string
    method: string
    description: string
  }>
  examples: Array<{
    name: string
    description: string
    method: string
    path: string
    required_headers: string[]
  }>
  notes: string[]
}

type CommandCatalogItem = {
  command_id: string
  aggregate: string
  intent: string
  mutating: boolean
  idempotent: boolean
  ui_surfaces: string[]
  backend_endpoints: string[]
}

type SuperglueStatus = {
  provider_key: string
  enabled: boolean
  sync_enabled: boolean
  execution_enabled: boolean
  tool_count: number
  healthy: boolean
  dashboard_url?: string | null
  graphql_url?: string | null
  rest_url?: string | null
  detail?: string | null
}

type SuperglueConfigSummary = {
  provider_key: string
  enabled: boolean
  sync_enabled: boolean
  execution_enabled: boolean
  require_tenant_secrets: boolean
  base_url_configured: boolean
  graphql_url_configured: boolean
  rest_url_configured: boolean
  dashboard_url?: string | null
  auth_token_configured: boolean
  sync_state_path: string
  sync_history_path: string
  quarantine_log_path: string
  execution_journal_path: string
  allowed_hosts: string[]
  allowed_domains: string[]
}

type SuperglueQuarantineSummary = {
  entry_count: number
  open_count: number
  resolved_count: number
  latest?: {
    entry_id?: string
    reason: string
    tool_id: string
    outcome: string
    status?: string
  } | null
  open_entries?: Array<{
    entry_id: string
    tool_id: string
    reason: string
    timestamp: string
    status: string
  }>
}

type SuperglueSyncHistorySummary = {
  entry_count: number
  latest?: {
    refreshed_at: string
    tool_count: number
  } | null
}

type SuperglueExecutionJournalSummary = {
  entry_count: number
  success_count: number
  error_count: number
  replay_count?: number
  average_latency_ms?: number
  total_cost_cents?: number
  artifact_count?: number
  latest?: {
    tool_id: string
    result_status: string
    timestamp: string
  } | null
}

type SuperglueAdminOverview = {
  provider_key: string
  tenant_id: string
  connector_count: number
  journal: {
    entry_count: number
    error_count: number
    artifact_count: number
  }
  quarantine: {
    open_count: number
    dead_letter_count: number
  }
}

type SuperglueMonitoringSummary = {
  provider_key: string
  tenant_id?: string | null
  run_count: number
  average_latency_ms: number
  total_cost_cents: number
  artifact_count: number
  connectors: Array<{
    tool_id: string
    runs: number
    errors: number
    replays: number
    average_latency_ms: number
    error_rate_pct: number
  }>
}

type SuperglueLiveReadiness = {
  provider_key: string
  tenant_id: string
  environment: string
  connector_count: number
  ready_connector_count: number
  blocked_connector_count: number
  execute_ready_count: number
  policy: {
    require_tenant_secrets: boolean
    execution_enabled: boolean
    alert_error_rate_pct: number
    alert_open_quarantine_count: number
    run_retention_days: number
    artifact_retention_days: number
  }
  connectors: Array<{
    connector_key: string
    display_name: string
    tool_id: string
    missing_credential_fields: string[]
    uses_placeholder_url: boolean
    ready: boolean
    blockers: string[]
  }>
  recommended_actions: string[]
}

type SuperglueDomainRolloutSummary = {
  provider_key: string
  tenant_id: string
  domain_count: number
  domains: Array<{
    domain_key: string
    connector_count: number
    connectors: Array<{
      connector_key: string
      tool_id: string
    }>
  }>
}

type SuperglueOnboardingPack = {
  provider_key: string
  tenant_id: string
  environment: string
  vault_path_prefix: string
  connector_count: number
  blocked_connector_count: number
  platform_secret_keys: Record<string, string[]>
  connectors: Array<{
    connector_key: string
    display_name: string
    secret_keys: Record<string, string[]>
  }>
}

type SuperglueRefreshResult = {
  provider_key: string
  refreshed_at: string
  tool_count: number
}

type AgentOpsOverview = {
  tenant_id: string
  schema_version: number
  budget_total_cents: number
  spent_total_cents: number
  remaining_total_cents: number
  blocked_budget_count: number
  monthly_run_count: number
  budget_summaries: Array<{
    capability_key: string
    monthly_budget_cents: number
    spent_cents: number
    remaining_cents: number
    blocked: boolean
  }>
  heartbeats: Array<{
    capability_key: string
    cadence: string
    enabled: boolean
    last_status?: string | null
  }>
  roles: Array<{
    role_key: string
    reports_to?: string | null
    owns_capabilities: string[]
    can_intervene?: boolean
    manages_roles?: string[]
  }>
  profiles?: Array<{
    profile_key: string
    owner_role: string
    escalation_role: string
    review_sla_hours: number
    stale_after_hours: number
    allowed_actions: string[]
    version: number
  }>
  goals: Array<{
    goal_key: string
    title: string
    active_ticket_count: number
  }>
  open_tickets: Array<{
    ticket_id: string
    capability_key: string
    status: string
    latest_summary: string
    work_item_id?: string | null
    work_item_title?: string | null
    owner_role?: string | null
    escalation_role?: string | null
    allowed_actions?: string[]
    blocker_reasons?: string[]
    requires_review?: boolean
    is_stale?: boolean
    age_minutes?: number
  }>
}

type AgentOpsDashboard = {
  tenant_id: string
  budget_health: string
  active_ticket_count: number
  intervention_count: number
  blocked_capabilities: string[]
  top_budget_pressures: Array<{
    capability_key: string
    remaining_cents: number
  }>
  recent_interventions: Array<{
    intervention_id: string
    ticket_id: string
    action: string
    resulting_status: string
    requested_by: string
  }>
  stale_work_count?: number
  review_queue_count?: number
  open_blocker_count?: number
  mobile_actions: string[]
}

type AgentIntervention = {
  intervention_id: string
  ticket_id: string
  action: string
  resulting_status: string
  requested_by: string
  note?: string | null
}

type AgentTemplateExport = {
  tenant_id: string
  template_key: string
  exported_at: string
  budgets: Array<{ capability_key: string; monthly_budget_cents: number }>
  heartbeats: Array<{ capability_key: string; cadence: string }>
  roles: Array<{ role_key: string }>
  goals: Array<{ goal_key: string }>
  skill_packs: Array<{ skill_pack_key: string; display_name: string }>
}

type AgentSkillPack = {
  skill_pack_key: string
  display_name: string
  role_key: string
  version?: number
  capability_keys: string[]
  skills: string[]
  prompt_contracts: string[]
}

type AgentMobileOpsOverview = {
  tenant_id: string
  urgent_ticket_count: number
  blocked_budget_count: number
  pending_intervention_count: number
  review_ticket_count?: number
  top_actions: string[]
}

type AgentConfigRevision = {
  revision_id: string
  config_type: string
  config_key: string
  version: number
  changed_by: string
  summary: string
}

type AgentControlCenter = {
  tenant_id: string
  dashboard: AgentOpsDashboard
  tickets: AgentOpsOverview['open_tickets']
  chain_of_command: AgentOpsOverview['roles']
  config_revisions: AgentConfigRevision[]
  mobile_overview: AgentMobileOpsOverview
}

type AgentPluginBoundaryReview = {
  tenant_id: string
  schema_version: number
  approved_patterns: string[]
  forbidden_patterns: string[]
  rationale: string[]
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''
const BACKEND_ORIGIN = API_BASE || (typeof window !== 'undefined' ? window.location.origin : '')

function absoluteUrl(path: string): string {
  if (!path.startsWith('/')) {
    return path
  }
  return `${BACKEND_ORIGIN}${path}`
}

function renderOnboardingEnvTemplate(pack: SuperglueOnboardingPack): string {
  const lines = [
    `# Superglue onboarding env template for tenant ${pack.tenant_id}`,
    `# Environment: ${pack.environment}`,
    '',
  ]
  for (const key of pack.platform_secret_keys.AUTH_TOKEN ?? []) {
    lines.push(`${key}=`)
  }
  lines.push('')
  for (const connector of pack.connectors) {
    lines.push(`# ${connector.display_name} (${connector.connector_key})`)
    for (const candidates of Object.values(connector.secret_keys)) {
      if (candidates.length > 0) {
        lines.push(`${candidates[0]}=`)
      }
    }
    lines.push('')
  }
  return `${lines.join('\n').trimEnd()}\n`
}

function renderOnboardingVaultTemplate(pack: SuperglueOnboardingPack): string {
  const lines = [
    `# Superglue onboarding vault mapping for tenant ${pack.tenant_id}`,
    `# Prefix: ${pack.vault_path_prefix}`,
    '',
    `[tenant:${pack.tenant_id}]`,
  ]
  for (const [key, candidates] of Object.entries(pack.platform_secret_keys)) {
    lines.push(`${key}=${candidates.join(',')}`)
  }
  lines.push('')
  for (const connector of pack.connectors) {
    lines.push(`[connector:${connector.connector_key}]`)
    for (const [field, candidates] of Object.entries(connector.secret_keys)) {
      lines.push(`${field}=${candidates.join(',')}`)
    }
    lines.push('')
  }
  return `${lines.join('\n').trimEnd()}\n`
}

function downloadTextArtifact(filename: string, content: string, mimeType = 'text/plain;charset=utf-8'): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

type AgentenIntegrationWorkspaceProps = {
  section?: ControlCenterSection
  title?: string
  subtitle?: string
}

export function AgentenIntegrationWorkspace({
  section = 'all',
  title = 'Agenten-Integration',
  subtitle = 'Offene Integrationsfaehigkeit fuer externe Agenten mit maschinenlesbarem Einstiegspunkt. Gap 048.',
}: AgentenIntegrationWorkspaceProps): JSX.Element {
  const stale5m = 5 * 60 * 1000
  const showOverview = section === 'all' || section === 'overview'
  const showSuperglue = section === 'all' || section === 'superglue'
  const showAgents = section === 'all' || section === 'agents'

  // ── Overview: always enabled (small payloads) ──
  const manifestQuery = useQuery({
    queryKey: ['admin', 'agent-manifest'],
    queryFn: async () => (await apiClient.get<AgentManifest>('/api/v1/admin/agent-manifest')).data,
  })
  const commandCatalogQuery = useQuery({
    queryKey: ['agent', 'command-catalog'],
    queryFn: async () => (await apiClient.get<CommandCatalogItem[]>('/api/v1/commands/catalog')).data,
  })

  // ── Idempotency ──
  const idempotencyOverviewQuery = useQuery({
    queryKey: ['agent', 'idempotency-overview'],
    queryFn: async () => (await apiClient.get<IdempotencyOverview>('/api/v1/process/actions/idempotency/overview')).data,
    staleTime: stale5m,
  })

  // ── Superglue ──
  const superglueStatusQuery = useQuery({
    queryKey: ['agent', 'superglue-status'],
    queryFn: async () => (await apiClient.get<SuperglueStatus>('/api/v1/agent/integrations/providers/superglue/sync-status')).data,
    staleTime: stale5m,
  })
  const superglueConfigQuery = useQuery({
    queryKey: ['agent', 'superglue-config'],
    queryFn: async () => (await apiClient.get<SuperglueConfigSummary>('/api/v1/agent/integrations/providers/superglue/config-summary')).data,
    staleTime: stale5m,
  })
  const superglueQuarantineQuery = useQuery({
    queryKey: ['agent', 'superglue-quarantine'],
    queryFn: async () => (await apiClient.get<SuperglueQuarantineSummary>('/api/v1/agent/integrations/providers/superglue/quarantine')).data,
    staleTime: stale5m,
  })
  const superglueHistoryQuery = useQuery({
    queryKey: ['agent', 'superglue-history'],
    queryFn: async () => (await apiClient.get<SuperglueSyncHistorySummary>('/api/v1/agent/integrations/providers/superglue/sync-history')).data,
    staleTime: stale5m,
  })
  const superglueJournalQuery = useQuery({
    queryKey: ['agent', 'superglue-journal'],
    queryFn: async () => (await apiClient.get<SuperglueExecutionJournalSummary>('/api/v1/agent/integrations/providers/superglue/execution-journal')).data,
    staleTime: stale5m,
  })
  const superglueAdminOverviewQuery = useQuery({
    queryKey: ['agent', 'superglue-admin-overview'],
    queryFn: async () => (await apiClient.get<SuperglueAdminOverview>('/api/v1/agent/integrations/providers/superglue/admin-overview', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const superglueMonitoringQuery = useQuery({
    queryKey: ['agent', 'superglue-monitoring'],
    queryFn: async () => (await apiClient.get<SuperglueMonitoringSummary>('/api/v1/agent/integrations/providers/superglue/monitoring')).data,
    staleTime: stale5m,
  })
  const superglueLiveReadinessQuery = useQuery({
    queryKey: ['agent', 'superglue-live-readiness'],
    queryFn: async () => (await apiClient.get<SuperglueLiveReadiness>('/api/v1/agent/integrations/providers/superglue/live-readiness', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const superglueOnboardingPackQuery = useQuery({
    queryKey: ['agent', 'superglue-onboarding-pack'],
    queryFn: async () => (await apiClient.get<SuperglueOnboardingPack>('/api/v1/agent/integrations/providers/superglue/onboarding-pack', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const superglueDomainRolloutsQuery = useQuery({
    queryKey: ['agent', 'superglue-domain-rollouts'],
    queryFn: async () => (await apiClient.get<SuperglueDomainRolloutSummary>('/api/v1/agent/integrations/providers/superglue/domain-rollouts', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })

  // ── Agent Ops ──
  const agentOpsOverviewQuery = useQuery({
    queryKey: ['agent', 'ops-overview'],
    queryFn: async () => (await apiClient.get<AgentOpsOverview>('/api/v1/agents/neuroassist/ops/overview', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentOpsDashboardQuery = useQuery({
    queryKey: ['agent', 'ops-dashboard'],
    queryFn: async () => (await apiClient.get<AgentOpsDashboard>('/api/v1/agents/neuroassist/ops/dashboard', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentInterventionsQuery = useQuery({
    queryKey: ['agent', 'ops-interventions'],
    queryFn: async () => (await apiClient.get<AgentIntervention[]>('/api/v1/agents/neuroassist/ops/interventions', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentTemplateQuery = useQuery({
    queryKey: ['agent', 'ops-template-export'],
    queryFn: async () => (await apiClient.get<AgentTemplateExport>('/api/v1/agents/neuroassist/ops/templates/export', { params: { tenant_id: 'default', template_key: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentSkillPacksQuery = useQuery({
    queryKey: ['agent', 'ops-skill-packs'],
    queryFn: async () => (await apiClient.get<AgentSkillPack[]>('/api/v1/agents/neuroassist/ops/skill-packs', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentMobileOverviewQuery = useQuery({
    queryKey: ['agent', 'ops-mobile-overview'],
    queryFn: async () => (await apiClient.get<AgentMobileOpsOverview>('/api/v1/agents/neuroassist/ops/mobile-overview', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentPluginBoundaryQuery = useQuery({
    queryKey: ['agent', 'ops-plugin-boundary'],
    queryFn: async () => (await apiClient.get<AgentPluginBoundaryReview>('/api/v1/agents/neuroassist/ops/plugin-boundary-review', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })
  const agentControlCenterQuery = useQuery({
    queryKey: ['agent', 'control-center'],
    queryFn: async () => (await apiClient.get<AgentControlCenter>('/api/v1/agents/neuroassist/ops/control-center', { params: { tenant_id: 'default' } })).data,
    staleTime: stale5m,
  })

  const downloadManifest = (): void => {
    if (!manifestQuery.data) {
      return
    }
    const blob = new Blob([`${JSON.stringify(manifestQuery.data, null, 2)}\n`], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'valeo-agent-manifest.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  const downloadSuperglueOnboardingJson = (): void => {
    if (!superglueOnboardingPackQuery.data) {
      return
    }
    downloadTextArtifact(
      `superglue-onboarding-${superglueOnboardingPackQuery.data.tenant_id}.json`,
      `${JSON.stringify(superglueOnboardingPackQuery.data, null, 2)}\n`,
      'application/json',
    )
  }

  const downloadSuperglueOnboardingEnv = (): void => {
    if (!superglueOnboardingPackQuery.data) {
      return
    }
    downloadTextArtifact(
      `superglue-onboarding-${superglueOnboardingPackQuery.data.tenant_id}.env`,
      renderOnboardingEnvTemplate(superglueOnboardingPackQuery.data),
    )
  }

  const downloadSuperglueOnboardingVault = (): void => {
    if (!superglueOnboardingPackQuery.data) {
      return
    }
    downloadTextArtifact(
      `superglue-onboarding-${superglueOnboardingPackQuery.data.tenant_id}.vault.txt`,
      renderOnboardingVaultTemplate(superglueOnboardingPackQuery.data),
    )
  }

  const downloadAgentTemplate = (): void => {
    if (!agentTemplateQuery.data) {
      return
    }
    downloadTextArtifact(
      `agent-ops-template-${agentTemplateQuery.data.tenant_id}.json`,
      `${JSON.stringify(agentTemplateQuery.data, null, 2)}\n`,
      'application/json',
    )
  }

  const applyAgentIntervention = async (ticketId: string, action: string): Promise<void> => {
    await apiClient.post(`/api/v1/agents/neuroassist/ops/tickets/${ticketId}/interventions`, {
      tenant_id: 'default',
      action,
      requested_by: 'admin-ui',
      note: `Applied from Agent Ops Dashboard: ${action}`,
    })
    await Promise.all([
      agentOpsOverviewQuery.refetch(),
      agentOpsDashboardQuery.refetch(),
      agentInterventionsQuery.refetch(),
      agentMobileOverviewQuery.refetch(),
      agentControlCenterQuery.refetch(),
    ])
  }

  if (manifestQuery.isLoading || commandCatalogQuery.isLoading) {
    return <LoadingState message="Agenten-Manifest wird geladen..." />
  }

  if (manifestQuery.isError || commandCatalogQuery.isError || !manifestQuery.data) {
    const firstError = manifestQuery.error ?? commandCatalogQuery.error
    return <ErrorState error={firstError as Error} onRetry={() => void manifestQuery.refetch()} />
  }

  const manifest = manifestQuery.data
  const openapiLink = manifest.links.find((link) => link.rel === 'openapi')
  const swaggerLink = manifest.links.find((link) => link.rel === 'swagger')
  const redocLink = manifest.links.find((link) => link.rel === 'redoc')
  const docsLink = manifest.links.find((link) => link.rel === 'agent-docs')
  const commandCatalog = commandCatalogQuery.data ?? []
  const idempotencyOverview = idempotencyOverviewQuery.data
  const superglueStatus = superglueStatusQuery.data
  const superglueConfig = superglueConfigQuery.data
  const superglueQuarantine = superglueQuarantineQuery.data
  const superglueHistory = superglueHistoryQuery.data
  const superglueJournal = superglueJournalQuery.data
  const superglueAdminOverview = superglueAdminOverviewQuery.data
  const superglueMonitoring = superglueMonitoringQuery.data
  const superglueLiveReadiness = superglueLiveReadinessQuery.data
  const superglueOnboardingPack = superglueOnboardingPackQuery.data
  const superglueDomainRollouts = superglueDomainRolloutsQuery.data
  const agentOpsOverview = agentOpsOverviewQuery.data
  const agentOpsDashboard = agentOpsDashboardQuery.data
  const agentInterventions = agentInterventionsQuery.data ?? []
  const agentTemplate = agentTemplateQuery.data
  const agentSkillPacks = agentSkillPacksQuery.data ?? []
  const agentMobileOverview = agentMobileOverviewQuery.data
  const agentPluginBoundary = agentPluginBoundaryQuery.data
  const agentControlCenter = agentControlCenterQuery.data
  const sampleTenant =
    window.localStorage.getItem('tenant_id') ||
    window.sessionStorage.getItem('tenant_id') ||
    '<tenant-uuid>'

  const commandSources: AgentUxSource[] = [
    {
      label: 'Agent Manifest',
      href: absoluteUrl('/api/v1/admin/agent-manifest'),
      description: 'Oeffentlicher Einstiegspunkt fuer externe Agenten, Tools und Installationspfade.',
    },
    {
      label: 'OpenAPI / MCP',
      href: absoluteUrl(openapiLink?.href ?? '/openapi.json'),
      description: 'Maschinenlesbare API- und Integrationssicht fuer Codegen und Agenten.',
    },
    {
      label: 'Command Catalog',
      href: absoluteUrl('/api/v1/commands/catalog'),
      description: `${commandCatalog.length} Prozess-Commands, davon ${commandCatalog.filter((item) => item.idempotent).length} idempotent.`,
    },
    {
      label: 'Idempotency Monitoring',
      href: absoluteUrl('/api/v1/process/actions/idempotency/overview'),
      description: 'Monitoring-Read-Model fuer Retry-Sicherheit, Store-Footprint und Replay-Nachweis.',
    },
  ]

  const confidenceFromOverview = idempotencyOverview?.confidence_score ?? 0
  const confidenceFromCatalog = commandCatalog.length > 0
    ? Math.round((commandCatalog.filter((item) => item.idempotent).length / commandCatalog.length) * 100)
    : 0
  const confidenceScore = idempotencyOverview
    ? Math.round((confidenceFromOverview + confidenceFromCatalog) / 2)
    : confidenceFromCatalog

  const refreshSuperglueSnapshot = async (): Promise<void> => {
    await apiClient.post<SuperglueRefreshResult>('/api/v1/agent/integrations/providers/superglue/sync-status/refresh')
    await Promise.all([
      superglueStatusQuery.refetch(),
      superglueConfigQuery.refetch(),
      superglueQuarantineQuery.refetch(),
      superglueHistoryQuery.refetch(),
      superglueMonitoringQuery.refetch(),
      superglueAdminOverviewQuery.refetch(),
      superglueLiveReadinessQuery.refetch(),
      superglueOnboardingPackQuery.refetch(),
    ])
  }

  const resolveQuarantineEntry = async (entryId: string): Promise<void> => {
    await apiClient.post(`/api/v1/agent/integrations/providers/superglue/quarantine/${entryId}/resolve`, null, {
      params: {
        resolved_by: 'admin-ui',
        note: 'reviewed in admin page',
      },
    })
    await Promise.all([
      superglueQuarantineQuery.refetch(),
      superglueJournalQuery.refetch(),
      superglueMonitoringQuery.refetch(),
      superglueAdminOverviewQuery.refetch(),
      superglueLiveReadinessQuery.refetch(),
      superglueOnboardingPackQuery.refetch(),
    ])
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold">
            <Bot className="h-6 w-6" />
            {title}
          </h1>
          <p className="mt-1 text-muted-foreground">
            Offene Integrationsfähigkeit für externe Agenten mit maschinenlesbarem Einstiegspunkt. Gap 048.
          </p>
        </div>
        <Button type="button" variant="outline" className="gap-2" onClick={downloadManifest}>
          <Download className="h-4 w-4" />
          Manifest herunterladen
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Leitstand</CardTitle>
            <CardDescription>
              Zentrale Uebersicht fuer API, Zugang, Monitoring und Betriebszustand.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant={section === 'overview' ? 'default' : 'outline'} size="sm">
              <Link to="/admin/control-center">Zur Leitstandsuebersicht</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Superglue Ops</CardTitle>
            <CardDescription>
              Connector-Betrieb, Onboarding, Quarantaene, Monitoring und Live Readiness.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant={section === 'superglue' ? 'default' : 'outline'} size="sm">
              <Link to="/admin/control-center/superglue">Superglue oeffnen</Link>
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Agent Ops</CardTitle>
            <CardDescription>
              Tickets, Chain of Command, Revisions, Eingriffe und Mobile-Ops fuer NeuroASSIST.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild variant={section === 'agents' ? 'default' : 'outline'} size="sm">
              <Link to="/admin/control-center/agent-ops">Agent Ops oeffnen</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {showOverview ? (
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileJson className="h-5 w-5" />
              Agent Manifest
            </CardTitle>
            <CardDescription>
              Maschinenlesbarer Startpunkt für externe Tools, Codegen und Agent-Runtimes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              <strong>Version:</strong> {manifest.version}
            </p>
            <p>
              <strong>Generiert:</strong> {new Date(manifest.generated_at).toLocaleString('de-DE')}
            </p>
            <p>
              <strong>Endpoint:</strong>{' '}
              <a
                href={absoluteUrl('/api/v1/admin/agent-manifest')}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary underline hover:no-underline"
              >
                {absoluteUrl('/api/v1/admin/agent-manifest')}
              </a>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Link2 className="h-5 w-5" />
              OpenAPI / MCP
            </CardTitle>
            <CardDescription>
              Kombination aus OpenAPI für Codegen und MCP-BFF für interaktive Copilot-Pfade.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {openapiLink ? <p><strong>OpenAPI:</strong> <a href={absoluteUrl(openapiLink.href)} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">{absoluteUrl(openapiLink.href)}</a></p> : null}
            {swaggerLink ? <p><strong>Swagger:</strong> <a href={absoluteUrl(swaggerLink.href)} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">{absoluteUrl(swaggerLink.href)}</a></p> : null}
            {redocLink ? <p><strong>ReDoc:</strong> <a href={absoluteUrl(redocLink.href)} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">{absoluteUrl(redocLink.href)}</a></p> : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Superglue Hub
            </CardTitle>
            <CardDescription>
              Kontrollierter Integrationspfad hinter der VALEO Integration Boundary.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Status:</strong> {superglueStatus?.healthy ? 'gesund' : 'nicht bereit'}</p>
            <p><strong>Tools:</strong> {superglueStatus?.tool_count ?? 0}</p>
            <p><strong>Sync:</strong> {superglueStatus?.sync_enabled ? 'aktiv' : 'deaktiviert'}</p>
            <p><strong>Execution:</strong> {superglueStatus?.execution_enabled ? 'aktiv' : 'deaktiviert'}</p>
            <p><strong>Quarantaene:</strong> {superglueQuarantine?.entry_count ?? 0} Eintraege</p>
            <p><strong>Sync-Historie:</strong> {superglueHistory?.entry_count ?? 0} Refreshes</p>
            <Button type="button" variant="outline" size="sm" className="gap-2" onClick={() => void refreshSuperglueSnapshot()}>
              <Download className="h-4 w-4" />
              Sync aktualisieren
            </Button>
            {superglueStatus?.dashboard_url ? (
              <a
                href={absoluteUrl(superglueStatus.dashboard_url)}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-primary underline hover:no-underline"
              >
                Dashboard / Status
                <ExternalLink className="h-4 w-4" />
              </a>
            ) : (
              <Badge variant="outline">Dashboard-Link folgt aus der Backend-Konfiguration</Badge>
            )}
          </CardContent>
        </Card>
      </div>
      ) : null}

      {showSuperglue ? (
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Superglue Admin Overview</CardTitle>
            <CardDescription>
              Tenant-bezogene Betriebskennzahlen fuer Connectoren, Journal und Quarantaene.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Connectoren:</strong> {superglueAdminOverview?.connector_count ?? 0}</p>
            <p><strong>Journal-Eintraege:</strong> {superglueAdminOverview?.journal.entry_count ?? 0}</p>
            <p><strong>Artefakte:</strong> {superglueAdminOverview?.journal.artifact_count ?? 0}</p>
            <p><strong>Quarantaene offen:</strong> {superglueAdminOverview?.quarantine.open_count ?? 0}</p>
            <p><strong>Dead-letter:</strong> {superglueAdminOverview?.quarantine.dead_letter_count ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Superglue Live Readiness</CardTitle>
            <CardDescription>
              Betriebliche Freigabe fuer echte Tenant-Credentials, Zielsystem-Onboarding und Policy-Werte.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Environment:</strong> {superglueLiveReadiness?.environment ?? '-'}</p>
            <p><strong>Ready:</strong> {superglueLiveReadiness?.ready_connector_count ?? 0} / {superglueLiveReadiness?.connector_count ?? 0}</p>
            <p><strong>Execute-ready:</strong> {superglueLiveReadiness?.execute_ready_count ?? 0}</p>
            <p><strong>Alert Error Rate:</strong> {superglueLiveReadiness?.policy.alert_error_rate_pct ?? 0}%</p>
            <p><strong>Open Quarantine Alert:</strong> {superglueLiveReadiness?.policy.alert_open_quarantine_count ?? 0}</p>
            <p><strong>Run Retention:</strong> {superglueLiveReadiness?.policy.run_retention_days ?? 0} Tage</p>
            <p><strong>Artifact Retention:</strong> {superglueLiveReadiness?.policy.artifact_retention_days ?? 0} Tage</p>
            {superglueLiveReadiness?.recommended_actions?.map((action) => (
              <p key={action} className="text-muted-foreground">{action}</p>
            ))}
            {superglueLiveReadiness?.connectors?.filter((connector) => !connector.ready).slice(0, 3).map((connector) => (
              <div key={connector.connector_key} className="rounded border p-2">
                <p><strong>{connector.display_name}</strong></p>
                <p>Blocker: {connector.blockers.join(', ') || 'keine'}</p>
                {connector.missing_credential_fields.length ? (
                  <p>Fehlende Credentials: {connector.missing_credential_fields.join(', ')}</p>
                ) : null}
                {connector.uses_placeholder_url ? <p>Zielsystem: Platzhalter-URL</p> : null}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Superglue Onboarding Pack</CardTitle>
            <CardDescription>
              Exportierbare Secret-Key- und Zielsystem-Hinweise fuer Ops pro Tenant.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Vault Prefix:</strong> <code>{superglueOnboardingPack?.vault_path_prefix}</code></p>
            <p><strong>Blocked Connectoren:</strong> {superglueOnboardingPack?.blocked_connector_count ?? 0}</p>
            <p><strong>AUTH_TOKEN Keys:</strong> {superglueOnboardingPack?.platform_secret_keys.AUTH_TOKEN?.length ?? 0}</p>
            <div className="flex flex-wrap gap-2 pt-1">
              <Button type="button" variant="outline" size="sm" onClick={downloadSuperglueOnboardingJson}>Onboarding JSON</Button>
              <Button type="button" variant="outline" size="sm" onClick={downloadSuperglueOnboardingEnv}>ENV Template</Button>
              <Button type="button" variant="outline" size="sm" onClick={downloadSuperglueOnboardingVault}>Vault Template</Button>
            </div>
            {superglueOnboardingPack?.connectors?.slice(0, 2).map((connector) => (
              <div key={connector.connector_key} className="rounded border p-2">
                <p><strong>{connector.display_name}</strong></p>
                <p>Secretfelder: {Object.keys(connector.secret_keys).join(', ')}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Superglue Konfiguration</CardTitle>
            <CardDescription>
              Maskierte Betriebsparameter und Hinweise fuer den produktiven Rollout.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Tenant-Secrets erzwungen:</strong> {superglueConfig?.require_tenant_secrets ? 'ja' : 'nein'}</p>
            <p><strong>Base URL konfiguriert:</strong> {superglueConfig?.base_url_configured ? 'ja' : 'nein'}</p>
            <p><strong>GraphQL URL konfiguriert:</strong> {superglueConfig?.graphql_url_configured ? 'ja' : 'nein'}</p>
            <p><strong>REST URL konfiguriert:</strong> {superglueConfig?.rest_url_configured ? 'ja' : 'nein'}</p>
            <p><strong>Auth Token gesetzt:</strong> {superglueConfig?.auth_token_configured ? 'ja' : 'nein'}</p>
            <p><strong>Sync State:</strong> <code>{superglueConfig?.sync_state_path}</code></p>
            <p><strong>Sync-History:</strong> <code>{superglueConfig?.sync_history_path}</code></p>
            <p><strong>Quarantaene Log:</strong> <code>{superglueConfig?.quarantine_log_path}</code></p>
            <p><strong>Execution Journal:</strong> <code>{superglueConfig?.execution_journal_path}</code></p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quarantaene / Hinweise</CardTitle>
            <CardDescription>
              Degradierte Superglue-Aufrufe werden getrennt nachvollzogen, ohne den Core zu blockieren.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Eintraege:</strong> {superglueQuarantine?.entry_count ?? 0}</p>
            <p><strong>Offen:</strong> {superglueQuarantine?.open_count ?? 0}</p>
            <p><strong>Erledigt:</strong> {superglueQuarantine?.resolved_count ?? 0}</p>
            <p><strong>Letztes Tool:</strong> {superglueQuarantine?.latest?.tool_id ?? '-'}</p>
            <p><strong>Letzter Grund:</strong> {superglueQuarantine?.latest?.reason ?? 'kein degradierter Aufruf'}</p>
            {superglueQuarantine?.open_entries?.length ? (
              <div className="space-y-2 pt-2">
                {superglueQuarantine.open_entries.slice(-3).reverse().map((entry) => (
                  <div key={entry.entry_id} className="rounded border p-2">
                    <p><strong>{entry.tool_id}</strong> | {entry.reason}</p>
                    <Button type="button" variant="outline" size="sm" onClick={() => void resolveQuarantineEntry(entry.entry_id)}>
                      Als erledigt markieren
                    </Button>
                  </div>
                ))}
              </div>
            ) : null}
            <Badge variant="outline">
              Write-Pfade bleiben weiter approval- und policy-gated.
            </Badge>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Sync History</CardTitle>
            <CardDescription>
              Letzte Snapshot-Aktualisierungen fuer Tool-Katalog und Provider-Sicht.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Refreshes:</strong> {superglueHistory?.entry_count ?? 0}</p>
            <p><strong>Letzter Lauf:</strong> {superglueHistory?.latest?.refreshed_at ?? '-'}</p>
            <p><strong>Letzte Tool-Anzahl:</strong> {superglueHistory?.latest?.tool_count ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Execution Journal</CardTitle>
            <CardDescription>
              Erfolgreiche und degradierte Superglue-Ausfuehrungen als kompakte Ops-Sicht.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Eintraege:</strong> {superglueJournal?.entry_count ?? 0}</p>
            <p><strong>Erfolgreich:</strong> {superglueJournal?.success_count ?? 0}</p>
            <p><strong>Fehler:</strong> {superglueJournal?.error_count ?? 0}</p>
            <p><strong>Replays:</strong> {superglueJournal?.replay_count ?? 0}</p>
            <p><strong>Artefakte:</strong> {superglueJournal?.artifact_count ?? 0}</p>
            <p><strong>Letztes Tool:</strong> {superglueJournal?.latest?.tool_id ?? '-'}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Connector Monitoring</CardTitle>
            <CardDescription>
              Laufzeiten, Fehlerraten und Kosten pro Connector im Superglue-Pfad.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Runs:</strong> {superglueMonitoring?.run_count ?? 0}</p>
            <p><strong>Average Latency:</strong> {superglueMonitoring?.average_latency_ms ?? 0} ms</p>
            <p><strong>Total Cost:</strong> {superglueMonitoring?.total_cost_cents ?? 0} ct</p>
            <p><strong>Artefakte:</strong> {superglueMonitoring?.artifact_count ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Domain Rollouts</CardTitle>
            <CardDescription>
              Freigeschaltete Superglue-Domänen fuer Procurement, Finance, Logistics und Zusatzrollen.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Domänen:</strong> {superglueDomainRollouts?.domain_count ?? 0}</p>
            {superglueDomainRollouts?.domains?.slice(0, 6).map((domain) => (
              <p key={domain.domain_key}>
                <strong>{domain.domain_key}:</strong> {domain.connector_count} Connectoren
              </p>
            ))}
          </CardContent>
        </Card>
      </div>

      {showOverview && idempotencyOverview ? (
        <div className="grid gap-4 xl:grid-cols-[1.4fr_0.9fr]">
          <AgentUxPanel
            title="Agent UX Panel"
            summary="Confidence, Quellen und naechste Aktion fuer agentenfaehige Arbeit im Prozesskern."
            confidence={confidenceScore}
            confidenceLabel="Agentic Readiness"
            sources={commandSources}
            action={{
              label: 'Idempotenz-Monitoring öffnen',
              href: '#idempotency-monitoring',
              description: 'Pruefe Replay-Sicherheit, Store-Footprint und Command-Abdeckung fuer sichere Retries.',
            }}
          />
          <div id="idempotency-monitoring">
            <IdempotencyMonitoringPanel overview={idempotencyOverview} />
          </div>
        </div>
      ) : null}

      {showAgents ? (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Agent Ops Budgeting</CardTitle>
            <CardDescription>
              Monatsbudget, Verbrauch und Guardrails pro produktiver NeuroASSIST-Faehigkeit.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Budget total:</strong> {agentOpsOverview?.budget_total_cents ?? 0} ct</p>
            <p><strong>Spent:</strong> {agentOpsOverview?.spent_total_cents ?? 0} ct</p>
            <p><strong>Remaining:</strong> {agentOpsOverview?.remaining_total_cents ?? 0} ct</p>
            <p><strong>Blocked:</strong> {agentOpsOverview?.blocked_budget_count ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agent Cost Ledger</CardTitle>
            <CardDescription>
              Kosten- und Run-Trace fuer tenant-spezifische Agentenlaeufe.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Monatslaeufe:</strong> {agentOpsOverview?.monthly_run_count ?? 0}</p>
            <p><strong>Heartbeats:</strong> {agentOpsOverview?.heartbeats.length ?? 0}</p>
            <p><strong>Open Tickets:</strong> {agentOpsOverview?.open_tickets.length ?? 0}</p>
            <p><strong>Goal Nodes:</strong> {agentOpsOverview?.goals.length ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agent Heartbeats</CardTitle>
            <CardDescription>
              Geplante Routinen fuer Reviews, Ingestion und Exception-Handling.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {agentOpsOverview?.heartbeats.slice(0, 3).map((heartbeat) => (
              <p key={heartbeat.capability_key}>
                <strong>{heartbeat.capability_key}:</strong> {heartbeat.cadence} · {heartbeat.last_status ?? 'noch kein Lauf'}
              </p>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agent Roles And Goals</CardTitle>
            <CardDescription>
              Org- und Zielsicht fuer laufende Agentenarbeit und Eskalationen.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Rollen:</strong> {agentOpsOverview?.roles.length ?? 0}</p>
            <p><strong>Ziele:</strong> {agentOpsOverview?.goals.length ?? 0}</p>
            {agentOpsOverview?.open_tickets.slice(0, 2).map((ticket) => (
              <p key={ticket.ticket_id}>
                <strong>{ticket.capability_key}:</strong> {ticket.latest_summary}
              </p>
            ))}
          </CardContent>
        </Card>
      </div>
      ) : null}

      {showAgents ? (
      <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <CardHeader>
            <CardTitle>Agent Control Center</CardTitle>
            <CardDescription>
              Zentrale Betriebsansicht fuer stale work, Review-Queue, Budgetdruck, letzte Eingriffe und offene Blocker.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Budget Health:</strong> {agentControlCenter?.dashboard.budget_health ?? agentOpsDashboard?.budget_health ?? 'unknown'}</p>
            <p><strong>Aktive Tickets:</strong> {agentControlCenter?.dashboard.active_ticket_count ?? agentOpsDashboard?.active_ticket_count ?? 0}</p>
            <p><strong>Stale Work:</strong> {agentControlCenter?.dashboard.stale_work_count ?? agentOpsDashboard?.stale_work_count ?? 0}</p>
            <p><strong>Review Queue:</strong> {agentControlCenter?.dashboard.review_queue_count ?? agentOpsDashboard?.review_queue_count ?? 0}</p>
            <p><strong>Open Blockers:</strong> {agentControlCenter?.dashboard.open_blocker_count ?? agentOpsDashboard?.open_blocker_count ?? 0}</p>
            <p><strong>Interventionen:</strong> {agentControlCenter?.dashboard.intervention_count ?? agentOpsDashboard?.intervention_count ?? 0}</p>
            {(agentControlCenter?.dashboard.top_budget_pressures ?? agentOpsDashboard?.top_budget_pressures ?? []).map((item) => (
              <p key={item.capability_key}>
                <strong>{item.capability_key}:</strong> {item.remaining_cents} ct verbleibend
              </p>
            ))}
            {(agentControlCenter?.dashboard.recent_interventions ?? []).slice(0, 2).map((entry) => (
              <p key={entry.intervention_id}>
                <strong>{entry.action}</strong> bei {entry.ticket_id} ({entry.requested_by})
              </p>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mobile Ops Surface</CardTitle>
            <CardDescription>
              Kompakte Sicht fuer wenige kritische Aktionen: freigeben, pausieren, eskalieren, Budgetwarnung sehen.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Urgent Tickets:</strong> {agentControlCenter?.mobile_overview.urgent_ticket_count ?? agentMobileOverview?.urgent_ticket_count ?? 0}</p>
            <p><strong>Review Tickets:</strong> {agentControlCenter?.mobile_overview.review_ticket_count ?? agentMobileOverview?.review_ticket_count ?? 0}</p>
            <p><strong>Blocked Budgets:</strong> {agentControlCenter?.mobile_overview.blocked_budget_count ?? agentMobileOverview?.blocked_budget_count ?? 0}</p>
            <p><strong>Pending Interventions:</strong> {agentControlCenter?.mobile_overview.pending_intervention_count ?? agentMobileOverview?.pending_intervention_count ?? 0}</p>
            {(agentControlCenter?.mobile_overview.top_actions ?? agentMobileOverview?.top_actions ?? []).map((action) => (
              <p key={action}>{action}</p>
            ))}
          </CardContent>
        </Card>
      </div>
      ) : null}

      {showAgents ? (
      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle>Ticket-Centered Agent Work</CardTitle>
            <CardDescription>
              Fachliche Arbeitsobjekte mit stale/review-Zustaenden, Blockern, Ownership und gezielten Eingriffen.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {(agentControlCenter?.tickets ?? agentOpsOverview?.open_tickets ?? []).slice(0, 4).map((ticket) => (
              <div key={ticket.ticket_id} className="rounded border p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <p><strong>{ticket.work_item_title ?? ticket.capability_key}</strong></p>
                  <Badge variant={ticket.is_stale ? 'destructive' : 'secondary'}>
                    {ticket.is_stale ? 'stale' : ticket.status}
                  </Badge>
                  {ticket.requires_review ? <Badge variant="outline">review</Badge> : null}
                </div>
                <p className="text-muted-foreground">{ticket.latest_summary}</p>
                <p><strong>Owner:</strong> {ticket.owner_role ?? 'unassigned'} · <strong>Eskalation:</strong> {ticket.escalation_role ?? 'tenant_operations_lead'}</p>
                <p><strong>Alter:</strong> {ticket.age_minutes ?? 0} min · <strong>Work Item:</strong> {ticket.work_item_id ?? ticket.ticket_id}</p>
                {(ticket.blocker_reasons?.length ?? 0) > 0 ? (
                  <p><strong>Blocker:</strong> {ticket.blocker_reasons?.join(', ')}</p>
                ) : null}
                <div className="mt-2 flex flex-wrap gap-2">
                  <Button type="button" size="sm" variant="outline" onClick={() => void applyAgentIntervention(ticket.ticket_id, 'approve')}>
                    Freigeben
                  </Button>
                  <Button type="button" size="sm" variant="outline" onClick={() => void applyAgentIntervention(ticket.ticket_id, 'pause')}>
                    Pausieren
                  </Button>
                  <Button type="button" size="sm" variant="outline" onClick={() => void applyAgentIntervention(ticket.ticket_id, 'escalate')}>
                    Eskalieren
                  </Button>
                </div>
              </div>
            ))}
            {agentInterventions.slice(0, 2).map((entry) => (
              <p key={entry.intervention_id}>
                <strong>{entry.action}</strong> {'->'} {entry.resulting_status} ({entry.requested_by})
              </p>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Chain Of Command</CardTitle>
            <CardDescription>
              Sichtbare Ownership-Kette fuer Agentenrollen, Eingriffsrechte und Eskalationswege.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {(agentControlCenter?.chain_of_command ?? agentOpsOverview?.roles ?? []).slice(0, 6).map((role) => (
              <div key={role.role_key} className="rounded border p-2">
                <p><strong>{role.role_key}</strong></p>
                <p>Reports to: {role.reports_to ?? 'root'}</p>
                <p>Capabilities: {role.owns_capabilities.join(', ') || 'none'}</p>
                <p>Intervention: {role.can_intervene ? 'allowed' : 'not allowed'}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      ) : null}

      {showAgents ? (
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Config Versions</CardTitle>
            <CardDescription>
              Revisionsverlauf fuer Skill-Packs, Budgets, Heartbeats und Agentprofile.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {(agentControlCenter?.config_revisions ?? []).slice(0, 6).map((revision) => (
              <div key={revision.revision_id} className="rounded border p-2">
                <p><strong>{revision.config_type}</strong> · {revision.config_key}</p>
                <p>Version: {revision.version} · By: {revision.changed_by}</p>
                <p className="text-muted-foreground">{revision.summary}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Portable Agent Templates</CardTitle>
            <CardDescription>
              Exportierbare Tenant-Setups ohne Secret-Material fuer wiederholbare Rollouts.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Template:</strong> {agentTemplate?.template_key ?? 'default'}</p>
            <p><strong>Budgets:</strong> {agentTemplate?.budgets.length ?? 0}</p>
            <p><strong>Heartbeats:</strong> {agentTemplate?.heartbeats.length ?? 0}</p>
            <p><strong>Skill Packs:</strong> {agentTemplate?.skill_packs.length ?? 0}</p>
            <Button type="button" variant="outline" size="sm" onClick={downloadAgentTemplate}>Template Export</Button>
          </CardContent>
        </Card>
      </div>
      ) : null}

      {showAgents ? (
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Agent Skill Packs</CardTitle>
            <CardDescription>
              Versionierbare Skill- und Prompt-Vertraege pro Rolle und Capability.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {agentSkillPacks.slice(0, 3).map((skillPack) => (
              <div key={skillPack.skill_pack_key} className="rounded border p-2">
                <p><strong>{skillPack.display_name}</strong></p>
                <p>Rolle: {skillPack.role_key}</p>
                <p>Version: {skillPack.version ?? 1}</p>
                <p>Skills: {skillPack.skills.join(', ')}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Plugin Boundary Review</CardTitle>
            <CardDescription>
              Explizite Architekturgrenze fuer Plugin-/Paperclip-Muster im VALEO-Kern.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Approved:</strong> {agentPluginBoundary?.approved_patterns.length ?? 0}</p>
            <p><strong>Forbidden:</strong> {agentPluginBoundary?.forbidden_patterns.length ?? 0}</p>
            {agentPluginBoundary?.rationale.map((line) => (
              <p key={line} className="text-muted-foreground">{line}</p>
            ))}
          </CardContent>
        </Card>
      </div>
      ) : null}

      {showOverview ? (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Authentifizierung
          </CardTitle>
          <CardDescription>
            Externe Agenten verwenden dieselben Kernheader wie das Frontend.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          {manifest.headers.map((header) => (
            <p key={header}>
              <code>{header}</code>
            </p>
          ))}
          <Badge variant="outline">
            Hauptstrang offen: dedizierte Agent-API-Keys und produktives Rate-Limiting
          </Badge>
        </CardContent>
      </Card>
      ) : null}

      {showOverview ? (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ExternalLink className="h-5 w-5" />
            Beispielaufrufe
          </CardTitle>
          <CardDescription>
            Sofort nutzbare Beispiele für externe Agenten- und Tool-Integrationen.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {manifest.examples.map((example) => (
            <div key={example.name} className="rounded-lg border p-4">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">{example.method}</Badge>
                <span className="font-medium">{example.name}</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{example.description}</p>
              <code className="mt-3 block whitespace-pre-wrap rounded bg-muted p-3 text-xs">
                {`curl -X ${example.method} "${absoluteUrl(example.path)}" \\
  -H "Authorization: Bearer <token>" \\
  -H "X-Tenant-ID: ${sampleTenant}"${example.method !== 'GET' ? ' \\\n  -H "Content-Type: application/json"' : ''}`}
              </code>
            </div>
          ))}
        </CardContent>
      </Card>
      ) : null}

      {showOverview ? (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Dokumentation
          </CardTitle>
          <CardDescription>
            Weiterführende Projekt- und Integrationsdokumentation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {docsLink ? (
            <p>
              <strong>Agenten-Dokumentation:</strong>{' '}
              <a href={docsLink.href} target="_blank" rel="noopener noreferrer" className="text-primary underline hover:no-underline">
                {docsLink.href}
              </a>
            </p>
          ) : null}
          {manifest.notes.map((note) => (
            <p key={note} className="text-muted-foreground">
              {note}
            </p>
          ))}
        </CardContent>
      </Card>
      ) : null}

      {showOverview ? (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Status & Abhängigkeiten
          </CardTitle>
          <CardDescription>
            Vorbereitende Teile in Codex, produktive Security-/MCP-Server-Pfade im Hauptstrang.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            <Badge>✓ Admin-Seite</Badge>
            <Badge>✓ Agent Manifest</Badge>
            <Badge>✓ OpenAPI (FastAPI)</Badge>
            <Badge>✓ MCP-Infrastruktur (Frontend)</Badge>
            <Badge variant="secondary">○ MCP-Server (Hauptstrang)</Badge>
            <Badge variant="secondary">○ Security/API-Keys produktiv (Hauptstrang)</Badge>
          </div>
        </CardContent>
      </Card>
      ) : null}
    </div>
  )
}

export default function AgentenIntegrationPage(): JSX.Element {
  return (
    <AgentenIntegrationWorkspace
      section="all"
      title="Agenten-Integration"
      subtitle="Legacy-Sammelseite fuer Agenten, Superglue und externe Einstiegspunkte. Fuer den Leitstand bitte den Admin-Unterbereich /admin/control-center verwenden."
    />
  )
}
