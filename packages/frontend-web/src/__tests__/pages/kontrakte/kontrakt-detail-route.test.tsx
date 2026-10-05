import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import KontraktDetailRoute from '@/pages/kontrakte/KontraktDetailRoute'

vi.mock('@/features/agrar-masks/kontrakt-mask-support', () => ({
  ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT: false,
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

describe('KontraktDetailRoute switch', () => {
  it('uses the legacy editor when the native flag is disabled', async () => {
    render(<KontraktDetailRoute />)
    expect(await screen.findByTestId('legacy-kontrakt-detail')).toBeInTheDocument()
  })
})
