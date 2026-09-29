import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import WiegungenPage from '@/pages/waage/wiegungen'

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

vi.mock('@/hooks/useTouchDevice', () => ({
  useTouchDevice: () => true,
}))

vi.mock('@/hooks/useKeyboardShortcuts', () => ({
  buildCoreMaskShortcuts: () => [],
  useKeyboardShortcuts: () => undefined,
}))

vi.mock('@/lib/api/weighing-tickets', () => ({
  useWeighingTickets: () => ({
    data: {
      items: [
        {
          id: 't-1',
          ticket_number: 'WS-1001',
          vehicle_plate: 'HOL-AB 12',
          scale_id: 'W1',
          gross_weight: 24,
          tare_weight: 12,
          net_weight: 12,
          billing_weight: 12,
          status: 'open',
          contract_id: null,
          allocation_status: 'offen',
        },
      ],
    },
    isError: false,
    refetch: vi.fn(),
  }),
  useOpenContracts: () => ({ data: [] }),
  useCreateWeighingTicket: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useUpdateWeighingTicket: () => ({ mutateAsync: vi.fn(), isPending: false, variables: undefined }),
  useAllocateContract: () => ({ mutateAsync: vi.fn(), isPending: false }),
}))

vi.mock('@/lib/api/supply-chain', () => ({
  useSupplyChainOverview: () => ({
    data: {
      waitingInbound: 0,
      openWeighingTickets: 1,
      blockedCharges: 0,
      freightInTransit: 0,
    },
  }),
}))

describe('WiegungenPage', () => {
  it('zeigt Anlegen und Suche ohne Rollenfokus auf Touch', () => {
    render(
      <MemoryRouter>
        <WiegungenPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Wiegungen' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Anlegen' })).toBeInTheDocument()
    expect(screen.getByLabelText('Wiegeschein suchen')).toBeInTheDocument()
    expect(screen.getByText('WS-1001')).toBeInTheDocument()
    expect(screen.queryByText('Rollenfokus')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Schließen' })).toBeInTheDocument()
  })
})
