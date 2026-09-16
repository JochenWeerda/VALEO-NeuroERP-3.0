import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return {
    ...actual,
    apiClient: { get: getMock, post: vi.fn(), put: vi.fn() },
  }
})

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual<typeof import('@/app/routing/typed-router')>('@/app/routing/typed-router')
  return {
    ...actual,
    useParams: () => ({ screenId: 'tenant__artikel-arbeitsliste' }),
  }
})

vi.stubGlobal('ResizeObserver', class {
  observe() {}
  unobserve() {}
  disconnect() {}
})

import StudioRunPage from '@/pages/admin/studio-run'

describe('StudioRunPage', () => {
  beforeEach(() => {
    getMock.mockResolvedValue({
      data: {
        schemaVersion: 1,
        id: 'tenant/artikel-arbeitsliste',
        domain: 'lager',
        mode: 'list',
        title: 'Artikel-Arbeitsliste',
        adapter: { type: 'native', sourceId: 'tenant/artikel-arbeitsliste', temporary: true },
        layout: { floorplan: 'worklist', columnNavigation: 'listDetail', density: 'compact', contextRail: 'none' },
        tables: [{ key: 'list', label: 'Artikel', columns: [{ key: 'name', label: 'Name' }] }],
        actions: [],
      },
    })
  })

  it('renders a published tenant screen from the runtime catalog', async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <MemoryRouter>
        <QueryClientProvider client={client}>
          <StudioRunPage />
        </QueryClientProvider>
      </MemoryRouter>,
    )
    expect(await screen.findByTestId('studio-run')).toHaveAttribute('data-screen-id', 'tenant/artikel-arbeitsliste')
  })
})
