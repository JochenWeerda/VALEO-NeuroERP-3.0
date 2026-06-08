import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/react-router-compat'
import FlowSpineStudioPage from '@/pages/workflow/flow-spine-studio'
import i18n from '@/i18n/config'

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
  it('rendert den lokalisierten Flow-Spine-Katalog', async () => {
    Object.defineProperty(i18n, 'resolvedLanguage', {
      value: 'de',
      configurable: true,
    })
    Object.defineProperty(i18n, 'language', {
      value: 'de',
      configurable: true,
    })

    getMock.mockResolvedValueOnce({
      data: {
        schema_version: 1,
        manifest_kind: 'FLOW_SPINE_PROCESS_CATALOG',
        generated_at: '2026-03-25T19:30:00Z',
        processes: [
          {
            key: 'order-to-cash',
            label: 'Auftrag bis Zahlung',
            route_path: '/workflow/flow-spine-order-to-cash',
            summary: 'Vertrieb, Lieferung, Faktura und Zahlung in einem agentenfaehigen Steuerraum.',
            domain: 'sales',
          },
        ],
      },
    })

    renderPage()

    expect(await screen.findByRole('heading', { name: 'Flow Spine Studio', level: 1 })).toBeInTheDocument()
    expect(getMock).toHaveBeenCalledWith('/api/v1/process/flow-spines/catalog?lang=de')
    expect(screen.getByText(/alle prozessräume auf einen blick/i)).toBeInTheDocument()
    expect(screen.getByText('Auftrag bis Zahlung')).toBeInTheDocument()
    expect(screen.getByText(/agentenfaehigen steuerraum/i)).toBeInTheDocument()
  })
})
