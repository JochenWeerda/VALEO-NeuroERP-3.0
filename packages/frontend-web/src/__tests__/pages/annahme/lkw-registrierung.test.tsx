/**
 * Tests für LKW-Registrierung (Annahme) – inkl. Scan-Dialog (F18).
 */
import { beforeEach, describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import LKWRegistrierungPage from '@/pages/annahme/lkw-registrierung'

const toastMock = vi.hoisted(() => vi.fn())
const navigateMock = vi.hoisted(() => vi.fn())
const apiGetMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock('react-dropzone', () => ({
  useDropzone: () => ({
    getRootProps: () => ({}),
    getInputProps: () => ({}),
    isDragActive: false,
  }),
}))

vi.mock('@/lib/axios', () => ({
  api: {
    get: apiGetMock,
    post: apiPostMock,
  },
}))

describe('LKWRegistrierungPage', () => {
  beforeEach(() => {
    toastMock.mockReset()
    navigateMock.mockReset()
    apiGetMock.mockReset()
    apiPostMock.mockReset()
    apiGetMock.mockResolvedValue({
      data: {
        items: [
          { id: 'art-weizen', name: 'Weizen', article_number: 'ART-WEIZEN' },
          { id: 'art-raps', name: 'Raps', article_number: 'ART-RAPS' },
        ],
      },
    })
    apiPostMock.mockResolvedValue({ data: { id: 'att-1' } })
  })

  const renderPage = () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <LKWRegistrierungPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('sollte LKW-Registrierung und Kennzeichen anzeigen', () => {
    renderPage()
    expect(screen.getAllByRole('heading', { name: 'LKW-Registrierung' }).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByRole('textbox', { name: /^Kennzeichen/i })).toBeInTheDocument()
  })

  it('sollte Scan-Button anzeigen und bei Klick Scan-Dialog öffnen (F18)', () => {
    renderPage()
    const scanButtons = screen.getAllByRole('button', { name: /Scan/i })
    expect(scanButtons.length).toBeGreaterThanOrEqual(1)
    fireEvent.click(scanButtons[0])
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Scan - Kennzeichen / Lieferschein')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Schliessen' })).toBeInTheDocument()
  })

  it('blockiert Weiter im ersten Wizard-Schritt ohne Kennzeichen', () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    return waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: 'Kennzeichen ist ein Pflichtfeld.',
          variant: 'destructive',
        }),
      )
      expect(screen.queryByRole('textbox', { name: /^Lieferant/i })).not.toBeInTheDocument()
    })
  })

  it('persistiert beim Abschluss eine echte article_id in der LKW-Registrierung', async () => {
    renderPage()

    fireEvent.change(screen.getByRole('textbox', { name: /^Kennzeichen/i }), { target: { value: 'AB-CD 1234' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await screen.findByRole('textbox', { name: /^Lieferant/i })
    fireEvent.change(screen.getByRole('textbox', { name: /^Lieferant/i }), { target: { value: 'Hof Meyer' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weizen' }))
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await screen.findByRole('heading', { name: /Bestaetigung|Bestätigung/i })
    fireEvent.click(screen.getByRole('button', { name: 'Abschliessen' }))

    await waitFor(() => {
      expect(apiPostMock).toHaveBeenLastCalledWith(
        '/api/v1/annahme/lkw-registrierung',
        expect.objectContaining({
          kennzeichen: 'AB-CD 1234',
          lieferant: 'Hof Meyer',
          article_id: 'art-weizen',
          artikel: 'Weizen',
        }),
      )
    })
  })
})
