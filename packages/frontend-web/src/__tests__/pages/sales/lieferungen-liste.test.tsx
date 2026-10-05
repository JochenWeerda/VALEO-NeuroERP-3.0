import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import LieferungenListePage from '@/pages/sales/lieferungen-liste'

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

vi.mock('@/lib/api/sales', () => ({
  useLieferungen: () => ({
    data: [
      {
        id: 'L-1',
        nummer: 'LS-1001',
        datum: '2026-09-17',
        kunde: 'Hof Müller',
        auftragsNr: 'AU-9',
        menge: 12,
        status: 'geplant',
      },
    ],
  }),
}))

describe('LieferungenListePage', () => {
  it('zeigt Suche und Liste ohne Rollenfokus auf Touch', () => {
    render(
      <MemoryRouter>
        <LieferungenListePage />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText(/search|Suchen|Suche/i)).toBeInTheDocument()
    expect(screen.getByText('LS-1001')).toBeInTheDocument()
    expect(screen.queryByText('Rollenfokus')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument()
  })
})
