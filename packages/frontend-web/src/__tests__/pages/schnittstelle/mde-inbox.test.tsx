import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import MdeInboxPage from '@/pages/schnittstelle/mde-inbox'

const { post, invalidateQueries, toast } = vi.hoisted(() => ({
  post: vi.fn(),
  invalidateQueries: vi.fn(),
  toast: vi.fn(),
}))

vi.mock('@/lib/api-client', () => ({ apiClient: { post } }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, onAction }: { screenId: string; onAction: (_key: string) => Promise<void> }) => (
    <div data-testid="native-worklist" data-screen-id={screenId}>
      <button type="button" onClick={() => void onAction('process_pending')}>Verarbeiten</button>
    </div>
  ),
}))

describe('MDE-Eingangskorb', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    post.mockResolvedValue({ data: { processed: 4, failed: 1 } })
    invalidateQueries.mockResolvedValue(undefined)
  })

  it('nutzt die native ScreenDefinition und aktualisiert nach Verarbeitung', async () => {
    render(<MdeInboxPage />)

    expect(screen.getByTestId('native-worklist')).toHaveAttribute('data-screen-id', 'schnittstelle/mde-inbox')
    fireEvent.click(screen.getByRole('button', { name: 'Verarbeiten' }))

    await waitFor(() => expect(post).toHaveBeenCalledWith(
      '/api/v1/mobile/sync-process',
      { reason: 'Manuelle Verarbeitung aus dem MDE-Eingangskorb' },
    ))
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['schnittstelle/mde-inbox'] })
    expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'MDE-Verarbeitung abgeschlossen' }))
  })
})
