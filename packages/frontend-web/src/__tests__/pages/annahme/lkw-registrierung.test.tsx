/**
 * Tests für LKW-Registrierung (Annahme) – inkl. Scan-Dialog (F18).
 */
import { beforeEach, describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import LKWRegistrierungPage from '@/pages/annahme/lkw-registrierung'

const toastMock = vi.fn()

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

vi.mock('react-dropzone', () => ({
  useDropzone: () => ({
    getRootProps: () => ({}),
    getInputProps: () => ({}),
    isDragActive: false,
  }),
}))

vi.mock('@/lib/axios', () => ({
  api: {
    post: vi.fn().mockResolvedValue({ data: { id: 'att-1' } }),
  },
}))

describe('LKWRegistrierungPage', () => {
  beforeEach(() => {
    toastMock.mockReset()
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
    expect(screen.getByRole('heading', { name: 'LKW-Registrierung' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /^Kennzeichen/i })).toBeInTheDocument()
  })

  it('sollte Scan-Button anzeigen und bei Klick Scan-Dialog öffnen (F18)', () => {
    renderPage()
    const scanButtons = screen.getAllByRole('button', { name: /Scan/i })
    expect(scanButtons.length).toBeGreaterThanOrEqual(1)
    fireEvent.click(scanButtons[0])
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Scan – Kennzeichen / Lieferschein')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Schließen' })).toBeInTheDocument()
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
})
