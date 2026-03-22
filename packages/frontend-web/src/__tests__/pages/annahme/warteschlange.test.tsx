import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import WarteschlangePage from '@/pages/annahme/warteschlange'

const navigateMock = vi.fn()
const refetchMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('@/lib/api/inventory', () => ({
  useWarteschlange: () => ({
    data: {
      items: [
        {
          id: 'queue-1',
          position: 1,
          kennzeichen: 'AB-CD 1234',
          lieferant: 'Mueller Agrar',
          artikel: 'Weizen',
          ankunft: '08:15',
          wartezeit: 12,
          status: 'wartend',
          lieferschein_nr: 'LS-42',
        },
      ],
      total: 1,
    },
    isLoading: false,
    refetch: refetchMock,
  }),
}))

describe('WarteschlangePage', () => {
  it('rendert Queue-Sicht im DS-Rahmen', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Annahme-Warteschlange', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Suche Warteschlange')).toBeInTheDocument()
    expect(screen.getByText('AB-CD 1234')).toBeInTheDocument()
  })

  it('filtert die Queue ueber die Suche', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Suche Warteschlange'), { target: { value: 'Mais' } })
    expect(screen.queryByText('AB-CD 1234')).not.toBeInTheDocument()
  })
})
