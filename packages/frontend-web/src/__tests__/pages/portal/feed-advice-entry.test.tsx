import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import PortalFeedAdvicePage from '@/pages/portal/rationsoptimierung'

const locationState = vi.hoisted(() => ({ search: '' }))

vi.mock('@/app/routing/typed-router', () => ({
  useLocation: () => locationState,
}))

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId }: { screenId: string }) => (
    <div data-testid="native-feed-cockpit">{screenId}</div>
  ),
}))

vi.mock('@/pages/futtermittel/rationsoptimierung', () => ({
  default: () => <div data-testid="expert-ration-workspace">Expert</div>,
}))

describe('Portal Fuetterungsberatung entry architecture', () => {
  beforeEach(() => {
    locationState.search = ''
  })

  it('starts in the native Meridian cockpit', () => {
    render(<PortalFeedAdvicePage />)

    expect(screen.getByTestId('native-feed-cockpit')).toHaveTextContent('agrar/feed-advice')
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()
  })

  it('loads the specialised solver only for a concrete task', async () => {
    locationState.search = '?mode=expert'
    render(<PortalFeedAdvicePage />)

    expect(await screen.findByTestId('expert-ration-workspace')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /zur fuetterungsuebersicht/i })).toHaveAttribute(
      'href',
      '/portal/rationsoptimierung',
    )
  })
})

