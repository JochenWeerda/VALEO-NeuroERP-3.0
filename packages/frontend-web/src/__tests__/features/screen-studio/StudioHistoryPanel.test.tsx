import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { StudioHistoryPanel } from '@/features/screen-studio/StudioHistoryPanel'

const runtime = vi.hoisted(() => vi.fn())
const schema = vi.hoisted(() => vi.fn())
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: schema }))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: runtime,
  UniversalMaskRenderer: ({ onAction }: { onAction: (_action: string, _row: { id: string }) => void }) =>
    <button onClick={() => onAction('compare', { id: 'immutable-event' })}>Vergleichen</button>,
}))

describe('native Studio history', () => {
  beforeEach(() => {
    runtime.mockReset().mockReturnValue({ plan: {}, tableRows: {}, entityData: {}, messages: [] })
    schema.mockReset().mockReturnValue({ data: { id: 'native' }, isLoading: false })
  })
  it('binds comparison to the selected immutable event through the universal runtime', () => {
    render(<StudioHistoryPanel draftId="own-draft" />)
    fireEvent.click(screen.getByText('Vergleichen'))
    expect(runtime).toHaveBeenCalledWith(expect.objectContaining({
      screenId: 'platform/studio-history-diff', entityId: 'immutable-event',
    }))
  })
  it('shows a loading error without pretending that history is empty', () => {
    schema.mockReturnValue({ error: new Error('unavailable'), isLoading: false })
    render(<StudioHistoryPanel draftId="own-draft" />)
    expect(screen.getByRole('alert')).toHaveTextContent('Historienmaske konnte nicht geladen werden.')
  })
})
