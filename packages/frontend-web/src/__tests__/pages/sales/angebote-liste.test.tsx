import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import AngeboteListePage from '@/pages/sales/angebote-liste'

const navigateMock = vi.fn()

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

vi.mock('@/hooks/useTouchDevice', () => ({
  useTouchDevice: () => true,
}))

vi.mock('@/hooks/useListActions', () => ({
  useListActions: () => ({
    handleExport: vi.fn(),
    handlePrint: vi.fn(),
  }),
}))

vi.mock('@/lib/api/sales', () => ({
  useAngebote: () => ({
    data: [
      {
        id: 'A-1',
        nummer: 'ANG-1001',
        datum: '2026-09-17',
        kunde: 'Hof Müller',
        betrag: 1250,
        gueltigBis: '2026-10-17',
        status: 'offen',
      },
    ],
  }),
}))

describe('AngeboteListePage', () => {
  it('zeigt Suche und Liste ohne Rollenfokus auf Touch', () => {
    render(
      <MemoryRouter>
        <AngeboteListePage />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText(/search|Suchen|Suche/i)).toBeInTheDocument()
    expect(screen.getByText('ANG-1001')).toBeInTheDocument()
    expect(screen.queryByText('Rollenfokus')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument()
  })
})
