import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import MaskRolloutRoute from '@/pages/workflow/mask-rollout/MaskRolloutRoute'

vi.mock('@/features/mask-rollouts/rollout-registry', () => ({
  isRolloutPilotEnabled: vi.fn(() => true),
}))

vi.mock('@/pages/workflow/mask-rollout/UniversalMaskRolloutPilotPage', () => ({
  default: ({ screenId, entityId }: { screenId: string; entityId: string }) => (
    <div data-testid="rollout-pilot">{screenId}:{entityId}</div>
  ),
}))

vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => ({ screenId: 'finance__ap-invoice', entityId: 'INV-001' }),
  Navigate: ({ to }: { to: string }) => <div data-testid="navigate">{to}</div>,
}))

describe('MaskRolloutRoute', () => {
  it('normalizes screenId and renders pilot page', async () => {
    render(<MaskRolloutRoute />)
    expect(await screen.findByTestId('rollout-pilot')).toHaveTextContent('finance/ap-invoice:INV-001')
  })
})
