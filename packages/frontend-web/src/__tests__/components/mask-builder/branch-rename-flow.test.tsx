import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const { executeAction } = vi.hoisted(() => ({ executeAction: vi.fn() }))
vi.mock('@/components/mask-builder', () => ({
  useHumanActionDispatch: () => ({ executeAction }),
  useUniversalMaskRuntime: () => ({
    plan: {}, entityData: { name: 'Nord', version: 123456 }, tableRows: {}, messages: [], refetch: vi.fn(),
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string, payload: object) => void }) =>
    <button onClick={() => onAction('bearbeiten', { id: 'branch-1' })}>Umbenennen</button>,
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['admin:all'] }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn().mockResolvedValue({}) }, getAxiosErrorMessage: () => '' }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: {
  id: 'admin/branches/detail', title: 'Niederlassung', adapter: { temporary: false },
  actions: [{
    key: 'bearbeiten', label: 'Umbenennen', permission: 'admin:all', dangerLevel: 'moderate',
    commandEndpoint: '/api/v1/admin/branches/{entity_id}/actions/bearbeiten',
    inputFields: [{ key: 'name', label: 'Name', type: 'text', required: true }],
    inputPrefill: 'entity', requiresExpectedVersion: true, requiresIdempotencyKey: true, auditReasonRequired: true,
  }],
}, isFetching: false }) }))

it('sends only the edited name and displayed version, then requires an audit reason', async () => {
  executeAction.mockResolvedValueOnce({ success: true, proposedChanges: [{ name: 'Nordwest' }] })
    .mockResolvedValueOnce({ success: true })
  render(<QueryClientProvider client={new QueryClient()}><UniversalNativeDetailPage screenId="admin/branches/detail" entityId="branch-1" /></QueryClientProvider>)
  fireEvent.click(screen.getByRole('button', { name: 'Umbenennen' }))
  const name = await screen.findByRole('textbox')
  expect(name).toHaveValue('Nord')
  fireEvent.change(name, { target: { value: 'Nordwest' } })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

  fireEvent.click(await screen.findByRole('button', { name: 'Ausführen', exact: true }))
  const reason = await screen.findByRole('textbox', { name: /Begründung/ })
  expect(executeAction.mock.calls.map(([request]) => request.mode)).toEqual(['dryRun'])
  expect(executeAction.mock.calls[0][0]).toMatchObject({ payload: { name: 'Nordwest' }, expectedVersion: 123456 })
  expect(executeAction.mock.calls[0][0].payload).toEqual({ name: 'Nordwest' })
  fireEvent.change(reason, { target: { value: 'Namenskorrektur' } })
  fireEvent.click(screen.getByRole('button', { name: 'Bestätigen & Ausführen' }))
  expect(executeAction.mock.calls[1][0]).toMatchObject({
    mode: 'execute', payload: { name: 'Nordwest' }, expectedVersion: 123456, auditReason: 'Namenskorrektur',
  })
})
