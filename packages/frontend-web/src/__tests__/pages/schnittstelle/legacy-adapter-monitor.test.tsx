import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: (props: Record<string, unknown>) => (
    <div data-testid={String(props.testId)} data-screen-id={String(props.screenId)} />
  ),
}))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn() } }))

import LegacyAdapterMonitorPage from '@/pages/schnittstelle/legacy-adapter-monitor'

describe('LegacyAdapterMonitorPage', () => {
  it('uses the central native runtime', () => {
    render(<LegacyAdapterMonitorPage />)
    expect(screen.getByTestId('legacy-adapter-monitor')).toHaveAttribute(
      'data-screen-id',
      'schnittstelle/legacy-adapter-monitor',
    )
  })
})
