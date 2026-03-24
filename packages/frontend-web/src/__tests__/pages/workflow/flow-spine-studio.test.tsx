import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineStudioPage from '@/pages/workflow/flow-spine-studio'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

function renderPage(): void {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <FlowSpineStudioPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('FlowSpineStudioPage', () => {
  it('rendert den backend-verdrahteten Order-to-Cash Prozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'order-to-cash',
        title: 'Auftragsprozess Uebersicht',
        subtitle: 'Aktive Steuerung der Order-to-Cash Kette.',
        instance_label: 'Auftrag AU-2026-4711',
        breadcrumb: ['Flow Spine UI', 'Auftragsprozess Uebersicht', 'Auftrag AU-2026-4711'],
        search_placeholder: 'Suche in Prozessen ...',
        mode: 'Flow',
        user_role: 'Operations Lead',
        left_navigation: { processes: [{ key: 'order-to-cash', label: 'Order-to-Cash', route_path: '/workflow/flow-spine-studio', active: true }], favorites: ['Wichtige Kunden'], recent_items: ['AU-2024-001'], role_switches: ['Sales Manager'] },
        badges: [{ label: 'SLA stabil', tone: 'ok' }],
        focus_node_id: 'delivery',
        nodes: [{
          id: 'delivery', label: 'Lieferung', status: 'active', icon: 'Truck', metric: 'In Zustellung', submetric: 'Live-Tracking', timestamp: '2026-03-24T10:00:00Z', insight: 'Supply Chain Alert',
          detail_rows: [{ label: 'Logistikpartner', value: 'Global Express Logistics' }],
          kpis: [{ label: 'KPI Health', value: '92%' }],
          documents: [{ label: 'Lieferschein LS-884', href: '/sales/lieferungen' }],
          actions: [{ label: 'Lieferung starten', href: '/sales/delivery', variant: 'primary', api_path: '/api/v1/channels/slack/process-actions/execute' }],
          agent: { headline: 'Supply Chain Alert', message: 'Expressoption empfohlen.', reasons: ['Lieferant A verspaetet'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Lieferantenvertrag_2024.pdf', href: '/dokumente/ablage' }], linked_modules: [{ label: 'Rechnungen', href: '/sales/rechnungen', api_path: '/api/v1/finance/invoices' }], domain: 'workflow' },
        footer_cards: [{ title: 'Agent Events', items: ['Delay Prediction aktualisiert'] }],
      },
    })

    renderPage()

    expect(await screen.findByRole('heading', { name: 'Auftragsprozess Uebersicht', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Globale Suche')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /order-to-cash/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Supply Chain Alert' })).toBeInTheDocument()
    expect(screen.getAllByTestId('agent-process-panel').length).toBeGreaterThan(0)
  })
})
