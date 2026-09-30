import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('@/features/agrar-masks/kontrakt-mask-support', () => ({
  ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT: true,
}))

vi.mock('@/pages/kontrakte/FrmKontraktDetail', () => ({
  default: () => <div data-testid="legacy-kontrakt-detail">Legacy</div>,
}))

vi.mock('@/pages/agrar/kontrakt-native', () => ({
  default: () => <div data-testid="agrar-kontrakt">Native</div>,
}))

vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => ({ id: 'contract-1' }),
  useSearchParams: () => [new URLSearchParams()],
}))

describe('KontraktDetailRoute native switch', () => {
  it('renders the native mask for an existing contract when the flag is on', async () => {
    const { default: KontraktDetailRoute } = await import('@/pages/kontrakte/KontraktDetailRoute')
    render(<KontraktDetailRoute />)
    expect(await screen.findByTestId('agrar-kontrakt')).toBeInTheDocument()
    expect(screen.queryByTestId('legacy-kontrakt-detail')).not.toBeInTheDocument()
  })
})
