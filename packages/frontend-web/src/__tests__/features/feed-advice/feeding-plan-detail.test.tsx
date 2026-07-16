import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FeedingPlanDetail } from '@/features/feed-advice/FeedingPlanDetail'

const navigate = vi.fn()
const print = vi.fn()

vi.mock('@tanstack/react-router', () => ({ useNavigate: () => navigate }))
vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: { adapter: { temporary: false } }, error: null }),
}))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({
    plan: { actions: [] }, entityError: null,
    entityData: { id: 'pv-1', plan_id: 'p-1', group_id: 'g-1', group_name: 'Hochleistung', name: 'Sommer', version_no: 2, source_ration_version_id: 'rv-3', animal_count: 42, dosing_step_kg: 0.5, rounding_mode: 'nearest', valid_from: '2026-07-16', valid_until: '2026-07-31', reason: 'Freigabe', published_by: 'advisor', published_at: '2026-07-16T10:00:00Z', plan_status: 'stale', is_stale: true, instructions: [] },
    tableRows: { instructions: [{ id: 'i-1', sequence: 1, feed_id: 'mais', feed_name: 'Maissilage', kg_fm_per_animal: 12.5, raw_batch_kg: 525, target_batch_kg: 525, rounding_delta_kg: 0 }] },
    tableQueryStates: {}, tableTotals: {}, lookupBindings: {}, setTableQuery: vi.fn(),
    userOverlay: {}, updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(),
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string) => void }) => <div>
    <button onClick={() => onAction('print_plan')}>Drucken / als PDF speichern</button>
    <button onClick={() => onAction('open_mobile')}>Mobile Stallansicht</button>
  </div>,
}))

describe('FeedingPlanDetail', () => {
  it('renders stale status and a provenance-complete print projection', () => {
    vi.stubGlobal('print', print)
    render(<FeedingPlanDetail versionId="pv-1" />)
    expect(screen.getByRole('status')).toHaveTextContent('veraltet')
    expect(screen.getByTestId('feeding-plan-print')).toHaveTextContent('pv-1')
    expect(screen.getByTestId('feeding-plan-print')).toHaveTextContent('rv-3')
    expect(screen.getByTestId('feeding-plan-print')).toHaveTextContent('Maissilage')
    fireEvent.click(screen.getByRole('button', { name: 'Drucken / als PDF speichern' }))
    expect(print).toHaveBeenCalledOnce()
  })

  it('opens the mobile stall journey through the declared action', () => {
    render(<FeedingPlanDetail versionId="pv-1" />)
    fireEvent.click(screen.getByRole('button', { name: 'Mobile Stallansicht' }))
    expect(navigate).toHaveBeenCalledWith({ to: '/futtermittel/fuetterungsdokumentation-mobil' })
  })
})
