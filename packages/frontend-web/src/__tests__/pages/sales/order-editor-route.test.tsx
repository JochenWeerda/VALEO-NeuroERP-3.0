import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import SalesOrderEditorPage from '@/pages/sales/order-editor'

vi.mock('@/features/sales-masks/sales-order-mask-support', () => ({
  ENABLE_UNIVERSAL_MASK_SALES_ORDER: false,
}))

vi.mock('@/pages/sales/OrderEditorLegacyPage', () => ({
  default: () => <div data-testid="legacy-order-editor">Legacy</div>,
}))

vi.mock('@/pages/sales/sales-order-native', () => ({
  default: () => <div data-testid="sales-sales-order">Native</div>,
}))

vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => ({ id: 'order-1' }),
  useSearchParams: () => [new URLSearchParams('id=order-1')],
}))

describe('SalesOrderEditorPage route switch', () => {
  it('uses legacy editor when the native flag is disabled', async () => {
    render(<SalesOrderEditorPage />)
    expect(await screen.findByTestId('legacy-order-editor')).toBeInTheDocument()
  })
})
