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
    useParams: () => ({ screenId: 'tenant__lieferanten-bewertung' }),
  }
})

vi.stubGlobal('ResizeObserver', class {
  observe() {}
  unobserve() {}
  disconnect() {}
})

import StudioRunPage from '@/pages/admin/studio-run'

const publishedScreen = {
  schemaVersion: 1,
  id: 'tenant/lieferanten-bewertung',
  domain: 'einkauf',
  mode: 'list',
  title: 'Lieferanten-Bewertung',
  adapter: { type: 'native', sourceId: 'tenant/lieferanten-bewertung', temporary: true },
  layout: { floorplan: 'worklist', columnNavigation: 'listDetail', density: 'compact', contextRail: 'none' },
  dataSources: [{ key: 'suppliers', endpoint: '/api/v1/einkauf/lieferanten', pageSize: 50 }],
  tables: [{
    key: 'list',
    label: 'Lieferanten',
    dataSourceKey: 'suppliers',
    serverPagination: true,
    columns: [
      { key: 'lieferantennummer', label: 'Nr' },
      { key: 'firmenname', label: 'Name' },
    ],
  }],
  actions: [],
}

describe('StudioRunPage', () => {
  beforeEach(() => {
    getMock.mockImplementation(async (url: string) => {
      if (String(url).includes('screen-definition')) {
        return { data: publishedScreen }
      }
      if (String(url).includes('overlays')) {
        return { data: { overlay: {} } }
      }
      if (String(url).includes('/einkauf/lieferanten')) {
        return { data: [{ id: 'lf-1', lieferantennummer: '70011', firmenname: 'Auricher Suessmost GmbH' }] }
      }
      return { data: [] }
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
    expect(await screen.findByTestId('studio-run')).toHaveAttribute('data-screen-id', 'tenant/lieferanten-bewertung')
  })

  it('loads supplier rows through the mask runtime', async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <MemoryRouter>
        <QueryClientProvider client={client}>
          <StudioRunPage />
        </QueryClientProvider>
      </MemoryRouter>,
    )
    expect(await screen.findByText('Auricher Suessmost GmbH')).toBeInTheDocument()
    expect(screen.queryByText('Keine Eintraege vorhanden.')).not.toBeInTheDocument()
  })
})
