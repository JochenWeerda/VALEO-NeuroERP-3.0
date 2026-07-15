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

vi.mock('@/features/feed-advice/RationLifecycleWorklist', () => ({
  RationLifecycleWorklist: () => <div data-testid="ration-lifecycle-list">List</div>,
}))

vi.mock('@/features/feed-advice/RationLifecycleDetail', () => ({
  RationLifecycleDetail: ({ rationId }: { rationId: string }) => <div data-testid="ration-lifecycle-detail">{rationId}</div>,
}))

vi.mock('@/features/feed-advice/FeedingBusinessWorklist', () => ({
  FeedingBusinessWorklist: () => <div data-testid="feeding-business-list">Betriebe</div>,
}))

vi.mock('@/features/feed-advice/FeedingGroupDetail', () => ({
  FeedingGroupDetail: ({ groupId }: { groupId: string }) => <div data-testid="feeding-group-detail">{groupId}</div>,
}))

vi.mock('@/features/feed-advice/FeedingReferenceData', () => ({
  FeedingReferenceData: () => <div data-testid="feeding-reference-data">Referenzdaten</div>,
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

  it('routes lifecycle list and detail without loading the solver', () => {
    locationState.search = '?view=rations'
    const { rerender } = render(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('ration-lifecycle-list')).toBeInTheDocument()
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()

    locationState.search = '?view=ration&ration_id=r-42'
    rerender(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('ration-lifecycle-detail')).toHaveTextContent('r-42')
  })

  it('routes inventory readiness through a native screen definition', () => {
    locationState.search = '?view=readiness'
    render(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('native-feed-cockpit')).toHaveTextContent('agrar/feed-readiness')
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()
  })

  it('routes controlling through a native screen definition', () => {
    locationState.search = '?view=controlling'
    render(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('native-feed-cockpit')).toHaveTextContent('agrar/feed-controlling')
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()
  })

  it('routes feeding businesses through the native worklist', () => {
    locationState.search = '?view=businesses'
    render(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('feeding-business-list')).toBeInTheDocument()
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()
  })

  it('routes a feeding group through the native object page', () => {
    locationState.search = '?view=group&group_id=group-42'
    render(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('feeding-group-detail')).toHaveTextContent('group-42')
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()
  })

  it('routes nutrient and unit definitions through the native reference view', () => {
    locationState.search = '?view=reference-data'
    render(<PortalFeedAdvicePage />)
    expect(screen.getByTestId('feeding-reference-data')).toBeInTheDocument()
    expect(screen.queryByTestId('expert-ration-workspace')).not.toBeInTheDocument()
  })
})
