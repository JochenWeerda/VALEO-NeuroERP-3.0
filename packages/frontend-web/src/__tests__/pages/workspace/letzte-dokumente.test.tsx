import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: (props: Record<string, unknown>) => (
    <div data-testid={String(props.testId)} data-screen-id={String(props.screenId)} />
  ),
}))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { delete: vi.fn() } }))

import LetzteDokumentePage from '@/pages/workspace/letzte-dokumente'

describe('LetzteDokumentePage', () => {
  it('uses the central native runtime', () => {
    render(<LetzteDokumentePage />)
    expect(screen.getByTestId('letzte-dokumente')).toHaveAttribute(
      'data-screen-id',
      'workspace/letzte-dokumente',
    )
  })
})
