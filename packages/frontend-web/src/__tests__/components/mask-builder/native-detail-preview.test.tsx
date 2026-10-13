import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const { executeAction, state } = vi.hoisted(() => ({ executeAction: vi.fn(), state: { binding: false, audit: false, data: { aktion_buchen: true, aktionshinweis: '' } as Record<string, unknown> } }))
vi.mock('@/components/mask-builder', () => ({
  useHumanActionDispatch: () => ({ executeAction }),
  useUniversalMaskRuntime: () => ({ plan: {}, entityData: state.data, tableRows: {}, messages: [], refetch: vi.fn() }),
  UniversalMaskRenderer: ({ onAction, messages }: { onAction: (key: string, payload: object) => void; messages: { message: string }[] }) => (
    <div><button onClick={() => onAction('buchen', state.data)}>Buchen</button>{messages.map((m, i) => <p key={i}>{m.message}</p>)}</div>
  ),
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['belege.buchen'] }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn().mockResolvedValue({}) }, getAxiosErrorMessage: () => '' }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: {
  id: 'beleg/purchase-invoice', title: 'Rechnung', adapter: { temporary: false },
  actions: [{ key: 'buchen', label: 'Buchen', enabledWhen: 'aktion_buchen', dangerLevel: 'moderate', commandEndpoint: '/api/v1/docflow/test/post', auditReasonRequired: state.audit, requiresConfirmation: state.binding, commandBinding: state.binding ? { adapter: 'docflow.v1', command: 'post', preview: false } : undefined }],
}, isFetching: false }) }))

describe('native detail preview failure boundary', () => {
  it.each(['Freigabe erforderlich', 'DocFlow-Vorschau gesperrt'])('never executes after rejected preview: %s', async (error) => {
    state.data = { aktion_buchen: true }
    executeAction.mockReset().mockResolvedValue({ success: false, error, proposedChanges: [] })
    render(<UniversalNativeDetailPage screenId="beleg/purchase-invoice" entityId="test" />)
    fireEvent.click(screen.getByRole('button', { name: 'Buchen' }))
    await waitFor(() => expect(screen.getByText(error)).toBeInTheDocument())
    expect(executeAction).toHaveBeenCalledTimes(1)
    expect(executeAction.mock.calls[0][0].mode).toBe('dryRun')
  })
})


it.each([{}, { aktion_buchen: false }, { aktion_buchen: false, aktionshinweis: 'Beleg ist storniert.' }])(
  'blocks direct dispatch without a permitted document state: %j', async (data) => {
    state.data = data
    executeAction.mockReset()
    render(<UniversalNativeDetailPage screenId="beleg/purchase-invoice" entityId="test" />)
    fireEvent.click(screen.getByRole('button', { name: 'Buchen' }))
    await waitFor(() => expect(screen.getByText(data.aktionshinweis || 'Diese Aktion ist im aktuellen Belegzustand gesperrt.')).toBeInTheDocument())
    expect(executeAction).not.toHaveBeenCalled()
  },
)


describe('native detail final execution failure', () => {
  it.each([
    { audit: false, success: false, error: 'Freigabe inzwischen abgelaufen' },
    { audit: false, success: false, validationErrors: [{ field: 'quantity', message: 'Menge unzulaessig' }] },
    { audit: true, success: false, error: 'Freigabe inzwischen abgelaufen' },
    { audit: true, success: false, validationErrors: [{ field: 'quantity', message: 'Menge unzulaessig' }] },
  ])('keeps the rejection visible after closing the action flow: %j', async (result) => {
    state.data = { aktion_buchen: true }
    state.audit = result.audit
    executeAction.mockReset()
      .mockResolvedValueOnce({ success: true, proposedChanges: [] })
      .mockResolvedValueOnce(result)
    render(<UniversalNativeDetailPage screenId="beleg/purchase-invoice" entityId="test" />)
    fireEvent.click(screen.getByRole('button', { name: 'Buchen' }))
    if (result.audit) {
      const reasonInput = await screen.findByRole('textbox')
      fireEvent.change(reasonInput, { target: { value: 'Fachliche Fehlerkorrektur' } })
      fireEvent.click(screen.getByRole('button', { name: 'Bestätigen & Ausführen' }))
    }
    await waitFor(() => expect(screen.getByText(result.error ?? 'Menge unzulaessig')).toBeInTheDocument())
    expect(executeAction.mock.calls.map(([request]) => request.mode)).toEqual(['dryRun', 'execute'])
    if (result.audit) expect(executeAction.mock.calls[1][0].auditReason).toBe('Fachliche Fehlerkorrektur')
    state.audit = false
  })
})


it('confirms a bound post without inventing a dry-run and carries the displayed version', async () => {
  state.binding = true
  state.data = { aktion_buchen: true, version: 7 }
  executeAction.mockReset().mockResolvedValue({ success: false, error: 'Freigabe erforderlich' })
  render(<UniversalNativeDetailPage screenId="beleg/purchase-invoice" entityId="test" />)
  fireEvent.click(screen.getByRole('button', { name: 'Buchen' }))
  expect(executeAction).not.toHaveBeenCalled()
  fireEvent.click(await screen.findByRole('button', { name: 'Bestätigen' }))
  await waitFor(() => expect(screen.getByText('Freigabe erforderlich')).toBeInTheDocument())
  expect(executeAction).toHaveBeenCalledTimes(1)
  expect(executeAction.mock.calls[0][0]).toMatchObject({ mode: 'execute', expectedVersion: 7, payload: {}, bindingSnapshot: JSON.stringify({ adapter: 'docflow.v1', command: 'post', preview: false }) })
  state.binding = false
})
