import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PruefkorbPage from '@/pages/finance/pruefkorb'

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
    onAction: (key: string, row: Record<string, unknown>) => void
  }) => (
    <div data-testid="native-worklist" data-screen-id={screenId}>
      <button
        type="button"
        data-testid={testId}
        onClick={() => onAction('pruefen', { id: 'befund-1', art: 'Mögliche Dublette', hinweis: 'Gleiche Fremdnummer' })}
      >
        bewerten
      </button>
    </div>
  ),
}))

describe('PruefkorbPage', () => {
  beforeEach(() => {
    post.mockReset()
    invalidateQueries.mockReset()
    toast.mockReset()
  })

  it('zeigt die Arbeitsliste aus der ScreenDefinition und hält die Bewertung über den Kommandoweg fest', async () => {
    post.mockResolvedValue({ data: { id: 'befund-1', status: 'geprueft' } })
    render(<PruefkorbPage />)
    expect(screen.getByTestId('native-worklist')).toHaveAttribute('data-screen-id', 'finance/pruefkorb')

    await userEvent.click(screen.getByTestId('finanz-pruefkorb'))
    expect(await screen.findByText(/Mögliche Dublette — Gleiche Fremdnummer/)).toBeInTheDocument()
    const speichern = screen.getByTestId('pruefkorb-bewertung-speichern')
    expect(speichern).toBeDisabled() // ohne Bewertung wird nichts festgehalten

    await userEvent.type(screen.getByLabelText('Bewertung'), 'Zweite Rechnung ist die Korrektur')
    await userEvent.click(speichern)
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/api/v1/kontrolle/befunde/befund-1/pruefung', {
        note: 'Zweite Rechnung ist die Korrektur',
      }),
    )
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['finance/pruefkorb'] })
    await waitFor(() => expect(screen.queryByTestId('pruefkorb-bewertung')).not.toBeInTheDocument())
  })

  it('zeigt den Grund des Servers, wenn die Bewertung abgelehnt wird, und lässt den Dialog offen', async () => {
    post.mockRejectedValue({ response: { data: { detail: 'Wer gebucht hat, prüft den Befund nicht selbst.' } } })
    render(<PruefkorbPage />)
    await userEvent.click(screen.getByTestId('finanz-pruefkorb'))
    await userEvent.type(await screen.findByLabelText('Bewertung'), 'Geprüft')
    await userEvent.click(screen.getByTestId('pruefkorb-bewertung-speichern'))
    await waitFor(() =>
      expect(toast).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Wer gebucht hat, prüft den Befund nicht selbst.',
          variant: 'destructive',
        }),
      ),
    )
    expect(invalidateQueries).not.toHaveBeenCalled()
    expect(screen.getByTestId('pruefkorb-bewertung')).toBeInTheDocument()
    expect(screen.getByTestId('pruefkorb-bewertung-speichern')).not.toBeDisabled()
  })
})
