import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import WaageListePage from '@/pages/waage/liste'

const navigateMock = vi.fn()
const toastMock = vi.fn()

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

vi.mock('@/lib/api/supply-chain', () => ({
  useSupplyChainOverview: () => ({ data: null, isLoading: false }),
}))

vi.mock('@/lib/professional-control-centers', () => ({
  summarizeSupplyOps: () => ({ totalOpen: 0, totalInTransit: 0, totalDelivered: 0, kpis: [] }),
}))

vi.mock('@/lib/api/betrieb', () => ({
  useWaagen: () => ({
    data: [
      {
        id: 'W-001',
        standort: 'Annahme 1',
        typ: 'LKW-Waage',
        maxKapazitaet: 60,
        letzteEichung: '2025-08-15',
        naechsteEichung: '2026-08-15',
        status: 'aktiv',
      },
      {
        id: 'W-002',
        standort: 'Verladung',
        typ: 'Bodenwaage',
        maxKapazitaet: 30,
        letzteEichung: '2025-06-01',
        naechsteEichung: '2025-06-30',
        status: 'wartung',
      },
    ],
    isLoading: false,
    isError: false,
    error: null,
    refetch: vi.fn(),
  }),
}))

describe('WaageListePage', () => {
  it('rendert die Waagenliste im DS-Rahmen', () => {
    render(
      <MemoryRouter>
        <WaageListePage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Waagen', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Suche Waagen')).toBeInTheDocument()
    expect(screen.getByText('Annahme 1')).toBeInTheDocument()
  })

  it('filtert nach Standort und Typ', () => {
    render(
      <MemoryRouter>
        <WaageListePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Suche Waagen'), { target: { value: 'boden' } })
    expect(screen.queryByText('Annahme 1')).not.toBeInTheDocument()
    expect(screen.getByText('Verladung')).toBeInTheDocument()
  })
})
