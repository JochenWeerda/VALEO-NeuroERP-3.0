import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const mocks = vi.hoisted(() => ({ execute: vi.fn(), post: vi.fn(), toast: vi.fn() }))

const SD = {
  id: 'crm/opportunity',
  title: 'Verkaufschance',
  adapter: { temporary: false },
  permissions: [],
  actions: [{
    key: 'create_activity',
    label: 'Aktivität anlegen',
    dangerLevel: 'safe',
    commandEndpoint: '/api/v1/crm/opportunities/{entity_id}/actions/create_activity',
    inputFields: [
      { key: 'subject', label: 'Betreff', type: 'text', required: true },
      { key: 'activity_type', label: 'Typ', type: 'select', required: true,
        options: [{ value: 'CALL', label: 'Anruf' }, { value: 'NOTE', label: 'Notiz' }] },
    ],
  }],
}

vi.mock('@tanstack/react-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: mocks.toast }) }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: SD, isLoading: false, isFetching: false, error: null, refetch: vi.fn() }),
}))
vi.mock('@/lib/api-client', () => ({
  apiClient: { post: mocks.post.mockResolvedValue({}), get: vi.fn() },
  getAxiosErrorMessage: (e: unknown) => String(e),
}))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({
    plan: { actions: SD.actions }, entityData: { id: 'opp-1', name: 'Weizen 2027' }, entityError: null,
    tableRows: {}, tableQueryStates: {}, tableTotals: {}, messages: [], lookupBindings: {},
    setTableQuery: vi.fn(), updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(), refetch: vi.fn(),
    isEntityLoading: false, userOverlay: undefined,
  }),
  useHumanActionDispatch: () => ({ executeAction: mocks.execute, loadingActionKey: null }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (k: string, p: Record<string, unknown>) => void }) => (
    <button onClick={() => onAction('create_activity', { id: 'opp-1' })}>Aktivität anlegen</button>
  ),
}))

function zeigen() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <UniversalNativeDetailPage screenId="crm/opportunity" entityId="opp-1" />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.execute.mockResolvedValue({ actionKey: 'create_activity', mode: 'execute', success: true, summary: 'angelegt' })
})

describe('Native Maske: Eingaben einer Aktion', () => {
  it('fragt die deklarierten Eingaben und schickt sie mit', async () => {
    zeigen()
    fireEvent.click(screen.getByRole('button', { name: 'Aktivität anlegen' }))
    const dialog = await screen.findByRole('dialog', { name: 'Aktivität anlegen' })
    expect(mocks.execute).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText(/Betreff/), { target: { value: 'Preis besprochen' } })
    fireEvent.change(screen.getByRole('combobox', { name: 'Typ' }), { target: { value: 'CALL' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(mocks.execute).toHaveBeenCalledTimes(1))
    expect(mocks.execute.mock.calls[0][0]).toMatchObject({
      actionKey: 'create_activity',
      mode: 'execute',
      payload: { id: 'opp-1', subject: 'Preis besprochen', activity_type: 'CALL' },
    })
    await waitFor(() => expect(dialog).not.toBeInTheDocument())
  })

  it('ohne Pflichtangaben wird nichts ausgefuehrt', async () => {
    zeigen()
    fireEvent.click(screen.getByRole('button', { name: 'Aktivität anlegen' }))
    await screen.findByRole('dialog')
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    expect(await screen.findAllByText(/ist ein Pflichtfeld/)).not.toHaveLength(0)
    expect(mocks.execute).not.toHaveBeenCalled()
  })

  it('Abbrechen fuehrt nichts aus', async () => {
    zeigen()
    fireEvent.click(screen.getByRole('button', { name: 'Aktivität anlegen' }))
    await screen.findByRole('dialog')
    fireEvent.click(screen.getByRole('button', { name: 'Abbrechen' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(mocks.execute).not.toHaveBeenCalled()
  })
})
