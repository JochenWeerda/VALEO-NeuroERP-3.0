import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { FeedingSupplyPage } from '@/features/feed-advice/FeedingSupplyPage'

const mocks = vi.hoisted(() => ({ create: vi.fn(), refetch: vi.fn() }))

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: { adapter: { temporary: false } }, error: null }),
}))

vi.mock('@/lib/api/feeding-supply', () => ({
  createProcurementHandoff: mocks.create,
}))

vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({
    plan: { id: 'plan' }, entityData: {}, entityError: null,
    tableRows: {}, tableQueryStates: {}, tableTotals: {}, lookupBindings: {},
    userOverlay: {}, updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(),
    setTableQuery: vi.fn(), refetch: mocks.refetch,
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string, row: Record<string, unknown>) => void }) => <div>
    <button onClick={() => onAction('create_handoff', {
      plan_version_id: 'pv-1', plan_version_no: 1, group_id: 'g-1', group_name: 'Hochleistung',
      feed_id: 'f-1', feed_name: 'Maissilage', daily_demand_kg: 100, horizon_days: 30,
      safety_pct: 10, gross_demand_kg: 3300, stock_kg: 100, reach_days: 1,
      shortage_kg: 3200, trade_unit_kg: 1000, suggested_order_kg: 4000,
      order_rounding_delta_kg: 800, status: 'critical',
    })}>Kritischen Bedarf uebergeben</button>
    <button onClick={() => onAction('create_handoff', {
      plan_version_id: 'pv-1', feed_id: 'f-2', stock_kg: null,
    })}>Unbekannten Bestand uebergeben</button>
  </div>,
}))

describe('FeedingSupplyPage', () => {
  beforeEach(() => { mocks.create.mockReset(); mocks.refetch.mockReset() })

  it('confirms an explicit proposal and never claims an order was created', async () => {
    mocks.create.mockResolvedValue({ id: 'handoff-1', status: 'proposed' })
    mocks.refetch.mockResolvedValue(undefined)
    render(<FeedingSupplyPage />)

    fireEvent.click(screen.getByRole('button', { name: 'Kritischen Bedarf uebergeben' }))
    expect(screen.getByText('4.000 kg')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Begruendung'), { target: { value: 'Unterdeckung fachlich geprueft' } })
    fireEvent.click(screen.getByRole('button', { name: 'Bedarf uebergeben' }))

    await waitFor(() => expect(mocks.create).toHaveBeenCalledOnce())
    expect(await screen.findByRole('status')).toHaveTextContent('Es wurde keine Bestellung erzeugt')
    expect(screen.getByRole('link', { name: /bestellvorschlaege oeffnen/i })).toHaveAttribute('href', '/einkauf/bestellvorschlaege')
  })

  it('does not interpret an unknown stock as zero', () => {
    render(<FeedingSupplyPage />)
    fireEvent.click(screen.getByRole('button', { name: 'Unbekannten Bestand uebergeben' }))
    expect(screen.getByRole('status')).toHaveTextContent('Bestand ist unbekannt')
    expect(mocks.create).not.toHaveBeenCalled()
  })
})
