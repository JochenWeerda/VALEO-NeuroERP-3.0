import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FeedingFeedDetail } from '@/features/feed-advice/FeedingFeedDetail'

const mocks = vi.hoisted(() => ({ update: vi.fn(), refetch: vi.fn() }))
vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: { adapter: { temporary: false } }, isLoading: false, error: null }),
}))
vi.mock('@/lib/api/feeding-feed-catalog', () => ({ updateFeedingFeed: mocks.update }))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({
    plan: { actions: [{ key: 'edit' }] },
    entityData: { id: 'feed-42', name: 'Maissilage', art: 'Grundfutter', feed_kind: 'forage', approval_status: 'approved', revision: 2, trockensubstanz: '35' },
    entityError: null, tableRows: {}, tableQueryStates: {}, tableTotals: {},
    setTableQuery: vi.fn(), updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(), lookupBindings: {}, refetch: mocks.refetch,
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string) => void }) => <button onClick={() => onAction('edit')}>Bearbeiten</button>,
}))

describe('FeedingFeedDetail', () => {
  it('stores master-data edits as an optimistic reasoned revision', async () => {
    mocks.update.mockResolvedValue({})
    render(<FeedingFeedDetail feedId="feed-42" />)
    fireEvent.click(screen.getByRole('button', { name: 'Bearbeiten' }))
    fireEvent.change(screen.getByLabelText('Bezeichnung'), { target: { value: 'Maissilage Nord' } })
    fireEvent.change(screen.getByLabelText('Aenderungsgrund'), { target: { value: 'Lieferung neu bewertet' } })
    fireEvent.click(screen.getByRole('button', { name: 'Neue Revision speichern' }))
    await waitFor(() => expect(mocks.update).toHaveBeenCalledWith('feed-42', expect.objectContaining({
      expected_revision: 2, reason: 'Lieferung neu bewertet', name: 'Maissilage Nord',
    })))
    expect(mocks.refetch).toHaveBeenCalled()
  })
})
