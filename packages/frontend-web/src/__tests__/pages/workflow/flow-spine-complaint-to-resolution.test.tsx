import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineComplaintToResolutionPage from '@/pages/workflow/flow-spine-complaint-to-resolution'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FlowSpineComplaintToResolutionPage', () => {
  it('rendert den Reklamationsprozessraum', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        process_key: 'complaint-to-resolution',
        title: 'Complaint-to-Resolution',
        subtitle: 'Reklamationen mit CRM und DMS.',
        instance_label: 'Reklamation REK-2026-044',
        breadcrumb: ['Flow Spine UI', 'Complaint-to-Resolution', 'Reklamation REK-2026-044'],
        search_placeholder: 'Suche in Reklamationen ...',
        mode: 'Fokus',
        user_role: 'Quality Service Lead',
        left_navigation: { processes: [{ key: 'complaint-to-resolution', label: 'Complaint-to-Resolution', route_path: '/workflow/flow-spine-complaint-to-resolution', active: true }], favorites: ['REK-2026-044'], recent_items: ['Kulanzoption bewertet'], role_switches: ['Service Desk'] },
        badges: [{ label: 'SLA im Ziel', tone: 'ok' }],
        focus_node_id: 'triage',
        nodes: [{
          id: 'triage', label: 'Triage', status: 'active', icon: 'ShieldCheck', metric: 'Prioritaet hoch', submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight: 'Kulanzpfad empfohlen',
          detail_rows: [{ label: 'SLA', value: '24h' }],
          kpis: [{ label: 'SLA Rest', value: '9h' }],
          documents: [{ label: 'Triage-Notiz.pdf', href: '/qualitaet/reklamationen' }],
          actions: [{ label: 'Case aktualisieren', href: '/qualitaet/reklamationen', variant: 'primary', api_path: '/api/v1/reklamationen/REK-2026-044/transition' }],
          agent: { headline: 'Kulanzpfad empfohlen', message: 'Risiko fuer Kundenabwanderung ist erhoeht.', reasons: ['Wiederholungskunde'], actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'] },
        }],
        right_panel: { resources: [{ label: 'Schadensfoto_884.jpg', href: '/dokumente/ablage' }], linked_modules: [{ label: 'Reklamationen', href: '/qualitaet/reklamationen', api_path: '/api/v1/reklamationen' }], domain: 'quality' },
        footer_cards: [{ title: 'SLA-Board', items: ['24h Erstreaktion'] }],
      },
    })

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(<MemoryRouter><QueryClientProvider client={queryClient}><FlowSpineComplaintToResolutionPage /></QueryClientProvider></MemoryRouter>)

    expect(await screen.findByRole('heading', { name: 'Complaint-to-Resolution', level: 1 })).toBeInTheDocument()
    expect(screen.getByText('Prioritaet hoch')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Kulanzpfad empfohlen' })).toBeInTheDocument()
  })
})
