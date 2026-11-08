import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { beforeEach, vi } from 'vitest'
import type { ReactNode } from 'react'
import definitions from './fixtures/native-batch11-12-builder-contracts.json'
import { MemoryRouter } from '@/app/routing/test-router'

// Real builder contracts and real runtime/renderers; only HTTP, session and navigation are replaced.
const transport = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn(), navigate: vi.fn(), roles: [] as string[] }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: transport.get, request: transport.request },
  getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'synthetic-user', roles: transport.roles, scopes: [] } }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => transport.navigate }))

beforeEach(() => { vi.clearAllMocks(); transport.roles = [] })

export function mountBatchList(page: ReactNode, screenId: keyof typeof definitions, row: Record<string, unknown>) {
  const definition = definitions[screenId]
  const source = definition.tables[0].dataSourceKey
  transport.get.mockImplementation(async (url: string) => {
    if (url === `/api/v1/masks/${screenId.replaceAll('/', '__')}/screen-definition`) return { data: definition }
    if (url.startsWith(`/api/v1/masks/${encodeURIComponent(screenId)}/data/${source}?`)) {
      return { data: { data: { items: [row], total: 1 } } }
    }
    if (url.startsWith('/api/v1/ux/overlays/')) return { data: { screen_id: screenId, overlay: {} } }
    if (definition.dataSources.some(item => url.startsWith(item.endpoint))) return { data: { items: [row], total: 1 } }
    throw new Error(`Unexpected HTTP read: ${url}`)
  })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><MemoryRouter>{page}</MemoryRouter></QueryClientProvider>)
}

export { transport }
