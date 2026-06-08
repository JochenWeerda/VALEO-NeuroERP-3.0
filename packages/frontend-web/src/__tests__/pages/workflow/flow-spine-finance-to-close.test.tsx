import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/react-router-compat'
import FlowSpineFinanceToClosePage from '@/pages/workflow/flow-spine-finance-to-close'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineFinanceToClosePage', () => {
  it('rendert den Finance-to-Close Prozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'finance-to-close',
        title: 'Finance-to-Close',
        subtitle: 'Buchung, Abstimmung und Abschluss.',
        instance_label: 'Periode Maerz 2026',
        breadcrumb: ['Flow Spine UI', 'Finance-to-Close', 'Periode Maerz 2026'],
        search_placeholder: 'Suche in Buchungen ...',
        mode: 'Fokus',
        user_role: 'Finance Lead',
        left_navigation: { processes: [{ key: 'finance-to-close', label: 'Finance-to-Close', route_path: '/workflow/flow-spine-finance-to-close', active: true }], favorites: ['Periode Maerz 2026'], recent_items: ['Abstimmung aktualisiert'], role_switches: ['Controller'] },
        badges: [{ label: 'Buchungen vollstaendig', tone: 'ok' }],
        focus_node_id: 'abstimmung',
        nodes: [{
          id: 'abstimmung', label: 'Abstimmung', status: 'active', icon: 'ArrowLeftRight', metric: '3 Konten offen', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Abstimmungsabweichung erkannt',
          detail_rows: [{ label: 'Differenz', value: 'EUR 240' }],
          kpis: [{ label: 'Abstimmungsquote', value: '97%' }],
          documents: [{ label: 'Abstimmungsprotokoll.pdf', href: '/finance/nebenbuch-abstimmung' }],
          actions: [{ label: 'Nebenbuch-Abstimmung', href: '/finance/nebenbuch-abstimmung', variant: 'primary', api_path: '/api/v1/finance/reconciliation' }],
          agent: { headline: 'Abstimmungsabweichung erkannt', message: 'Klaerung vor USTVA und Sign-off noetig.', reasons: ['Konto 1200 offen'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Buchungsjournal_Maerz.xlsx', href: '/finance/bookings/new' }], linked_modules: [{ label: 'USTVA', href: '/finance/ustva', api_path: '/api/v1/compliance/ustva' }], domain: 'workflow' },
        footer_cards: [{ title: 'Agent Events', items: ['USTVA-Frist aktualisiert'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<MemoryRouter><QueryClientProvider client={queryClient}><FlowSpineFinanceToClosePage /></QueryClientProvider></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: 'Finance-to-Close', level: 1 })).toBeInTheDocument()
    expect(screen.getByText('3 Konten offen')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Abstimmungsabweichung erkannt' })).toBeInTheDocument()
  })
})
