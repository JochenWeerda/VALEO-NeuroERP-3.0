import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/react-router-compat'
import FlowSpineServiceToCustomerPage from '@/pages/workflow/flow-spine-service-to-customer'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineServiceToCustomerPage', () => {
  it('rendert den Service-to-Customer Prozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'service-to-customer',
        title: 'Service-to-Customer',
        subtitle: 'Serviceanfrage, Disposition und Rueckmeldung.',
        instance_label: 'Servicefall SVC-2026-071',
        breadcrumb: ['Flow Spine UI', 'Service-to-Customer', 'Servicefall SVC-2026-071'],
        search_placeholder: 'Suche in Servicefaellen ...',
        mode: 'Flow',
        user_role: 'Service Coordinator',
        left_navigation: { processes: [{ key: 'service-to-customer', label: 'Service-to-Customer', route_path: '/workflow/flow-spine-service-to-customer', active: true }], favorites: ['SVC-2026-071'], recent_items: ['Kundenfenster geaendert'], role_switches: ['Field Service'] },
        badges: [{ label: 'Tour im Plan', tone: 'ok' }],
        focus_node_id: 'dispatch',
        nodes: [{
          id: 'dispatch', label: 'Einsatz', status: 'active', icon: 'Truck', metric: 'Vor Ort', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Kunde informiert',
          detail_rows: [{ label: 'ETA', value: '09:40' }],
          kpis: [{ label: 'SLA', value: '97%' }],
          documents: [{ label: 'Anfahrtsskizze.png', href: '/agribusiness/field-service-tasks' }],
          actions: [{ label: 'Field Task', href: '/agribusiness/field-service-tasks', variant: 'primary', api_path: '/api/agribusiness/field-service-tasks' }],
          agent: { headline: 'Kunde informiert', message: 'ETA stabil, Vorbereitung auf Rueckmeldung.', reasons: ['Kunde bestaetigt'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Serviceauftrag_071.pdf', href: '/service/anfragen' }], linked_modules: [{ label: 'Field Service', href: '/agribusiness/field-service-tasks', api_path: '/api/agribusiness/field-service-tasks' }], domain: 'service' },
        footer_cards: [{ title: 'Tourenstatus', items: ['Route Nordwest'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<MemoryRouter><QueryClientProvider client={queryClient}><FlowSpineServiceToCustomerPage /></QueryClientProvider></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /einsatz/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Kunde informiert' })).toBeInTheDocument()
  })
})
