/**
 * Rohware-Annahme — Wizard-Schrittvalidierung (VK-020).
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import RohwareAnnahmePage from '@/pages/annahme/rohware'

const toastMock = vi.fn()
const postMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: (...args: unknown[]) => postMock(...args),
  },
}))

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: (): JSX.Element => <div data-testid="agent-process-panel" />,
  AgentSuggestionBadge: (): null => null,
}))

describe('RohwareAnnahmePage', () => {
  beforeEach(() => {
    toastMock.mockReset()
    postMock.mockReset()
    postMock.mockResolvedValue({ data: { id: 'ha-1', acceptance_number: 'A-2026-001' } })
  })

  const renderPage = (): ReturnType<typeof render> => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <RohwareAnnahmePage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('sollte Rohware-Annahme-Titel anzeigen', () => {
    renderPage()
    expect(screen.getByRole('heading', { name: 'Rohware-Annahme' })).toBeInTheDocument()
  })

  it('blockiert Weiter im ersten Schritt ohne Lieferant und Kennzeichen', async () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: 'Lieferant ist ein Pflichtfeld.',
          variant: 'destructive',
        }),
      )
    })
  })

  it('blockiert Weiter im Ware-Schritt ohne Artikel/Lager/positives Netto', async () => {
    renderPage()

    fireEvent.change(screen.getByPlaceholderText('Name des Lieferanten'), {
      target: { value: 'Testhof Nord' },
    })
    fireEvent.change(screen.getByPlaceholderText(/AB-CD 1234/i), {
      target: { value: 'AB CD 999' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(screen.getByText('Ware & Gewicht')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: 'Bitte einen Artikel auswaehlen.',
          variant: 'destructive',
        }),
      )
    })
  })
})
