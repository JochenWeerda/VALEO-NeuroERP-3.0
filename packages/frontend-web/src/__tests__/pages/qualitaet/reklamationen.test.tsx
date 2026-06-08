import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import ReklamationenPage from '@/pages/qualitaet/reklamationen'

const navigateMock = vi.fn()

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('@/lib/api/misc-modules', () => ({
  useReklamationen: () => ({
    data: [
      {
        id: 'rek-1',
        nummer: 'REK-001',
        kunde: 'Agrar Mueller',
        artikel: 'Weizen',
        grund: 'Feuchte',
        datum: '2026-03-20',
        prioritaet: 'hoch',
        status: 'neu',
      },
      {
        id: 'rek-2',
        nummer: 'REK-002',
        kunde: 'Landhandel Nord',
        artikel: 'Gerste',
        grund: 'Besatz',
        datum: '2026-03-19',
        prioritaet: 'normal',
        status: 'in-bearbeitung',
      },
    ],
    isLoading: false,
  }),
}))

describe('ReklamationenPage', () => {
  it('zeigt Reklamationsliste und Suchfeld', () => {
    render(
      <MemoryRouter>
        <ReklamationenPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Reklamationen', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Suche Reklamationen')).toBeInTheDocument()
    expect(screen.getByText('REK-001')).toBeInTheDocument()
  })

  it('filtert Reklamationen ueber die Suche', () => {
    render(
      <MemoryRouter>
        <ReklamationenPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Suche Reklamationen'), { target: { value: 'Landhandel Nord' } })
    expect(screen.queryByText('REK-001')).not.toBeInTheDocument()
    expect(screen.getByText('REK-002')).toBeInTheDocument()
  })
})
