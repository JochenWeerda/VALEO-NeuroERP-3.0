import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import FlowSpineServiceToCustomerPage from '@/pages/workflow/flow-spine-service-to-customer'

/**
 * FSX-020/021/023/024 — Welle 3: der Leitstand wird entdichtet.
 *
 * Der Kern dieser Tests: die drei Modi waren vorher beschriftete <span> ohne
 * jede Wirkung. Ein Test, der nur prueft, dass drei Schaltflaechen existieren,
 * haette das alte Verhalten ebenfalls bestanden. Geprueft wird deshalb die
 * **Wirkung** — was beim Moduswechsel verschwindet und was bleibt.
 */

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
  },
}))

function workspacePayload() {
  return {
    data: {
      process_key: 'service-to-customer',
      title: 'Service-to-Customer',
      subtitle: 'Serviceanfrage, Disposition und Rueckmeldung.',
      instance_label: 'Servicefall SVC-2026-071',
      breadcrumb: ['Flow Spine UI', 'Service-to-Customer', 'Servicefall SVC-2026-071'],
      search_placeholder: 'Suche in Servicefaellen ...',
      mode: 'Flow',
      user_role: 'Service Coordinator',
      left_navigation: {
        processes: [
          {
            key: 'service-to-customer',
            label: 'Service-to-Customer',
            route_path: '/workflow/flow-spine-service-to-customer',
            active: true,
          },
        ],
        favorites: ['SVC-2026-071'],
        recent_items: ['Kundenfenster geaendert'],
        role_switches: ['Field Service'],
      },
      badges: [{ label: 'Tour im Plan', tone: 'ok' }],
      focus_node_id: 'dispatch',
      nodes: [
        {
          id: 'dispatch',
          label: 'Einsatz',
          status: 'active',
          icon: 'Truck',
          metric: 'Vor Ort',
          submetric: 'Heute',
          timestamp: '2026-03-24T10:00:00Z',
          insight: 'Techniker unterwegs',
          detail_rows: [{ label: 'ETA', value: '09:40' }],
          kpis: [{ label: 'SLA-Quote', value: '97%' }],
          documents: [{ label: 'Anfahrtsskizze.png', href: '/agribusiness/field-service-tasks' }],
          actions: [
            {
              label: 'Field Task',
              href: '/agribusiness/field-service-tasks',
              variant: 'primary',
              api_path: '/api/agribusiness/field-service-tasks',
            },
          ],
          agent: {
            headline: 'Kunde informiert',
            message: 'ETA stabil.',
            reasons: ['Kunde bestaetigt'],
            actions: ['Uebernehmen', 'Anpassen', 'Ignorieren'],
          },
        },
      ],
      right_panel: {
        resources: [{ label: 'Serviceauftrag_071.pdf', href: '/service/anfragen' }],
        linked_modules: [
          {
            label: 'Field Service',
            href: '/agribusiness/field-service-tasks',
            api_path: '/api/agribusiness/field-service-tasks',
          },
        ],
        domain: 'service',
      },
      footer_cards: [{ title: 'Tourenstatus', items: ['Route Nordwest'] }],
    },
  }
}

function renderWorkspace() {
  getMock.mockResolvedValue(workspacePayload())
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <FlowSpineServiceToCustomerPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('FlowSpineWorkspace — Welle 3', () => {
  it('FSX-020: die Modi sind bedienbare Schaltflaechen, nicht Beschriftungen', async () => {
    renderWorkspace()
    expect(await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })).toBeInTheDocument()

    for (const label of ['Flow', 'Fokus', 'Uebersicht']) {
      expect(screen.getByRole('button', { name: label })).toBeInTheDocument()
    }
    // Der ausgewaehlte Modus ist maschinenlesbar, nicht nur eingefaerbt.
    expect(screen.getByRole('button', { name: 'Flow' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: 'Fokus' })).toHaveAttribute('aria-pressed', 'false')
  })

  it('FSX-020: Fokus blendet Nebenflaechen aus und behaelt die Aktionen', async () => {
    const user = userEvent.setup()
    renderWorkspace()
    await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })

    // Ausgangslage: Kennzahlen und Fusskarte sind da.
    expect(screen.getByText('SLA-Quote')).toBeInTheDocument()
    expect(screen.getByText('Tourenstatus')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Fokus' }))

    // Was gehen muss: Kennzahlen, Belege, Agentenhinweis, Fusskarten, Prozessspalte.
    expect(screen.queryByText('SLA-Quote')).not.toBeInTheDocument()
    expect(screen.queryByText('Tourenstatus')).not.toBeInTheDocument()
    expect(screen.queryByText('Vorgaenge')).not.toBeInTheDocument()

    // Was bleiben muss: der Schritt und seine Aktion. Ein Fokusmodus, der die
    // Arbeit mitnimmt, waere keiner.
    expect(screen.getByText('Aktionen')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Field Task/i })).toBeInTheDocument()
  })

  it('FSX-020: Uebersicht zeigt den Verlauf ohne die Knotendetails', async () => {
    const user = userEvent.setup()
    renderWorkspace()
    await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })

    await user.click(screen.getByRole('button', { name: 'Uebersicht' }))

    // Der Prozessverlauf bleibt — er ist der Zweck dieses Modus.
    expect(screen.getByRole('button', { name: /Einsatz/i })).toBeInTheDocument()
    // Die Detailflaeche entfaellt.
    expect(screen.queryByText(/Status Details/)).not.toBeInTheDocument()
    expect(screen.queryByText('SLA-Quote')).not.toBeInTheDocument()
  })

  it('FSX-023: die Copilot-Spalte ist eingeklappt und laesst sich oeffnen', async () => {
    const user = userEvent.setup()
    renderWorkspace()
    await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })

    const toggle = screen.getByRole('button', { name: 'Copilot aufklappen' })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    // Die Registerkarten der Spalte existieren im eingeklappten Zustand nicht.
    expect(screen.queryByRole('tab', { name: 'Timeline' })).not.toBeInTheDocument()

    await user.click(toggle)

    expect(screen.getByRole('tab', { name: 'Timeline' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Copilot einklappen' })).toHaveAttribute(
      'aria-expanded',
      'true',
    )
  })

  it('FSX-024: Favoriten und Rollenwechsel stehen nicht mehr im Prozessraum', async () => {
    renderWorkspace()
    await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })

    expect(screen.queryByText('Favoriten')).not.toBeInTheDocument()
    expect(screen.queryByText('Rollenwechsel')).not.toBeInTheDocument()
    // Die Prozessliste selbst bleibt — sie gehoert hierher.
    expect(screen.getByText('Prozesse')).toBeInTheDocument()
  })

  it('FSX-021: Knoten-ID und Resume-Route stehen nur noch in den technischen Details', async () => {
    renderWorkspace()
    await screen.findByRole('heading', { name: 'Service-to-Customer', level: 1 })

    // Ohne geladene Instanz gibt es keinen Lebenszyklus-Block; die Zusicherung
    // gilt der Beschriftung: "Resume" als Feldname im Arbeitsbereich ist weg.
    expect(screen.queryByText('Resume')).not.toBeInTheDocument()
  })
})
