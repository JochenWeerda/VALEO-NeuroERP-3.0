import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import MobileFuetterungsdokumentation from '@/pages/futtermittel/fuetterungsdokumentation-mobil'

const mocks = vi.hoisted(() => ({
  current: { data: [{
    id: 'plan-version-2', plan_id: 'plan-1', group_id: 'group-1', group_name: 'Hochleistung', name: 'Sommer',
    version_no: 2, source_ration_version_id: 'ration-v3', animal_count: 42, dosing_step_kg: 0.5,
    rounding_mode: 'nearest', valid_from: '2026-07-16', valid_until: '2026-07-31', reason: 'Freigabe',
    published_by: 'advisor', published_at: '2026-07-16T10:00:00Z', plan_status: 'current', is_stale: false,
    instructions: [{ id: 'i-1', sequence: 1, feed_id: 'mais', feed_name: 'Maissilage', kg_fm_per_animal: 12.5, raw_batch_kg: 525, target_batch_kg: 525, rounding_delta_kg: 0 }],
  }], isLoading: false },
  history: { data: [], refetch: vi.fn() },
  mutation: { mutate: vi.fn(), data: undefined, error: null, isPending: false },
}))

vi.mock('@tanstack/react-query', () => ({
  useQuery: ({ queryKey }: { queryKey: string[] }) => queryKey[0] === 'current-feeding-plans-mobile'
    ? mocks.current
    : mocks.history,
  useMutation: () => mocks.mutation,
}))

describe('mobile feeding plan', () => {
  beforeEach(() => localStorage.clear())

  it('uses the current plan version and its rounded batch target', async () => {
    render(<MobileFuetterungsdokumentation />)
    expect(await screen.findByRole('heading', { name: 'Hochleistung' })).toBeInTheDocument()
    expect(screen.getByText(/Plan v2/)).toBeInTheDocument()
    expect(screen.getByText('Maissilage')).toBeInTheDocument()
    expect(screen.getByText('525.0 kg')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Jetzt füttern' }))
    expect(screen.getByText('Ist-Mengen dokumentieren')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Ist-Fütterung speichern' }))
    expect(mocks.mutation.mutate).toHaveBeenCalledWith(expect.objectContaining({
      plan_version_id: 'plan-version-2',
      cause_class: 'normal',
      components: [{ feed_id: 'mais', actual_kg: 525 }],
    }))
    const cached = JSON.parse(localStorage.getItem('valeo.feeding-plan.mobile.v2') ?? '{}')
    expect(cached.planVersionId).toBe('plan-version-2')
  })
})
