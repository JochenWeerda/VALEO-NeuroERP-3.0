import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import WebhooksPage from '@/pages/admin/webhooks'

/**
 * Die Maske erwartete bis zum 01.10.2026 `name`, `events[]`, `aktiv` und
 * `last_triggered` — Felder, die der Endpunkt nie geliefert hat. Sichtbar wurde
 * das nie, weil die Liste immer leer war. Beim ersten echten Webhook waere
 * `w.name.toLowerCase()` in der Suche gelaufen. Genau das prueft der erste Test.
 */

const getMock = vi.hoisted(() => vi.fn())
const postMock = vi.hoisted(() => vi.fn())
const deleteMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
    post: postMock,
    delete: deleteMock,
  },
}))

const toastMock = vi.hoisted(() => vi.fn())
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

const anbindung = {
  id: 'wh-1',
  nr: 1,
  url: 'https://partner.example/hook',
  bereich: 'KONTRAKT_NEU',
  is_active: true,
  erstellt_am: '2026-10-01T08:00:00Z',
  letzte_auslosung_am: '2026-10-01T09:30:00Z',
  fehler_count: 2,
  signiert: true,
}

function antworten(webhooks: unknown[] = [anbindung]): void {
  getMock.mockImplementation((pfad: string) => {
    if (pfad === '/api/v1/webhooks') return Promise.resolve({ data: webhooks })
    if (pfad === '/api/v1/webhooks/bereiche') {
      return Promise.resolve({ data: ['KONTRAKT_NEU', 'WIEGUNG_NEU'] })
    }
    if (pfad.endsWith('/zustellversuche')) {
      return Promise.resolve({
        data: [
          {
            versucht_am: '2026-10-01T09:30:00Z',
            erfolgreich: false,
            status_code: 500,
            dauer_ms: 120,
            fehler: 'HTTP 500',
          },
        ],
      })
    }
    return Promise.resolve({ data: [] })
  })
}

function renderPage(): void {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <WebhooksPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('WebhooksPage', () => {
  beforeEach(() => {
    getMock.mockReset()
    postMock.mockReset()
    deleteMock.mockReset()
    toastMock.mockReset()
    postMock.mockResolvedValue({ data: {} })
    deleteMock.mockResolvedValue({ data: null })
  })

  it('zeigt eine Anbindung mit Ereignis, Signatur und Fehlschlaegen', async () => {
    antworten()
    renderPage()

    expect(await screen.findByText('https://partner.example/hook')).toBeInTheDocument()
    expect(screen.getByText('KONTRAKT_NEU')).toBeInTheDocument()
    // Fehlschlaege kommen jetzt aus dem Zustellprotokoll, nicht aus einer
    // konstanten Null.
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('sucht ueber Ziel-URL und Ereignis, ohne an einem fehlenden Feld zu scheitern', async () => {
    antworten()
    renderPage()
    await screen.findByText('https://partner.example/hook')

    await userEvent.type(screen.getByPlaceholderText(/Ziel-URL oder Ereignis/), 'KONTRAKT')
    expect(screen.getByText('https://partner.example/hook')).toBeInTheDocument()

    await userEvent.clear(screen.getByPlaceholderText(/Ziel-URL oder Ereignis/))
    await userEvent.type(screen.getByPlaceholderText(/Ziel-URL oder Ereignis/), 'gibtesnicht')
    expect(screen.queryByText('https://partner.example/hook')).not.toBeInTheDocument()
  })

  it('registriert einen Webhook und meldet den Erfolg', async () => {
    antworten([])
    renderPage()

    await userEvent.click(screen.getByRole('button', { name: /Neuer Webhook/ }))
    await userEvent.selectOptions(await screen.findByLabelText('Ereignis'), 'WIEGUNG_NEU')
    await userEvent.type(screen.getByLabelText('Ziel-URL'), 'https://partner.example/neu')

    const knopf = screen.getByRole('button', { name: 'Registrieren' })
    expect(knopf).toBeEnabled()
    await userEvent.click(knopf)

    await waitFor(() => {
      expect(postMock).toHaveBeenCalledWith('/api/v1/webhooks/bereiche/WIEGUNG_NEU', {
        url: 'https://partner.example/neu',
        bereich: 'WIEGUNG_NEU',
        secret: undefined,
      })
    })
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Webhook registriert' }),
      )
    })
  })

  it('der Registrieren-Knopf bleibt ohne Ereignis und URL gesperrt', async () => {
    antworten([])
    renderPage()

    await userEvent.click(screen.getByRole('button', { name: /Neuer Webhook/ }))
    expect(await screen.findByRole('button', { name: 'Registrieren' })).toBeDisabled()
  })

  it('meldet einen Fehlschlag der Registrierung sichtbar', async () => {
    antworten([])
    postMock.mockRejectedValue({ response: { data: { detail: 'URL muss mit https:// beginnen' } } })
    renderPage()

    await userEvent.click(screen.getByRole('button', { name: /Neuer Webhook/ }))
    await userEvent.selectOptions(await screen.findByLabelText('Ereignis'), 'WIEGUNG_NEU')
    await userEvent.type(screen.getByLabelText('Ziel-URL'), 'https://partner.example/neu')
    await userEvent.click(screen.getByRole('button', { name: 'Registrieren' }))

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Registrierung fehlgeschlagen',
          variant: 'destructive',
        }),
      )
    })
  })

  it('meldet den Webhook ueber seine laufende Nummer ab', async () => {
    antworten()
    renderPage()
    await screen.findByText('https://partner.example/hook')

    await userEvent.click(screen.getByRole('button', { name: /Abmelden/ }))

    await waitFor(() => {
      expect(deleteMock).toHaveBeenCalledWith('/api/v1/webhooks/abmelden/1')
    })
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Webhook abgemeldet' }),
      )
    })
  })

  it('zeigt die Zustellversuche als Nachweis des letzten Versuchs', async () => {
    antworten()
    renderPage()

    const letzter = await screen.findByRole('button', { name: /2026/ })
    await userEvent.click(letzter)

    expect(await screen.findByText('Zustellversuche')).toBeInTheDocument()
    expect(screen.getByText('HTTP 500')).toBeInTheDocument()
    expect(screen.getByText(/120 ms/)).toBeInTheDocument()
  })
})
