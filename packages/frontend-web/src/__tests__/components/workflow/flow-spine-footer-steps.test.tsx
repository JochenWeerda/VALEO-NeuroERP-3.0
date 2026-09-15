import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import FlowSpineServiceToCustomerPage from '@/pages/workflow/flow-spine-service-to-customer'

/**
 * FSX-022 — Naechste Schritte sind Aktionen oder sie entfallen.
 * Geprueft wird die Wirkung: Zeilen mit href werden Schaltflaechen, die
 * entschuldigende Checklisten-Zeile faellt weg, Feststellungen bleiben Text.
 */

const getMock = vi.hoisted(() => vi.fn())
const navigateMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual<typeof import('@/app/routing/typed-router')>(
    '@/app/routing/typed-router',
  )
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

function workspacePayload() {
  return {
    data: {
      process_key: 'service-to-customer',
      title: 'Service-to-Customer',
      subtitle: 'Serviceanfrage, Disposition und Rueckmeldung.',
      instance_label: 'Servicefall SVC-2026-071',
      breadcrumb: ['Flow Spine UI', 'Service-to-Customer', 'Servicefall SVC-2026-071'],
      search_placeholder: 'Suche in Servicefaellen ...',
      mode: 'Flow',
      user_role: 'Service Coordinator',
      left_navigation: {
        processes: [
          {
            key: 'service-to-customer',
            label: 'Service-to-Customer',
            route_path: '/workflow/flow-spine-service-to-customer',
            active: true,
          },
        ],
        favorites: ['SVC-2026-071'],
        recent_items: ['Kundenfenster geaendert'],
        role_switches: ['Field Service'],
      },
      badges: [{ label: 'Tour im Plan', tone: 'ok' }],
      focus_node_id: 'dispatch',
      nodes: [
        {
          id: 'dispatch',
          label: 'Einsatz',
          status: 'active',
          icon: 'Truck',
          metric: 'Vor Ort',
          submetric: 'Heute',
          timestamp: '2026-03-24T10:00:00Z',
          insight: 'Techniker unterwegs',
          detail_rows: [{ label: 'ETA', value: '09:40' }],
          kpis: [{ label: 'SLA-Quote', value: '97%' }],
          documents: [{ label: 'Anfahrtsskizze.png', href: '/agribusiness/field-service-tasks' }],
          actions: [
            {
              label: 'Field Task',
              href: '/agribusiness/field-service-tasks',
              variant: 'primary',
              api_path: '/api/agribusiness/field-service-tasks',
            },
          ],
          agent: {
            headline: 'Kunde informiert',
            message: 'ETA stabil.',
            reasons: ['Kunde bestaetigt'],
            actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'],
          },
        },
      ],
      right_panel: {
        resources: [{ label: 'Serviceauftrag_071.pdf', href: '/service/anfragen' }],
        linked_modules: [
          {
            label: 'Field Service',
            href: '/agribusiness/field-service-tasks',
            api_path: '/api/agribusiness/field-service-tasks',
          },
        ],
        domain: 'service',
      },
      footer_cards: [
        { title: 'Tourenstatus', items: ['Route Nordwest'] },
        {
          title: 'Naechste Schritte',
          items: [{ label: 'Aktivitaet buchen', href: '/crm/aktivitaeten' }],
        },
      ],
    },
  }
}

function renderWorkspace() {
  getMock.mockResolvedValue(workspacePayload())
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <FlowSpineServiceToCustomerPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('FlowSpineWorkspace — FSX-022 Fusskarten', () => {
  it('macht Naechste Schritte mit href zur Navigation und laesst Feststellungen Text', async () => {
    renderWorkspace()
    expect(await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })).toBeInTheDocument()

    expect(screen.queryByText(/keine Navigation/)).not.toBeInTheDocument()
    expect(screen.getByText('Route Nordwest')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Route Nordwest' })).not.toBeInTheDocument()

    const step = screen.getByRole('button', { name: 'Aktivitaet buchen' })
    await userEvent.click(step)
    expect(navigateMock).toHaveBeenCalledWith('/crm/aktivitaeten')
  })
})
