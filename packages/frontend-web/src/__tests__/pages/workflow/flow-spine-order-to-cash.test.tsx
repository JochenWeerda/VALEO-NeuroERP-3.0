import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from '@/app/routing/react-router-compat'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import FlowSpineOrderToCashPage from '@/pages/workflow/flow-spine-order-to-cash'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
    post: vi.fn(),
  },
}))

vi.mock('@/hooks/use-toast', () => ({
  toast: vi.fn(),
}))

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

const WORKSPACE_PAYLOAD = {
  schema_version: 1,
  manifest_kind: 'FLOW_SPINE_WORKSPACE',
  generated_at: '2026-03-25T19:30:00Z',
  process_key: 'order-to-cash',
  title: 'Auftragsprozess Uebersicht',
  subtitle: 'Aktive Steuerung der Auftrag-bis-Zahlung-Kette mit KI-Copilot.',
  instance_label: 'Auftrag AU-2026-4711',
  breadcrumb: ['Flow Spine', 'Auftragsprozess Uebersicht', 'Auftrag AU-2026-4711'],
  search_placeholder: 'Suche in Prozessen, Auftraegen oder Rechnungen ...',
  mode: 'Ablauf',
  user_role: 'Betriebsleitung',
  left_navigation: {
    processes: [{ key: 'order-to-cash', label: 'Auftrag bis Zahlung', route_path: '/workflow/flow-spine-order-to-cash', active: true }],
    favorites: ['Wichtige Kunden'],
    recent_items: ['AU-2026-4711'],
    role_switches: ['Sales Manager'],
  },
  badges: [{ label: 'SLA stabil', tone: 'ok' }],
  focus_node_id: 'delivery',
  nodes: [
    {
      id: 'delivery',
      label: 'Lieferung',
      status: 'active',
      icon: 'Truck',
      metric: 'In Zustellung',
      submetric: 'Live-Tracking',
      timestamp: '2026-03-25T19:30:00Z',
      insight: 'Supply Chain Alert',
      detail_rows: [{ label: 'Tracking', value: 'GXL-7782-XQ' }],
      kpis: [{ label: 'OTD', value: '92%' }],
      documents: [{ label: 'Lieferschein LS-884', href: '/sales/lieferungen' }],
      actions: [{ label: 'Lieferung starten', href: '/sales/delivery', variant: 'primary', api_path: '/api/v1/channels/slack/process-actions/execute' }],
      agent: {
        headline: 'Supply Chain Alert',
        message: 'Alternativ-Sourcing empfohlen.',
        reasons: ['Lieferant A verspaetet'],
        actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'],
      },
    },
  ],
  right_panel: {
    resources: [{ label: 'Lieferantenvertrag_2024.pdf', href: '/dokumente/ablage' }],
    linked_modules: [{ label: 'Auftragsanlage', href: '/sales/orders/new', api_path: '/api/v1/sales/orders' }],
    domain: 'Prozesse',
  },
  footer_cards: [{ title: 'Naechste Schritte', items: ['Live-Daten anbinden'] }],
}

function setupGetMock(): void {
  getMock.mockImplementation((url: unknown) => {
    const u = typeof url === 'string' ? url : ''
    if (u.includes('/timeline')) {
      return Promise.resolve({
        data: { instance_id: 'test-inst', process_key: 'order-to-cash', tenant_id: 't1', events: [] },
      })
    }
    if (u.includes('/order-to-cash/instances')) {
      return Promise.resolve({
        data: { process_key: 'order-to-cash', total: 0, instances: [] },
      })
    }
    if (u.includes('/flow-spines/order-to-cash')) {
      return Promise.resolve({ data: WORKSPACE_PAYLOAD })
    }
    return Promise.reject(new Error(`Unexpected GET: ${String(url)}`))
  })
}

function renderPage(): void {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <FlowSpineOrderToCashPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('FlowSpineOrderToCashPage', () => {
  beforeEach(() => {
    getMock.mockReset()
    setupGetMock()
  })

  it('rendert den Order-to-Cash-Prozessraum', async () => {
    renderPage()

    expect(await screen.findByRole('heading', { name: 'Auftragsprozess Uebersicht', level: 1 })).toBeInTheDocument()
    expect(getMock).toHaveBeenCalledWith('/api/v1/process/flow-spines/order-to-cash?lang=de')
    expect(screen.getByText('Auftrag bis Zahlung')).toBeInTheDocument()
    expect(screen.getByText('Lieferung')).toBeInTheDocument()
  })
})
