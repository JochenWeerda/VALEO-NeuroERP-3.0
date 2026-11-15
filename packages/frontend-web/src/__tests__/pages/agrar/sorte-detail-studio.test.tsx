import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import definition from '../../fixtures/agrar-sorte-studio.json'
import Page from '@/pages/agrar/saatgut/sortenregister'

const state = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn(), post: vi.fn(), navigate: vi.fn(), permissions: ['agrar.sorte.update'] as string[] }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition, isLoading: false, isError: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: state.get, request: state.request, post: state.post }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@tanstack/react-router', async original => ({ ...await original<object>(), useNavigate: () => state.navigate }))
vi.mock('@/app/routing/typed-router', async original => ({ ...await original<object>(), useParams: () => ({ id: 's1' }), useNavigate: () => state.navigate }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: 'test', scopes: [], roles: [] } }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => state.permissions }))

const sorte = { id: 's1', variety_number: 'W-1', name: 'Weizen A', description: 'Original', crop_type: 'WHEAT', zuechter: 'Züchter', zulassungsjahr: 2020, reifezahl: '3', qualitaetsgruppe: 'A', aktiv: true }
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><MemoryRouter><Page /></MemoryRouter></QueryClientProvider>)
}
beforeEach(() => {
  vi.clearAllMocks(); state.permissions = ['agrar.sorte.update']; state.post.mockResolvedValue({ data: {} })
  state.get.mockImplementation(async (url: string) => {
    if (url === '/api/v1/agrar/varieties/s1') return { data: sorte }
    if (url.startsWith('/api/v1/ux/overlays/')) return { data: { screen_id: 'agrar/saatgut/sorte', overlay: {} } }
    throw new Error(`Unexpected GET ${url}`)
  })
  state.request.mockImplementation(async ({ data }: { data: Record<string, unknown> }) => ({ data: { ...sorte, ...data } }))
})

it('laedt den Sortenstamm und speichert eine Aenderung ueber den echten PUT-Vertrag', async () => {
  mount()
  expect(await screen.findByText('Weizen A')).toBeVisible()
  fireEvent.click(await screen.findByRole('button', { name: 'Bearbeiten' }))
  const dialog = await screen.findByRole('dialog')
  expect(within(dialog).getByLabelText(/Sortennummer/)).toHaveValue('W-1')
  fireEvent.change(within(dialog).getByLabelText('Sorte'), { target: { value: 'Weizen B' } })
  fireEvent.click(within(dialog).getByRole('button', { name: 'Weiter' }))
  await waitFor(() => expect(state.request).toHaveBeenCalledWith(expect.objectContaining({ method: 'PUT', url: '/api/v1/agrar/varieties/s1', data: expect.objectContaining({ name: 'Weizen B', variety_number: 'W-1' }) })))
})

it('bietet ohne Schreibrecht keine Bearbeitung an', async () => {
  state.permissions = []
  mount()
  expect(await screen.findByText('Weizen A')).toBeVisible()
  expect(screen.queryByRole('button', { name: 'Bearbeiten' })).not.toBeInTheDocument()
  expect(state.request).not.toHaveBeenCalled()
})

it('lehnt eine leere Sortennummer vor dem Speichern ab', async () => {
  mount()
  fireEvent.click(await screen.findByRole('button', { name: 'Bearbeiten' }))
  const dialog = await screen.findByRole('dialog')
  fireEvent.change(within(dialog).getByLabelText('Sortennummer'), { target: { value: '' } })
  fireEvent.click(within(dialog).getByRole('button', { name: 'Weiter' }))
  expect(state.request).not.toHaveBeenCalled()
  expect(within(dialog).getByLabelText('Sortennummer')).toHaveValue('')
})
