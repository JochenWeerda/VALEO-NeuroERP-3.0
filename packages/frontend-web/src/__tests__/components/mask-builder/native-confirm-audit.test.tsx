import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const { execute } = vi.hoisted(() => ({ execute: vi.fn() }))
vi.mock('@/components/mask-builder', () => ({
  useHumanActionDispatch: () => ({ executeAction: execute }),
  useUniversalMaskRuntime: () => ({ plan: {}, entityData: { aktion_stornieren: true, version: 3 }, tableRows: {}, messages: [], refetch: vi.fn() }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string, payload: object) => void }) =>
    <button onClick={() => onAction('stornieren', {})}>Stornieren</button>,
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['belege.stornieren'] }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn().mockResolvedValue({}) }, getAxiosErrorMessage: () => '' }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: {
  id: 'beleg/purchase-invoice', title: 'Rechnung', adapter: { temporary: false },
  actions: [{ key: 'stornieren', label: 'Stornieren', enabledWhen: 'aktion_stornieren', dangerLevel: 'critical',
    commandEndpoint: '/api/v1/docflow/{entity_id}/reverse', requiresConfirmation: true, auditReasonRequired: true,
    commandBinding: { adapter: 'docflow.v1', command: 'reverse', preview: false } }],
}, isFetching: false }) }))
beforeEach(() => { execute.mockReset().mockResolvedValue({ success: true }) })
function mount() { render(<UniversalNativeDetailPage screenId="beleg/purchase-invoice" entityId="synthetic-invoice" />) }

it('preserves the required audit stage after the real Radix confirmation and executes only with the entered reason', async () => {
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Stornieren' }))
  fireEvent.click(await screen.findByRole('button', { name: 'Bestätigen', exact: true }))
  const reason = await screen.findByRole('textbox')
  expect(execute).not.toHaveBeenCalled()
  expect(screen.getByRole('button', { name: 'Bestätigen & Ausführen' })).toBeDisabled()
  fireEvent.change(reason, { target: { value: 'Genehmigter synthetischer Pruefstorno' } })
  fireEvent.click(screen.getByRole('button', { name: 'Bestätigen & Ausführen' }))
  await waitFor(() => expect(execute).toHaveBeenCalledTimes(1))
  expect(execute.mock.calls[0][0]).toMatchObject({ actionKey: 'stornieren', mode: 'execute', expectedVersion: 3,
    auditReason: 'Genehmigter synthetischer Pruefstorno' })
})

it.each(['confirmation','audit'])('cancels at the %s stage without sending a command', async stage => {
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Stornieren' }))
  if (stage === 'audit') {
    fireEvent.click(await screen.findByRole('button', { name: 'Bestätigen', exact: true }))
    await screen.findByRole('textbox')
  }
  fireEvent.click(screen.getByRole('button', { name: 'Abbrechen' }))
  await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
  expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
  expect(execute).not.toHaveBeenCalled()
})
