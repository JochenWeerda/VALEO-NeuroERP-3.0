import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import BelegKontrollePage from '@/pages/auswertungen/beleg-kontrolle'

const post = vi.fn()
const invalidateQueries = vi.fn()
const toast = vi.fn()

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: () => ({ invalidateQueries }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: { post: (...args: unknown[]) => post(...args) },
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast }),
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
        onClick={() => { void onAction('resolve', { id: 'case-1', source_route: '/verkauf/lieferschein/1' }) }}
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
    toast.mockReset()
    vi.stubGlobal('prompt', vi.fn(() => 'Fachlich geprueft und erledigt'))
  })

  it('ruft den Kommando-Weg der Maske mit Begruendung und Wiederholungsschluessel', async () => {
    post.mockResolvedValue({ data: { success: true, summary: 'Status resolved.' } })
    render(<BelegKontrollePage />)
    expect(screen.getByTestId('native-worklist')).toHaveAttribute('data-screen-id', 'auswertungen/beleg-kontrolle')
    await userEvent.click(screen.getByTestId('beleg-kontrolle'))
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/api/v1/document-control/exceptions/case-1/actions/resolve', {
        _auditReason: 'Fachlich geprueft und erledigt',
        _idempotencyKey: expect.any(String),
      }),
    )
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['auswertungen/beleg-kontrolle'] })
  })

  it('meldet eine fachliche Ablehnung nicht als Erfolg', async () => {
    post.mockResolvedValue({ data: { success: false, error: 'Uebergang resolved -> resolved nicht erlaubt.' } })
    render(<BelegKontrollePage />)
    await userEvent.click(screen.getByTestId('beleg-kontrolle'))
    await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })))
    expect(invalidateQueries).not.toHaveBeenCalled()
  })

  it('fuehrt denselben Fall nicht doppelt aus, solange er laeuft', async () => {
    let resolve: (value: unknown) => void = () => {}
    post.mockReturnValue(new Promise(r => { resolve = r }))
    render(<BelegKontrollePage />)
    await userEvent.click(screen.getByTestId('beleg-kontrolle'))
    await userEvent.click(screen.getByTestId('beleg-kontrolle'))
    expect(post).toHaveBeenCalledTimes(1)
    resolve({ data: { success: true } })
    await waitFor(() => expect(invalidateQueries).toHaveBeenCalledTimes(1))
  })
})
