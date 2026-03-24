import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import FlowSpineStudioPage from '@/pages/workflow/flow-spine-studio'

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: () => <div data-testid="agent-process-panel">agent panel</div>,
}))

describe('FlowSpineStudioPage', () => {
  it('rendert den Flow-Spine-Arbeitsraum', () => {
    render(
      <MemoryRouter>
        <FlowSpineStudioPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Flow Spine - Order-to-Cash', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Globale Suche')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Agent' })).toBeInTheDocument()
    expect(screen.getByText('Flow Spine UI')).toBeInTheDocument()
    expect(screen.getAllByTestId('agent-process-panel').length).toBeGreaterThan(0)
  })
})
