import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DokumentenRuecklaufPage from '@/pages/docflow/dokumenten-ruecklauf'

const { get, post, invalidateQueries, toast } = vi.hoisted(() => ({
  get: vi.fn(), post: vi.fn(), invalidateQueries: vi.fn(), toast: vi.fn(),
}))

vi.mock('@/lib/api-client', () => ({ apiClient: { get, post } }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, onAction }: { screenId: string; onAction: (_key: string, _row: Record<string, unknown>) => Promise<void> }) => (
    <div data-testid="native-worklist" data-screen-id={screenId}>
      <button type="button" onClick={() => void onAction('mark_received', { id: 'case-1' })}>Eingang</button>
    </div>
  ),
}))

describe('Dokumentenruecklauf', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'prompt').mockReturnValue('Posteingang geprueft')
    post.mockResolvedValue({ data: { id: 'case-1', return_status: 'received' } })
    invalidateQueries.mockResolvedValue(undefined)
  })

  it('nutzt die native ScreenDefinition und auditiert Statuswechsel', async () => {
    render(<DokumentenRuecklaufPage />)
    expect(screen.getByTestId('native-worklist')).toHaveAttribute('data-screen-id', 'docflow/dokumenten-ruecklauf')
    fireEvent.click(screen.getByRole('button', { name: 'Eingang' }))
    await waitFor(() => expect(post).toHaveBeenCalledWith('/api/v1/docflow/returns/case-1/transition', {
      kind: 'return', target: 'received', reason: 'Posteingang geprueft',
    }))
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['docflow/dokumenten-ruecklauf'] })
  })
})
