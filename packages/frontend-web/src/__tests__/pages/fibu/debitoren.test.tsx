import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import DebitorenPage from '@/pages/fibu/debitoren'

vi.mock('@/lib/api/fibu', () => ({
  useDebitorenOP: () => ({
    data: [
      {
        id: 'op-1',
        rechnungsnr: 'RE-2025-0123',
        kunde: 'Agrar Schmidt GmbH',
        kundennr: '10001',
        datum: '2025-03-01',
        faelligkeit: '2025-03-15',
        betrag: 1250,
        offen: 1250,
        ueberfaellig: true,
        mahnStufe: 1,
      },
    ],
    isLoading: false,
    isError: false,
    error: null,
    refetch: vi.fn(),
  }),
}))

// Mock useNavigate
vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

describe('DebitorenPage', () => {
  const renderPage = () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <DebitorenPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('sollte rendern', () => {
    renderPage()
    
    expect(screen.getByText('Debitorenbuchhaltung')).toBeInTheDocument()
    expect(screen.getByText('Offene Posten Kunden')).toBeInTheDocument()
  })

  it('sollte KPIs anzeigen', () => {
    renderPage()
    
    expect(screen.getByText('Offene Posten')).toBeInTheDocument()
    expect(screen.getByText('Gesamt Offen')).toBeInTheDocument()
    expect(screen.getByText('Überfällig')).toBeInTheDocument()
  })

  it('sollte Mock-Daten in Tabelle anzeigen', () => {
    renderPage()
    
    expect(screen.getByText('RE-2025-0123')).toBeInTheDocument()
    expect(screen.getByText('Agrar Schmidt GmbH')).toBeInTheDocument()
  })
})
