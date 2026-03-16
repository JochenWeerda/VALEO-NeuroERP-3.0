import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const view = {
  statusLabel: 'Freigegeben',
  statusClassName: 'bg-blue-50 text-blue-800 border-blue-300',
  summary: 'Aktion ist zulaessig.',
  details: ['Detail A', 'Detail B', 'Detail C'],
  requiresApproval: true,
}

describe('CompactDecisionCard', () => {
  function renderWithQueryClient(node: JSX.Element) {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    return render(<QueryClientProvider client={queryClient}>{node}</QueryClientProvider>)
  }

  beforeEach(() => {
    vi.resetModules()
  })

  it('begrenzt Details fuer einfache Rollen kontrolliert auf Standarddichte', async () => {
    vi.doMock('@/lib/auth', () => ({
      auth: {
        getUser: () => ({ roles: ['user'] }),
      },
    }))
    vi.doMock('@/hooks/useTenant', () => ({
      useTenant: () => ({ tenantId: '00000000-0000-0000-0000-000000000001', setTenantId: vi.fn() }),
    }))

    const { CompactDecisionCard } = await import('@/components/workflow/CompactDecisionCard')

    renderWithQueryClient(<CompactDecisionCard view={view} title="Policy" />)

    expect(screen.getByText('Policy')).toBeInTheDocument()
    expect(screen.getByText('Detail A')).toBeInTheDocument()
    expect(screen.getByText('Detail B')).toBeInTheDocument()
    expect(screen.queryByText('Detail C')).not.toBeInTheDocument()
  })

  it('zieht agrar-settlement ueber das Manifest auf volle Details', async () => {
    vi.doMock('@/lib/auth', () => ({
      auth: {
        getUser: () => ({ roles: ['user'] }),
      },
    }))
    vi.doMock('@/hooks/useTenant', () => ({
      useTenant: () => ({ tenantId: 'tenant-agrar-01', setTenantId: vi.fn() }),
    }))

    const { CompactDecisionCard } = await import('@/components/workflow/CompactDecisionCard')

    renderWithQueryClient(<CompactDecisionCard view={view} pageDomain="agrar-settlement" />)

    expect(screen.getByText('Detail A')).toBeInTheDocument()
    expect(screen.getByText('Detail B')).toBeInTheDocument()
    expect(screen.getByText('Detail C')).toBeInTheDocument()
  })
})
