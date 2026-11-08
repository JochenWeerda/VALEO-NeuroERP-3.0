import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { beforeEach, vi } from 'vitest'
import type { ReactNode } from 'react'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import definitions from './fixtures/native-list-builder-contracts.json'
import { MemoryRouter } from '@/app/routing/test-router'

// These fixtures are the unmodified output of the three canonical Python list builders.
// Only transport and the authenticated session are replaced; compiler/runtime/renderers run normally.
const transport = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn(), navigate: vi.fn(), roles: [] as string[] }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: transport.get, request: transport.request },
  getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'synthetic-user', roles: transport.roles, scopes: [] } }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => transport.navigate }))

beforeEach(() => { vi.restoreAllMocks(); vi.clearAllMocks(); transport.roles = [] })

export function mountList(page: ReactNode, screenId: string, row: Record<string, unknown>, schema?: ScreenDefinition) {
  if (schema) vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({ width: 1440, height: 600, top: 0, left: 0, right: 1440, bottom: 600, x: 0, y: 0, toJSON: () => ({}) })
  const definition = schema ?? (definitions as unknown as Record<string, ScreenDefinition>)[screenId]
  transport.get.mockImplementation(async (url: string) => {
    if (url === `/api/v1/masks/${screenId.replaceAll('/', '__')}/screen-definition`) return { data: definition }
    if (url.startsWith(`/api/v1/masks/${encodeURIComponent(screenId)}/data/list?`)) return { data: { data: { items: [row], total: 1 } } }
    if (url.startsWith('/api/v1/ux/overlays/')) return { data: { screen_id: screenId, overlay: {} } }
    if (url.startsWith(definition.dataSources![0].endpoint)) return { data: { items: [row], total: 1 } }
    throw new Error(`Unexpected HTTP read: ${url}`)
  })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><MemoryRouter>{page}</MemoryRouter></QueryClientProvider>)
}

export { transport }
