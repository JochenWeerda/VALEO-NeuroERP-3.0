import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/features/sales-masks/sales-order-mask-support', () => ({
  ENABLE_UNIVERSAL_MASK_SALES_ORDER: true,
}))

vi.mock('@/pages/sales/OrderEditorLegacyPage', () => ({
  default: () => <div data-testid="legacy-order-editor">Legacy</div>,
}))

vi.mock('@/pages/sales/sales-order-native', () => ({
  default: () => <div data-testid="sales-sales-order">Native</div>,
}))

vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => ({ id: 'order-1' }),
  useSearchParams: () => [new URLSearchParams()],
}))

describe('SalesOrderEditorPage native switch', () => {
  it('renders the native mask for an existing order when the flag is on', async () => {
    const { default: SalesOrderEditorPage } = await import('@/pages/sales/order-editor')
    render(<SalesOrderEditorPage />)
    expect(await screen.findByTestId('sales-sales-order')).toBeInTheDocument()
    expect(screen.queryByTestId('legacy-order-editor')).not.toBeInTheDocument()
  })
})
