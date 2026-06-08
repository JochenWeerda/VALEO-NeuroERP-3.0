import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import FlowSpineHarvestToSettlementPage from '@/pages/workflow/flow-spine-harvest-to-settlement'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineHarvestToSettlementPage', () => {
  it('rendert den Harvest-to-Settlement Prozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'harvest-to-settlement',
        title: 'Harvest-to-Settlement',
        subtitle: 'Ernteannahme, Trocknung und Abrechnung.',
        instance_label: 'Kampagne ERN-2026-004',
        breadcrumb: ['Flow Spine UI', 'Harvest-to-Settlement', 'Kampagne ERN-2026-004'],
        search_placeholder: 'Suche in Annahmen ...',
        mode: 'Flow',
        user_role: 'Agrar Operations',
        left_navigation: { processes: [{ key: 'harvest-to-settlement', label: 'Harvest-to-Settlement', route_path: '/workflow/flow-spine-harvest-to-settlement', active: true }], favorites: ['Kampagne ERN-2026-004'], recent_items: ['Trocknungsgrad aktualisiert'], role_switches: ['Lagerleitung'] },
        badges: [{ label: 'Qualitaet stabil', tone: 'ok' }],
        focus_node_id: 'trocknung',
        nodes: [{
          id: 'trocknung', label: 'Trocknung', status: 'active', icon: 'Sparkles', metric: '8,1 t aktiv', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Trocknungskapazitaet an Grenze',
          detail_rows: [{ label: 'Trockner', value: 'Linie T-3' }],
          kpis: [{ label: 'Kapazitaet', value: '78%' }],
          documents: [{ label: 'Trockner-Log.xlsx', href: '/dokumente/ablage' }],
          actions: [{ label: 'Trockner planen', href: '/workflow/workflow-monitoring', variant: 'primary', api_path: '/api/v1/background-jobs/queues' }],
          agent: { headline: 'Trocknungskapazitaet an Grenze', message: 'Umlagerung oder Dritttrockner empfohlen.', reasons: ['Silo 3 kritisch'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Annahme-Protokoll ERN-2026.pdf', href: '/agrar/ernte-annahme-erfassung' }], linked_modules: [{ label: 'Abrechnung', href: '/annahme/abrechnung', api_path: '/api/v1/agrar/settlements' }], domain: 'workflow' },
        footer_cards: [{ title: 'Agent Events', items: ['Trocknungswarnung aktualisiert'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<MemoryRouter><QueryClientProvider client={queryClient}><FlowSpineHarvestToSettlementPage /></QueryClientProvider></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: 'Harvest-to-Settlement', level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /trocknung/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Trocknungskapazitaet an Grenze' })).toBeInTheDocument()
  })
})
