import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const { get, request, toast, state } = vi.hoisted(() => ({
  get: vi.fn(), request: vi.fn(), toast: vi.fn(), state: { allowed: true },
}))
const definition: ScreenDefinition = {
  schemaVersion: 1, id: 'admin/webhooks-liste', domain: 'admin', mode: 'list', title: 'Webhook-Verwaltung',
  actions: [{ key: 'register', label: 'Neuer Webhook', kind: 'primary', dangerLevel: 'moderate',
    permission: 'studio.admin-webhooks.register', commandEndpoint: '/api/v1/webhooks/', method: 'POST', requiresConfirmation: true,
    inputFields: [
      { key: 'event_area', label: 'Ereignis', type: 'select', required: true,
        optionsSource: { endpoint: '/api/v1/webhooks/areas', valueKey: 'name', labelKey: 'name' } },
      { key: 'url', label: 'Ziel-URL', type: 'text', required: true },
      { key: 'secret', label: 'Signiergeheimnis (optional)', type: 'password' },
    ] }],
  tables: [{ key: 'webhooks', label: 'Webhooks', dataSourceKey: 'webhooks', columns: [], rowActions: [
    { key: 'unregister', label: 'Abmelden', dangerLevel: 'moderate', method: 'DELETE',
      commandEndpoint: '/api/v1/webhooks/{entity_id}', requiresConfirmation: true, permission: 'studio.admin-webhooks.unregister' },
  ] }],
}
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({
  useScreenPermissions: () => state.allowed ? ['studio.admin-webhooks.register', 'studio.admin-webhooks.unregister'] : [],
}))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: 'user-1' } }) }))
vi.mock('@/lib/auth', () => ({ auth: { getAccessToken: () => 'token' } }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get, request }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction }: { onAction: (key: string, row: object) => void }) => <>
    <button onClick={() => onAction('register', {})}>Registrieren</button>
    <button onClick={() => onAction('unregister', { id: 'stable-uuid-123', nr: 42 })}>Zeile abmelden</button>
  </>,
}))

beforeEach(() => {
  vi.clearAllMocks(); state.allowed = true
  get.mockResolvedValue({ data: [{ name: 'order.created' }] })
  request.mockResolvedValue({ data: { success: true } })
})
function mount() {
  render(<QueryClientProvider client={new QueryClient()}><NativeListPage screenId="admin/webhooks-liste" /></QueryClientProvider>)
}

it('loads real event options, validates URL and confirms before registering', async () => {
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Registrieren' }))
  await waitFor(() => expect(get).toHaveBeenCalledWith('/api/v1/webhooks/areas'))
  await screen.findByRole('option', { name: 'order.created' })
  fireEvent.change(screen.getByRole('combobox', { name: 'Ereignis' }), { target: { value: 'order.created' } })
  const secret = screen.getByLabelText('Signiergeheimnis (optional)')
  expect(secret).toHaveAttribute('type', 'password')
  fireEvent.change(secret, { target: { value: 'secret-value' } })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(screen.getByLabelText(/Ziel-URL/)).toBeInTheDocument()
  expect(request).not.toHaveBeenCalled()
  fireEvent.change(screen.getByLabelText(/Ziel-URL/), { target: { value: 'https://example.test/hook' } })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  const confirmation = await screen.findByRole('dialog')
  expect(within(confirmation).getByText(/Bitte bestaetigen Sie die Ausfuehrung/)).toBeVisible()
  expect(request).not.toHaveBeenCalled()
  fireEvent.click(within(confirmation).getByRole('button', { name: 'Neuer Webhook' }))
  await waitFor(() => expect(request).toHaveBeenCalledWith(expect.objectContaining({
    url: '/api/v1/webhooks/', method: 'POST', data: expect.objectContaining({
      event_area: 'order.created', url: 'https://example.test/hook', secret: 'secret-value',
    }),
  })))
})

it('confirms deletion and uses the stable ID instead of the display number', async () => {
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Zeile abmelden' }))
  expect(request).not.toHaveBeenCalled()
  fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Abmelden' }))
  await waitFor(() => expect(request).toHaveBeenCalledWith(expect.objectContaining({
    url: '/api/v1/webhooks/stable-uuid-123', method: 'DELETE',
  })))
})

it('rejects direct callbacks without projected permission before any request', () => {
  state.allowed = false; mount()
  fireEvent.click(screen.getByRole('button', { name: 'Registrieren' }))
  fireEvent.click(screen.getByRole('button', { name: 'Zeile abmelden' }))
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(get).not.toHaveBeenCalled()
  expect(request).not.toHaveBeenCalled()
})
