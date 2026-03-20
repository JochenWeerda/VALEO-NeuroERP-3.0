import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import AgentenIntegrationPage from '@/pages/admin/agenten-integration'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
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
  })

  it('zeigt Agent UX Panel und Idempotency Monitoring', async () => {
    renderPage()

    expect(await screen.findByText('Agent UX Panel')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Idempotency Monitoring' })).toBeInTheDocument()
    expect(screen.getByText('84%')).toBeInTheDocument()
    expect(screen.getByText('Command Catalog')).toBeInTheDocument()
  })
})
