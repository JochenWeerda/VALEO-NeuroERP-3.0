import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FeedingGroupDetail } from '@/features/feed-advice/FeedingGroupDetail'

const mocks = vi.hoisted(() => ({
  update: vi.fn(),
  refetch: vi.fn(),
}))

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: { adapter: { temporary: false } }, isLoading: false, error: null }),
}))

vi.mock('@/lib/api/feeding-groups', () => ({
  updateFeedingGroup: mocks.update,
}))

vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({
    plan: { actions: [{ key: 'edit_group' }] },
    entityData: {
      id: 'group-42', name: 'Frischmelker', revision: 3, animal_count: 36,
      profile_code: 'fresh_cow', pregnancy_status: 'unknown', risk_level: 'medium',
      valid_from: '2026-07-01', valid_until: null,
    },
    entityError: null, tableRows: {}, tableQueryStates: {}, tableTotals: {},
    setTableQuery: vi.fn(), updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(),
    lookupBindings: {}, refetch: mocks.refetch,
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string) => void }) => (
    <button onClick={() => onAction('edit_group')}>Tiergruppe bearbeiten</button>
  ),
}))

describe('FeedingGroupDetail', () => {
  it('stores edits as a reasoned optimistic revision', async () => {
    mocks.update.mockResolvedValue({})
    render(<FeedingGroupDetail groupId="group-42" />)

    fireEvent.click(screen.getByRole('button', { name: 'Tiergruppe bearbeiten' }))
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Frischmelker A' } })
    fireEvent.change(screen.getByLabelText('Aenderungsgrund'), { target: { value: 'Tierzahl aktualisiert' } })
    fireEvent.click(screen.getByRole('button', { name: 'Neue Revision speichern' }))

    await waitFor(() => expect(mocks.update).toHaveBeenCalledWith(
      'group-42', expect.objectContaining({
        expected_revision: 3,
        reason: 'Tierzahl aktualisiert',
        name: 'Frischmelker A',
      }),
    ))
    expect(mocks.refetch).toHaveBeenCalled()
  })
})
