import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from '@/app/routing/test-router'
import { TypedParamsContext } from '@/app/routing/typed-router'
import SaatgutStammPage from '@/pages/agrar/saatgut-stamm'
import definitions from '../fixtures/native-stamm-route-builder-contracts.json'

// The routed page, legacy create form, compiler, runtime and renderers stay real.
const transport = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), request: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: transport,
  getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'synthetic-user', roles: [], scopes: [] } }) }))

beforeEach(() => {
  vi.clearAllMocks()
  transport.post.mockResolvedValue({ data: {} })
  transport.get.mockImplementation(async (url: string) => {
    if (url === '/api/v1/masks/agrar__saatgut/screen-definition') return { data: definitions['agrar/saatgut'] }
    if (url === '/api/v1/agrar/saatgut/synthetic-seed') {
      return { data: { id: 'synthetic-seed', name: 'SYNTHETIC-SEED', artikelnummer: 'SEED-001', status: 'aktiv' } }
    }
    if (url.startsWith('/api/v1/ux/overlays/')) return { data: { screen_id: 'agrar/saatgut', overlay: {} } }
    throw new Error(`Unexpected HTTP read: ${url}`)
  })
})

function mountRoute(path: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}>
    <MemoryRouter initialEntries={[path]}><Routes>
      <Route path="/agrar/saatgut-stamm/:id" element={<SaatgutStammPage />} />
      <Route path="/agrar/saatgut-stamm" element={<SaatgutStammPage />} />
    </Routes></MemoryRouter>
  </QueryClientProvider>)
}

it('mounts an existing Saatgut entity through its canonical detail builder and runtime', async () => {
  mountRoute('/agrar/saatgut-stamm/synthetic-seed')
  expect(await screen.findByTestId('agrar-saatgut-stamm')).toBeTruthy()
  expect(transport.get).toHaveBeenCalledWith('/api/v1/masks/agrar__saatgut/screen-definition', expect.anything())
  expect(transport.get).toHaveBeenCalledWith('/api/v1/agrar/saatgut/synthetic-seed')
  expect(transport.post).toHaveBeenCalledWith('/api/v1/recent-documents/touch', expect.objectContaining({
    screen_id: 'agrar/saatgut', document_id: 'synthetic-seed',
  }))
  expect(transport.post).not.toHaveBeenCalledWith('/api/v1/agrar/saatgut', expect.anything())
})

it.each(['neu', 'new'])('mounts /agrar/saatgut-stamm/%s as creation without a detail read', async (creationId) => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(<QueryClientProvider client={client}><MemoryRouter initialEntries={[`/agrar/saatgut-stamm/${creationId}`]}>
    <TypedParamsContext.Provider value={{ id: creationId }}><SaatgutStammPage /></TypedParamsContext.Provider>
  </MemoryRouter></QueryClientProvider>)
  expect(await screen.findByRole('heading', { name: 'Neues Saatgut' }, { timeout: 5000 })).toBeTruthy()
  expect(transport.get).not.toHaveBeenCalledWith('/api/v1/masks/agrar__saatgut/screen-definition', expect.anything())
  expect(transport.get).not.toHaveBeenCalledWith(`/api/v1/agrar/saatgut/${creationId}`)
  expect(transport.post).not.toHaveBeenCalled()
})
