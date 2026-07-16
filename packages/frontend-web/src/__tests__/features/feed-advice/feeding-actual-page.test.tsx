import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { FeedingActualPage } from '@/features/feed-advice/FeedingActualPage'

const mocks = vi.hoisted(() => ({ exportCsv: vi.fn(), assign: vi.fn(), click: vi.fn() }))

vi.mock('@/lib/api/feeding-actual', () => ({ exportActualFeedingsCsv: mocks.exportCsv }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, onAction }: {
    screenId: string
    onAction: (key: string) => void
  }) => <div data-testid="native-actuals">{screenId}
    <button onClick={() => onAction('export_csv')}>CSV exportieren</button>
  </div>,
}))

describe('FeedingActualPage', () => {
  beforeEach(() => {
    mocks.exportCsv.mockReset()
    mocks.click.mockReset()
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: vi.fn(() => 'blob:actuals') })
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() })
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(mocks.click)
  })

  it('renders through the native Meridian screen and exports the grant-filtered CSV', async () => {
    mocks.exportCsv.mockResolvedValue(new Blob(['actual_record_id']))
    render(<FeedingActualPage />)
    expect(screen.getByTestId('native-actuals')).toHaveTextContent('agrar/feeding-actuals')
    fireEvent.click(screen.getByRole('button', { name: 'CSV exportieren' }))
    await waitFor(() => expect(mocks.exportCsv).toHaveBeenCalledOnce())
    expect(mocks.click).toHaveBeenCalledOnce()
    expect(screen.getByRole('status')).toHaveTextContent('berechtigten Ist-Fuetterungen')
  })
})
