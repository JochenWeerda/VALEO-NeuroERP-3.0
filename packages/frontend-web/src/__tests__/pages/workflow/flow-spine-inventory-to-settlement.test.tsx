import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/react-router-compat'
import FlowSpineInventoryToSettlementPage from '@/pages/workflow/flow-spine-inventory-to-settlement'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineInventoryToSettlementPage', () => {
  it('rendert Inventory-to-Settlement ueber den Backend-Contract', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'inventory-to-settlement',
        title: 'Inventory-to-Settlement',
        subtitle: 'Lager, Versand und Settlement.',
        instance_label: 'Welle INV-2026-031',
        breadcrumb: ['Flow Spine UI', 'Inventory-to-Settlement', 'Welle INV-2026-031'],
        search_placeholder: 'Suche in Wellen ...',
        mode: 'Uebersicht',
        user_role: 'Warehouse Ops',
        left_navigation: { processes: [{ key: 'inventory-to-settlement', label: 'Inventory-to-Settlement', route_path: '/workflow/flow-spine-inventory-to-settlement', active: true }], favorites: ['Welle INV-2026-031'], recent_items: ['Rampenfenster neu zugeordnet'], role_switches: ['Lagerleitung'] },
        badges: [{ label: 'Bestand stabil', tone: 'ok' }],
        focus_node_id: 'picking',
        nodes: [{
          id: 'picking', label: 'Kommissionierung', status: 'active', icon: 'Package', metric: '85% erledigt', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Welle 2 benoetigt Eingriff',
          detail_rows: [{ label: 'Completion', value: '85%' }],
          kpis: [{ label: 'Wave Completion', value: '85%' }],
          documents: [{ label: 'Wellenliste.pdf', href: '/lager/lagerbewegungen' }],
          actions: [{ label: 'Kommissionierung', href: '/lager/terminal', variant: 'primary', api_path: '/api/v1/pick-lists' }],
          agent: { headline: 'Welle 2 benoetigt Eingriff', message: 'Engpasssteuerung oder Rampenwechsel empfohlen.', reasons: ['Prioritaetswelle blockiert'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'ASN-442.xml', href: '/verladung' }], linked_modules: [{ label: 'Verladung', href: '/verladung', api_path: '/api/v1/tours' }], domain: 'workflow' },
        footer_cards: [{ title: 'Agent Events', items: ['Rampenwarnung aktualisiert'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <MemoryRouter>
        <QueryClientProvider client={queryClient}>
          <FlowSpineInventoryToSettlementPage />
        </QueryClientProvider>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Inventory-to-Settlement', level: 1 })).toBeInTheDocument()
    expect(screen.getByText('85% erledigt')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Welle 2 benoetigt Eingriff' })).toBeInTheDocument()
  })
})
