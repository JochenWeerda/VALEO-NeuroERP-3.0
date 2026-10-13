import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const { executeAction } = vi.hoisted(() => ({ executeAction: vi.fn() }))
vi.mock('@/components/mask-builder', () => ({
  useHumanActionDispatch: () => ({ executeAction }),
  useUniversalMaskRuntime: () => ({ plan: {}, entityData: {}, tableRows: {}, messages: [], refetch: vi.fn() }),
  UniversalMaskRenderer: ({ onAction, messages }: { onAction: (key: string, payload: object) => void; messages: { message: string }[] }) => (
    <div><button onClick={() => onAction('buchen', {})}>Buchen</button>{messages.map((m, i) => <p key={i}>{m.message}</p>)}</div>
  ),
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['belege.buchen'] }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn().mockResolvedValue({}) }, getAxiosErrorMessage: () => '' }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: {
  id: 'beleg/purchase-invoice', title: 'Rechnung', adapter: { temporary: false },
  actions: [{ key: 'buchen', label: 'Buchen', dangerLevel: 'moderate', commandEndpoint: '/api/v1/docflow/test/post' }],
}, isFetching: false }) }))

describe('native detail preview failure boundary', () => {
  it.each(['Freigabe erforderlich', 'DocFlow-Vorschau gesperrt'])('never executes after rejected preview: %s', async (error) => {
    executeAction.mockReset().mockResolvedValue({ success: false, error, proposedChanges: [] })
    render(<UniversalNativeDetailPage screenId="beleg/purchase-invoice" entityId="test" />)
    fireEvent.click(screen.getByRole('button', { name: 'Buchen' }))
    await waitFor(() => expect(screen.getByText(error)).toBeInTheDocument())
    expect(executeAction).toHaveBeenCalledTimes(1)
    expect(executeAction.mock.calls[0][0].mode).toBe('dryRun')
  })
})
