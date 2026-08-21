import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import BelegKontrollePage from '@/pages/auswertungen/beleg-kontrolle'

const post = vi.fn()
const invalidateQueries = vi.fn()

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({ invalidateQueries }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: { post: (...args: unknown[]) => post(...args) },
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({
    screenId,
    testId,
    onAction,
  }: {
    screenId: string
    testId: string
    onAction: (key: string, row: Record<string, unknown>) => Promise<void>
  }) => (
    <div data-testid="native-worklist" data-screen-id={screenId}>
      <button
        type="button"
        data-testid={testId}
        onClick={() => onAction('resolve', { id: 'case-1', source_route: '/verkauf/lieferschein/1' })}
      >
        resolve
      </button>
    </div>
  ),
}))

describe('BelegKontrollePage', () => {
  beforeEach(() => {
    post.mockReset()
    invalidateQueries.mockReset()
    vi.stubGlobal('prompt', vi.fn(() => 'Fachlich geprueft und erledigt'))
  })

  it('renders native worklist and posts audited resolve', async () => {
    post.mockResolvedValue({ data: { id: 'case-1', status: 'resolved' } })
    render(<BelegKontrollePage />)
    expect(screen.getByTestId('native-worklist')).toHaveAttribute('data-screen-id', 'auswertungen/beleg-kontrolle')
    await userEvent.click(screen.getByTestId('beleg-kontrolle'))
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/api/v1/document-control/exceptions/case-1/transition', {
        target: 'resolved',
        reason: 'Fachlich geprueft und erledigt',
      }),
    )
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['auswertungen/beleg-kontrolle'] })
  })
})
