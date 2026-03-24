import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineContractToSettlementPage from '@/pages/workflow/flow-spine-contract-to-settlement'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineContractToSettlementPage', () => {
  it('rendert den agrarischen Contract-to-Settlement Prozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'contract-to-settlement',
        title: 'Contract-to-Settlement',
        subtitle: 'Agrarischer Kernfluss ohne Medienbruch.',
        instance_label: 'Kette CTS-2026-014',
        breadcrumb: ['Flow Spine UI', 'Contract-to-Settlement', 'Kette CTS-2026-014'],
        search_placeholder: 'Suche in Kontrakten ...',
        mode: 'Flow',
        user_role: 'Agrar Operations',
        left_navigation: { processes: [{ key: 'contract-to-settlement', label: 'Contract-to-Settlement', route_path: '/workflow/flow-spine-contract-to-settlement', active: true }], favorites: ['Kette CTS-2026-014'], recent_items: ['Annahme aktualisiert'], role_switches: ['Annahmeleitung'] },
        badges: [{ label: '3 von 4 Gliedern gruen', tone: 'ok' }],
        focus_node_id: 'acceptance',
        nodes: [{
          id: 'acceptance', label: 'Annahme', status: 'active', icon: 'Truck', metric: 'ANH-551', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Annahme sauber verknuepft',
          detail_rows: [{ label: 'Wiegeschein', value: 'WT-9911' }],
          kpis: [{ label: 'Link Score', value: '100%' }],
          documents: [{ label: 'Wiegeschein WT-9911', href: '/waage/wiegungen' }],
          actions: [{ label: 'Annahme bearbeiten', href: '/agrar/ernte-annahme-erfassung', variant: 'primary', api_path: '/api/v1/agrar/harvest-acceptance' }],
          agent: { headline: 'Annahme sauber verknuepft', message: 'Kontrakt- und Ticketbezug sind vollstaendig.', reasons: ['Kein Medienbruch'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Kontrakt_884.pdf', href: '/kontrakte' }], linked_modules: [{ label: 'Abrechnung', href: '/annahme/abrechnung', api_path: '/api/v1/agrar/settlements' }], domain: 'annahme' },
        footer_cards: [{ title: 'Naechste Schritte', items: ['Freigabe abschliessen'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<MemoryRouter><QueryClientProvider client={queryClient}><FlowSpineContractToSettlementPage /></QueryClientProvider></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: 'Contract-to-Settlement', level: 1 })).toBeInTheDocument()
    expect(screen.getByText('ANH-551')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Annahme sauber verknuepft' })).toBeInTheDocument()
  })
})
