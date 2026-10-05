import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FeedingReferenceData } from '@/features/feed-advice/FeedingReferenceData'

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, testId }: { screenId: string; testId: string }) => (
    <div data-testid={testId}>{screenId}</div>
  ),
}))

describe('FeedingReferenceData', () => {
  it('renders the native Meridian reference-data screen', () => {
    render(<FeedingReferenceData />)
    expect(screen.getByTestId('feeding-reference-data')).toHaveTextContent('agrar/feeding-reference-data')
  })
})
