import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useNewsletterVersand } from '@/features/crm/newsletter-versand'

const mocks = vi.hoisted(() => ({ post: vi.fn(), get: vi.fn(), toast: vi.fn() }))
vi.mock('@/lib/api-client', () => ({
  apiClient: { post: mocks.post, get: mocks.get },
  getAxiosErrorMessage: (e: unknown) => String((e as Error).message),
}))
vi.mock('@/hooks/use-toast', () => ({ toast: mocks.toast }))

function Liste(): JSX.Element {
  const newsletter = useNewsletterVersand('kunden')
  return (
    <>
      {newsletter.dialog}
      <button type="button" onClick={() => newsletter.starten(['a@b.example', 'c@d.example'])}>Newsletter</button>
    </>
  )
}

function zeichnen(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><Liste /></QueryClientProvider>)
}

beforeEach(() => vi.clearAllMocks())

// Bis 08.10.2026 schickte die Liste nur einen Betreff und meldete "versendet",
// waehrend das Backend nichts versandte.
describe('Newsletter-Versand', () => {
  it('fragt Betreff und Text ab und meldet, was der Server annahm', async () => {
    mocks.post.mockResolvedValue({ data: { versendet: 1, fehlgeschlagen: 1, empfaenger_ungueltig: 0 } })
    zeichnen()
    fireEvent.click(screen.getByRole('button', { name: 'Newsletter' }))
    fireEvent.change(screen.getByLabelText(/Betreff/), { target: { value: 'Erntetermine' } })
    fireEvent.change(screen.getByLabelText(/^Text/), { target: { value: 'Annahme ab Montag' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(mocks.post).toHaveBeenCalledWith('/api/v1/crm/kommunikation/newsletter', {
      empfaenger: ['a@b.example', 'c@d.example'], typ: 'kunden', betreff: 'Erntetermine', text: 'Annahme ab Montag',
    }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({
      title: 'Newsletter teilweise versendet', description: '1 von 2 Empfängern erreicht.',
    })))
  })

  it('ohne Text wird nichts gesendet', () => {
    zeichnen()
    fireEvent.click(screen.getByRole('button', { name: 'Newsletter' }))
    fireEvent.change(screen.getByLabelText(/Betreff/), { target: { value: 'Nur Betreff' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    expect(mocks.post).not.toHaveBeenCalled()
  })

  it('zeigt den Fehler, wenn der Versand nicht eingerichtet ist', async () => {
    mocks.post.mockRejectedValue(new Error('E-Mail-Versand ist nicht eingerichtet'))
    zeichnen()
    fireEvent.click(screen.getByRole('button', { name: 'Newsletter' }))
    fireEvent.change(screen.getByLabelText(/Betreff/), { target: { value: 'X' } })
    fireEvent.change(screen.getByLabelText(/^Text/), { target: { value: 'Y' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({
      title: 'Versand fehlgeschlagen', variant: 'destructive',
    })))
  })
})
