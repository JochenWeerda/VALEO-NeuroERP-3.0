import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineProcureToPayPage from '@/pages/workflow/flow-spine-procure-to-pay'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineProcureToPayPage', () => {
  it('rendert Procure-to-Pay ueber den Flow-Spine-Backend-Contract', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'procure-to-pay',
        title: 'Beschaffungsprozess Uebersicht',
        subtitle: 'Bedarf bis Zahlung.',
        instance_label: 'Bestellung PO-2026-188',
        breadcrumb: ['Flow Spine UI', 'Beschaffungsprozess Uebersicht', 'Bestellung PO-2026-188'],
        search_placeholder: 'Suche in Bestellungen ...',
        mode: 'Fokus',
        user_role: 'Procurement Lead',
        left_navigation: { processes: [{ key: 'procure-to-pay', label: 'Procure-to-Pay', route_path: '/workflow/flow-spine-procure-to-pay', active: true }], favorites: ['PO-2026-188'], recent_items: ['Lieferavis aktualisiert'], role_switches: ['Einkauf'] },
        badges: [{ label: 'Budget im Rahmen', tone: 'ok' }],
        focus_node_id: 'purchase-order',
        nodes: [{
          id: 'purchase-order', label: 'Bestellung', status: 'active', icon: 'ShoppingCart', metric: 'PO-2026-188', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'ETA bedroht Skonto-Fenster',
          detail_rows: [{ label: 'Lieferant', value: 'TechLogistics' }],
          kpis: [{ label: 'Spend', value: 'EUR 18.420' }],
          documents: [{ label: 'Bestellung.pdf', href: '/einkauf/bestellungen' }],
          actions: [{ label: 'Bestellung oeffnen', href: '/einkauf/bestellungen', variant: 'primary', api_path: '/api/v1/einkauf-bestellvorschlag' }],
          agent: { headline: 'ETA bedroht Skonto-Fenster', message: 'Expressoption oder Zweitlieferant empfohlen.', reasons: ['Hafenverzoegerung'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Lieferavis.xml', href: '/einkauf/anlieferavis' }], linked_modules: [{ label: 'Wareneingang', href: '/einkauf/wareneingang', api_path: '/api/v1/einkauf/wareneingang' }], domain: 'workflow' },
        footer_cards: [{ title: 'Agent Events', items: ['ETA-Warnung aktualisiert'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <MemoryRouter>
        <QueryClientProvider client={queryClient}>
          <FlowSpineProcureToPayPage />
        </QueryClientProvider>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Beschaffungsprozess Uebersicht', level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /procure-to-pay/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'ETA bedroht Skonto-Fenster' })).toBeInTheDocument()
  })
})
