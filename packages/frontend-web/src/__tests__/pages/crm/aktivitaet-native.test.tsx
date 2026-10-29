import '@testing-library/jest-dom/vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'
import definition from '../../fixtures/crm-activity-studio.json'

const state = vi.hoisted(() => ({ post: vi.fn(), get: vi.fn(), request: vi.fn(), navigate: vi.fn(), permissions: ['crm.activity.update'] as string[] }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition, isError: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: state.post, get: state.get, request: state.request }, getAxiosErrorMessage: () => 'Fehler' }))
vi.mock('@tanstack/react-router', async original => ({ ...await original<object>(), useNavigate: () => state.navigate }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: 'test', scopes: [], roles: [] } }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => state.permissions }))
vi.mock('@/app/routing/typed-router', async original => ({ ...await original<object>(), useNavigate: () => state.navigate }))

function mount(id = 'neu') {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<MemoryRouter initialEntries={['/crm/aktivitaet/neu']}><QueryClientProvider client={client}><UniversalNativeDetailPage screenId="crm/aktivitaet" entityId={id} /></QueryClientProvider></MemoryRouter>)
}
beforeEach(() => { vi.clearAllMocks(); state.permissions = ['crm.activity.update'] })

describe('CRM native activity creation', () => {
  it('creates the three lists together and reuses the intent on retry', async () => {
    state.post.mockRejectedValueOnce(new Error('uncertain')).mockResolvedValueOnce({ data: { id: 'created-1' } })
    mount()
    fireEvent.change(await screen.findByLabelText('Betreff'), { target: { value: 'Testtermin' } })
    fireEvent.change(screen.getByLabelText('Besprochene Themen'), { target: { value: 'one\ntwo' } })
    fireEvent.change(screen.getByLabelText('Besprochene Bestellungen'), { target: { value: 'order' } })
    fireEvent.change(screen.getByLabelText('Naechste Schritte'), { target: { value: 'follow' } })
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(state.post).toHaveBeenCalledTimes(1))
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(state.post).toHaveBeenCalledTimes(2))
    const first = state.post.mock.calls[0][1], second = state.post.mock.calls[1][1]
    expect(first).toMatchObject({ title: 'Testtermin', main_topics: ['one', 'two'], orders_placed: ['order'], follow_up_actions: ['follow'] })
    expect(first.idempotency_key).toBeTruthy()
    expect(second.idempotency_key).toBe(first.idempotency_key)
    expect(first).not.toHaveProperty('tenant_id')
    expect(state.get).not.toHaveBeenCalled()
    await waitFor(() => expect(state.navigate).toHaveBeenCalledWith('/crm/aktivitaet/created-1'))
  })
})



describe('CRM native activity detail', () => {
  const activity = { id: 'a1', version: 4, type: 'call', title: 'Original', customer: '', contact_person: '', date: null, status: 'planned', assigned_to: '', main_topics: ['old'], orders_placed: [], follow_up_actions: [] }
  beforeEach(() => {
    state.post.mockResolvedValue({ data: {} }); state.get.mockImplementation(async (url: string) => {
      if (url.includes('/activities/a1')) return { data: activity }
      throw new Error(`Unexpected GET ${url}`)
    })
    state.request.mockImplementation(async ({ data }: { data: Record<string, unknown> }) => ({ data: { actionKey: 'update', mode: data._mode ?? 'execute', success: true, proposedChanges: data._mode ? ['Aktivitaet entfernen'] : [], activity, version: 4 } }))
  })
  it('waits for the entity before offering edits and prefills the loaded data', async () => {
    let resolveGet!: (value: unknown) => void
    state.get.mockReturnValue(new Promise(resolve => { resolveGet = resolve }))
    mount('a1')
    expect(screen.queryByRole('button', { name: 'Bearbeiten' })).not.toBeInTheDocument()
    resolveGet({ data: activity })
    fireEvent.click(await screen.findByRole('button', { name: 'Bearbeiten' }))
    const title = within(await screen.findByRole('dialog')).getByLabelText('Betreff')
    await waitFor(() => expect(title).toHaveValue('Original'))
  })
  it('prepopulates and submits an edit with the read version and intent', async () => {
    mount('a1')
    fireEvent.click(await screen.findByRole('button', { name: 'Bearbeiten' }))
    const title = within(await screen.findByRole('dialog')).getByLabelText('Betreff')
    await waitFor(() => expect(title).toHaveValue('Original'))
    fireEvent.change(title, { target: { value: 'Changed' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(state.request).toHaveBeenCalled())
    expect(state.request.mock.calls[0][0].data).toMatchObject({ title: 'Changed', expected_version: 4, _idempotencyKey: expect.any(String) })
  })
  it('previews deletion before execution and carries the same version', async () => {
    mount('a1')
    fireEvent.click(await screen.findByRole('button', { name: 'Aktivitaet loeschen' }))
    expect(state.request).not.toHaveBeenCalled()
    fireEvent.click(await screen.findByRole('button', { name: 'Bestätigen' }))
    await waitFor(() => expect(state.request).toHaveBeenCalledTimes(1))
    expect(state.request.mock.calls[0][0].data).toMatchObject({ _mode: 'dryRun', expected_version: 4 })
    fireEvent.click(await screen.findByRole('button', { name: 'Ausführen' }))
    await waitFor(() => expect(state.request).toHaveBeenCalledTimes(2))
    expect(state.request.mock.calls[1][0].data).toMatchObject({ expected_version: 4, _idempotencyKey: state.request.mock.calls[0][0].data._idempotencyKey })
    expect(state.request.mock.calls[1][0].data).not.toHaveProperty('_mode')
  })
  it('does not offer editing to a read-only user', async () => {
    state.permissions = []
    mount('a1')
    await screen.findByDisplayValue('Original')
    const edit = screen.queryByRole('button', { name: 'Bearbeiten' })
    if (edit) expect(edit).toBeDisabled()
    expect(state.request).not.toHaveBeenCalled()
  })
  it('does not offer creation without the projected permission', async () => {
    state.permissions = []
    mount()
    expect(await screen.findByText(/keine Berechtigung/i)).toBeInTheDocument()
    expect(state.post).not.toHaveBeenCalled()
  })
})
