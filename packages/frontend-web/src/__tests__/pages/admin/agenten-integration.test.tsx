import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import AgentenIntegrationPage from '@/pages/admin/agenten-integration'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
    post: vi.fn().mockResolvedValue({ data: { provider_key: 'superglue', refreshed_at: '2026-04-04T10:00:00Z', tool_count: 3 } }),
  },
}))

function renderPage(): void {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  render(
    <QueryClientProvider client={queryClient}>
      <AgentenIntegrationPage />
    </QueryClientProvider>,
  )
}

describe('AgentenIntegrationPage', () => {
  beforeEach(() => {
    getMock.mockReset()
    getMock
      .mockResolvedValueOnce({
        data: {
          version: '1.0.0',
          generated_at: '2026-03-19T10:00:00Z',
          auth: {},
          headers: ['Authorization', 'X-Tenant-ID'],
          links: [
            { rel: 'openapi', href: '/openapi.json', method: 'GET', description: 'OpenAPI' },
            { rel: 'swagger', href: '/docs', method: 'GET', description: 'Swagger UI' },
            { rel: 'redoc', href: '/redoc', method: 'GET', description: 'ReDoc' },
            { rel: 'agent-docs', href: '/docs/agent', method: 'GET', description: 'Docs' },
          ],
          examples: [],
          notes: [],
        },
      })
      .mockResolvedValueOnce({
        data: [
          { command_id: 'settlement.preview', aggregate: 'settlement', intent: 'Preview', mutating: false, idempotent: true, ui_surfaces: [], backend_endpoints: [] },
          { command_id: 'settlement.create', aggregate: 'settlement', intent: 'Create', mutating: true, idempotent: true, ui_surfaces: [], backend_endpoints: [] },
        ],
      })
      .mockResolvedValueOnce({
        data: {
          schema_version: 1,
          confidence_score: 84,
          catalog: {
            total_commands: 12,
            idempotent_commands: 8,
            human_confirmation_commands: 3,
            agent_ready_commands: 6,
            idempotent_coverage_pct: 67,
          },
          store: {
            total_records: 24,
            tenant_count: 2,
            execution_count: 24,
            command_count: 7,
            aggregate_count: 4,
            commands: ['ApproveAPInvoice'],
            aggregates: ['ap_invoice'],
          },
          recommended_action: 'Idempotente Commands sind live und replay-sicher.',
          lookup_paths: [
            '/api/v1/process/actions/execute',
            '/api/v1/process/actions/idempotency/{tenant_id}/{idempotency_key}',
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          enabled: true,
          sync_enabled: true,
          execution_enabled: false,
          tool_count: 3,
          healthy: true,
          dashboard_url: '/api/v1/agent/integrations/providers/superglue/sync-status',
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          enabled: true,
          sync_enabled: true,
          execution_enabled: false,
          require_tenant_secrets: true,
          base_url_configured: true,
          graphql_url_configured: true,
          rest_url_configured: true,
          dashboard_url: '/api/v1/agent/integrations/providers/superglue/sync-status',
          auth_token_configured: false,
          sync_state_path: 'runtime/superglue/sync-state.json',
          sync_history_path: 'runtime/superglue/sync-history.jsonl',
          quarantine_log_path: 'runtime/superglue/quarantine.jsonl',
          execution_journal_path: 'runtime/superglue/execution-journal.jsonl',
          allowed_hosts: [],
          allowed_domains: [],
        },
      })
      .mockResolvedValueOnce({
        data: {
          entry_count: 1,
          open_count: 1,
          resolved_count: 0,
          latest: {
            entry_id: 'sgq-1',
            tool_id: 'sg.document.search',
            reason: 'temporary backend outage',
            outcome: 'degraded',
          },
          open_entries: [
            {
              entry_id: 'sgq-1',
              tool_id: 'sg.document.search',
              reason: 'temporary backend outage',
              timestamp: '2026-04-04T10:00:00Z',
              status: 'open',
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          entry_count: 2,
          latest: {
            refreshed_at: '2026-04-04T10:00:00Z',
            tool_count: 3,
          },
        },
      })
      .mockResolvedValueOnce({
        data: {
          entry_count: 4,
          success_count: 3,
          error_count: 1,
          replay_count: 1,
          artifact_count: 2,
          latest: {
            tool_id: 'sg.document.search',
            result_status: 'success',
            timestamp: '2026-04-04T10:05:00Z',
          },
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          tenant_id: 'default',
          connector_count: 9,
          journal: { entry_count: 4, error_count: 1, artifact_count: 2 },
          quarantine: { open_count: 1, dead_letter_count: 0 },
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          run_count: 4,
          average_latency_ms: 85,
          total_cost_cents: 120,
          artifact_count: 2,
          connectors: [],
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          tenant_id: 'default',
          environment: 'staging',
          connector_count: 9,
          ready_connector_count: 2,
          blocked_connector_count: 7,
          execute_ready_count: 1,
          policy: {
            require_tenant_secrets: true,
            execution_enabled: false,
            alert_error_rate_pct: 5,
            alert_open_quarantine_count: 5,
            run_retention_days: 30,
            artifact_retention_days: 14,
          },
          connectors: [
            {
              connector_key: 'document_search',
              display_name: 'Superglue Document Search',
              tool_id: 'default.sg.document.search',
              missing_credential_fields: ['apiKey'],
              uses_placeholder_url: true,
              ready: false,
              blockers: ['missing_credentials', 'placeholder_system_url'],
            },
          ],
          recommended_actions: ['1 Connector(en) brauchen tenant-spezifische Live-Credentials.'],
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          tenant_id: 'default',
          environment: 'staging',
          vault_path_prefix: 'valeo-neuroerp',
          connector_count: 9,
          blocked_connector_count: 7,
          platform_secret_keys: {
            AUTH_TOKEN: ['SUPERGLUE__TENANT__default__AUTH_TOKEN'],
          },
          connectors: [
            {
              connector_key: 'document_search',
              display_name: 'Superglue Document Search',
              secret_keys: {
                SYSTEM_URL: ['SUPERGLUE__TENANT__default__CONNECTOR__document_search__SYSTEM_URL'],
                apiKey: ['SUPERGLUE__TENANT__default__CONNECTOR__document_search__APIKEY'],
              },
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          provider_key: 'superglue',
          tenant_id: 'default',
          domain_count: 6,
          domains: [
            { domain_key: 'finance', connector_count: 1, connectors: [] },
            { domain_key: 'procurement', connector_count: 1, connectors: [] },
          ],
        },
      })
  })

  it('zeigt Agent UX Panel und Idempotency Monitoring', async () => {
    renderPage()

    expect(await screen.findByText('Agent UX Panel')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Idempotency Monitoring' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Superglue Hub' })).toBeInTheDocument()
    expect(screen.getByText('Superglue Konfiguration')).toBeInTheDocument()
    expect(screen.getByText('Quarantaene / Hinweise')).toBeInTheDocument()
    expect(screen.getByText('Sync History')).toBeInTheDocument()
    expect(screen.getByText('Execution Journal')).toBeInTheDocument()
    expect(screen.getByText('Superglue Admin Overview')).toBeInTheDocument()
    expect(screen.getByText('Connector Monitoring')).toBeInTheDocument()
    expect(screen.getByText('Superglue Live Readiness')).toBeInTheDocument()
    expect(screen.getByText('Superglue Onboarding Pack')).toBeInTheDocument()
    expect(screen.getByText('Domain Rollouts')).toBeInTheDocument()
    expect(screen.getByText('84%')).toBeInTheDocument()
    expect(screen.getByText('Command Catalog')).toBeInTheDocument()
    expect(screen.getByText('temporary backend outage')).toBeInTheDocument()
    expect(screen.getByText(/tenant-spezifische Live-Credentials/i)).toBeInTheDocument()
    expect(screen.getByText(/finance:/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Als erledigt markieren' })).toBeInTheDocument()
  })
})
