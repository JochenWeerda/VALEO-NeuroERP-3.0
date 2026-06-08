import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import FlowSpineComplianceToReportPage from '@/pages/workflow/flow-spine-compliance-to-report'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineComplianceToReportPage', () => {
  it('rendert den Compliance-to-Report Prozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'compliance-to-report',
        title: 'Compliance-to-Report',
        subtitle: 'CO2, EUDR und ESG Reporting.',
        instance_label: 'Reporting CO2-2026-Q1',
        breadcrumb: ['Flow Spine UI', 'Compliance-to-Report', 'Reporting CO2-2026-Q1'],
        search_placeholder: 'Suche in CO2, EUDR und Reports ...',
        mode: 'Uebersicht',
        user_role: 'Compliance Lead',
        left_navigation: { processes: [{ key: 'compliance-to-report', label: 'Compliance-to-Report', route_path: '/workflow/flow-spine-compliance-to-report', active: true }], favorites: ['CO2-2026-Q1'], recent_items: ['EUDR-Nachweis importiert'], role_switches: ['Nachhaltigkeit'] },
        badges: [{ label: 'Audit-Trail vollstaendig', tone: 'ok' }],
        focus_node_id: 'aggregation',
        nodes: [{
          id: 'aggregation', label: 'Aggregation', status: 'active', icon: 'Calculator', metric: 'Q1 konsolidiert', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Aggregation laeuft',
          detail_rows: [{ label: 'CO2', value: '284 t' }],
          kpis: [{ label: 'Readiness', value: '91%' }],
          documents: [{ label: 'CO2_Bilanz_Q1.pdf', href: '/nachhaltigkeit/co2-bilanz' }],
          actions: [{ label: 'CO2 Bilanz', href: '/nachhaltigkeit/co2-bilanz', variant: 'primary', api_path: '/api/v1/sustainability/reports' }],
          agent: { headline: 'Aggregation laeuft', message: 'Eine Management-Freigabe steht noch aus.', reasons: ['Q1 konsolidiert'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'EUDR_Nachweis_551.pdf', href: '/nachhaltigkeit/eudr-compliance' }], linked_modules: [{ label: 'ESG Report', href: '/nachhaltigkeit/esg-report', api_path: '/api/v1/sustainability/reports' }], domain: 'workflow' },
        footer_cards: [{ title: 'Agent Events', items: ['CO2-Daten aktualisiert'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<MemoryRouter><QueryClientProvider client={queryClient}><FlowSpineComplianceToReportPage /></QueryClientProvider></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: 'Compliance-to-Report', level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /aggregation/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Aggregation laeuft' })).toBeInTheDocument()
  })
})
