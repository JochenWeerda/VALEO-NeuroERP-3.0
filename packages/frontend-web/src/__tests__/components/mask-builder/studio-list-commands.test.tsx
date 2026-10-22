import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'

const state = vi.hoisted(() => ({ request: vi.fn(), toast: vi.fn(), version: 7 }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: state.toast }) }))
vi.mock('@/lib/export-utils', () => ({ exportToCSV: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: { request: state.request }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['studio.entity.crm.write'] }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: {
  id: 'tenant/studio_example', actions: [], tables: [{ key: 'list', rowActions: [{
    key: 'deactivate', label: 'Deaktivieren', auditReasonRequired: true,
    commandEndpoint: '/api/v1/studio/entities/studio_example/{entity_id}/actions/delete',
  }] }],
} }) }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction, permissions }: {
    onAction: (key: string, row: object) => void; permissions: string[]
  }) => <button disabled={!permissions.includes('studio.entity.crm.write')}
    onClick={() => onAction('deactivate', { id: 'record-1', version: state.version })}>Datensatz deaktivieren</button>,
}))

beforeEach(() => { vi.clearAllMocks(); state.version = 7 })

async function begin() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const key = ['tenant-51', 'tenant/studio_example', undefined, 'table', 'list']
  client.setQueryData(key, { items: [{ id: 'record-1', version: 7 }] })
  render(<QueryClientProvider client={client}><NativeListPage screenId="tenant/studio_example" /></QueryClientProvider>)
  fireEvent.click(screen.getByRole('button', { name: 'Datensatz deaktivieren' }))
  fireEvent.change(await screen.findByRole('textbox'), { target: { value: 'Synthetische Abnahme' } })
  return { client, key }
}

it('sends the displayed version and invalidates tenant-prefixed table data after success', async () => {
  state.request.mockResolvedValue({ data: { success: true } })
  const { client, key } = await begin()
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  await waitFor(() => expect(state.request).toHaveBeenCalledTimes(1))
  expect(state.request.mock.calls[0][0]).toMatchObject({
    url: '/api/v1/studio/entities/studio_example/record-1/actions/delete',
    data: { expected_version: 7, _auditReason: 'Synthetische Abnahme', _idempotencyKey: expect.any(String) },
  })
  await waitFor(() => expect(client.getQueryState(key)?.isInvalidated).toBe(true))
})

it('retries an uncertain response with the same key and uses a new key for changed intent', async () => {
  state.request.mockRejectedValue(new Error('Connection interrupted'))
  await begin()
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  await waitFor(() => expect(state.toast).toHaveBeenCalledTimes(1))
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  await waitFor(() => expect(state.toast).toHaveBeenCalledTimes(2))
  const first = state.request.mock.calls[0][0].data._idempotencyKey
  expect(state.request.mock.calls[1][0].data._idempotencyKey).toBe(first)
  fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Geaenderte Begruendung' } })
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  await waitFor(() => expect(state.toast).toHaveBeenCalledTimes(3))
  expect(state.request.mock.calls[2][0].data._idempotencyKey).not.toBe(first)
})

it('refuses a generated update without a usable displayed version before HTTP', async () => {
  state.version = 0
  await begin()
  fireEvent.click(screen.getByRole('button', { name: 'Deaktivieren' }))
  await waitFor(() => expect(state.toast).toHaveBeenCalledWith(expect.objectContaining({
    variant: 'destructive', description: expect.stringContaining('Version fehlt'),
  })))
  expect(state.request).not.toHaveBeenCalled()
})
