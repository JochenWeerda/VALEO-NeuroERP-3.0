import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import AdminControlCenterPage from '@/pages/admin/control-center/index'

const getMock = vi.hoisted(() => vi.fn())
const postMock = vi.hoisted(() => vi.fn())

vi.mock('@/pages/admin/agenten-integration', () => ({
  AgentenIntegrationWorkspace: ({ title }: { title?: string }) => <div>{title ?? 'workspace'}</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
    post: postMock,
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
      <AdminControlCenterPage />
    </QueryClientProvider>,
  )
}

describe('AdminControlCenterPage', () => {
  beforeEach(() => {
    getMock.mockReset()
    postMock.mockReset()
    postMock.mockResolvedValue({ data: {} })
    getMock
      .mockResolvedValueOnce({
        data: {
          tenant_id: 'default',
          storage_path: 'runtime/agent-ops/planning.json',
          calendar_window: '14d',
          suggested_items: [
            {
              plan_id: 'heartbeat:finance',
              kind: 'agent_heartbeat',
              title: 'finance_skonto_assistant',
              owner: 'finance_action_assistant',
              cadence: 'daily',
              status: 'active',
              next_hint: 'scheduler://neuroassist/default',
            },
            {
              plan_id: 'superglue:document',
              kind: 'superglue_connector',
              title: 'Superglue Document Search',
              owner: 'superglue-ops',
              cadence: 'onboarding',
              status: 'blocked',
              next_hint: 'missing_credentials',
            },
          ],
          planned_items: [
            {
              plan_id: 'manual:daily-rollout-review',
              title: 'Daily Rollout Review',
              kind: 'manual_ops',
              owner: 'tenant_operations_lead',
              scheduled_for: '2026-04-09T09:00:00Z',
              status: 'planned',
              notes: 'Admin Kontrollzentrum',
            },
          ],
          summary: {
            heartbeat_count: 1,
            planned_item_count: 1,
            blocked_connector_count: 1,
          },
        },
      })
      .mockResolvedValueOnce({
        data: {
          tenant_id: 'default',
          incident_count: 2,
          open_quarantine_count: 1,
          blocked_connector_count: 1,
          stale_ticket_count: 1,
          review_ticket_count: 1,
          journal_error_count: 1,
          incidents: [
            {
              incident_id: 'agent:agt-run-1',
              source: 'agent_ops',
              severity: 'high',
              title: 'Finance Approval Case',
              status: 'pending_approval',
              owner: 'finance_action_assistant',
              escalation_target: 'tenant_operations_lead',
              recommended_action: 'escalate',
            },
            {
              incident_id: 'superglue:quarantine:sgq-1',
              source: 'superglue_quarantine',
              severity: 'high',
              title: 'default.sg.document.search',
              status: 'open',
              owner: 'superglue-ops',
              escalation_target: 'tenant_operations_lead',
              recommended_action: 'resolve_quarantine',
            },
          ],
        },
      })
  })

  it('shows KPI cards, quick actions and filtered incidents', async () => {
    renderPage()

    expect(await screen.findByText('Admin Kontroll- und Ueberwachungszentrum')).toBeInTheDocument()
    expect(screen.getByText('Offene Vorfaelle')).toBeInTheDocument()
    expect(screen.getByText('Prioritaet und Quick Actions')).toBeInTheDocument()
    expect(screen.getByText('Scheduling und Planung')).toBeInTheDocument()
    expect(screen.getByText('Incident / Alert / Escalation Center')).toBeInTheDocument()
    expect(screen.getAllByText('Finance Approval Case').length).toBeGreaterThan(0)
    expect(screen.getByText('Superglue Document Search')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'superglue' }))
    expect(screen.getByText('default.sg.document.search')).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText('Vorfaelle filtern...'), { target: { value: 'finance' } })
    expect(screen.getByText('Finance Approval Case')).toBeInTheDocument()
  })
})
