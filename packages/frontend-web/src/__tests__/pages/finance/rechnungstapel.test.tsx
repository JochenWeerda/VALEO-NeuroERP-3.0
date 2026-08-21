import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: (p: Record<string, unknown>) => <div data-testid={String(p.testId)} data-screen-id={String(p.screenId)} /> }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries: vi.fn() }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: vi.fn() } }))
import RechnungstapelPage from '@/pages/finance/rechnungstapel'
describe('RechnungstapelPage', () => {
  it('uses the central native mask runtime', () => {
    render(<RechnungstapelPage />)
    expect(screen.getByTestId('rechnungstapel')).toHaveAttribute('data-screen-id', 'finance/rechnungstapel')
  })
})
